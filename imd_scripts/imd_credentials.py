"""
IMD API credentials.

All four imd_* scripts import from this file.
"""

# --- REPLACE THESE THREE VALUES ---
IMD_EMAIL    = "W"
IMD_PASSWORD = "W"
IMD_API_KEY  = "W"   # from the IMD console

# --- Leave the rest alone ---
BASE_URL       = "https://api.imd.gov.in/api/v1"
TOKEN_URL      = "https://api.imd.gov.in/api/oauth/token.php"
TOKEN_CACHE    = "imd_token.json"     # local file; script re-uses until expiry
CAPTURE_DIR    = "imd_captures"       # per-endpoint JSON dumps land here
