"""
STEP 2 -- Hit every whitelisted endpoint once, save each raw JSON.

Run AFTER imd_01_get_token.py has produced imd_token.json.

For each of the 9 whitelisted endpoints:
    1. GET the endpoint with X-API-KEY + Bearer token
    2. Print HTTP status and first 400 chars of response
    3. If HTTP 200 and JSON: save full raw JSON to imd_captures/<endpoint>.json
    4. Print PASS/FAIL summary at the end

We call each endpoint WITHOUT query parameters first, because the docs
show every endpoint's cURL example with no parameters. If a specific
endpoint requires parameters, IMD will return an error message telling
us which ones -- we'll add those in Step 3.

Usage: python imd_02_hit_all_endpoints.py
"""

import json, os, sys, time
try:
    import requests
except ImportError:
    sys.exit("pip install requests")

from imd_credentials import IMD_API_KEY, BASE_URL, TOKEN_CACHE, CAPTURE_DIR

# --- load cached token ---
if not os.path.exists(TOKEN_CACHE):
    sys.exit(f"{TOKEN_CACHE} not found. Run imd_01_get_token.py first.")

with open(TOKEN_CACHE) as f:
    cache = json.load(f)

if int(time.time()) >= cache["expires_at"]:
    sys.exit("Token expired. Re-run imd_01_get_token.py.")

TOKEN = cache["access_token"]

HEADERS = {
    "X-API-KEY":     IMD_API_KEY,
    "Authorization": f"Bearer {TOKEN}",
    "Accept":        "application/json",
}

os.makedirs(CAPTURE_DIR, exist_ok=True)

# 9 whitelisted endpoints per the IMD API docs
ENDPOINTS = [
    "cityforecast_mapping",
    "districtwarning",
    "staterainfall",
    "stationnowcast",
    "districtrainfall",
    "districtnowcast",
    "cityforecastloc",
    "aws_data",
    "current_wx",
]

results = []
for name in ENDPOINTS:
    url = f"{BASE_URL}/{name}"
    print("=" * 70)
    print(f"GET {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
    except requests.RequestException as e:
        print(f"NETWORK ERROR: {e}")
        results.append((name, "NET-ERR", str(e)[:80]))
        continue

    print(f"HTTP {r.status_code}    {len(r.content)} bytes")
    # first 400 chars of body, whatever it is
    body_preview = r.text[:400].replace("\n", " ")
    print(f"body[:400]: {body_preview}")

    if r.status_code == 200:
        try:
            j = r.json()
            path = os.path.join(CAPTURE_DIR, f"{name}.json")
            with open(path, "w") as f:
                json.dump(j, f, indent=2)
            # count top-level keys or list length so we know what came back
            if isinstance(j, dict):
                shape = f"dict, {len(j)} top-level keys: {list(j.keys())[:6]}"
            elif isinstance(j, list):
                shape = f"list, {len(j)} elements"
            else:
                shape = type(j).__name__
            print(f"SAVED: {path}    shape: {shape}")
            results.append((name, "OK", shape))
        except ValueError:
            print("HTTP 200 but response is not JSON")
            results.append((name, "OK-NOTJSON", body_preview[:80]))
    else:
        results.append((name, f"HTTP-{r.status_code}", body_preview[:80]))

print("=" * 70)
print("SUMMARY:")
for name, status, note in results:
    print(f"  {name:26s}  {status:12s}  {note}")

ok = sum(1 for _,s,_ in results if s == "OK")
print(f"\n{ok}/{len(ENDPOINTS)} endpoints returned JSON.")
print(f"Raw JSON dumps in ./{CAPTURE_DIR}/")
print("\nNext: paste the SUMMARY block back to Claude and we'll pick which")
print("endpoint(s) to parse for the paper.")
