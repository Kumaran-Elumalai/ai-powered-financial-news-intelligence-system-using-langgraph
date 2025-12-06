<!-- # Evaluation Report (auto-generated template)

This folder contains lightweight evaluation scripts for the Financial News Intelligence system.

## What is evaluated
- **NER** (small manual set): precision, recall, F1.
- **Deduplication**: accuracy on a few pairs.
- **Impact mapping**: ticker mapping accuracy on a few entities.
- **Ranking**: Hit@1 and Hit@3 for a few test queries.

## How to run
From project root:
```bash
python evaluation/run_all.py
# OR run individual scripts
python evaluation/ner_eval.py
python evaluation/dedupe_eval.py
python evaluation/impact_eval.py
python evaluation/ranking_eval.py

``` -->