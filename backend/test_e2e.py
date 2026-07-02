import urllib.request
import json
import sys
import time

url = 'http://127.0.0.1:8000/api/analyze-call'
payload = {
    'user_id': 'user_30912',
    'adviser_id': 'adviser_8741',
    'voice_url': 'https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_85133471_35297953_46795036ae2b/rec_audio_call_85133471_35297953_46795036ae2b_audio_1782196082989.mp3'
}

print("Sending POST request to backend...")
start_time = time.time()
req = urllib.request.Request(url, method='POST')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req, data=json.dumps(payload).encode('utf-8')) as response:
        code = response.getcode()
        body = response.read().decode('utf-8')
        elapsed = time.time() - start_time
        print(f"Status: {code}")
        print(f"Elapsed: {elapsed:.2f}s")
        data = json.loads(body)
        print("Success:", data.get("success"))
        if data.get("success"):
            print("Language Detected:", data.get("language"))
            print("Sample Transcript:", data.get("transcript")[:200] if data.get("transcript") else "None")
            print("Metrics:", data.get("metrics"))
            print("Turns Sample:")
            for turn in data.get("turns", [])[:3]:
                print(f"  {turn.get('speaker').capitalize()}: {turn.get('text')}")
        else:
            print("Error:", data.get("error"))
except Exception as e:
    print("Request failed:", e)
