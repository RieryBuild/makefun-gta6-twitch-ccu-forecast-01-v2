"""Backtest for the GTA VI Twitch CCU forecaster v2 (main.py).

Two out-of-sample checks, both scored with the exact pinball loss from
RULES.txt Scoring (mean over hours x levels of 2*max(tau*d, (tau-1)*d),
d = ln(y) - ln(q)):

1. Leave-one-out over the comparables: every comparable launch with a
   complete release day becomes a pseudo-case (its hour 1 as "known", its
   hours 2..24 as truth, the other comparables as its training set) and is
   forecast by main.forecast_case.  This is the honest, leakage-free check
   and the SELECTION metric: the launch being forecast is never in its own
   training set.  Reported for all 37 launches and for the hour-1 slices
   >= 5,000 / >= 50,000 / >= 100,000 viewers.  The final case's hour 1
   will be a real audience (UK, CET, NZ, Australia and Japan already
   unlocked at 00:00 UTC), so the >= 50,000 slice is the most relevant;
   the all-37 mean is dragged up by launches whose hour 1 was pre-unlock
   noise (prints of 164-4,941 viewers, peaks 90-2,100x hour 1).

2. The four practice cases (p00-p03), scored against their true release-day
   curves.  The truth files are NOT in this repository: pass their directory
   with --truth-dir.  Each file is the SullyGnome "Average viewers" series
   for the launch month, from which the release day's 24 hourly values are
   read (hour 1 is cross-checked against the case's known print).  This is
   a DEV number only: the four practice launches are the dev set, so a
   variant is never selected because it minimises them.

A starter (persistence baseline) implementation and the v1 model (per-hour
log-log OLS, no slope damping, unscaled spread) are included for
comparison; all three are scored through the same code path.

Usage:
    python3 backtest.py [--kit <kit-dir>] [--truth-dir <dir>]
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import main as entry

Z = entry.Z
LEVELS = entry.LEVELS
KIT = Path.home() / "workspace" / "makefun-work" / "gta6-twitch-ccu-forecast-01-kit"


def parse_time(text):
    return datetime.fromisoformat(str(text).replace("Z", "+00:00"))


def pinball(truth_hours, forecast):
    """truth_hours: 23 values for hours 2..24. Returns (loss, miss%, cov)."""
    rows = {row["hour"]: row["q"] for row in forecast["hours"]}
    total = 0.0
    count = 0
    log_miss = []
    covered = 0
    for i, y in enumerate(truth_hours):
        h = i + 2
        y = max(1.0, float(y))
        qs = rows[h]
        for tau, q in zip(LEVELS, qs):
            d = math.log(y) - math.log(max(1e-9, float(q)))
            total += 2.0 * max(tau * d, (tau - 1.0) * d)
            count += 1
        log_miss.append(abs(math.log(y) - math.log(float(qs[2]))))
        if qs[0] <= y <= qs[4]:
            covered += 1
    loss = total / count
    miss = 100.0 * (math.exp(sum(log_miss) / len(log_miss)) - 1.0)
    return loss, miss, covered / len(truth_hours)


def starter_forecast(p1):
    hours = []
    for h in range(2, 25):
        qs = [entry.round2_half_up(p1 * math.exp(z * 0.15 * math.sqrt(h - 1))) for z in Z]
        hours.append({"hour": h, "q": qs})
    return {"hours": hours}


def v1_forecast_case(case):
    """v1 model rebuilt from its description, for comparison only.

    Per-hour log-log OLS (core fit hour-1 >= 5,000, adaptive blend below
    50k), no slope damping, spread = residual SD floored 0.20 / capped
    0.90, unscaled.  Uses entry's parsing helpers, not v1's code.
    """
    curves = entry.comparable_curves(case)
    known = case.get("known") or []
    first = next((k for k in known if k.get("hour") == 1), None)
    p1 = max(1.0, float(first["viewers"])) if first is not None else 1.0
    log_p1 = math.log(p1)
    hours = []
    for h in range(2, 25):
        hi = h - 2
        core = [(p, c) for p, c in curves if p >= 5000.0]
        def fit(sub):
            return entry.least_squares(
                [math.log(p) for p, c in sub if c[hi] is not None],
                [math.log(c[hi]) for p, c in sub if c[hi] is not None],
            )
        cf, af = fit(core), fit(curves)
        mu = sd = None
        if cf and af:
            if p1 >= 50000.0:
                mu, sd = cf[0] + cf[1] * log_p1, cf[2]
            else:
                w = (math.log(50000.0) - log_p1) / (math.log(50000.0) - math.log(5000.0))
                w = max(0.0, min(1.0, w))
                mu = (1 - w) * (cf[0] + cf[1] * log_p1) + w * (af[0] + af[1] * log_p1)
                sd = (1 - w) * cf[2] + w * af[2]
        elif cf or af:
            f = cf or af
            mu, sd = f[0] + f[1] * log_p1, f[2]
        if mu is None:
            ratio = entry.median_log_ratio(curves, hi)
            mu, sd = (log_p1 + ratio, 0.5) if ratio is not None else (log_p1, 0.15 * math.sqrt(h - 1))
        sd = max(0.20, min(0.90, sd))
        qs = []
        prev = 0.0
        for z in Z:
            v = max(1.0, min(1e9, math.exp(mu + z * sd)))
            if v < prev:
                v = prev
            prev = v
            qs.append(entry.round2_half_up(v))
        hours.append({"hour": h, "q": qs})
    return {"hours": hours}


def comparable_as_case(name, day_start, hourly, others):
    """Build a pseudo-case dict for one launch, training on `others`."""
    comps = []
    for other_name, other_start, other_hourly in others:
        comps.append(
            {
                "name": other_name,
                "day_start": other_start,
                "hourly": [
                    {"from": (parse_time(other_start) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"), "viewers": v}
                    for i, v in enumerate(other_hourly)
                ],
            }
        )
    return {
        "known": [{"hour": 1, "viewers": hourly[0], "channels": None, "reads": 1}],
        "forecast": [{"hour": h} for h in range(2, 25)],
        "comparables": comps,
    }


def load_comparable_curves(kit_dir):
    case = json.loads((kit_dir / "input" / "p00.in").read_text(encoding="utf-8"))
    curves = []
    for comp in case["comparables"]:
        start = parse_time(comp["day_start"])
        by_hour = {}
        for point in comp["hourly"]:
            when = parse_time(point["from"])
            off = int((when - start).total_seconds() // 3600)
            if 0 <= off < 24 and point["viewers"] and point["viewers"] > 0:
                by_hour[off + 1] = float(point["viewers"])
        if len(by_hour) == 24:
            curves.append((comp["name"], comp["day_start"], [by_hour[h] for h in range(1, 25)]))
    return curves


def practice_truth(truth_dir, case_id, day):
    """Read a launch month's SullyGnome series and return release-day hours."""
    data = json.loads((Path(truth_dir) / f"{case_id}.json").read_text(encoding="utf-8"))
    labels = data["data"]["labels"]
    series = next(d for d in data["data"]["datasets"] if "Average" in d["label"])["data"]
    idx = labels.index(day + " 00:00")
    return [float(v) for v in series[idx : idx + 24]]


def run_loo(curves):
    rows = []
    for i, (name, start, hourly) in enumerate(curves):
        others = [c for j, c in enumerate(curves) if j != i]
        pseudo = comparable_as_case(name, start, hourly, others)
        t0 = time.perf_counter()
        forecast = entry.forecast_case(pseudo)
        ms = (time.perf_counter() - t0) * 1000.0
        loss, miss, cov = pinball(hourly[1:], forecast)
        v_loss, _, _ = pinball(hourly[1:], v1_forecast_case(pseudo))
        s_loss, _, _ = pinball(hourly[1:], starter_forecast(hourly[0]))
        rows.append((name, hourly[0], loss, miss, cov, v_loss, s_loss, ms))
    return rows


def run_practice(kit_dir, truth_dir):
    rows = []
    specs = [
        ("p00", "2026-09-15"),
        ("p01", "2018-10-26"),
        ("p02", "2022-11-09"),
        ("p03", "2023-10-20"),
    ]
    for case_id, day in specs:
        case = json.loads((kit_dir / "input" / f"{case_id}.in").read_text(encoding="utf-8"))
        truth = practice_truth(truth_dir, case_id, day)
        assert truth[0] == case["known"][0]["viewers"], f"{case_id}: truth hour 1 mismatch"
        t0 = time.perf_counter()
        forecast = entry.forecast_case(case)
        ms = (time.perf_counter() - t0) * 1000.0
        loss, miss, cov = pinball(truth[1:], forecast)
        v_loss, v_miss, v_cov = pinball(truth[1:], v1_forecast_case(case))
        s_loss, s_miss, s_cov = pinball(truth[1:], starter_forecast(truth[0]))
        rows.append((case_id + " " + case["game"]["name"], truth[0], loss, miss, cov, v_loss, s_loss, ms))
        rows[-1] = rows[-1] + (s_miss, s_cov, v_miss, v_cov)
    return rows


def mean(rows, idx):
    return sum(r[idx] for r in rows) / len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", default=str(KIT))
    parser.add_argument("--truth-dir", default="/tmp/practice-truth")
    args = parser.parse_args()
    kit_dir = Path(args.kit)

    curves = load_comparable_curves(kit_dir)
    print(f"comparable curves with a complete release day: {len(curves)}")
    loo = run_loo(curves)
    print("\nLEAVE-ONE-OUT over comparables (v2 vs v1 vs starter, same pseudo-cases)")
    print(f"{'launch':38s} {'p1':>9s} {'v2':>7s} {'v1':>7s} {'d':>7s} {'miss%':>6s} {'cov':>5s} {'starter':>7s} {'ms':>6s}")
    for name, p1, loss, miss, cov, v_loss, s_loss, ms in loo:
        print(f"{name[:38]:38s} {p1:9.0f} {loss:7.4f} {v_loss:7.4f} {loss - v_loss:+7.4f} {miss:6.1f} {cov:5.2f} {s_loss:7.4f} {ms:6.1f}")
    for label, subset in [
        ("LOO all-37", loo),
        ("LOO hour-1 >= 5,000", [r for r in loo if r[1] >= 5000]),
        ("LOO hour-1 >= 50,000", [r for r in loo if r[1] >= 50000]),
        ("LOO hour-1 >= 100,000", [r for r in loo if r[1] >= 100000]),
    ]:
        print(f"{label}: v2 {mean(subset, 2):.4f} (v1 {mean(subset, 5):.4f}, starter {mean(subset, 6):.4f})  "
              f"miss {mean(subset, 3):.1f}%  cov {mean(subset, 4):.3f}  n={len(subset)}")

    truth_dir = Path(args.truth_dir)
    if truth_dir.is_dir():
        prac = run_practice(kit_dir, truth_dir)
        print("\nPRACTICE CASES (true SullyGnome release-day curves; DEV numbers only)")
        print(f"{'case':38s} {'p1':>9s} {'v2':>7s} {'v1':>7s} {'miss%':>6s} {'cov':>5s} {'starter':>7s}")
        for row in prac:
            print(f"{row[0][:38]:38s} {row[1]:9.0f} {row[2]:7.4f} {row[5]:7.4f} {row[3]:6.1f} {row[4]:5.2f} {row[6]:7.4f}")
        print(f"PRACTICE MEAN v2 {mean(prac, 2):.4f} (v1 {mean(prac, 5):.4f}, starter {mean(prac, 6):.4f})  "
              f"miss {mean(prac, 3):.1f}%  cov {mean(prac, 4):.3f}")
    else:
        print(f"\n(truth dir {truth_dir} not found: practice scoring skipped)")


if __name__ == "__main__":
    main()
