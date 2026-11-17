# Backtest — GTA VI Twitch CCU forecaster v2

Model: per-hour log-log OLS, `ln y_h = a_h + b_h * ln p1`, fitted at run
time from the case's own comparables, with the slope shrunk toward 1
(`b' = 1 + k*(b - 1)`, intercept refit at the training mean) and `k`
tapering from 1.0 at hour-1 prints ≤ 5,000 to 0.7 at prints ≥ 50,000;
core fit hour-1 ≥ 5,000, adaptive blend below 50k as in v1; spread =
per-hour residual SD × 0.85, floored 0.20 / capped 0.90. See `main.py`.

Scoring everywhere below is the exact RULES.txt pinball loss on the log
scale: mean over hours x levels of `2 * max(tau*d, (tau-1)*d)` with
`d = ln(y) - ln(q)`. Typical miss = `100 * (exp(mean |ln y - ln q50|) - 1)`.
Coverage = share of hours with `q05 <= y <= q95` (honest ≈ 0.9).

## 1. Practice cases (p00–p03) — DEV numbers only

The practice `.in` files hold no truth for hours 2–24, so the truth was
read from SullyGnome's public "Average viewers" series for each launch
month (the documented endpoint in the kit's `input/NOTICE.txt`, one
targeted read per launch). Hour 1 of each fetched series matches the
case's known print exactly (23,357 / 116,550 / 269,517 / 119,087),
confirming the series is the dev answer. These truth files live outside
this repository (`/tmp`, validation only) and are **not** used by `main.py`
in any way — the entry never sees them.

**These are dev numbers, not the selection criterion.** The four practice
launches are the dev set: a variant was never adopted because it
minimised them. Selection used §2 (leave-one-out over the comparables).
Several variants below improved this table while worsening §2 and were
rejected for exactly that reason — that is the dev-set trap at small
scale, and §5 names them.

| case | hour-1 print | v2 loss | v1 loss | typical miss | 90% cov | starter loss |
|---|---|---|---|---|---|---|
| p00 Marvel's Wolverine | 23,357 | 0.2507 | 0.2286 | 53.2% | 0.96 | 0.7437 |
| p01 Red Dead Redemption 2 | 116,550 | 0.2025 | 0.2107 | 43.4% | 0.96 | 0.2868 |
| p02 God of War Ragnarök | 269,517 | 0.1259 | 0.1508 | 19.1% | 1.00 | 0.2146 |
| p03 Marvel's Spider-Man 2 | 119,087 | 0.1839 | 0.1899 | 31.2% | 0.83 | 0.3033 |
| **mean** | | **0.1908** | **0.1950** | **36.7%** | **0.935** | **0.3871** |

The starter's 0.3871 reproduces the house baseline's published ~0.387,
which validates the scoring implementation end to end. v2 improves the
practice mean 0.1950 → 0.1908 (−2.2%), driven by the three big-print
cases; p00 (the smallest practice print, 23,357) regresses 0.2286 →
0.2507, because the slope damping trims the explosive growth a small
hour 1 can still produce. The final case will not be a small-print
launch (see §2), so that regression is accepted and disclosed, not
hidden.

## 2. Leave-one-out over the 37 comparables — the selection metric

Each comparable launch with a complete release day becomes a pseudo-case
(its hour 1 as "known", hours 2–24 as truth, the other 36 comparables as
its training set). The forecast launch is never in its own training set,
so this is leakage-free. Run with `python3 backtest.py`. v1's numbers are
scored through the same code path (a from-description rebuild of v1 in
`backtest.py`, not v1's code).

| launch | hour-1 | v2 loss | v1 loss | Δ | miss% | cov | starter |
|---|---:|---:|---:|---:|---:|---:|---:|
| ELDEN RING | 875,155 | 0.0975 | 0.1311 | −0.0336 | 6.7 | 1.00 | 0.2108 |
| Resident Evil Requiem | 46,345 | 1.1040 | 1.0145 | +0.0895 | 287.7 | 0.13 | 1.2729 |
| Hogwarts Legacy | 387,358 | 0.1441 | 0.1558 | −0.0117 | 22.8 | 1.00 | 0.2881 |
| Cyberpunk 2077 | 851,999 | 0.1309 | 0.1423 | −0.0114 | 18.0 | 1.00 | 0.2299 |
| Ghost of Yōtei | 27,206 | 0.1639 | 0.1754 | −0.0115 | 21.1 | 0.96 | 0.4734 |
| Monster Hunter Wilds | 152,314 | 0.4115 | 0.4188 | −0.0073 | 89.3 | 0.61 | 0.4273 |
| Black Myth: Wukong | 4,941 | 1.6497 | 1.6190 | +0.0307 | 678.9 | 0.39 | 3.4340 |
| Hollow Knight: Silksong | 164 | 0.5567 | 0.5470 | +0.0097 | 135.5 | 0.74 | 3.9411 |
| Battlefield 6 | 2,470 | 0.4189 | 0.4120 | +0.0070 | 92.0 | 0.78 | 2.4065 |
| Call of Duty: Black Ops 6 | 139,097 | 0.2060 | 0.2226 | −0.0166 | 45.5 | 0.96 | 0.2620 |
| Call of Duty: Modern Warfare III | 114,417 | 0.1230 | 0.1345 | −0.0115 | 18.5 | 1.00 | 0.1520 |
| Call of Duty: Black Ops 7 | 79,207 | 0.1046 | 0.1205 | −0.0159 | 10.6 | 1.00 | 0.1733 |
| Call of Duty: Modern Warfare 4 | 59,162 | 0.1113 | 0.1200 | −0.0087 | 13.1 | 1.00 | 0.2361 |
| 007 First Light | 127,800 | 0.2593 | 0.2428 | +0.0165 | 59.5 | 0.83 | 0.3484 |
| Forza Horizon 6 | 26,312 | 0.1263 | 0.1437 | −0.0174 | 12.9 | 1.00 | 0.4098 |
| Marathon | 1,393 | 1.2486 | 1.2076 | +0.0410 | 384.6 | 0.39 | 1.7452 |
| Saros | 6,400 | 0.5764 | 0.5823 | −0.0059 | 133.9 | 0.70 | 0.6011 |
| The Legend of Zelda: Tears of the Kingdom | 129,948 | 0.2181 | 0.2302 | −0.0122 | 50.6 | 1.00 | 0.3087 |
| Starfield | 156,828 | 0.3787 | 0.3262 | +0.0525 | 86.6 | 0.52 | 0.2909 |
| Baldur's Gate 3 | 3,447 | 0.5046 | 0.4979 | +0.0067 | 142.5 | 0.91 | 2.1768 |
| Diablo IV | 533,455 | 0.1358 | 0.1888 | −0.0530 | 21.9 | 1.00 | 0.1254 |
| Borderlands 4 | 133,568 | 0.2726 | 0.2552 | +0.0174 | 62.2 | 0.91 | 0.2529 |
| Kingdom Come: Deliverance II | 414 | 0.4873 | 0.4695 | +0.0177 | 124.7 | 0.57 | 3.4638 |
| Assassin's Creed Shadows | 146,993 | 0.3104 | 0.2793 | +0.0311 | 70.0 | 0.70 | 0.3452 |
| DOOM: The Dark Ages | 50,351 | 0.2710 | 0.2956 | −0.0246 | 60.1 | 0.83 | 0.2564 |
| Elden Ring Nightreign | 319,909 | 0.1686 | 0.1453 | +0.0233 | 37.7 | 1.00 | 0.2516 |
| Clair Obscur: Expedition 33 | 10,639 | 0.2207 | 0.2267 | −0.0060 | 42.5 | 1.00 | 1.1450 |
| Death Stranding 2: On the Beach | 42,221 | 0.2025 | 0.2319 | −0.0294 | 38.0 | 0.91 | 0.1762 |
| FINAL FANTASY VII REBIRTH | 53,526 | 0.1302 | 0.1524 | −0.0222 | 19.9 | 1.00 | 0.1734 |
| The Last of Us Part II | 365,019 | 0.1258 | 0.1478 | −0.0219 | 15.1 | 0.91 | 0.2470 |
| Ghost of Tsushima | 131,910 | 0.1271 | 0.1460 | −0.0188 | 21.8 | 1.00 | 0.2283 |
| Halo Infinite | 20,526 | 0.6477 | 0.6513 | −0.0036 | 152.6 | 0.61 | 0.6314 |
| Forza Horizon 5 | 43,895 | 0.3290 | 0.3505 | −0.0215 | 74.0 | 0.74 | 0.3248 |
| Stellar Blade | 27,057 | 0.1591 | 0.1848 | −0.0258 | 27.8 | 1.00 | 0.3725 |
| ARC Raiders | 1,410 | 0.8807 | 0.8591 | +0.0216 | 263.8 | 0.61 | 3.3766 |
| Marvel Rivals | 165,939 | 0.2577 | 0.2370 | +0.0207 | 53.9 | 0.83 | 0.2097 |
| HELLDIVERS 2 | 419 | 0.5748 | 0.5628 | +0.0120 | 132.6 | 0.70 | 3.4288 |

| slice | v2 | v1 | starter | typical miss (v2) | 90% cov (v2) |
|---|---:|---:|---:|---:|---:|
| all 37 | 0.3739 | 0.3737 | 0.9297 | 95.4% | 0.817 |
| hour-1 ≥ 5,000 (n=29) | **0.2591** | 0.2639 | 0.3595 | 54.3% | 0.867 |
| hour-1 ≥ 50,000 (n=20) | **0.1992** | 0.2046 | 0.2509 | 39.2% | 0.904 |
| hour-1 ≥ 100,000 (n=16) | **0.2104** | 0.2127 | 0.2611 | 42.5% | 0.891 |

Paired comparison (v2 − v1 per launch): v2 wins on 22 of 37 launches;
mean paired Δ −0.0048 on hour-1 ≥ 5,000 and −0.0054 on hour-1 ≥ 50,000.
The wins concentrate in the biggest launches (ELDEN RING −0.034, Diablo
IV −0.053, The Last of Us Part II −0.022), where the slope damping stops
the unshrunk fit over-extrapolating; the losses concentrate in launches
whose curves genuinely exploded past what hour 1 predicted (Resident
Evil Requiem +0.090, Starfield +0.053) and in the pre-unlock-noise
launches below 5,000, where damping trims real growth.

Why the ≥ 50,000 slice is the relevant one for the final: at 00:00 UTC
on 19 Nov the UK, central Europe, New Zealand, Australia and Japan are
already unlocked, so GTA VI's hour 1 will be a real audience, not
pre-unlock noise — certainly above 50,000 (the category already reads
~1,240 viewers before release, and the launch is the largest in the
comparables' history). The all-37 mean is reported for completeness; it
is dominated by eight launches whose hour 1 was pre-unlock noise and
cannot occur for the final case.

Caveat on the size of the gain: the improvement is real but modest
(−2.6% on the ≥ 50,000 slice) and uneven. A split-half check of the
37 launches (first/second half by name; odd/even index) shows v2 winning
clearly in two halves (≥ 50,000: 0.1826 vs 0.1898; 0.1687 vs 0.1834)
and flat-to-slightly-worse in the other two (0.2376 vs 0.2374; 0.2241 vs
0.2220). The gain is driven by a handful of large launches, not by a
uniform improvement. Nothing here promises a final result: the final's
truth is one unobserved launch day.

## 3. Why the dev top 20 are ~0.001 (Investigation #1, carried from v1)

The gap is **not** a hidden structure in the input files. Verified facts:

- The case files contain no leakage: every practice case's `history` ends
  at its checkpoint, and the comparables exclude all four practice launches.
- The dev answers are **public historical data**: the four practice launches
  are past SullyGnome curves, fetchable from the endpoint the kit's own
  `input/NOTICE.txt` documents. Any entry can look up the four true
  release-day curves and replay them (matched by game name / hour-1 print)
  with a razor-thin spread, scoring ~0.000x with typical miss 0% and
  coverage 1.0.
- The live dev board confirms it: 176 entries score ≤ 0.01, then a cliff —
  the honest cluster starts around 0.12 (first loss ≥ 0.12 is rank 252).
  The top titles say it themselves: "memorized practice curves",
  "verified practice answers", "known-curve replay", "practice-anchored".
- The final cannot be won that way: h00's truth is the live 19 Nov
  recording, in no input file and in no public dataset. A memorised-practice
  entry falls back to whatever honest model it ships (or persistence) on
  the final and scores like one. This entry therefore ships **only the
  honest model** — no practice answers are stored anywhere in the
  repository (verified: none of the 92 distinctive hours-2–24 truth values
  appears in any repo file) — and is judged on the numbers in §1–2 above,
  not on the dev board's memorised top.

The honest cluster's leaders (~0.12) use, by their own titles, LOO-stacked
log-space ensembles with per-hour bias correction, Holt-smoothed kernels,
shrunk-slope OLS with US-unlock bias correction, and regime-weighted ridge
forecasters. The principles behind those titles were tested here as
variants (see §5); the ones that survived the LOO arbiter are the
shrunk slope and the calibrated spread that v2 ships. The remaining gap
to 0.12 on the practice set is not claimed as reachable by this model:
several of the leaders' named ingredients ("practice-bias correction")
are, on their face, tuned to the four practice launches.

## 4. How the held-out split was built

- Source: the 38 comparables in the kit's `p00.in` (all four practice
  cases carry the same comparable set). One of them — the Grand Theft
  Auto VI category's own pre-release history (day_start 2026-08-27) —
  has no complete release day and is excluded, leaving 37 launches.
- Each launch's release-day curve is its 24 hourly SullyGnome points from
  its `day_start` (00:00 UTC of its release date). A launch counts only
  when all 24 hours are present and positive.
- For each held-out launch, the pseudo-case's `comparables` are the other
  36 launches' day curves, in the case-file format; the forecast is
  `main.forecast_case` on that pseudo-case, unchanged. Nothing about the
  held-out launch — its name, its curve, its hour-1 print beyond the
  pseudo-case's `known` row — enters the fit.
- Slices are by the held-out launch's own hour-1 print (≥ 5,000 / ≥ 50,000
  / ≥ 100,000), decided before any variant was measured, because the
  final's hour 1 is known in advance to be large. No slice was chosen
  after seeing results.
- The practice cases are a second, independent held-out check (the four
  practice launches are excluded from every case's comparables), but with
  n = 4 they are reported as dev numbers only and never used to select a
  variant.

## 5. Iteration log (self-critique cycles, all measured on LOO)

All numbers are LOO hour-1 ≥ 5,000 unless stated; v1 baseline 0.2639,
practice 0.1950. "LOO" = the §2 check; "practice" = the §1 dev number.

- **Round 1 — spread variants.** LOO-residual spread (within-training
  LOO residual SD per hour): LOO 0.2879, practice 0.2325 — worse on both.
  Empirical LOO-residual quantiles per hour: LOO 0.2766, practice 0.2117 —
  worse. Within-training LOO bias correction + LOO spread: LOO 0.2905.
  Kernel-weighted local OLS (bw 1.0) + LOO spread: LOO 0.2913. 50/50
  ensemble (OLS + median-ratio) + LOO spread: LOO 0.2831. Lesson: v1's
  in-sample residual SD was already well calibrated (LOO coverage 0.900);
  LOO-based spreads over-widen (coverage 0.95–0.96) and lose pinball.
  The game is the median, not the spread.
- **Round 2 — median variants, v1 spread kept.** Proper slope shrink
  (b' = 1 + k(b−1), intercept refit): k = 0.85 → LOO 0.2576, practice
  0.1973; k = 0.7 → LOO 0.2542, practice 0.2000; k = 0.5 → LOO 0.2550.
  Local median-ratio (p1-matched subset): LOO 0.3121 — rejected. Peak +
  shape two-stage: LOO 0.3120 — rejected. Huber-robust OLS: LOO 0.2620,
  practice 0.1996 — no material gain. 25% median-ratio ensemble: LOO
  0.2548. SD scale 0.85 (flat): LOO 0.2633, practice 0.1903; SD 0.90:
  LOO 0.2632. SD floor 0.15: no change.
- **Round 3 — combos.** Shrink 0.7 + SD 0.85: LOO 0.2531, practice
  0.1943. Shrink 0.85 + SD 0.85: LOO 0.2567, practice 0.1918. Shrink 0.6
  + SD 0.85: LOO 0.2529. Huber + shrink: no gain. Season-conditional fit
  (winter/summer split, season-matched LOO): LOO 0.2707, practice 0.2016
  — rejected; halving the training set costs more than the unlock-step
  timing is worth (same conclusion as v1's winter-only test, now with a
  proper season-matched LOO). Mu smoothing across hours: no gain.
- **Round 4 — bias correction, stacking, SD diagnostic.** US-unlock bias
  correction (hours 5–8, within-training LOO bias): LOO flat (0.2534 vs
  0.2531), practice 0.1909 — no material gain, rejected for complexity.
  All-hours bias correction ×0.5: LOO 0.2670 (worse) but practice 0.1773
  (much better) — **rejected as the dev-set trap**: a correction that
  helps 4 launches and hurts 29 is not a correction. 3-learner stacking
  (simplex weights from within-training LOO): LOO 0.3021 (much worse) but
  practice 0.1811 — **rejected the same way**. Per-hour SD-scale
  diagnostic: optimal scale varies 0.6–1.1 by hour, but a smoothed
  hour-profile gained only +0.0005 — rejected as overfitting.
- **Round 5 — taper, recency, 2-predictor.** Tapered shrink (k 1.0 at
  p1 ≤ 5k → 0.7 at p1 ≥ 50k) + SD 0.85: LOO 0.2591, practice 0.1908,
  all-37 0.3739 (≈ v1's 0.3737 — the taper recovers the small-print
  regime the flat shrink damaged). Recency ≥ 2022 / ≥ 2023: LOO 0.2570 /
  0.2586 (worse), practice 0.1884 / 0.1885 (better) — rejected, same trap
  pattern. Two-predictor OLS (+ pre-release 24h max): LOO 0.2626,
  practice 0.2246 — rejected; the pre-release spike misleads small
  launches. Stronger top-end shrink (k → 0.5 above 300k): LOO ≥ 50k
  0.2015 (worse) — rejected; k = 0.7 is the plateau.
- **Self-critique cycle 1 (on the built v2).** Taper ranges 10k–100k and
  5k–100k: LOO 0.2609 / 0.2599 (worse than 5k–50k's 0.2591), practice
  better only via p00 alone — kept 5k–50k. SD 0.90 / 0.95: LOO ≥ 5k
  flat (0.2590 / 0.2592), coverage better (0.883 / 0.895) but ≥ 50k and
  practice worse — kept 0.85, the final being a big-print launch.
  Global (pooled) LOO-bias correction: LOO worse on every slice
  (≥ 5k 0.2621), practice better (0.1855) — rejected, same trap pattern.
  Residual-skew diagnostic: LOO residuals are near-symmetric (skew
  −0.04; 17.5% below −0.5 log vs 9.1% above +0.5), so no asymmetric
  upper-tail widening — the danger is over-prediction, not explosion.
- **Self-critique cycle 2 (on the built v2).** Spread recomputed around
  the damped fit instead of the OLS fit: LOO ≥ 5k 0.2590 (identical),
  practice 0.1918 (slightly worse) — kept the simpler OLS residual SD.
  Robustness hardening adopted instead: safe hour-1 extraction (bad or
  non-numeric prints fall back instead of crashing) and two-tier
  per-case failure handling (an unreadable case file writes nothing, so
  the grader's persistence fallback applies; a parsed case whose fit
  fails falls back to persistence at its own hour-1 print). Backtest
  numbers unchanged after these fixes.

## 6. Validation runs (final files, 18 Nov 2026)

- `python3 backtest.py` → LOO ≥ 5k 0.2591 / ≥ 50k 0.1992 / ≥ 100k 0.2104 /
  all-37 0.3739; practice mean 0.1908 (starter 0.3871), typical miss
  36.7%, coverage 0.935. Full output: §1–2 above.
- Output validity: all four practice cases produce exactly 23 rows, hours
  2–24, five finite non-decreasing quantiles in (0, 1e9], ≤ 1,544 bytes each.
- Determinism: two full runs byte-identical (`diff -r` clean).
- Runtime: ~265 ms for all 4 cases wall (incl. Python startup), ~2.6 ms
  forecast time per case; far inside the 8 s cap.
- Vanilla Python: fresh `venv --without-pip` (no third-party packages),
  `python -P -s main.py` reproduces byte-identical outputs. Stdlib only
  (`json`, `math`, `os`, `sys`, `pathlib`, `datetime`).
- Edge cases tested: no comparables, tiny/huge/zero/non-numeric hour-1
  print, malformed comparables, missing `known`, empty case dict,
  malformed case file (skipped, other cases still written) — all produce
  a valid 23-row forecast or a clean skip.
- No practice answers in the repo: none of the 92 distinctive
  hours-2–24 truth values (≥ 10,000 viewers) appears in any repo file.
