from app.utilities.scan import upload_to_gemini, extract_json, generation_config_scan, possible_food_labels, food_classes
from datetime import datetime
from app.schemas.scan_schema import ScanHistorySchema
from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from botocore.exceptions import NoCredentialsError, ClientError
from sqlalchemy.orm import Session
from app.database import get_db
import boto3
import open_clip
from app.security import  get_user
from app.models.scan_model import ScanHistory
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
import torch.nn.functional as F
# from transformers import CLIPProcessor, CLIPModel
import torch
import os
import io

router = APIRouter(tags=["Scan"])

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
BUCKET_NAME = os.environ["BUCKET_NAME"]

# Configure s3 bucket
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name=os.getenv("REGION"),
)
S3_BASE_URL = f'https://{BUCKET_NAME}.s3.amazonaws.com/'

# #Load the CLIP model and processor from Huggling Face
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load the pretrained CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained=False)

# Load the fine-tuned weights
model.load_state_dict(torch.load('clip_models/clip_finetuned3.pth', map_location=device)) 


# Move the model to the correct device and enter eval mode
model.to(device)
model.eval() 

food_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config_scan,
  system_instruction="I need your response in the form of a json that looks like this. Make sure to check all needed resource and go on the internet if neccessary to get the accurate information for the given food and be very detailed in your responses. I don't want any value to be null, the overall_score should be in percentage, the portion_size_recommendations should be in gram, and others should take their standard units. \n\nYour response should be a JSON in this form:\n\n{\n  \"name\": \"Okro Soup\",\n  \"glycemic_index\": 18,\n  \"calorie_level\": 150,\n  \"diabetic_friendly\": true,\n  \"recommendations\": \"This meal is suitable for diabetic patients. It contains low glycemic index and is rich in fibers.\",\n  \"ingredients\": [\n    \"800g fresh Okro, chopped\",\n    \"200g beef, washed\",\n    \"800g assorted beef & dried cod, washed and cut into small pieces\",\n    \"Smoked fish\",\n    \"2 seasoning cubes (Knorr beef cubes)\",\n    \"2 tbsp locust bean (iru)\",\n    \"Cayenne pepper (use according to your preference)\",\n    \"2-3 tbsp palm oil (optional)\",\n    \"Salt\",\n    \"A tiny bit of Potash (Kaun)\",\n    \"1 small onion\",\n    \"1 tbsp ground crayfish\",\n    \"⅓ cup Ukazi leaves (optional)\",\n    \"Ginger and garlic (optional)\",\n    \"1.5 to 2 cups water/stock\"\n  ],\n  \"instructions\": [\n    \"Chop okra and set aside.\",\n    \"Place a pan on medium heat and add beef, assorted beef, dried cod, salt, seasoning, onion, ginger, garlic, and a little water. Bring to boil until tender.\",\n    \"Separate the stock from the meat and sieve to achieve a clean stock.\",\n    \"Place a clean pan on medium heat, add the stock, beef, assorted beef, and dried fish, and bring to boil for about 3-5 minutes.\",\n    \"Add potash, then the chopped okra. Stir till all is well combined and cook for another minute.\",\n    \"Add crayfish and cayenne pepper. Stir till well combined, add palm oil, stir and cook for about 2 minutes.\",\n    \"Add seasoning and salt, then add ukazi leaves (if using) and smoked mackerel. Cook for another 2-3 minutes.\",\n    \"Serve with your preferred swallow.\"\n  ],\n  \"carbohydrate_content\": 5,\n  \"protein_content\": 20,\n  \"overall_score\": 90,\n  \"fiber_content\": 10\n  \"net_carb\": 15,\n  \"fat\": 10,\n  \"portion_size_recommendations\": 200,\n  \"cholesterol\": 10\n}\n\n",
)

def generate_unique_filename(original_filename: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Extract the file extension
    file_extension = original_filename.split('.')[-1]
    file_name = original_filename.split('.')[0]
    # Construct the unique filename
    return f"{file_name}_{timestamp}.{file_extension}"

def upload_to_s3(file_path: str, bucket_name: str, object_name: str):
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return f"{S3_BASE_URL}{object_name}"
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def delete_image_from_s3(bucket_name: str, object_name: str):
    try:
        s3_client.delete_object(Bucket = bucket_name, Key = object_name)
        print(f"Object {object_name} deleted successfully")
    except NoCredentialsError:
        print("S3 credentials not available")
    except ClientError as e:
        print(f"Error deleting object: {e}")

@router.post("/process-image")
async def process_image(file: UploadFile = File(...), db: Session = Depends(get_db), user:dict = Depends(get_user)):
    try:
        mime_type = file.content_type
        file_extension = mime_type.split('/')[-1]
        image = Image.open(io.BytesIO(await file.read()))
        # image = image.convert("RGB")  # Ensure image is in RGB mode
        # image = image.resize((256, 256))
        file_path = f"temp_image.{file_extension}"
        image.save(file_path)

        input_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension
        input_tensor = input_tensor.to(device)

        # labels = [f"A photo of {label} nigerian food" for label in possible_food_labels]

        # inputs = clip_processor(text=labels, images=image, return_tensors="pt", padding=True)
        # outputs = clip_model(**inputs)
        # logits_per_image = outputs.logits_per_image # this is the image-text similarity score
        # probs = logits_per_image.softmax(dim=1) # we can take the softmax to get the label probabilities

        with torch.no_grad():
            outputs = model(input_tensor)
    
            # If outputs is a tuple, extract the logits (usually the first element)
            if isinstance(outputs, tuple):
                outputs = outputs[0]
    
            # Apply softmax to get probabilities
            probabilities = F.softmax(outputs, dim=1)
    
            # Get the predicted class index and its probability
            _, predicted = torch.max(probabilities, 1)
            predicted_class_index = predicted.item()
            predicted_class_probability = probabilities[0][predicted_class_index].item()
    
        # Print the predicted class index and the corresponding probability
        print(f'Predicted class index: {predicted_class_index}')
        print(f'Probability assigned to predicted class: {predicted_class_probability*100 }')
        print(f'Predicted food: {food_classes[predicted_class_index]}')


        # best_label_idx = torch.argmax(probs, dim=1).item()
        # best_label = possible_food_labels[best_label_idx]
        best_label = food_classes[predicted_class_index]
        # probs[0][best_label_idx].item()

        if predicted_class_probability*100 > 0.4:
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
        result = extract_json(clean_json_string)

        # Upload image to S3 in the 'Scan images/' folder
        filename = generate_unique_filename(file.filename)
        s3_key = f"Scan images/{filename}"
        s3_url = upload_to_s3(file_path, BUCKET_NAME, s3_key)
        result['image'] = ""

        scan_history = ScanHistory(user_id=user.id, scan_result=result)
        db.add(scan_history)
        db.commit()
        db.refresh(scan_history)

        image.close()

        # Now, convert the cleaned string to a JSON object
        return result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan-history", response_model=List[ScanHistorySchema])
async def get_scan_history(db: Session = Depends(get_db), user:dict = Depends(get_user)):
    return db.query(ScanHistory).filter(ScanHistory.user_id == user.id).all()

@router.delete("/scan-history/{scan_id}")
async def delete_scan_history(scan_id: int, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id, ScanHistory.user_id == user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan history not found")
    db.delete(scan)
    db.commit()
    # Delete image form s3 bucket
    image = scan.scan_result["image"]
    s3_key = f"Scan images/{image}"
    delete_image_from_s3(bucket_name=BUCKET_NAME, object_name=s3_key)
   
    return {"detail": f"Scan history deleted successfully {scan}"}
