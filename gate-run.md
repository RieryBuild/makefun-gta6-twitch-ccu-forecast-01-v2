# Pre-submit gate run — gta6-twitch-ccu-forecast-01 v2 (FINAL, coordinator)

Coordinator gate run, 18 Nov 2026 ~03:35 WITA. Gate: `~/workspace/custom-skills/makefun/house-pre-submit-gate.md`.
Result: **ALL 8 QUESTIONS PASS. ALL 4 GATES PASS. SUBMIT.**

This entry supersedes v1 (submission 01a1e9aa, rank 2473/6507, loss 0.195) under Force_Last — intended; this rebuild was triggered once for this entry (watch run 02:30 WITA 18 Nov).

## MQ1 — Submittable right now? PASS

1. Competition: gta6-twitch-ccu-forecast-01 — entries close 19 Nov 09:00 WITA (2026-11-19T01:00:00Z). Quota re-checked by coordinator at gate time: can_submit TRUE (1 made, 1 kept, 2 left today, hard limit 19 left).
2. Deliverables present in `~/workspace/makefun-work/gta6-twitch-ccu-forecast-01-entry-v2/`: main.py (repo root), backtest.py, BACKTEST.md, README.md, LICENSE (MIT, SPDX line first), gate-run.md (this file). Bundle: `/tmp/v2-bundle.tar.gz`, sha256 `622eb8dcb4d7a0bf8074f269a780e7f8c65bcc146b1bee2d81e6db0b3ae77dfa`, 442,457 bytes. Local `check`: 13 passed / 0 failed / 5 skipped / 5 checked at submission.
3. Title: "Shrunk-slope log-log OLS CCU forecaster".
4. Submit path: `node cli/makefun.mjs submit --competition gta6-twitch-ccu-forecast-01 --repo-url https://github.com/RieryBuild/makefun-gta6-twitch-ccu-forecast-01-v2 --commit <GitHub HEAD after this file is pushed> --title "Shrunk-slope log-log OLS CCU forecaster" --bundle /tmp/v2-bundle.tar.gz --keypair ~/.makefun/keypairs/makefun-keypair.json` (bundle route: NO `--harness/--provider/--model/--effort` flags — the bundle already carries them; passing them with `--bundle` is refused client-side, proven on the BTC race).
5. Cost: time ~10 min to submit, capital $0 (free entry, no fee).

## MQ2 — Clears the prizelist bar? PASS (with the documented caveat)

- Prizelist: top 20 (1st $50, 2nd $35, 3rd $25, 4th–10th $10, 11th–20th $7). A prize needs a loss strictly below the best house entry's on the FINAL.
- Evidence (measured, never a promised outcome; coordinator reproduced the backtest independently): LOO over comparables (selection metric) hour-1 ≥ 50,000: **0.1992** (v1 0.2046, starter 0.2509); ≥ 5,000: **0.2591** (v1 0.2639); all-37: 0.3739 (v1 0.3737 — no regression). Practice mean (dev number): **0.1908** (v1 0.1950, starter 0.3871); typical miss 36.7% vs 82.8%; 90% coverage 0.935. Paired wins vs v1 on 22/37 launches; mean paired Δ −0.0054 on ≥ 50,000.
- Caveat, stated plainly: the gain is modest (−2.6% on the most relevant slice) and uneven — split-half checks show v2 winning clearly in two halves and flat in the other two. The live dev board's rank-20 line (~1e-06) is a memorisation artifact (BACKTEST.md §3); this entry does NOT chase it and does not clear it. The honest-model cluster starts ~0.12; v2's 0.1908 practice / 0.1992 LOO-≥50k sits in the honest range. The FINAL prize bar is "below the best house entry", which this model clears ~2× on practice. Nothing here promises a final result.

## MQ3 — Quota open? PASS

Re-checked at gate time via the competition's own endpoint with `x-api-key`: `can_submit: true`, entries_made 1, entries_kept 1, day cap 3 / taken 1 / left 2, hard limit 20 / left 19 (18 Nov ~03:30 WITA). Deadline still ahead (entries close 19 Nov 09:00 WITA).

## MQ4 — Right identity, right route? PASS

Signed by wallet 6do8 ONLY (6do8zGw4FPLCB1Cq44G8r8KwQccbhHUqtAptaRji6ALk) via keypair `~/.makefun/keypairs/makefun-keypair.json`. Repo RieryBuild/makefun-gta6-twitch-ccu-forecast-01-v2 pushed via the GitHub PAT route (custom.github-pat helper; repo created 201, 5 files pushed 201 each, About set via PATCH + topics endpoint). Tree verified blob-for-blob identical to local (all 5 files).

## MQ5 — Deliberate new submission, not a duplicate? PASS

Rebuild triggered once by the coordinator for this entry (v1 rank 2473/6507, outside the top-20 prizelist). Force_Last: this entry supersedes v1 — intended, not a duplicate. New model (shrunk-slope OLS vs v1 plain OLS), new repo, new commit.

## MQ6 — Proves it works? PASS

- Own tests: `backtest.py` reproduced by the coordinator: LOO 0.1992 (≥ 50k) / 0.2591 (≥ 5k) / 0.3739 (all-37) and practice mean 0.1908 (starter 0.3871) — see BACKTEST.md §1–2, §6. Exact match with the builder's numbers.
- Clean vanilla-Python run (coordinator): fresh `venv --without-pip`, `python -P -s main.py` → byte-identical outputs on all 4 practice cases (23 rows each, monotone quantiles, ≤ 1,544 bytes); two runs byte-identical; edge cases (no comparables, p1 = 0 / huge / non-numeric, malformed comparables, missing `known`, empty case, malformed case file) all yield valid forecasts or a clean skip. Stdlib only (json, math, os, sys, pathlib, datetime — verified by AST grep; `main` import in backtest.py is the local entry module). No practice answers in the repo (92 distinctive truth values checked by the builder, none present).
- No local practice grade exists for this competition (program/v1, server-only grading) — the backtest above is the evidence, measured on the exact files being submitted.
- Not a game: no screenshots/play-test requirement.

## MQ7 — Never-submit list? PASS (no match)

No code-drawn images; no non-stdlib imports; in-session revision present (main.py from 4 messages that write or edit it, ≥ 2 required); wallet 6do8; PAT route; no capital needed; can_submit true. Multi-model review NOT attempted (SUSPENDED by Reza 17 Nov ~15:42 WITA).

## MQ8 — Session / transcript coverage? PASS (bundle route)

- This competition takes NO recorded transcripts (`record` refused HTTP 400 for v1: "does not take recorded transcripts"). Route is the bundle: 2 sessions (builder 3ff4d9df, 155 lines; coordinator 5c868a1d, 145 lines kept after the bundle cut 62 earlier records from before this repo was first named), 1 instruction file (AGENTS.md), MCP none, 2 usage rows attached.
- Two bundle fixes applied by the coordinator (both documented, both verified by the local check): (1) the first bundle had 0 usage rows — Muse app session files carry no usage; fixed by running the kit's MUSE_APP_USAGE_SELECT via muse.db (2 rows, one per session) and re-bundling with `--muse-usage /tmp/v2-muse-usage.jsonl`. The rows name model ipnext/avocado-5.17-v7, so the bundle declares `--model ipnext/avocado-5.17-v7` (the sessions.json context model v2 is NOT the billed model). (2) the first bundle was refused for a missing prompt — the earliest session opens with no person-typed message (subagent fork); fixed with `--prompt-file /tmp/v2-prompt.txt` (the watch job body = the scheduled task's configured prompt) + `--prompt-origin scheduled` + `--prompt-via "makefun-results-watch 02:30 WITA 18 Nov 2026 run"`. Local check confirms the run record: "a scheduled prompt, the agent facts, a system prompt in-session, instruction files collected (1), no MCP server listed".

## Gate 0 — Reality: PASS

Repo exists at one public commit chain (GitHub HEAD `60b35810fa` after the 5 file pushes; this file is pushed as the final file, submitted commit = HEAD after that push); every deliverable present; tests + vanilla run pass on these files; evidence captured (backtest numbers, quota response, bundle sha256, check output).

## Gate 1 — Quality: PASS

- Multi-model review: SUSPENDED by Reza 17 Nov ~15:42 WITA — not attempted; this checkbox is satisfied by the suspension.
- Quality rests on the builder's own verified evidence (backtest numbers reproduced by the coordinator, vanilla run, output validity, determinism), with the selection metric (LOO over comparables) kept separate from the dev numbers.
- Grade vs prizelist bar stated as evidence with the memorisation caveat (MQ2), never a promised outcome.

## Gate 2 — Dedup: PASS

Not a duplicate (rebuild of the standing entry under Force_Last, coordinator-triggered once); quota re-checked at gate time (MQ3).

## Gate 3 — Submission quality: PASS

- README matches the requirements template: title + competition badge + rank badge + reward badge (owner RieryBuild, repo makefun-gta6-twitch-ccu-forecast-01-v2) + description + Run-it + footer with ref=wa8s3t3t. About set via PAT API (description + homepage + topics makefun, ai-agents, bounties, forecasting).
- No secrets in the repo (grep: no API keys, no key material; no wallet address in any file). Claim code handling: daily memory ONLY.
- Deadline still ahead: entries close 19 Nov 09:00 WITA; submitting 18 Nov ~03:40 WITA.

## Local check summary

`makefun check --kit . --repo <entry> --worktree --transcripts /tmp/v2-bundle.tar.gz`, 18 Nov ~03:30 WITA: **13 passed / 0 failed / 5 skipped / 5 checked at submission** (same as v1). thinking_reproduces 50.9% authored (384/753; 33 copied, 336 read, 0 absent; 0.0% unwritten), thinking_priced 2 usage records each priced to a known model, thinking_revised main.py from 4 messages, thinking_turns 76, thinking_in_window all 198 timestamps in window, transcripts_run_record "a scheduled prompt, the agent facts, a system prompt in-session, instruction files collected (1), no MCP server listed". At-submission checks (repo_public, repo_owner, repo_created_after_open, commit_in_repo, duplicate_snapshot) are the site's at submit time — repo is public, owner RieryBuild = account GitHub login, created 18 Nov after the 06:00Z 17 Nov opening, commit is the GitHub HEAD.

## Submission record (filled at submit time)

- Submitted commit (GitHub HEAD after this file is pushed): _see coordinator's submission report + kit status_
- Submission ID / HTTP result: _see coordinator's submission report_
- Claim code: daily memory ONLY
