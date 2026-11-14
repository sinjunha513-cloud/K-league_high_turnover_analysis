# K League 1 High Turnover Analysis

**Junha Shin · Individual project · 2 months · GPT-assisted analysis**

An event-based study of first-shot conversion after high turnovers in **198 matches, 12 teams, rounds 1–33 of the 2024 K League 1 season**. This is an observational analysis of event-derived control transitions, not a direct measurement of pressing intensity or causal tactical effects.

[Read the revised illustrated report](reports/K_League_High_Turnover_Report.pdf) · [Executed notebook](전방탈취_최종본.ipynb) · [Analysis code](analysis/revalidate.py)

## Revalidated results — 14 November 2026

| Measure | Original reproduced analysis | Revised analysis |
|---|---:|---:|
| High turnovers | 5,303 | 5,290 |
| First shots within 15 seconds | 1,204 | 1,211 |
| Goals from those first shots | 95 | 94 |
| Shot conversion | 22.70% | 22.89% |
| Duplicate shot links | 1 | 0 |

The revised overall shot-conversion estimate has a match-bootstrap 95% interval of **21.72–24.13%**. Central, half-space and flank conversion rates are **37.42%, 22.05% and 11.60%**. Intervals describe sampling variability, not uncertainty in event annotation.

A descriptive binomial GLM adjusts for turnover x-coordinate and type, team, opponent, period, elapsed time, home status and the score strictly before the turnover. Standard errors are clustered by match. The central-versus-flank adjusted odds ratio is **5.61 (95% CI 4.68–6.71)**. This is not a probability ratio, a causal effect or an externally validated predictive model.

## What was repaired and tested

- Reproduced the previous 5,303 / 1,204 / 95 baseline from the supplied raw files.
- Counted one turnover per inferred control transition and removed duplicate shot attribution.
- Used an explicit control-event set including Catch, Ball Received and Take-On.
- Credited blocks at the subsequent confirmed control event: both the time origin and location refer to confirmed control. **This changes the operational definition from the earlier block-contact origin.**
- Reconstructed final scores from scoring shots and own goals: **198/198 match scores agree**.
- Cross-checked inferred attack direction against goal-kick positions in **766 match-period-team units**, with no conflicts. This is an internal consistency check, not video ground truth.
- Removed the old progression-speed metric: it combined event-end distance with event-start elapsed time and produced implausible values. A secondary start-to-start net ball-progression rate is computed only for intervals of at least one second; it is not player speed.
- Replaced post-turnover model variables such as “Direct Shot”, pass count and carrying with information available at the confirmed-control origin.
- Verified model convergence and full design rank (34/34); checked nonlinear x, removal of Duel, and removal of Block.
- Tested 5/10/15/20-second windows, x thresholds of 65/70/75m, control rules, block windows and ordering. The central-versus-flank association persists in these checks.
- Passed **10 boundary-case tests**.

## Definitions and remaining limitations

Main threshold: normalized x ≥ 70m. The sequence ends at the first shot, opposing control, stoppage, restart, period boundary or 15 seconds. Goals refer only to the first shot; rebounds and own goals are not part of this outcome.

**270 of 1,211 linked shots share the turnover timestamp.** The primary ordering uses time_seconds then action_id. Counting only positive-time shot links gives 941/5,290 (17.79%), a conservative timing check rather than a claim that simultaneous records were actual failures. There are 627 backwards timestamp steps under action_id ordering.

Possession remains an event-derived operational estimate. Success in a duel or a recorded touch does not necessarily establish stable possession. No manually labelled video or another season was used for external validation. Off-ball positioning, pressing intensity, player ability and some match context remain unobserved. The dataset covers rounds 1–33, not the full season.

## Reproduce

Python 3.12 was used. Install the analysis dependencies:

```bash
pip install -r requirements.txt
python analysis/revalidate.py --data raw_data.csv --matches match_info.csv --out results_revalidated
python analysis/robustness.py results_revalidated
python analysis/test_revalidate.py
```

Alternatively place both CSV files beside the notebook and run its cells in order. The notebook embeds the main analysis code. The supplementary script adds overall bootstrap intervals and model sensitivity checks.

The raw files and event-level outputs are not redistributed publicly. Obtain the original files under their applicable terms. Aggregate outputs are in results_revalidated/. Running the code also produces sequences.csv locally. Source file SHA-256 and software versions are recorded in audit.json.

The notebook in archive/ is the previous analysis for traceability; **do not use its old numbers as the current result**.

## Contribution and research motivation

I used GPT extensively for code generation, revision, debugging and this revalidation. I contributed the sports-domain question and interpretation and am still developing independent Python reading, modification and debugging skills.

The gap between event records and continuous player movement motivates my interest in estimating movement from football video, handling tracking uncertainty, and studying interactions and future motion. These are future research interests; no tracking or world model has been trained in this project.
