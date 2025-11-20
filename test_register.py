import urllib.request
import urllib.error

try:
    print("Accediendo a /register...")
    response = urllib.request.urlopen('http://127.0.0.1:5000/register', timeout=5)
    print(f'✓ Status: {response.status}')
except urllib.error.HTTPError as e:
    print(f'✗ HTTP Error {e.code}: {e.reason}')
    body = e.read().decode()
    print("\n--- Error Response (first 2000 chars) ---")
    print(body[:2000])
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
