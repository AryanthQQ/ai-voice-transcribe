import requests
import json
import time

url = "http://localhost:8000/api/analyze-call"
payload = {
    "voice_url": "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_85133471_35297953_46795036ae2b/rec_audio_call_85133471_35297953_46795036ae2b_audio_1782196082989.mp3",
    "adviser_id": "test_adviser",
    "user_id": "test_user"
}
start = time.time()
print(f"Sending request to {url}...")
max_retries = 10
for i in range(max_retries):
    try:
        response = requests.post(url, data=payload)
        break
    except requests.exceptions.ConnectionError:
        print(f"Server not ready, retrying in 5 seconds... ({i+1}/{max_retries})")
        time.sleep(5)
else:
    print("Failed to connect to the server after multiple retries.")
    exit(1)
print(f"Request took {time.time() - start:.2f} seconds.")
try:
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Failed to decode JSON. Raw response:")
    print(response.text)
