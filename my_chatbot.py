# Project: AI Chatbot
# Built by: Arun
# Description: A conversational AI chatbot using Google Gemini API
# Skills used: Python, REST API, Functions, Loops, Dictionaries

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

print("Connected to MongoDB!")

# Conversation history
conversation_history = []

def ask_ai(question):
    conversation_history.append("User: " + question)
    full_conversation = "\n".join(conversation_history)
    
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
    
    response = requests.post(url, json=data)
    result = response.json()
    answer = result["candidates"][0]["content"]["parts"][0]["text"]
    conversation_history.append("AI: " + answer)
    
    conversations.insert_one({
        "user": "Arun",
        "question": question,
        "answer": answer,
        "time": datetime.now()
    })
    
    return answer

print("🤖 Buddy - AI Chatbot with Memory + MongoDB!")
print("Type 'quit' to exit\n")

while True:
    question = input("You: ")
    if question == "quit":
        print("Goodbye Arun!")
        break
    answer = ask_ai(question)
    print("AI:", answer)
    print()