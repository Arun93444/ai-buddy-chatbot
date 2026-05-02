import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

data = {
    "contents": [{"parts": [{"text": "Say hello!"}]}]
}

response = requests.post(url, json=data)
print(response.json())