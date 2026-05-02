import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# AI Setup
api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

# MongoDB Setup
mongo_url = os.environ.get("MONGO_URL")
client = MongoClient(mongo_url)
db = client["buddy_chatbot"]
conversations = db["conversations"]

# Page config
st.set_page_config(page_title="Buddy AI", page_icon="🤖")
st.title("🤖 Buddy — Your AI Learning Mentor")
st.caption("Ask me anything about AI!")

# Chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Buddy anything..."):
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build conversation
    full_conversation = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in st.session_state.messages
    ])

    personality = """You are Buddy - a friendly AI mentor 
    who teaches AI concepts to beginners in simple words."""

    data = {
        "contents": [
            {
                "parts": [
                    {"text": personality + "\n\n" + full_conversation}
                ]
            }
        ]
    }

    # Get AI response
    response = requests.post(url, json=data)
    result = response.json()
    answer = result["candidates"][0]["content"]["parts"][0]["text"]

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Save to MongoDB
    conversations.insert_one({
        "user": "Arun",
        "question": prompt,
        "answer": answer,
        "time": datetime.now()
    })