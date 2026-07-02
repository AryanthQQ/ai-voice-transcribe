import urllib.request
import urllib.parse
import json
import time

url = "http://localhost:8000/api/analyze-call"
data = {
    "sender_ref_code": "agent_123",
    "reciever_ref_code": "cust_456",
    "voice_url": "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_78154535_62551043_345637900926/rec_audio_call_78154535_62551043_345637900926_audio_1782196256613.mp3"
}

encoded_data = urllib.parse.urlencode(data).encode('utf-8')
req = urllib.request.Request(url, data=encoded_data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

start = time.time()
print("Sending request to backend... This may take a while.", flush=True)
try:
    with urllib.request.urlopen(req, timeout=3600) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"Request took {time.time() - start:.2f} seconds", flush=True)
        
        if result.get("success"):
            print("SUCCESS! Transcript:", flush=True)
            for item in result.get("transcript", []):
                print(f"[{item['speaker']}] {item['text']}", flush=True)
        else:
            print(f"FAILED! Error: {result.get('error')}", flush=True)
except Exception as e:
    print(f"Exception occurred: {e}", flush=True)
