import urllib.request
import urllib.error

req = urllib.request.Request('http://localhost:8000/api/analyze-call', method='OPTIONS')
req.add_header('Origin', 'http://localhost:5173')
req.add_header('Access-Control-Request-Method', 'POST')
req.add_header('Access-Control-Request-Headers', 'content-type')

try:
    resp = urllib.request.urlopen(req)
    print('Status:', resp.getcode())
    print('Headers:', resp.headers)
except urllib.error.URLError as e:
    print('Error:', e)
