import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def process_with_llm(transcript):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """You are a transcript formatter. 
Given a JSON transcript of a conversation, update the 'text' fields using these rules:
1. If the text is in Hindi (written in Devanagari), transliterate it into colloquial Roman Hinglish (e.g. 'लड़का' -> 'ladka', 'नहीं' -> 'nahi').
2. Keep any English words exactly as they are.
3. If the text is in ANY other regional language (like Marathi, Kannada, Tamil, etc.), TRANSLATE it into English.
4. Maintain the exact JSON structure and array format. Return ONLY the raw JSON array. No markdown, no conversational text.
"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(transcript, ensure_ascii=False)}
        ],
        "temperature": 0.0
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        print(content)
    else:
        print("Error:", response.text)

test_transcript = [
    {"speaker": "Speaker 0", "text": "नहीं, आपकी आवाज़ थोड़ा लड़का, लड़का जैसी लग रही है।", "time": "04:01"},
    {"speaker": "Speaker 1", "text": "लग रही होगी ना। Network problem issue.", "time": "04:05"},
    {"speaker": "Speaker 0", "text": "Network problem कैसे हो सकती है?", "time": "04:08"}
]

process_with_llm(test_transcript)
