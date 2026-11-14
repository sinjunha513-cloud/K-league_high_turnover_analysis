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

## Final results

The final report uses the revised possession-change rules. It identifies 5,303 valid high turnovers; 1,204 linked to a shot within 15 seconds (22.7%) and 95 linked to a goal (1.79%). Among shot-linked sequences, 7.9% also linked to a goal.

| Event category | High turnovers | Shot-linked | Goal-linked | Shot rate | Goal rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Recovery | 3,548 | 903 | 64 | 25.5% | 1.80% |
| Duel | 610 | 84 | 6 | 13.8% | 0.98% |
| Interception | 510 | 89 | 11 | 17.5% | 2.16% |
| Tackle | 397 | 74 | 7 | 18.6% | 1.76% |
| Block | 238 | 54 | 7 | 22.7% | 2.94% |
| **Total** | **5,303** | **1,204** | **95** | **22.7%** | **1.79%** |

These counts describe turnover-linked sequences, not unique match shots or goals. Event-based possession inference and observed associations do not establish causal effects of pressing. See the attached report for figures, methods, and limitations.

## Final report

The complete report, including figures, is available as [DOCX](./reports/K%EB%A6%AC%EA%B7%B81_%EC%A0%84%EB%B0%A9%ED%83%88%EC%B7%A8_%EB%B6%84%EC%84%9D_%EA%B2%B0%EA%B3%BC%EB%B3%B4%EA%B3%A0%EC%84%9C_%EC%99%84%EC%84%B1%EB%B3%B8.docx).

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
