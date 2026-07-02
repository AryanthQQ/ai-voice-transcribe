from gtts import gTTS
import os

tts = gTTS(text="Hello, how can I help you today?", lang='en')
tts.save("test_speech.mp3")

import requests
import json

url = "http://localhost:8000/transcribe"
files = {'file': open('test_speech.mp3', 'rb')}
data = {'language': 'en', 'translate': 'true'}

print("Sending request to /transcribe...")
response = requests.post(url, files=files, data=data)

print(json.dumps(response.json(), indent=2))
