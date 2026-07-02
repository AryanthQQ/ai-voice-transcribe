import urllib.request
import json

url = "http://localhost:8000/api/analyze-call"
data = {
    "voice_url": "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_62815017_24874032_b624e6ff6f96/rec_audio_call_62815017_24874032_b624e6ff6f96_audio_1782502095594.mp3",
    "sender_ref_code": "test_sender",
    "reciever_ref_code": "test_receiver"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
