"""
IMD API credentials TEMPLATE.

Copy this file to `imd_credentials.py`, fill in your own IMD API
credentials, and DO NOT commit `imd_credentials.py` to version control.
The real credentials file is excluded via .gitignore.

Reviewers with their own IMD API access can populate this file and
re-run `imd_01_get_token.py` → `imd_02_hit_all_endpoints.py` to hit
the live endpoints themselves.

Reviewers without IMD access can skip the live-query scripts and
work directly from the raw JSON responses committed under
../imd_captures/, which are the exact 04 Aug 2026 responses cited
in the paper.
"""

# Replace with your own IMD credentials before running.
IMD_EMAIL    = "your_registered_email_here@example.com"
IMD_PASSWORD = "your_password_here"
IMD_API_KEY  = "your_imd_api_key_here"

# Leave these alone unless IMD changes their API surface.
BASE_URL     = "https://api.imd.gov.in/api/v1"
TOKEN_URL    = "https://api.imd.gov.in/api/oauth/token.php"
TOKEN_CACHE  = "imd_token.json"
CAPTURE_DIR  = "../imd_captures"
