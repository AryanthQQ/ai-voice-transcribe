import requests
import json
import time

url = "http://localhost:8000/api/analyze-call"
payload = {
    "voice_url": "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_51018965_31277493_7c84cf5cb0b6/rec_audio_call_51018965_31277493_7c84cf5cb0b6_audio_1782196134722.mp3",
    "adviser_id": "test_adviser",
    "user_id": "test_user"
}
start = time.time()
print(f"Sending request to {url}...")
response = requests.post(url, data=payload)
print(f"Request took {time.time() - start:.2f} seconds.")
try:
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Failed to decode JSON. Raw response:")
    print(response.text)
