import os
import base64
import streamlit as st
from dotenv import load_dotenv

# Load environment variables prior to importing the agent module
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from agent import app_graph

st.set_page_config(
    page_title="AI Nutrition Studio", 
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Refined UI Styling Theme
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        
        /* Base typography & layout setup */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #f8fafc;
            color: #0f172a;
        }

        .main .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 1050px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
            padding: 1.5rem 1rem;
        }
        
        /* Headers */
        .app-title {
            font-size: 2.25rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: #0f172a;
            margin-bottom: 0.25rem;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .app-subtitle {
            font-size: 1rem;
            color: #64748b;
            margin-bottom: 2rem;
            font-weight: 400;
            line-height: 1.5;
        }

        /* Custom Card Container */
        .settings-card {
            background-color: #f1f5f9;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
        }

        /* Streamlit Chat Messages & Cards */
        [data-testid="stChatMessage"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 1.25rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
            transition: border-color 0.2s ease-in-out;
        }

        [data-testid="stChatMessage"]:hover {
            border-color: #cbd5e1 !important;
        }

        /* Status & Tool Activity Container */
        div[data-testid="stStatusWidget"] {
            border: 1px solid #e2e8f0 !important;
            background-color: #f8fafc !important;
            border-radius: 12px !important;
            padding: 0.6rem 0.85rem !important;
            box-shadow: none !important;
        }

        /* Form Controls & Inputs */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] input {
            border-radius: 8px !important;
            border-color: #cbd5e1 !important;
        }

        /* Chat Input Box */
        div[data-testid="stChatInput"] {
            border-radius: 14px !important;
            border: 1px solid #cbd5e1 !important;
            box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.05) !important;
        }

        /* Image Display */
        img {
            border-radius: 12px !important;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    st.error("OPENAI_API_KEY not found in your .env file. Please add it to continue.")
    st.stop()

st.sidebar.markdown("<h2 style='color: #0f172a; font-weight:700; font-size:1.25rem; margin-bottom:1rem;'>🎯 Profile Settings</h2>", unsafe_allow_html=True)
selected_goal = st.sidebar.selectbox("Dietary Goal", ["General Health", "Weight Loss", "Muscle Gain", "Keto", "Low Sodium", "Cancer Protocol"])
selected_allergies = st.sidebar.text_input("Allergies / Restrictions", "None specified")

st.markdown("<h1 class='app-title'>🥗 AI Nutrition Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Snap a photo or drop food questions below for intent-aware tracking and clinical diet retrieval.</p>", unsafe_allow_html=True)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    if isinstance(msg, (HumanMessage, AIMessage)):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            content = msg.content
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        st.write(item.get("text"))
                    elif item.get("type") == "image_url":
                        st.image(item.get("image_url").get("url"), caption="Attached Meal", width=350)
            else:
                st.write(content)

user_prompt = st.chat_input(
    "Ask a question or upload an image of your meal...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"]
)

if user_prompt:
    text_content = user_prompt.text if hasattr(user_prompt, "text") else str(user_prompt)
    attached_files = user_prompt.files if hasattr(user_prompt, "files") else []
    
    content_payload = []
    if text_content:
        content_payload.append({"type": "text", "text": text_content})
        
    if attached_files:
        for uploaded_file in attached_files:
            buffered = uploaded_file.getvalue()
            base64_image = base64.b64encode(buffered).decode("utf-8")
            image_url = f"data:image/jpeg;base64,{base64_image}"
            content_payload.append({"type": "image_url", "image_url": {"url": image_url}})

    new_message = HumanMessage(content=content_payload if content_payload else text_content)
    st.session_state.chat_messages.append(new_message)
    
    with st.chat_message("user"):
        if text_content:
            st.write(text_content)
        if attached_files:
            for f in attached_files:
                st.image(f, caption="Uploaded Meal", width=350)

    with st.chat_message("assistant"):
        with st.status("Analyzing intent and clinical database...", expanded=False) as status:
            inputs = {
                "messages": st.session_state.chat_messages,
                "dietary_goal": selected_goal,
                "allergies": selected_allergies,
                "intent": ""
            }
            final_response_content = ""
            
            for event in app_graph.stream(inputs, stream_mode="values"):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if isinstance(latest_msg, AIMessage) and latest_msg.content:
                        final_response_content = latest_msg.content

            status.update(label="Analysis Complete", state="complete")
        
        st.write(final_response_content)
        st.session_state.chat_messages.append(AIMessage(content=final_response_content))