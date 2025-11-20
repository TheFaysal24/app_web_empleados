#!/usr/bin/env python
import urllib.request
import urllib.error
import sys

try:
    print("Testing connection to http://127.0.0.1:5000...")
    response = urllib.request.urlopen('http://127.0.0.1:5000', timeout=5)
    print(f"✓ Status: {response.status}")
    html = response.read().decode()
    print(f"✓ Response length: {len(html)} characters")
    print("\n--- First 800 chars ---")
    print(html[:800])
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}")
    try:
        error_body = e.read().decode()
        print("\n--- Error Response ---")
        print(error_body[:800])
    except:
        pass
except urllib.error.URLError as e:
    print(f"✗ URL Error: {e.reason}")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
