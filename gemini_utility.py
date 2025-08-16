import os
import json

import google.generativeai as genai

# Loading the api key securely from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

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
