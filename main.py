import os
import streamlit as st
import sqlite3
import uuid
import datetime
from PIL import Image
from streamlit_option_menu import option_menu
from gemini_utility import (load_gemini_pro_model,
                            aura_vision_response,
                            embedding_model_response,
                            aura_response,
                            generate_title,
                            aura_response_stream) # Added aura_response_stream
from streamlit_cookies_manager import CookieManager

# --- NEW ROBUST DATABASE LOGIC START ---
# Database functions for saving and retrieving messages
def setup_database():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            title TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
    
# This code block MUST be at the very top of your file after imports.
if 'db_setup_complete' not in st.session_state:
    setup_database()
    st.session_state.db_setup_complete = True

def save_message(user_id, session_id, role, content, title=None):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (user_id, session_id, title, role, content) VALUES (?, ?, ?, ?, ?)",
        (user_id, session_id, title, role, content)
    )
    conn.commit()
    conn.close()

def get_conversation_history(user_id, session_id):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY timestamp ASC",
        (user_id, session_id,)
    )
    history = cursor.fetchall()
    conn.close()
    return history

def get_recent_sessions(user_id):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT session_id, title
        FROM messages
        WHERE user_id = ? AND title IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 10;
    ''', (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

# Function to format database history for Gemini model
def format_history_for_gemini(db_history):
    gemini_history = []
    for role, content in db_history:
        gemini_history.append({"role": role, "parts": [content]})
    return gemini_history

# --- END OF NEW ROBUST DATABASE LOGIC ---

# Main app logic starts here
cookies = CookieManager()
if not cookies.ready():
    st.stop()

if "user_id" not in st.session_state:
    try:
        user_id = cookies["user_id"]
    except KeyError:
        user_id = str(uuid.uuid4())
        cookies["user_id"] = user_id
        cookies.save()
    st.session_state.user_id = user_id
else:
    user_id = st.session_state.user_id


# Set custom Streamlit theme via st.markdown
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
        .css-1v0mbdj {
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
    page_title="Aura AI - by Sameer Prajapati",
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

    st.header("Recent Conversations")
    if st.button("➕ New Chat"):
        if 'session_id' in st.session_state:
            del st.session_state.session_id
        if 'chat_session' in st.session_state:
            del st.session_state.chat_session
        st.rerun()

    recent_sessions = get_recent_sessions(user_id)
    if recent_sessions:
        for session_id, title in recent_sessions:
            if st.button(title or "New Chat", key=session_id):
                st.session_state.session_id = session_id
                if 'chat_session' in st.session_state:
                    del st.session_state.chat_session
                st.rerun()
    st.markdown("---")
    st.markdown("<div style='text-align: center;'><span style='font-size: 16px; color: gray;'>Your Personal LLM Assistant</span></div>", unsafe_allow_html=True)

# Function to translate role between gemini-pro & streamlit terminology
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# ChatBot Page
if selected == "ChatBot":
    model = load_gemini_pro_model()
    
    # Initialize a new session or load an old one
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    st.title("🤖 Aura AI ChatBot")
    st.write("Chat with Aura AI, Your Intelligent Assistant.")

    # Get and display the full conversation history from the database
    full_conversation = get_conversation_history(user_id, st.session_state.session_id)
    for role, content in full_conversation:
        with st.chat_message(translate_role_for_streamlit(role)):
            st.markdown(content)
    
    user_prompt = st.chat_input("Ask Aura...")
    if user_prompt:
        is_new_conversation = not full_conversation
        
        # Display the user message immediately
        st.chat_message("user").markdown(user_prompt)

        with st.spinner("Thinking..."):
            if is_new_conversation:
                generated_title = generate_title(user_prompt)
                save_message(user_id, st.session_state.session_id, "user", user_prompt, title=generated_title)
            else:
                save_message(user_id, st.session_state.session_id, "user", user_prompt)
            
            # Format the full conversation for the model
            formatted_history = format_history_for_gemini(full_conversation)
            
            # Add the current user prompt to the history for the API call
            formatted_history.append({"role": "user", "parts": [user_prompt]})
            
            # Use generate_content with the full history and stream=True
            streamed_response = model.generate_content(formatted_history, stream=True)
            
            # Use a new message container for the assistant's streamed response
            with st.chat_message("assistant"):
                full_response = ""
                message_placeholder = st.empty()
                for chunk in streamed_response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        save_message(user_id, st.session_state.session_id, "model", full_response)

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


# --- Text at the bottom of every page ---
st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True) # Add some space
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Developed by Sameer Prajapati</p>", unsafe_allow_html=True)









