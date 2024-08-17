import google.generativeai as genai
import json
import re


def upload_to_gemini(file_path, mime_type):
    file = genai.upload_file(file_path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def extend_search(text, span):
    # Extend the search to try to capture nested structures
    start, end = span
    nest_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            nest_count += 1
        elif text[i] == '}':
            nest_count -= 1
            if nest_count == 0:
                return text[start:i+1]
    return text[start:end]

def extract_json(text_response):
    # This pattern matches a string that starts with '{' and ends with '}'
    pattern = r'\{[^{}]*\}'
    matches = re.finditer(pattern, text_response)
    json_objects = []
    for match in matches:
        json_str = match.group(0)
        try:
            # Validate if the extracted string is valid JSON
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            # Extend the search for nested structures
            extended_json_str = extend_search(text_response, match.span())
            try:
                json_obj = json.loads(extended_json_str)
                json_objects.append(json_obj)
            except json.JSONDecodeError:
                # Handle cases where the extraction is not valid JSON
                continue
    if json_objects:
        return json_objects[0]
    else:
        return None  # Or handle this case as you prefer

# Create the model
generation_config_scan = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

generation_config_recommendation = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

# possible_food_labels = [
#     "Jollof Rice", "Egusi Soup", "Efo Riro", "Banga Soup", "Ofada Rice and Ofada Sauce",
#     "Edikang Ikong Soup", "Amala and Gbegiri with Ewedu Soup", "Ogbono Soup", "Nkwobi", "Afang Soup",
#     "Tuwo", "Waina Masa", "Fried Plantain", "Miyan Taushe", "Oha Soup", "Beans Porridge and Plantain",
#     "Bitterleaf Soup", "Ofe Nsala", "Suya", "Yam Porridge", "Okra Soup", "Pepper Soup", "Pounded Yam",
#     "Eba", "Garri and Groundnut", "Moi Moi", "Abacha and Ugba", "Adalu", "Rice and Beans", "Fried Rice",
#     "Jollof Rice with Fried Plantain", "Jollof Rice with Moi Moi", "Jollof Rice with Chicken",
#     "Jollof Rice with Beef", "Jollof Rice with Fish", "Egusi Soup with Pounded Yam", "Egusi Soup with Eba",
#     "Egusi Soup with Fufu", "Efo Riro with Pounded Yam", "Efo Riro with Eba", "Efo Riro with Fufu",
#     "Banga Soup with Starch", "Banga Soup with Eba", "Banga Soup with Fufu", "Ofada Rice with Plantain",
#     "Ofada Rice with Moi Moi", "Edikang Ikong Soup with Pounded Yam", "Edikang Ikong Soup with Eba",
#     "Edikang Ikong Soup with Fufu", "Amala with Gbegiri and Ewedu", "Ogbono Soup with Pounded Yam",
#     "Ogbono Soup with Eba", "Ogbono Soup with Fufu", "Afang Soup with Pounded Yam", "Afang Soup with Eba",
#     "Afang Soup with Fufu", "Tuwo with Miyan Taushe", "Fried Plantain with Jollof Rice", "Fried Plantain with Rice",
#     "Miyan Taushe with Tuwo", "Oha Soup with Pounded Yam", "Oha Soup with Eba", "Oha Soup with Fufu",
#     "Beans Porridge with Plantain", "Bitterleaf Soup with Pounded Yam", "Bitterleaf Soup with Eba",
#     "Bitterleaf Soup with Fufu", "Ofe Nsala with Pounded Yam", "Ofe Nsala with Eba", "Ofe Nsala with Fufu",
#     "Suya with Onions and Tomatoes", "Yam Porridge with Plantain", "Okra Soup with Pounded Yam", "Okra Soup with Eba",
#     "Okra Soup with Fufu", "Pepper Soup with Rice", "Pepper Soup with Yam", "Pepper Soup with Plantain",
#     "Pounded Yam with Egusi Soup", "Pounded Yam with Ogbono Soup", "Pounded Yam with Efo Riro",
#     "Eba with Egusi Soup", "Eba with Ogbono Soup", "Eba with Efo Riro", "Garri with Groundnut",
#     "Moi Moi with Jollof Rice", "Moi Moi with Fried Rice", "Abacha with Ugba", "Abacha with Fish", "Adalu with Plantain"
# ]
possible_food_labels = [
    "Jollof Rice", "Egusi Soup", "Efo Riro", "Banga Soup", "ofada rice and ofada sauce", "Amala", "Ofada rice",
    "Edikang Ikong Soup", "Amala and ewedu soup", "Ogbono Soup", "Nkwobi", "Afang Soup (Ukazi soup)", "Tuwo", "Masa (Waina)", "Miyan Taushe",
    "Oha Soup", "Beans porridge and plantain", "Bitterleaf Soup (Ofe Onugbu)", "Ofe Nsala (White soup)", "Suya",
   "Yam", "Okra soup","Pepper Soup", "Eba", "Moin Moin (Bean Pudding)"
]

food_classes = ['Afang Soup',
 'Amala and ewedu soup',
 'Banga Soup',
 'Beans Porridge and Plantain',
 'Bitterleaf Soup (Ofe Onugbu)',
 'Eba',
 'Edikang Ikong Soup',
 'Efo Riro (Stewed Spinach)',
 'Egusi Soup',
 'Fried Plantain',
 'Jellof Rice',
 'Miyan Taushe',
 'Moi Moi (Bean Pudding)',
 'Nkwobi',
 'Ofada Rice and Sauce',
 'Ofe Nsala (White Soup)',
 'Ogbono Soup',
 'Okra Soup',
 'Pepper Soup',
 'Spagetti',
 'Suya',
 'Tuwo',
 'Waina (Masa)',
 'Yam Porridge']