import urllib.request
import tempfile
from pitch_diarize import pitch_diarize

# Download audio
print("Downloading audio...")
voice_url = "https://friendshiphub-live.s3.ap-south-1.amazonaws.com/recordings/getstreamcalls/audio_call_85133471_35297953_46795036ae2b/rec_audio_call_85133471_35297953_46795036ae2b_audio_1782196082989.mp3"
req = urllib.request.Request(voice_url, headers={'User-Agent': 'Mozilla/5.0'})
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
    with urllib.request.urlopen(req) as response:
        temp_audio.write(response.read())
    temp_path = temp_audio.name

# Mock whisper segments (from earlier)
mock_segments = [
    {"start": 2.0, "end": 4.0, "text": "hello hello"},
    {"start": 8.0, "end": 12.0, "text": "han jee batao"},
    {"start": 30.0, "end": 34.0, "text": "dil todkar hasatee hai mera vaphae tumhen yad aaegee"},
]

turns = pitch_diarize(temp_path, mock_segments)
for t in turns:
    print(t)
