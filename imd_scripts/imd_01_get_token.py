"""
STEP 1 -- Get a JWT token from IMD.
Run this first. Token is cached for 1 hour in imd_token.json.

Usage: python imd_01_get_token.py
"""

import json, os, sys, time
try:
    import requests
except ImportError:
    sys.exit("pip install requests   # first, then re-run")

from imd_credentials import (
    IMD_EMAIL, IMD_PASSWORD, TOKEN_URL, TOKEN_CACHE
)

if "your_registered_email" in IMD_EMAIL or "your_password_here" in IMD_PASSWORD:
    sys.exit("Fill IMD_EMAIL and IMD_PASSWORD in imd_credentials.py first.")

payload = {"email": IMD_EMAIL, "password": IMD_PASSWORD}
print(f"POST {TOKEN_URL}")
print(f"body: {{'email': {IMD_EMAIL!r}, 'password': '***'}}")

r = requests.post(TOKEN_URL, json=payload, timeout=15)
print(f"HTTP {r.status_code}")
print("-" * 60)

try:
    body = r.json()
except Exception:
    print("Response was not JSON. Raw text (first 1000 chars):")
    print(r.text[:1000])
    sys.exit(1)

print(json.dumps(body, indent=2)[:800])
print("-" * 60)

if r.status_code != 200:
    sys.exit(f"Token request failed with HTTP {r.status_code}.")

token = body.get("access_token")
if not token:
    sys.exit("No 'access_token' field in response.")

expires_in = body.get("expires_in", 3600)
cache = {
    "access_token": token,
    "expires_at":   int(time.time()) + int(expires_in) - 30,  # 30s safety
    "obtained_at":  int(time.time()),
}
with open(TOKEN_CACHE, "w") as f:
    json.dump(cache, f, indent=2)

print(f"\nOK. Token cached in {TOKEN_CACHE}")
print(f"Valid for ~{expires_in} seconds.")
print(f"Now run:  python imd_02_hit_all_endpoints.py")
