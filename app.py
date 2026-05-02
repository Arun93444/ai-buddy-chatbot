import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

load_dotenv(override=True)
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

# Fix avatar
st.markdown("""
<style>
    .stChatMessage > div:first-child {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif !important; }

.stApp { background-color: #0d0d0f; }

/* Hide streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #141416 !important;
    border-right: 1px solid #2a2a2e !important;
}
section[data-testid="stSidebar"] * { color: #888888 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #f0f0f0 !important; }

/* Logo */
.logo-text {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, #7c6af7, #4fc3f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-sub {
    font-size: 11px;
    color: #888888;
    letter-spacing: 1px;
    margin-top: 2px;
}

.status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    background: #4fc3f7;
    border-radius: 50%;
    margin-right: 5px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Stats */
.stat-card {
    background: #141416;
    border: 1px solid #2a2a2e;
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7c6af7, transparent);
}

.stat-num {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px;
    font-weight: 800;
    color: #f0f0f0;
}

.stat-label {
    font-size: 11px;
    color: #888888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}

.stat-change {
    font-size: 11px;
    color: #a8edcc;
    margin-top: 4px;
}

/* Quick buttons */
.stButton button {
    background: #141416 !important;
    border: 1px solid #2a2a2e !important;
    color: #888888 !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px !important;
}

.stButton button:hover {
    background: #1c1c1f !important;
    border-color: #7c6af7 !important;
    color: #f0f0f0 !important;
    transform: translateY(-1px) !important;
}

/* Chat messages */
.stChatMessage {
    background: #141416 !important;
    border: 1px solid #2a2a2e !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

/* Chat input */
.stChatInput {
    border-top: 1px solid #2a2a2e !important;
    background: #0d0d0f !important;
}

.stChatInput input {
    background: #141416 !important;
    border: 1px solid #2a2a2e !important;
    border-radius: 12px !important;
    color: #f0f0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stChatInput input::placeholder { color: #444444 !important; }
.stChatInput input:focus { border-color: #7c6af7 !important; }

/* Divider */
hr { border-color: #2a2a2e !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0d0f; }
::-webkit-scrollbar-thumb { background: #2a2a2e; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7c6af7; }

/* Hide username avatar text */
.stChatMessage [data-testid="stChatMessageAvatarAssistant"] {display: none !important;}
.stChatMessage [data-testid="stChatMessageAvatarUser"] {display: none !important;}
[class*="avatarImage"] {display: none !important;}
[class*="Avatar"] {display: none !important;}
.eyeqlp51 {display: none !important;}
[class*="avatar"] {display: none !important;}

/* Section labels */
.section-label {
    font-size: 10px;
    color: #444444;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* Badges */
.badge {
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(124,106,247,0.15);
    color: #a89ef5;
    border: 1px solid rgba(124,106,247,0.3);
    display: inline-block;
    margin-right: 6px;
}

.badge-green {
    background: rgba(168,237,204,0.1);
    color: #a8edcc;
    border-color: rgba(168,237,204,0.3);
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="logo-text">Buddy.AI</div>
    <div class="logo-sub">
        <span class="status-dot"></span>Powered by Gemini
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("**Navigation**")
    st.markdown("💬 Chat")
    st.markdown("📚 Learn")
    st.markdown("⚙️ Settings")
    
    st.divider()
    
    st.markdown("**Recent Chats**")
    recent = list(conversations.find().sort("time", -1).limit(8))
    if recent:
        for conv in recent:
            time_str = conv["time"].strftime("%H:%M")
            question = conv["question"][:30] + "..." if len(conv["question"]) > 30 else conv["question"]
            st.markdown(f"`{time_str}` {question}")
    else:
        st.markdown("*No history yet*")
    
    st.divider()
    total = conversations.count_documents({})
    st.markdown(f"**Total:** `{total}` conversations")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Header
st.markdown("""
<div style="text-align:center;padding:20px 0 10px">
    <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;
    background:linear-gradient(135deg,#7c6af7,#4fc3f7);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        Buddy.AI
    </div>
    <div style="color:#888;font-size:0.9rem;margin-top:4px">
        Your Personal AI Learning Mentor
    </div>
    <div style="margin-top:8px">
        <span class="badge">Gemini 2.5</span>
        <span class="badge badge-green">MongoDB Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Stats
total_chats = conversations.count_documents({})
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{total_chats}</div>
        <div class="stat-label">Conversations</div>
        <div class="stat-change">All time</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card" style="border-top:2px solid #4fc3f7">
        <div class="stat-num">🟢</div>
        <div class="stat-label">Status</div>
        <div class="stat-change">Always online</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card" style="border-top:2px solid #a8edcc">
        <div class="stat-num">∞</div>
        <div class="stat-label">Knowledge</div>
        <div class="stat-change">Gemini powered</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick questions
st.markdown('<p class="section-label">Quick Questions</p>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

suggestions = {
    col1: "What is Machine Learning?",
    col2: "How does ChatGPT work?",
    col3: "What is RAG in AI?",
    col4: "How to get an AI job?"
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
       "content": "Hey! I'm **Buddy**, your AI learning mentor!\n\nI'm here to help you learn AI from scratch. Ask me anything!"
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = selected or st.chat_input("Ask Buddy anything about AI...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    full_conversation = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in st.session_state.messages
    ])

    personality = """You are Buddy - a friendly AI mentor who teaches 
    AI concepts to beginners in simple words. Use emojis and 
    simple analogies. Always encourage the user."""

    data = {
        "contents": [
            {
                "parts": [
                    {"text": personality + "\n\n" + full_conversation}
                ]
            }
        ]
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(url, json=data)
            result = response.json()
            if "candidates" in result:
                answer = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                answer = "Sorry, I am having trouble. Please try again!"
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