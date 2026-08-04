"""
plot_fig_ekf.py
================
Regenerates Fig. 3 of the ASTRA INDICON 2026 paper: one-dimensional
Kalman filter on the real moisture stream.

Usage:
    python scripts/plot_fig_ekf.py

Output: figures/ASTRA_fig_ekf_real.png
"""
import csv, os, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

HERE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(HERE, "..", "data", "ASTRA_capture.csv")
OUT  = os.path.join(HERE, "..", "figures", "ASTRA_fig_ekf_real.png")

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         9,
    "axes.linewidth":    0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "axes.edgecolor":    "#2b2b2b",
    "grid.color":        "#c8c8c8",
    "grid.linestyle":    ":",
    "grid.linewidth":    0.55,
})

C_RAW = "#9a9a9a"
C_KF  = "#b2223a"

rows = []
with open(CSV) as f:
    for x in csv.DictReader(f):
        rows.append({
            "t":   int(x["elapsed_s"]),
            "pct": float(x["moisture_pct"]),
            "st":  float(x["soil_temp_c"]),
        })
rows = [r for r in rows if r["st"] > -100]

t = [r["t"]/3600 for r in rows]
z = [r["pct"] for r in rows]
n = len(z)

# Empirical R from 5-pt HP residual
def moving_avg(x, w=5):
    out, half = [], w // 2
    for i in range(len(x)):
        lo = max(0, i-half); hi = min(len(x), i+half+1)
        out.append(sum(x[lo:hi]) / (hi-lo))
    return out
trend = moving_avg(z, 5)
resid = [z[i] - trend[i] for i in range(n)]
R = sum(v*v for v in resid) / (n-1)
Q = 0.01

xhat = [z[0]]
P = 1.0
for k in range(1, n):
    x_pred = xhat[-1]
    P_pred = P + Q
    K = P_pred / (P_pred + R)
    xhat.append(x_pred + K * (z[k] - x_pred))
    P = (1 - K) * P_pred

def dv(x):
    d = [x[i]-x[i-1] for i in range(1, len(x))]
    return sum(v*v for v in d) / (len(d)-1)
red = 100 * (1 - dv(xhat)/dv(z))

fig, ax = plt.subplots(figsize=(3.5, 2.4))
ax.plot(t, z,    color=C_RAW, lw=0.55, alpha=0.9, label="Raw capacitive")
ax.plot(t, xhat, color=C_KF,  lw=1.1,               label="KF output")
ax.set_xlabel("Elapsed time (h)", fontsize=9)
ax.set_ylabel("Soil moisture (% VWC)", fontsize=9)
ax.set_xlim(0, 25)
ax.set_ylim(50, 72)
ax.xaxis.set_major_locator(MultipleLocator(4))
ax.yaxis.set_major_locator(MultipleLocator(5))
ax.grid(True, which="major", alpha=0.75)

leg = ax.legend(loc="lower right", frameon=True, fontsize=7.5,
                handlelength=1.8, borderpad=0.4)
leg.get_frame().set_edgecolor("#c0c0c0")
leg.get_frame().set_linewidth(0.4)
leg.get_frame().set_facecolor("white")
leg.set_zorder(5)

txt = ("Q = %.2f,  R = %.3f\n"
       "Sample-diff var reduced by %.1f%%\n"
       "Steady-state K = %.3f") % (Q, R, red, K)
ax.text(0.98, 0.97, txt, transform=ax.transAxes,
        ha="right", va="top", fontsize=7,
        color="#2b2b2b", zorder=5,
        bbox=dict(boxstyle="round,pad=0.32",
                  facecolor="white",
                  edgecolor="#c0c0c0", lw=0.4))

plt.tight_layout()
plt.savefig(OUT, dpi=600, bbox_inches="tight")
print(f"Wrote {OUT}")
print(f"Variance reduction: {red:.2f}%")
print(f"R (empirical) = {R:.5f}")
print(f"Steady-state K = {K:.4f}")
