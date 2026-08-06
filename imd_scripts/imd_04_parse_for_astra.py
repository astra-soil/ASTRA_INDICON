"""
STEP 4 (v2) -- Parse Jammu-City forecast from cityforecastloc and compute
              p_t for the ASTRA Algorithm 1.

Run: python imd_04_parse_for_astra.py
"""

import json, os, sys, datetime

CAPTURE_DIR = "imd_captures"

# --------------------------------------------------------------------------
# Explicit mapping: IMD phrase vocabulary -> P(24h rainfall >= 10 mm)
#
# Two independent components combine (max, not sum) to yield p_t:
#   (a) rainfall-intensity cue  (IMD's official rainfall-amount vocabulary)
#   (b) event-frequency cue     (spells / thundershowers / widespread etc.)
# p_t = clamp( max(a, b), 0.05, 0.95 )
#
# This mapping is a design choice of the ASTRA Layer-2 integration,
# documented in Section III-B and Section IV-F. It is revisable
# without touching Algorithm 1.
# --------------------------------------------------------------------------

# Component (a): official IMD rainfall-intensity vocabulary
# https://mausam.imd.gov.in defines these thresholds:
#   very light         <  2.5 mm  -> < 10 mm ceiling: p ~ 0.10
#   light         2.5 - 7.5 mm    -> < 10 mm: p ~ 0.25
#   moderate      7.6 - 35.5 mm   -> >= 10 mm likely: p ~ 0.80
#   rather heavy 35.6 - 64.4 mm   -> >= 10 mm certain: p ~ 0.92
#   heavy        64.5 - 124.4 mm  -> p ~ 0.95
#   very heavy       > 124.5 mm   -> p ~ 0.95
INTENSITY_CUES = [
    ("extremely heavy",  0.95),
    ("very heavy",       0.95),
    ("rather heavy",     0.92),
    ("heavy rain",       0.92),
    ("moderate rain",    0.80),
    ("light rain",       0.25),
    ("very light rain",  0.10),
]

# Component (b): event-frequency / cloud cover cues
EVENT_CUES = [
    ("widespread",             0.75),
    ("a few spells",           0.55),
    ("some spells",            0.55),
    ("one or two spells",      0.35),
    ("thundershower",          0.45),  # thundershowers implicit rain
    ("thunderstorm",           0.45),
    ("cloudy",                 0.20),
    ("partly cloudy",          0.15),
    ("clear sky",              0.05),
]


def phrase_to_p_rain(phrase: str) -> float:
    if not phrase:
        return 0.0
    s = phrase.lower()

    # component (a): pick the strongest intensity match
    p_a = 0.05
    for cue, p in INTENSITY_CUES:
        if cue in s:
            p_a = max(p_a, p)
            break   # ordered strongest-first; take first match

    # component (b): pick the strongest event/cloud match
    p_b = 0.05
    for cue, p in EVENT_CUES:
        if cue in s:
            p_b = max(p_b, p)

    return max(0.05, min(0.95, max(p_a, p_b)))


def load_json(name):
    with open(os.path.join(CAPTURE_DIR, f"{name}.json")) as f:
        return json.load(f)


# --- 1. locate Jammu-City record ---
loc_data = load_json("cityforecastloc")
jammu = None
for row in loc_data:
    if row.get("Station_Name") == "Jammu-City":
        jammu = row
        break

if not jammu:
    sys.exit("Jammu-City not found in cityforecastloc.")

# --- 2. compute p_t and derived quantities ---
today_phrase = jammu.get("Todays_Forecast", "") or ""
p_t = phrase_to_p_rain(today_phrase)

t_max_c = jammu.get("Todays_Forecast_Max_Temp")
t_min_c = jammu.get("Todays_Forecast_Min_temp")
past_rain = jammu.get("Past_24_hrs_Rainfall")
lat, lon = jammu.get("Latitude"), jammu.get("Longitude")
date_str = jammu.get("Date")

# --- 3. locate district warning color for Jammu ---
dw = load_json("districtwarning")
jammu_warn = None
for row in dw:
    if str(row.get("District", "")).upper() == "JAMMU":
        jammu_warn = row
        break

warn_color_map = {"1": "Green (no warning)",
                  "2": "Yellow (be updated)",
                  "3": "Orange (be prepared)",
                  "4": "Red (take action)"}
day1_color = jammu_warn.get("Day1_Color") if jammu_warn else None
day1_color_label = warn_color_map.get(str(day1_color), f"unknown({day1_color})")

# --- 4. print ASTRA-consumable summary ---
print("=" * 70)
print("IMD LIVE FEED SUMMARY -- for ASTRA Algorithm 1 forecast conditioning")
print("=" * 70)
print(f"Endpoint       : https://api.imd.gov.in/api/v1/cityforecastloc")
print(f"Station        : Jammu-City")
print(f"Coordinates    : {lat} N, {lon} E")
print(f"Date of data   : {date_str}")
print(f"Query time     : {datetime.datetime.now().isoformat(timespec='seconds')}")
print()
print(f"Todays_Forecast (raw)      : {today_phrase!r}")
print(f"phrase_to_p_rain(phrase)   : p_t = {p_t:.2f}")
print(f"Todays_Forecast_Max_Temp   : {t_max_c} degC")
print(f"Todays_Forecast_Min_temp   : {t_min_c} degC")
print(f"Past_24_hrs_Rainfall       : {past_rain} mm")
print()
print(f"District warning (Jammu)   : Day1 color = {day1_color} = {day1_color_label}")
print(f"5-day warning colours      : "
      f"{jammu_warn.get('Day1_Color')} / {jammu_warn.get('Day2_Color')} / "
      f"{jammu_warn.get('Day3_Color')} / {jammu_warn.get('Day4_Color')} / "
      f"{jammu_warn.get('Day5_Color')}")
print()
print("This p_t value would be consumed unchanged by Algorithm 1 line 4")
print("('Fetch IMD 24h precipitation forecast p_t').")
print("=" * 70)

# --- 5. also print the 7-day forecast table for the paper appendix ---
print("\n7-day forecast table (for paper Table II):")
print(f"{'Day':<7} {'Max':>5} {'Min':>5}  {'p_t':>4}  {'Forecast phrase':<50}")
print("-" * 78)
day_keys = [("Today", "Todays_Forecast_Max_Temp", "Todays_Forecast_Min_temp",
             "Todays_Forecast")]
for d in range(2, 8):
    day_keys.append((f"Day+{d-1}",
                     f"Day_{d}_Max_Temp",
                     f"Day_{d}_Min_temp",
                     f"Day_{d}_Forecast"))
for lbl, mk, ik, fk in day_keys:
    mx = jammu.get(mk, "-")
    mn = jammu.get(ik, "-")
    ph = (jammu.get(fk) or "-")
    p  = phrase_to_p_rain(ph)
    print(f"{lbl:<7} {str(mx):>5} {str(mn):>5}  {p:>.2f}  {ph[:50]}")

print("\nDone. Paste this output back to Claude.")
