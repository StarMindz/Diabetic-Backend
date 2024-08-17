from app.utilities.scan import upload_to_gemini, extract_json, generation_config_scan, possible_food_labels
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from transformers import CLIPProcessor, CLIPModel
import torch
import os
import io

router = APIRouter(tags=["Scan"])

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

#Load the CLIP model and processor from Huggling Face
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


food_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config_scan,
  system_instruction="I need your response in the form of a json that looks like this. Make sure to check all needed resource and go on the internet if neccessary to get the accurate information for the given food and be very detailed in your responses. I don't want any value to be null, the overall_score should be in percentage, the portion_size_recommendations should be in gram, and others should take their standard units. \n\nYour response should be a JSON in this form:\n\n{\n  \"name\": \"Okro Soup\",\n  \"glycemic_index\": 18,\n  \"calorie_level\": 150,\n  \"diabetic_friendly\": true,\n  \"recommendations\": \"This meal is suitable for diabetic patients. It contains low glycemic index and is rich in fibers.\",\n  \"ingredients\": [\n    \"800g fresh Okro, chopped\",\n    \"200g beef, washed\",\n    \"800g assorted beef & dried cod, washed and cut into small pieces\",\n    \"Smoked fish\",\n    \"2 seasoning cubes (Knorr beef cubes)\",\n    \"2 tbsp locust bean (iru)\",\n    \"Cayenne pepper (use according to your preference)\",\n    \"2-3 tbsp palm oil (optional)\",\n    \"Salt\",\n    \"A tiny bit of Potash (Kaun)\",\n    \"1 small onion\",\n    \"1 tbsp ground crayfish\",\n    \"⅓ cup Ukazi leaves (optional)\",\n    \"Ginger and garlic (optional)\",\n    \"1.5 to 2 cups water/stock\"\n  ],\n  \"instructions\": [\n    \"Chop okra and set aside.\",\n    \"Place a pan on medium heat and add beef, assorted beef, dried cod, salt, seasoning, onion, ginger, garlic, and a little water. Bring to boil until tender.\",\n    \"Separate the stock from the meat and sieve to achieve a clean stock.\",\n    \"Place a clean pan on medium heat, add the stock, beef, assorted beef, and dried fish, and bring to boil for about 3-5 minutes.\",\n    \"Add potash, then the chopped okra. Stir till all is well combined and cook for another minute.\",\n    \"Add crayfish and cayenne pepper. Stir till well combined, add palm oil, stir and cook for about 2 minutes.\",\n    \"Add seasoning and salt, then add ukazi leaves (if using) and smoked mackerel. Cook for another 2-3 minutes.\",\n    \"Serve with your preferred swallow.\"\n  ],\n  \"carbohydrate_content\": 5,\n  \"protein_content\": 20,\n  \"overall_score\": 90,\n  \"fiber_content\": 10\n  \"net_carb\": 15,\n  \"fat\": 10,\n  \"portion_size_recommendations\": 200,\n  \"cholesterol\": 10\n}\n\n",
)


@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        mime_type = file.content_type
        file_extension = mime_type.split('/')[-1]
        image = Image.open(io.BytesIO(await file.read()))
        file_path = f"temp_image.{file_extension}"
        image.save(file_path)

        labels = [f"A photo of {label} nigerian food" for label in possible_food_labels]

        inputs = clip_processor(text=labels, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        logits_per_image = outputs.logits_per_image # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1) # we can take the softmax to get the label probabilities


        best_label_idx = torch.argmax(probs, dim=1).item()
        best_label = possible_food_labels[best_label_idx]

        if probs[0, best_label_idx] > 0.8:
            prompt = f"You are to serve as the nutritionist for an app that help diabetic patients get all the needed nutritional information about Nigerian local meals to make better diet decision and determine if the meal is safe for them or not. Get the accurate informations for {best_label}. Be very detailed in your responses"
            response = food_model.generate_content(prompt)
        else:
            files = [
                upload_to_gemini(file_path, mime_type=mime_type),
            ]

            # Assuming start_chat() and send_message() are synchronous
            chat_session = food_model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            files[0],
                        ],
                    },
                ]
            )

            prompt = "You are to serve as the nutritionist for an app that help diabetic patients get all the needed nutritional information about Nigerian local meals to make better diet decision and determine if the meal is safe for them or not. Get the accurate informations for the food image attached to this prompt. Be very detailed in your responses"
            response = chat_session.send_message(prompt)

        clean_json_string = str(response.text).strip('`')

        # Now, convert the cleaned string to a JSON object
        return extract_json(clean_json_string)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))