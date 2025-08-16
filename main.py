import os

from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu

from gemini_utility import (load_gemini_pro_model,
                            aura_vision_response,
                            embedding_model_response,
                            aura_response)

# Set custom Streamlit theme via st.markdown (for background, fonts, etc.)
st.markdown("""
    <style>
        body {
            background: linear-gradient(120deg, #e0eafc, #cfdef3);
        }
        .stApp {
            font-family: 'Segoe UI', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #f0f5ff;
        }
        .css-1v0mbdj {  /* Title style */
            color: #4636e3 !important;
        }
        .chat-message {
            border-radius: 8px;
            padding: 8px;
            margin-bottom: 4px;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Aura AI",
    page_icon="🧠",
    layout="wide"
)

# Sidebar with menu
with st.sidebar:
    st.markdown("<div style='text-align: center;'><h1>🧠 Aura AI</h1></div>", unsafe_allow_html=True)
    selected = option_menu("Navigation",
                           ["ChatBot", "Image Captioning", "Embed Text", "Ask me Anything"],
                           menu_icon='robot', icons=['chat-left','card-image','card-text','question-circle'],
                           default_index=0)
    st.markdown("---")
    st.markdown("<div style='text-align: center;'><span style='font-size: 16px; color: gray;'>Your Personal LLM Assistant</span></div>", unsafe_allow_html=True)

# Function to translate role between gemini-pro & streamlit terminology
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# ChatBot Page
if selected == "ChatBot":
    model = load_gemini_pro_model()
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
    st.title("🤖 Aura AI ChatBot")
    st.write("Chat with Aura AI, your intelligent assistant powered by Gemini LLM.")

    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)
    user_prompt = st.chat_input("Ask Aura...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        with st.spinner("Thinking..."):
            aura_response = st.session_state.chat_session.send_message(user_prompt)
        with st.chat_message("assistant"):
            st.markdown(aura_response.text)

# Image Captioning Page
elif selected == "Image Captioning":
    st.title("✨ Picture Perfect Captions")
    st.write("Upload an image and Aura AI will generate a creative caption.")
    uploaded_image = st.file_uploader("Upload an image...", type=["jpg","jpeg","png"], help="Supported formats: jpg, jpeg, png")
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image.resize((800, 500)), caption="Uploaded Image", use_container_width=True)
        if st.button("Generate Caption"):
            with st.spinner("Generating caption..."):
                default_prompt = "Write a Short Caption for this image"
                caption = aura_vision_response(default_prompt, image)
            st.success("✨ Caption: " + caption)
    else:
        st.info("Please upload an image to continue.")

# Text Embedding Page
elif selected == "Embed Text":
    st.title("🔠 Text Embedding")
    st.write("Enter text to get its LLM embedding vector.")
    input_text = st.text_area("Text to embed", placeholder="Enter your text here...", help="Paste any text for embedding")
    if st.button("Get Embeddings"):
        if input_text.strip():
            with st.spinner("Generating embedding..."):
                response = embedding_model_response(input_text)
            st.code(response, language="json")
        else:
            st.warning("Please enter some text.")

# Question-Answering Page
elif selected == "Ask me Anything":
    st.title("❓ Ask Aura Anything")
    st.write("Type your question and get an intelligent answer instantly.")
    user_prompt = st.text_area("Your question", placeholder="Ask Aura...", help="Type any question for Aura AI")
    if st.button("Get an Answer"):
        if user_prompt.strip():
            with st.spinner("Thinking..."):
                response = aura_response(user_prompt)
            st.markdown(response)
        else:
            st.warning("Please enter a question.")

