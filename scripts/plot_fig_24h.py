"""
plot_fig_24h.py
================
Regenerates Fig. 2 of the ASTRA INDICON 2026 paper: 24.5-hour indoor
bench multi-sensor capture from the Layer-1 headed device (Arduino UNO
R4 WiFi + capacitive moisture + DS18B20 + DHT22), sampled at 5-minute
intervals.

Clock started at 17:11:22 IST on the capture date; the plot's time-of-
day axis is derived from that start.

Usage:
    python scripts/plot_fig_24h.py

Deps: pip install pandas numpy matplotlib
Output: figures/ASTRA_fig_24h.png / .pdf
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(HERE, "..", "data", "ASTRA_capture.csv")
OUT_PNG = os.path.join(HERE, "..", "figures", "ASTRA_fig_24h.png")
OUT_PDF = os.path.join(HERE, "..", "figures", "ASTRA_fig_24h.pdf")

df = pd.read_csv(CSV)

# Synthesise timestamp axis from elapsed_s
START = pd.Timestamp("2026-08-03 17:11:22")
df["timestamp"] = START + pd.to_timedelta(df["elapsed_s"], unit="s")

print(f"Loaded {len(df)} rows spanning "
      f"{df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")

# Drop DS18B20 -127 error rows from soil-temp trace only
df_soilt = df[df["soil_temp_c"] > -100].copy()
dropped  = len(df) - len(df_soilt)
print(f"DS18B20 -127 read failures dropped from soil-temp trace: {dropped}")

print("\nChannel statistics (over 24.5 h):")
for src, col, unit in [
        (df,       "moisture_pct", "% VWC"),
        (df_soilt, "soil_temp_c",  "\N{DEGREE SIGN}C"),
        (df,       "air_temp_c",   "\N{DEGREE SIGN}C"),
        (df,       "humidity_pct", "% RH"),
    ]:
    v = src[col]
    print(f"  {col:14s}: min={v.min():7.2f}  max={v.max():7.2f}  "
          f"mean={v.mean():7.2f}  std={v.std():6.2f}  ({unit})")

# ---------- Plot ----------
plt.rcParams.update({
    "font.family":       "serif",
    "font.size":         8,
    "axes.linewidth":    0.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
})

fig, axes = plt.subplots(3, 1, figsize=(3.4, 4.2), dpi=300, sharex=True)

ax = axes[0]
ax.plot(df["timestamp"], df["moisture_pct"], color="C0", linewidth=0.9)
ax.set_ylabel("Soil moist.\n(% VWC)")
ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.6)

ax = axes[1]
ax.plot(df_soilt["timestamp"], df_soilt["soil_temp_c"],
        color="C3", linewidth=0.9, label="Soil (DS18B20)")
ax.plot(df["timestamp"], df["air_temp_c"],
        color="C1", linewidth=0.9, linestyle="--", label="Air (DHT22)")
ax.set_ylabel("Temp. (\N{DEGREE SIGN}C)")
ax.legend(loc="lower left", frameon=False, fontsize=6.5, ncol=2)
ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.6)

ax = axes[2]
ax.plot(df["timestamp"], df["humidity_pct"], color="C2", linewidth=0.9)
ax.set_ylabel("Rel. hum.\n(%)")
ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.6)

axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
axes[-1].set_xlabel("Time of day")

for ax in axes:
    ax.tick_params(axis="both", labelsize=7)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

plt.tight_layout()
plt.subplots_adjust(hspace=0.28)
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
plt.savefig(OUT_PDF, bbox_inches="tight")
print(f"\nSaved: {OUT_PNG}\n       {OUT_PDF}")
