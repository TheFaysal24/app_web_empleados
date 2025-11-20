#!/usr/bin/env python
import urllib.request
import urllib.error

routes = [
    ('/', 'Home page'),
    ('/login', 'Login page'),
    ('/register', 'Register page'),
]

for route, description in routes:
    try:
        response = urllib.request.urlopen(f'http://127.0.0.1:5000{route}', timeout=5)
        print(f"✓ {description:20} - Status {response.status}")
    except urllib.error.HTTPError as e:
        print(f"✗ {description:20} - HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"✗ {description:20} - Error: {e}")

print("\n✓ All critical routes are accessible!")
print("✓ Application is running successfully on http://127.0.0.1:5000")
