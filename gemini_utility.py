import os
import json

import google.generativeai as genai

# Get the Working directory
working_directory = os.path.dirname(os.path.abspath(__file__))

config_file_path = f"{working_directory}/config.json"
config_data = json.load(open(config_file_path))

# Loading the api key
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]

# Configuring GenAI with api key
genai.configure(api_key=GOOGLE_API_KEY)

# Function to generate content based on user prompt
def load_gemini_pro_model():
    gemini_pro_model = genai.GenerativeModel("gemini-2.5-flash")
    return gemini_pro_model

# Function to caption the image provided by user
def aura_vision_response(prompt, image):
    gemini_vision_model = genai.GenerativeModel("gemini-2.5-flash")
    response = gemini_vision_model.generate_content([prompt, image])
    result = response.text
    return result

# Function to get Embedding text
def embedding_model_response(input_text):
    embedding_model = "models/embedding-001"
    embedding = genai.embed_content(model=embedding_model,
                                    content=input_text,
                                    task_type="retrieval_document")
    embedding_list = embedding["embedding"]
    return embedding_list

# Function to get response
def aura_response(user_prompt):
    gemini_pro_model = genai.GenerativeModel("gemini-2.5-flash")
    response = gemini_pro_model.generate_content(user_prompt)
    result = response.text
    return result

# Function to generate a title using the Gemini model
def generate_title(text):
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Create a very short title, no more than 4 words, for the following text: {text}"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()
