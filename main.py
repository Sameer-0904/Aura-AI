import os

from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu

from gemini_utility import (load_gemini_pro_model,
                            aura_vision_response,
                            embedding_model_response,
                            aura_response)

# Get the Working directory
working_directory = os.path.dirname(os.path.abspath(__file__))

# Setting up the page config
st.set_page_config(
    page_title="Aura AI",
    page_icon="🧠",
    layout="centered"
)

with st.sidebar:
    selected = option_menu("Aura AI",
                           ["ChatBot",
                            "Image Captioning",
                            "Embed Text",
                            "Ask me Anything"],
                           menu_icon='robot', icons=['chat-left','card-image','card-text','question-circle'],
                           default_index=0)

# Function to translate role between gemini-pro & streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return  "assistant"
    else:
        return user_role
#_________________________________________________________________________________

# ChatBot Page
if selected == "ChatBot":
    model = load_gemini_pro_model()

    # Initialize chat session in streamlit if not present
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    # Streamlit page title
    st.title("🤖 ChatBot")

    # Display the Chat History
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask Aura...")

    if user_prompt:
        st.chat_message("user").markdown(user_prompt)

        aura_response = st.session_state.chat_session.send_message(user_prompt)

        # Get Aura's response
        with st.chat_message("assistant"):
            st.markdown(aura_response.text)

#_______________________________________________________________________________________

# Image Captioning Page
if selected == "Image Captioning":
    # streamlit page title
    st.title("Picture Perfect Captions ✨📷")

    uploaded_image = st.file_uploader("Upload an Images...", type=["jpg","jpeg","png"])

    if st.button("Generate Caption"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_image = image.resize((800, 500))
            st.image(resized_image)

        default_prompt = "Write a Short Caption for this image"

        # Getting the response from vision model
        caption = aura_vision_response(default_prompt, image)

        with col2:
            st.info(caption)

#____________________________________________________________________________________________

# Text Embedding Page
if selected == "Embed Text":
    st.title("🔠 Embed Text")

    # Input text box
    input_text = st.text_area(label="", placeholder="Enter the text to get the Embeddings...")

    if st.button("Get Embeddings"):
        response = embedding_model_response(input_text)
        st.markdown(response)

#____________________________________________________________________________________________

# Question-Answering Page
if selected == "Ask me Anything":
    st.title("❓ Ask me a Question")

    # Text box to enter prompt
    user_prompt = st.text_area(label="", placeholder="Ask Aura...")

    if st.button("Get an Answer"):
        response = aura_response(user_prompt)
        st.markdown(response)