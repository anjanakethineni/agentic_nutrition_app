import os
import base64
import streamlit as st
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from agent import app_graph

load_dotenv()

st.set_page_config(
    page_title="Agentic Nutrition Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url('https://googleapis.com');
        
        html, body, [data-testid="stWidgetLabel"] {
            font-family: 'Inter', sans-serif !important;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        [data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0 !important;
            padding-top: 1rem;
        }
        
        .app-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .app-subtitle {
            font-size: 1.1rem;
            color: #64748b;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }

        div[data-testid="stStatusWidget"] {
            border: 1px solid #e2e8f0 !important;
            background-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }

        img {
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    st.error("OPENAI_API_KEY not found in your .env file. Please add it to continue.")
    st.stop()

st.sidebar.markdown("<h2 style='color: #0f172a; font-weight:600; margin-bottom:1rem;'>🎯 Profile Settings</h2>", unsafe_allow_html=True)
selected_goal = st.sidebar.selectbox("Dietary Goal", ["General Health", "Weight Loss", "Muscle Gain", "Keto", "Low Sodium"])
selected_allergies = st.sidebar.text_input("Allergies / Restrictions", "None specified")

st.markdown("<h1 class='app-title'>🥗 AI Nutrition Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Snap a photo or drop food questions directly into the interface bar below for intent-aware tracking calculations.</p>", unsafe_allow_html=True)

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
        with st.status("Agent analyzing customer intent & nutritional graphs...", expanded=False) as status:
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

            status.update(label="Analysis Finished", state="complete")
        
        st.write(final_response_content)
        st.session_state.chat_messages.append(AIMessage(content=final_response_content))
        