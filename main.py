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
    page_title="Aura AI",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for a modern, clean UI
st.markdown("""
    <style>
        .stApp {
            background-color: #eef2f8; /* Lighter blue-gray background for better contrast */
            font-family: 'Segoe UI', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff; /* Use a clean white background */
        }
        .st-emotion-cache-1v3l74s { /* Targeting the sidebar text element */
            color: #1a1a1a;
        }
        h1, .st-emotion-cache-1v0mbdj {
            color: #1a1a1a; /* Darker title color */
            font-weight: 600;
        }
        .st-emotion-cache-1v0mbdj {
            text-align: center;
        }
        .stButton>button {
            border: 1px solid #4B0082;
            color: #4B0082;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #4B0082;
            color: white;
        }
        .chat-message {
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: #1a1a1a; /* Set a dark color for text */
        }
        .chat-message.user {
            background-color: #e6f3ff;
            border: 1px solid #b3d9ff;
        }
        .chat-message.assistant {
            background-color: #f7f9fa;
            border: 1px solid #e0e6ed;
        }
        .st-emotion-cache-1cypcdb { /* Streamlit header padding */
            padding-top: 1rem;
        }
        /* New styles to fix text visibility */
        .st-emotion-cache-19r633d { /* This targets the nav-link text */
            color: #1a1a1a;
        }
        .st-emotion-cache-163v2p5 { /* This targets the text in the chat input */
            color: #1a1a1a;
        }
        .st-emotion-cache-1vb5141 { /* This targets the chat input text and placeholder */
            color: #1a1a1a;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation Menu ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🧠 Aura AI</h1>", unsafe_allow_html=True)
    selected = option_menu("Navigation",
                           ["ChatBot", "Image Captioning", "Embed Text", "Ask me Anything"],
                           menu_icon='robot',
                           icons=['chat-left-dots', 'image', 'code', 'question-circle'],
                           default_index=0,
                           styles={
                               "container": {"padding": "0!important", "background-color": "#ffffff"},
                               "icon": {"color": "#4B0082", "font-size": "20px"},
                               "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#f0f2f6", "color": "#1a1a1a"},
                               "nav-link-selected": {"background-color": "#f0f2f6", "font-weight": "bold", "color": "#4B0082"},
                           })
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Your Personal LLM Assistant</p>", unsafe_allow_html=True)

# --- Helper Function for Chat UI ---
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else "user"

# --- Main Page Content ---

if selected == "ChatBot":
    st.title("🤖 Aura AI ChatBot")
    st.write("Start a conversation with Aura AI, your intelligent assistant.")

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
    st.write("Upload an image, and Aura AI will generate a creative caption for you.")

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
                st.markdown(f"**✨ Caption:** `{caption}`")

elif selected == "Embed Text":
    st.title("🔤 Text Embedding")
    st.write("Enter any text below to get its embedding vector from a large language model.")

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
    st.write("Type your question and get an intelligent answer instantly from Aura AI.")

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
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Developed by Sameer Prajapati</p>", unsafe_allow_html=True)
