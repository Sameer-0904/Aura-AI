
import os
import time

from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu

from gemini_utility import (load_gemini_pro_model,
                            aura_vision_response,
                            embedding_model_response,
                            aura_response)

# --- App Configuration ---
st.set_page_config(
    page_title="Aura AI - Your Personal Assistant",
    page_icon="🧠",
    layout="wide"
)

# Improved CSS for better text visibility and contrast
st.markdown("""
    <style>
        /* App background and font */
        .stApp {
            background-color: #f7f9fc !important; /* Even lighter background */
            font-family: 'Segoe UI', sans-serif !important;
            color: #191919 !important;
        }
        /* Sidebar styles */
        .st-emotion-cache-6qob1r { /* Streamlit sidebar container */
            background-color: #ffffff !important;
            color: #191919 !important;
        }
        .sidebar .sidebar-content,
        .st-emotion-cache-1v3l74s,
        .st-emotion-cache-19r633d {
            background-color: #ffffff !important;
            color: #191919 !important;
        }
        /* Sidebar title */
        .sidebar-title {
            color: #4B0082 !important;
            font-weight: bold !important;
            font-size: 28px !important;
            text-align: center !important;
            margin-bottom: 0.5em !important;
        }
        /* Navigation menu */
        .st-emotion-cache-1cypcdb,
        .st-emotion-cache-19r633d {
            color: #1a1a1a !important;
        }
        /* Main title */
        h1, .st-emotion-cache-1v0mbdj {
            color: #4B0082 !important; /* More visible and on-brand */
            font-weight: 700 !important;
            text-align: center !important;
        }
        /* Subtitles and section headers */
        h2, h3, h4, h5, h6 {
            color: #191919 !important;
            font-weight: 600 !important;
        }
        /* Chat message box improvements */
        .chat-message {
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            color: #191919 !important;
            background-color: #e9effa !important;
        }
        .chat-message.user {
            background-color: #d1ecff !important;
            border: 1px solid #9ad1ff !important;
        }
        .chat-message.assistant {
            background-color: #f0f2f6 !important;
            border: 1px solid #d7dde6 !important;
        }
        /* Buttons */
        .stButton>button {
            border: 1px solid #4B0082;
            color: #4B0082 !important;
            background-color: #ffffff !important;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 17px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #4B0082 !important;
            color: #ffffff !important;
        }
        /* Text areas/input */
        textarea, input, .st-emotion-cache-163v2p5, .st-emotion-cache-1vb5141 {
            color: #191919 !important;
            background-color: #fff !important;
        }
        /* Info/warning/success boxes */
        .stAlert {
            color: #191919 !important;
            background-color: #f0f2f6 !important;
        }
        /* Caption text */
        .caption-text {
            color: #4B0082 !important;
            font-weight: 600 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation Menu ---
with st.sidebar:
    st.markdown("<h1 class='sidebar-title'>🧠 Aura AI</h1>", unsafe_allow_html=True)
    selected = option_menu("Navigation",
                           ["ChatBot", "Image Captioning", "Embed Text", "Ask me Anything"],
                           menu_icon='robot',
                           icons=['chat-left-dots', 'image', 'code', 'question-circle'],
                           default_index=0,
                           styles={
                               "container": {"padding": "0!important", "background-color": "#ffffff"},
                               "icon": {"color": "#4B0082", "font-size": "20px"},
                               "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#f0f2f6", "color": "#191919"},
                               "nav-link-selected": {"background-color": "#e9effa", "font-weight": "bold", "color": "#4B0082"},
                           })
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #4B0082; font-size: 15px;'>Your Personal LLM Assistant</p>", unsafe_allow_html=True)

# --- Helper Function for Chat UI ---
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else "user"

# --- Main Page Content ---
if selected == "ChatBot":
    st.title("🤖 Aura AI ChatBot")
    st.markdown("<h3 style='color:#191919;'>Start a conversation with Aura AI, your intelligent assistant.</h3>", unsafe_allow_html=True)

    model = load_gemini_pro_model()
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
    
    # Display chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Handle user input
    user_prompt = st.chat_input("Ask Aura a question...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        with st.spinner("Aura is thinking..."):
            aura_response = st.session_state.chat_session.send_message(user_prompt)
        with st.chat_message("assistant"):
            st.markdown(aura_response.text)

elif selected == "Image Captioning":
    st.title("🖼️ Image Captioning")
    st.markdown("<h3 style='color:#191919;'>Upload an image, and Aura AI will generate a creative caption for you.</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"], help="Supported formats: jpg, jpeg, png")
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        else:
            st.info("Please upload an image to continue.")

    with col2:
        if uploaded_image:
            if st.button("Generate Caption"):
                with st.spinner("Generating caption..."):
                    default_prompt = "Write a short and creative caption for this image"
                    caption = aura_vision_response(default_prompt, image)
                    time.sleep(1) # Simulate a slight delay for better UX
                st.success("Caption generated!")
                st.markdown(f"<span class='caption-text'>✨ Caption:</span> `{caption}`", unsafe_allow_html=True)

elif selected == "Embed Text":
    st.title("🔤 Text Embedding")
    st.markdown("<h3 style='color:#191919;'>Enter any text below to get its embedding vector from a large language model.</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        input_text = st.text_area("Text to embed", placeholder="Enter your text here...", height=250, help="Paste any text for embedding")
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) # Add some vertical space
        if st.button("Get Embeddings"):
            if input_text.strip():
                with st.spinner("Generating embedding..."):
                    response = embedding_model_response(input_text)
                    time.sleep(1)
                st.success("Embedding generated successfully!")
                st.code(response, language="json")
            else:
                st.warning("Please enter some text.")

elif selected == "Ask me Anything":
    st.title("❓ Ask Aura Anything")
    st.markdown("<h3 style='color:#191919;'>Type your question and get an intelligent answer instantly from Aura AI.</h3>", unsafe_allow_html=True)

    user_prompt = st.text_area("Your question", placeholder="Type your question here...", help="Type any question for Aura AI", height=150)
    
    if st.button("Get an Answer"):
        if user_prompt.strip():
            with st.spinner("Aura is thinking..."):
                response = aura_response(user_prompt)
            st.markdown("---")
            st.info("Answer:")
            st.markdown(response)
        else:
            st.warning("Please enter a question to get an answer.")

# --- Text at the bottom of every page ---
st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True) # Add some space
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4B0082; font-size: 14px;'>Developed by Sameer Prajapati</p>", unsafe_allow_html=True)
