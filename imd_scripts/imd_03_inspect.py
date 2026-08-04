"""
STEP 3 -- Inspect one full record from the two endpoints ASTRA actually
consumes: cityforecastloc (7-day forecast) and aws_data (real-time station).

Also filter for J&K / Jammu region so we can see what's available near
the study region (approx 32.28 N, 74.75 E, near Jammu city).

Run AFTER imd_02_hit_all_endpoints.py.
Usage: python imd_03_inspect.py
"""

import json, os, sys

CAPTURE_DIR = "imd_captures"

def show_first_record(name):
    path = os.path.join(CAPTURE_DIR, f"{name}.json")
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        return None
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list) or not data:
        print(f"{name}: not a non-empty list")
        return None

    print("=" * 70)
    print(f"{name}: {len(data)} records, first record full structure:")
    print("=" * 70)
    print(json.dumps(data[0], indent=2))
    return data


def find_near_jammu(name, data):
    """Look for stations in J&K or near Jammu lat/lon."""
    if not data:
        return
    print()
    print(f"--- {name}: J&K / Jammu-area records ---")
    matches = []
    for row in data:
        # try common state/district field names
        state_val = str(row.get("STATE", row.get("State", row.get("states", "")))).upper()
        dist_val  = str(row.get("DISTRICT", row.get("District", row.get("State_District", "")))).upper()
        stn_val   = str(row.get("STATION", row.get("Station", row.get("Station_Name", "")))).upper()
        if ("JAMMU" in state_val or "JAMMU" in dist_val or "JAMMU" in stn_val
                or "KASHMIR" in state_val):
            matches.append(row)

    print(f"Found {len(matches)} J&K/Jammu-area records.")
    for m in matches[:5]:
        # show a compact one-liner
        keys_to_show = ["Station_Name", "Station", "STATION", "District",
                        "DISTRICT", "State_District",
                        "Latitude", "Longitude",
                        "Date", "DATE",
                        "CURR_TEMP", "Today_Max_temp", "Past_24_hrs_Rainfall",
                        "RAINFALL", "RH", "Humidity"]
        compact = {k: m[k] for k in keys_to_show if k in m}
        print(json.dumps(compact))


# --- inspect the two ASTRA-critical endpoints ---
for ep in ("cityforecastloc", "aws_data"):
    d = show_first_record(ep)
    find_near_jammu(ep, d)
    print()

# --- also peek at districtwarning for J&K entries ---
print("=" * 70)
print("BONUS: districtwarning J&K entries (for Aarogya Kavach heat-alert future)")
print("=" * 70)
with open(os.path.join(CAPTURE_DIR, "districtwarning.json")) as f:
    dw = json.load(f)
jk = [r for r in dw if "JAMMU" in str(r.get("District", "")).upper()
                    or "KASHMIR" in str(r.get("District", "")).upper()]
print(f"Found {len(jk)} J&K district warnings")
for r in jk[:5]:
    print(json.dumps(r))
