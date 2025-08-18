import os
import json
import streamlit as st

import google.generativeai as genai

# No longer need working_directory, config_file_path, or json.load

# Loading the api key securely from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configuring GenAI with api key
genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_resource(ttl=3600)
def load_gemini_pro_model():
    gemini_pro_model = genai.GenerativeModel("gemini-2.5-flash")
    return gemini_pro_model

def aura_vision_response(prompt, image):
    gemini_vision_model = genai.GenerativeModel("gemini-2.5-flash")
    response = gemini_vision_model.generate_content([prompt, image])
    result = response.text
    return result

def embedding_model_response(input_text):
    embedding_model = "models/embedding-001"
    embedding = genai.embed_content(model=embedding_model,
                                    content=input_text,
                                    task_type="retrieval_document")
    embedding_list = embedding["embedding"]
    return embedding_list

def aura_response(user_prompt):
    gemini_pro_model = genai.GenerativeModel("gemini-2.5-flash")
    response = gemini_pro_model.generate_content(user_prompt)
    result = response.text
    return result

@st.cache_resource(ttl=3600)
def generate_title(text):
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Create a very short title, no more than 4 words, for the following text: {text}"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()
