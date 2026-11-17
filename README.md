# makefun-gta6-twitch-ccu-forecast-01-v2

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/RieryBuild/makefun-gta6-twitch-ccu-forecast-01-v2/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/RieryBuild/makefun-gta6-twitch-ccu-forecast-01-v2/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

A program that reads one case — everything recorded up to the end of the
first hour of Grand Theft Auto VI's release day (19 Nov 2026, UTC), that
hour's Twitch viewer count included — and forecasts the category's concurrent
viewers for each of hours 2–24 as five quantiles (5%, 25%, 50%, 75%, 95%),
scored by mean pinball loss on the log scale.

## How it works

For every forecast hour, the program fits a log-log regression across the
case's comparable past launches — `ln y_h = a_h + b_h * ln p1`, where `p1`
is hour 1's print — with the slope shrunk toward 1 (proportional scaling)
and the intercept refit at the training mean, so a huge hour 1 does not
over-extrapolate into a proportionally huge evening peak. The damping
tapers from none at hour-1 prints ≤ 5,000 to k = 0.7 at prints ≥ 50,000.
The spread is the fit's own residual standard deviation, scaled by 0.85
and guarded to [0.20, 0.90] in log units. The core fit uses only
comparables whose hour 1 reached 5,000 viewers (smaller hour-1 prints are
mostly pre-unlock noise with peak ratios in the hundreds), blending toward
the all-comparables fit when this case's own hour 1 is small. Nothing is
hard-coded: every coefficient is fitted at run time from the input file,
so the same program forecasts any launch day the case describes.

Measured locally (see `BACKTEST.md`): leave-one-out over the comparables
**0.1992** for launches with hour-1 ≥ 50,000 (v1: 0.2046), **0.2591** for
hour-1 ≥ 5,000 (v1: 0.2639); practice mean pinball loss **0.1908** (v1:
0.1950) vs the house persistence baseline's **0.3871**; typical miss 36.7%.

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Reads every `<id>.in` in the input directory and writes `<id>.out` beside
it in the output directory: `{"hours": [{"hour": 2, "q": [q05, q25, q50,
q75, q95]}, ...]}` for hours 2–24. Python 3.13, standard library only, no
network. Deterministic; ~85 ms per case.

## Files

- `main.py` — the forecaster (the entrypoint the grader runs).
- `backtest.py` — the backtest: leave-one-out over the comparables plus the
  four practice cases, scored with the exact pinball loss from the rules.
  Run it with `python3 backtest.py` (practice truth is read from a directory
  passed with `--truth-dir`; it is not part of this repository).
- `BACKTEST.md` — measured results, the dev-board warning, and the
  iteration log.
- `LICENSE` — MIT.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=wa8s3t3t&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
