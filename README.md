# K League 1 High Turnover & Attacking Transition Analysis

**Event-based analysis of attacking outcomes following high turnovers in the 2024 K League 1 season**

## Overview

This project investigates how winning the ball in advanced areas of the pitch relates to subsequent shots and goals. A key methodological challenge is distinguishing an event recorded for the opposing team (such as a block) from an actual change in possession.

## Research questions

- How often do identified high turnovers lead to shots or goals within 15 seconds?
- How do outcomes differ by turnover event type?
- How sensitive are the results to possession-change and sequence-tracking rules?

## Data

The analysis was developed using 2024 K League 1 event data from the K League–University of Seoul Public AI Competition (DACON).

| Item | Value |
| --- | ---: |
| Matches | 198 |
| Teams | 12 |
| Recorded events | 579,306 |

The original event dataset is not redistributed here. Refer to the data provider's access and licensing terms.

## Approach

1. Normalize event locations relative to attacking direction.
2. Identify candidate ball recoveries in advanced areas of the pitch.
3. Evaluate whether subsequent events support a genuine change in possession, rather than relying solely on a change of event-performing team.
4. Track subsequent attacking actions within a 15-second window.
5. Summarize shot- and goal-linked sequences by turnover category.

**Methodological note:** Possession is inferred from event records rather than continuously observed. The definition of possession change can materially affect results.

## Preliminary results

The revised analysis produced the following summary. These are project analysis outputs and remain subject to case-level validation.

| Metric | Revised result |
| --- | ---: |
| Identified high turnovers | 11,018 |
| Shot-linked sequences within 15 seconds | 998 |
| Goal-linked sequences | 78 |
| Shot-linked share | 9.06% |
| Goal-linked share | 0.71% |

### By event category

| Event category | High turnovers | Shot-linked | Goal-linked |
| --- | ---: | ---: | ---: |
| Recovery | 5,082 | 734 | 52 |
| Interception | 3,114 | 83 | 8 |
| Duel | 1,494 | 66 | 6 |
| Tackle | 745 | 67 | 6 |
| Block | 583 | 48 | 6 |
| **Total** | **11,018** | **998** | **78** |

Earlier analysis outputs were 11,660 turnovers, 1,352 shot-linked sequences, and 145 goal-linked sequences. The revised results reflect changes in the identification and tracking logic; a complete case-by-case reconciliation of these differences has not yet been established.

These statistics describe observed event sequences, not causal effects of pressing.

## Repository contents

```text
K-league_high_turnover_analysis/
├── 전방탈취_최종본.ipynb   # Analysis notebook
├── requirements.txt       # Python dependencies (provisional; awaiting import verification)
├── .gitignore             # Files excluded from Git tracking
└── README.md              # Project documentation
```

## Running the analysis

1. Clone this repository.
2. Create a Python virtual environment.
3. Install the listed dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Obtain the source dataset separately and update local data paths in the notebook.
5. Open [전방탈취_최종본.ipynb](./전방탈취_최종본.ipynb) in Jupyter or VS Code and execute the cells in order.

**Reproducibility status:** The notebook is provided, but the original dataset is not. The dependency list has not yet been fully validated against the notebook imports, and execution has not been independently verified.

## Limitations and next steps

- Validate ambiguous possession changes using individual event sequences.
- Reconcile initial and revised analysis outputs on a case-by-case basis.
- Evaluate the sensitivity of results to alternative turnover definitions and time windows.
- Add verified visualizations and team-level comparisons.

## Author

**Junha Shin** — [GitHub profile](https://github.com/sinjunha513-cloud)

Interests: sports analytics, statistics, machine learning, and data science.
