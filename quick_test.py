#!/usr/bin/env python
import urllib.request

routes = [('/', 'Home'), ('/login', 'Login'), ('/register', 'Register')]

for route, name in routes:
    try:
        urllib.request.urlopen(f'http://127.0.0.1:5000{route}', timeout=5)
        print(f"OK {name:15} - Status 200")
    except urllib.error.HTTPError as e:
        print(f"ERROR {name:15} - Status {e.code}")
    except Exception as e:
        print(f"ERROR {name:15} - Error: {e}")
