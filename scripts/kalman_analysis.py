#!/usr/bin/env python3
"""
kalman_analysis.py
==================
Reproduces the Kalman filter constants reported in ASTRA INDICON 2026,
Section IV-D: R = 0.059 (%VWC)^2, K_ss = 0.336, variance reduction = 58.2%.

Usage:
    python scripts/kalman_analysis.py

Input:  data/ASTRA_capture.csv (295 rows, 5-min sampling)
Output: prints numerical constants to stdout

No dependencies beyond Python 3 stdlib.
"""
import csv, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(HERE, "..", "data", "ASTRA_capture.csv")

def main():
    rows = []
    with open(CSV) as f:
        for x in csv.DictReader(f):
            rows.append({
                "i":   int(x["sample_idx"]),
                "t":   int(x["elapsed_s"]),
                "pct": float(x["moisture_pct"]),
                "st":  float(x["soil_temp_c"]),
            })

    # Drop DS18B20 -127 error row (disclosed in paper Section IV-A)
    rows_clean = [r for r in rows if r["st"] > -100]
    dropped = len(rows) - len(rows_clean)
    print(f"Loaded {len(rows)} rows; dropped {dropped} DS18B20 -127 error(s); "
          f"{len(rows_clean)} clean rows for analysis")

    z = [r["pct"] for r in rows_clean]
    n = len(z)

    # Estimate measurement noise sigma from HP residual of 5-pt MA
    def moving_avg(x, w=5):
        out, half = [], w // 2
        for i in range(len(x)):
            lo = max(0, i-half); hi = min(len(x), i+half+1)
            out.append(sum(x[lo:hi]) / (hi-lo))
        return out
    trend = moving_avg(z, 5)
    resid = [z[i] - trend[i] for i in range(n)]
    sigma = (sum(r*r for r in resid) / (n-1)) ** 0.5
    R = sigma ** 2

    # 1D Kalman filter with paper-specified Q
    Q = 0.01
    xhat = [z[0]]
    P = 1.0
    for k in range(1, n):
        x_pred = xhat[-1]
        P_pred = P + Q
        K = P_pred / (P_pred + R)
        xhat.append(x_pred + K * (z[k] - x_pred))
        P = (1 - K) * P_pred
    K_ss = K

    # Sample-to-sample differential variance reduction
    def diff_var(x):
        d = [x[i]-x[i-1] for i in range(1, len(x))]
        return sum(v*v for v in d) / (len(d)-1)
    var_raw  = diff_var(z)
    var_filt = diff_var(xhat)
    reduction = 100 * (1 - var_filt/var_raw)

    print()
    print("=" * 60)
    print("PAPER-REPORTED CONSTANTS -- reproduced from raw CSV:")
    print("=" * 60)
    print(f"  Measurement noise sigma_hat : {sigma:.3f} % VWC")
    print(f"  R (empirical)               : {R:.5f} (% VWC)^2")
    print(f"  Q (paper-specified)         : {Q}")
    print(f"  Steady-state Kalman gain K  : {K_ss:.4f}")
    print(f"  Sample-diff variance (raw)  : {var_raw:.5f} (% VWC)^2")
    print(f"  Sample-diff variance (filt) : {var_filt:.5f} (% VWC)^2")
    print(f"  Variance reduction          : {reduction:.2f} %")
    print("=" * 60)

    # Paper's expected values (for CI verification)
    expected = [
        ("R",         R,       0.059,   0.001),
        ("K_ss",      K_ss,    0.336,   0.005),
        ("reduction", reduction, 58.2,  0.5),
    ]
    print("\nSanity check against paper's reported values:")
    all_ok = True
    for name, actual, target, tol in expected:
        ok = abs(actual - target) <= tol
        all_ok &= ok
        print(f"  {name:12s}: actual={actual:.4f} vs paper={target}  "
              f"(tol {tol})  {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
