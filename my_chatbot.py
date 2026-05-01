# Project: AI Chatbot
# Built by: Arun
# Description: A conversational AI chatbot using Google Gemini API
# Skills used: Python, REST API, Functions, Loops, Dictionaries

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

# This list stores the full conversation history
conversation_history = []

def ask_ai(question):
    # Add user question to history
    conversation_history.append("User: " + question)
    
    # Build full conversation as one text
    full_conversation = "\n".join(conversation_history)
    
    # Give it a personality!
    personality = """You are Buddy — a friendly AI mentor 
    who teaches AI concepts to beginners in simple words. 
    You always encourage the user and explain things 
    like a patient teacher."""
    
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
    
    # Add AI answer to history
    conversation_history.append("AI: " + answer)
    
    return answer

print("🤖 AI Chatbot with Memory!")
print("Type 'quit' to exit\n")

while True:
    question = input("You: ")
    if question == "quit":
        print("Goodbye Arun!")
        break
    answer = ask_ai(question)
    print("AI:", answer)
    print()