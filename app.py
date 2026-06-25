import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

mongo_url = os.environ.get("MONGO_URL")
mongo_client = MongoClient(mongo_url)
db = mongo_client["buddy_chatbot"]
conversations = db["conversations"]

st.set_page_config(
    page_title="Buddy AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #212121; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide keyboard_double text */
[data-testid="stSidebarCollapseButton"] {display: none !important;}
button[kind="header"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
section[data-testid="stSidebarCollapseButton"] {display: none !important;}

[data-testid="stChatMessageAvatarAssistant"] {display: none !important;}
[data-testid="stChatMessageAvatarUser"] {display: none !important;}
.stChatMessage > div:first-child {display: none !important;}
[class*="avatar"] {display: none !important;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2a2a2a !important;
}
section[data-testid="stSidebar"] * { color: #ececec !important; }

/* Chat messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 8px 0 !important;
}

/* User message */
.stChatMessage[data-testid="chat-message-user"] {
    background: #2a2a2a !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 12px 16px !important;
    max-width: 75% !important;
    margin-left: auto !important;
}

/* Input */
.stChatInput {
    border-top: 1px solid #2a2a2a !important;
    background: #212121 !important;
    padding: 10px 0 !important;
}
.stChatInput input {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 14px !important;
    color: #ececec !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
.stChatInput input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 1px rgba(124,106,247,0.2) !important;
}
.stChatInput input::placeholder { color: #666 !important; }

/* Buttons */
.stButton button {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    color: #ececec !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    border-color: #7c6af7 !important;
    color: #a89ef5 !important;
    background: rgba(124,106,247,0.08) !important;
}

/* Stats */
.stat-card {
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.stat-num {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #7c6af7, #4fc3f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-lbl { font-size: 11px; color: #8e8ea0; margin-top: 2px; }

hr { border-color: #2a2a2a !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #212121; }
::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7c6af7; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 4px 16px;display:flex;align-items:center;justify-content:space-between">
        <div style="display:flex;align-items:center;gap:10px">
            <div style="width:28px;height:28px;border-radius:6px;
            background:linear-gradient(135deg,#7c6af7,#4fc3f7);
            display:flex;align-items:center;justify-content:center;font-size:14px">🤖</div>
            <span style="font-size:16px;font-weight:700;
            background:linear-gradient(135deg,#7c6af7,#4fc3f7);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent">Buddy.AI</span>
        </div>
        <span style="font-size:18px;color:#8e8ea0;cursor:pointer">✏️</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✏️ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("**TODAY**")
    recent = list(conversations.find().sort("time", -1).limit(5))
    if recent:
        for conv in recent:
            q = conv["question"][:35] + "..." if len(conv["question"]) > 35 else conv["question"]
            st.markdown(f"<div style='padding:7px 10px;border-radius:8px;font-size:13px;color:#ececec;cursor:pointer;margin-bottom:2px;border-left:2px solid #7c6af7'>💬 {q}</div>", unsafe_allow_html=True)

    st.divider()
    total = conversations.count_documents({})
    st.markdown(f"**Total Chats:** `{total}`")

    st.divider()
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 4px">
        <div style="width:32px;height:32px;border-radius:50%;
        background:linear-gradient(135deg,#7c6af7,#4fc3f7);
        display:flex;align-items:center;justify-content:center;
        font-size:13px;font-weight:700;color:#fff">A</div>
        <div>
            <div style="font-size:13px;font-weight:600;color:#ececec">Arun Prasath</div>
            <div style="font-size:11px;color:#8e8ea0">AI Engineer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Top bar
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0">
        <div style="background:#2a2a2a;border:1px solid #3a3a3a;border-radius:8px;
        padding:6px 14px;font-size:14px;font-weight:500;color:#ececec;
        display:inline-flex;align-items:center;gap:8px">
            🤖 Buddy AI
            <span style="font-size:11px;background:linear-gradient(135deg,#7c6af7,#4fc3f7);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:600">
            Gemini 2.5</span> ▼
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="display:flex;gap:8px;justify-content:flex-end;padding:8px 0">
        <span style="font-size:11px;padding:4px 10px;border-radius:20px;
        background:rgba(124,106,247,0.1);color:#a89ef5;
        border:1px solid rgba(124,106,247,0.2)">MongoDB ✓</span>
        <span style="font-size:11px;padding:4px 10px;border-radius:20px;
        background:rgba(79,195,247,0.08);color:#4fc3f7;
        border:1px solid rgba(79,195,247,0.2)">Online 🟢</span>
    </div>
    """, unsafe_allow_html=True)

# Stats
total_chats = conversations.count_documents({})
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="stat-card">
        <span style="font-size:18px">💬</span>
        <div><div class="stat-num">{total_chats}</div><div class="stat-lbl">Total Chats</div></div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="stat-card">
        <span style="font-size:18px">⚡</span>
        <div><div class="stat-num">100%</div><div class="stat-lbl">Uptime</div></div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="stat-card">
        <span style="font-size:18px">🧠</span>
        <div><div class="stat-num">∞</div><div class="stat-lbl">Knowledge</div></div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Quick questions
col1, col2, col3, col4 = st.columns(4)
suggestions = {
    col1: "💡 What is RAG?",
    col2: "🤖 What is AI Agent?",
    col3: "🚀 How to get AI job?",
    col4: "🔥 Fine tuning vs RAG?"
}
selected = None
for col, q in suggestions.items():
    with col:
        if st.button(q):
            selected = q

st.divider()

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
    "role": "assistant",
    "content": "Hey! 👋 I'm **Buddy**, your personal AI mentor.\n\nWhat would you like to learn today?"
})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = selected or st.chat_input("Message Buddy...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    full_conversation = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in st.session_state.messages
    ])

    personality = """You are Buddy — a smart, friendly AI assistant like ChatGPT.

IMPORTANT RULES for answering:
- Give CLEAR and DIRECT answers — not too long, not too short
- Use bullet points for lists
- Use bold for key terms
- Add relevant emojis but don't overdo it
- If question is simple — give short crisp answer
- If question is technical — give structured answer with examples
- Always sound confident and helpful
- Never say "Great question!" or be overly complimentary
- Get straight to the point like ChatGPT does"""

    data = {
        "contents": [{"parts": [{"text": personality + "\n\nConversation:\n" + full_conversation}]}]
    }

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = requests.post(url, json=data)
            result = response.json()
            if "candidates" in result:
                answer = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                answer = "Sorry, I'm having trouble connecting. Please try again!"
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    conversations.insert_one({
        "user": "Arun",
        "question": prompt,
        "answer": answer,
        "time": datetime.now()
    })

    st.rerun()

# Footer
st.markdown("""
<div style="text-align:center;font-size:11px;color:#555;padding:8px 0">
    Buddy AI · Powered by Google Gemini & MongoDB · Built by Arun Prasath
</div>
""", unsafe_allow_html=True)