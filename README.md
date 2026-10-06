# ASTRA reproducibility bundle

**Anonymised repository for double-blind review.** Full author identity, institutional affiliation, and acknowledgements restored at camera-ready.

This repository accompanies the paper:

> **ASTRA: An Explainable Edge-and-App Decision Support Architecture for Water and Fertiliser Optimisation in Indian Smallholder Agriculture**
> Anonymous submission

It contains everything a reviewer needs to independently reproduce the numerical constants and figures reported in **Section IV (Indoor Bench Characterisation)** and the **live IMD-endpoint integration of Section IV-E**.

---

## What this repo lets you check in 60 seconds

```bash
git clone https://github.com/astra-indicon-2026/astra
cd astra
python3 scripts/kalman_analysis.py
```

Expected output (verbatim, matches paper Table I and Section IV-D):

```
Measurement noise sigma_hat : 0.243 % VWC
R (empirical)               : 0.05899 (% VWC)^2
Steady-state Kalman gain K  : 0.3356
Variance reduction          : 58.18 %

Sanity check against paper's reported values:
  R           : PASS
  K_ss        : PASS
  reduction   : PASS
```

If all three checks say `PASS`, the paper's Section IV-D constants are reproducible from the raw CSV in this repo with zero fitted parameters — the only tuning constant `Q = 0.01` is stated in the paper, and `R` is derived from the data.

---

## Layout

```
astra/
├── README.md                             ← this file
├── data/
│   └── ASTRA_capture.csv                 ← raw 24.5 h bench capture
│                                           (295 rows, 5-min sampling,
│                                            columns: sample_idx, elapsed_s,
│                                            moisture_raw, moisture_pct,
│                                            soil_temp_c, air_temp_c, humidity_pct)
├── scripts/
│   ├── kalman_analysis.py                ← reproduces R, K, 58.2% variance reduction
│   ├── plot_fig_24h.py                   ← regenerates paper Fig. 2
│   └── plot_fig_ekf.py                   ← regenerates paper Fig. 3
├── figures/
│   ├── ASTRA_fig_24h.png                 ← paper Fig. 2 (24.5 h capture)
│   └── ASTRA_fig_ekf_real.png            ← paper Fig. 3 (Kalman on real data)
├── imd_scripts/
│   ├── imd_01_get_token.py               ← IMD OAuth JWT bootstrap
│   ├── imd_02_hit_all_endpoints.py       ← queries all 9 whitelisted endpoints
│   ├── imd_03_inspect.py                 ← inspects returned records
│   ├── imd_04_parse_for_astra.py         ← phrase-to-p_t mapping (Section IV-E)
│   └── imd_credentials.example.py        ← template; DO NOT commit real credentials
└── imd_captures/                         ← raw JSON of 04 Aug 2026 IMD queries
    ├── cityforecastloc.json              ← source of Table III
    └── districtwarning.json              ← source of the Y/Y/O/O/O sequence
```

---

## Section-by-section reproduction guide

### Section IV (indoor bench characterisation)

1. `data/ASTRA_capture.csv` is the exact 295-row CSV the paper analyses. Every number in **Table I** (per-channel range and mean), **Fig. 2** (3-panel time series), and **Section IV-B** (physical consistency checks) is computable from it.

2. **Table I** per-channel statistics — verify with:
   ```python
   import csv, statistics as st
   rows = [r for r in csv.DictReader(open("data/ASTRA_capture.csv"))]
   moist = [float(r["moisture_pct"]) for r in rows]
   print(min(moist), max(moist), st.mean(moist))   # 52.85, 70.25, 61.28
   ```

3. **Fig. 2** — `python3 scripts/plot_fig_24h.py` (writes `figures/ASTRA_fig_24h.png`)

4. **Fig. 3 + Section IV-D** — `python3 scripts/kalman_analysis.py` prints R, K, variance reduction; `python3 scripts/plot_fig_ekf.py` writes `figures/ASTRA_fig_ekf_real.png`.

### Section IV-E (live IMD-endpoint validation)

1. `imd_captures/cityforecastloc.json` is the actual JSON blob returned by IMD's `cityforecastloc` endpoint on 04 August 2026 at approximately 18:59 IST. It is a 1.86 MB list of 1,274 station forecasts.

2. To find the Jammu-City record referenced in the paper's Table III:
   ```bash
   python3 -c "import json; d=json.load(open('imd_captures/cityforecastloc.json')); print([r for r in d if r['Station_Name']=='Jammu-City'][0])"
   ```

3. To reproduce the p_t = 0.80 result for `Todays_Forecast = "Generally cloudy sky with moderate rain"`:
   ```bash
   cd imd_scripts && python3 imd_04_parse_for_astra.py
   ```
   (This script uses `../imd_captures/cityforecastloc.json` — no live IMD call required.)

4. The paper's Table II (phrase-to-p_t mapping) is implemented in `imd_scripts/imd_04_parse_for_astra.py`, functions `INTENSITY_CUES` and `EVENT_CUES`. Read the source; it is 20 lines.

### Section V (paired-realisation simulation)

Simulation source code is not currently included in this bundle because it references an older internal test harness. A cleaned, self-contained version will be added as `scripts/paired_simulation.py` and released with the camera-ready version alongside the restored author identity. The simulation parameters listed in Section V (soil physics, Hargreaves ET_0, K_c, gamma rainfall distribution, baseline policy) are sufficient to re-implement from the paper text alone.

---

## Live IMD API calls

The paper's Section IV-E was executed on 04 August 2026 against IMD's live `https://api.imd.gov.in/api/v1` endpoint. Reviewers wishing to re-execute the live call themselves would need:

- Their own IMD API key (issued individually and IP-bound; see [IMD API documentation](https://api.imd.gov.in/))
- Fill in `imd_scripts/imd_credentials.py` (**not included in this repo** for obvious reasons)
- Run `imd_01_get_token.py` → `imd_02_hit_all_endpoints.py`

For reviewers who do not have their own IMD credentials: the raw JSON captured on 04 August 2026 is included in `imd_captures/` so the parsing logic and phrase-to-p_t mapping can be verified against the exact response the paper cites.

---

## Data-provenance note

- The 295-row moisture CSV was captured on a physical Arduino UNO R4 WiFi + DS18B20 + DHT22 + capacitive-soil-moisture rig by a Python logger writing every 5 minutes using `os.fsync` after each row. Capture started 17:11:22 IST on 03 August 2026 and ran for 24.5 hours.
- Row index 57 (`elapsed_s = 17100`, ≈21:56 IST) is a DS18B20 `-127.0 °C` 1-Wire read failure. This row is disclosed in Section IV-A of the paper and is dropped by `kalman_analysis.py`. It is retained in the CSV so that reviewers can verify the drop is legitimate rather than assumed away.
- No values in the CSV have been synthesised, imputed, interpolated, or filtered before analysis.

---

