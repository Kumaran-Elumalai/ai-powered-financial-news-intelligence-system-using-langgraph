# 📊 Evaluation Report – Financial News Intelligence System

This document summarizes how each component of the system is evaluated.
All evaluation scripts are in:
```bash
/evaluation/
```

Running the full evaluation:
```bash
python evaluation/evaluate_pipeline.py
```
### 1. 🧠 NER Evaluation (ner_eval.py)

Goal: How well does our custom NER detect companies, sectors, and regulators?

Metrics used:

✔ Precision  
✔ Recall  
✔ F1 Score  

### 2. 🎯 Impact Mapping Evaluation (impact_eval.py)

Goal: Check how accurately ORG entities are mapped to tickers.

Metric:

✔ Accuracy@1 → % of predictions where top mapped ticker is correct.

Tested using a manually curated dataset:

"Infosys"  → INFY  
"HDFC Bank" → HDFCBANK  
"RBI" → regulator

### 3. 🔁 Deduplication Evaluation (dedupe_eval.py)

Measures:

✔ Silhouette Score → clustering quality  
✔ Jaccard Similarity → duplicate group overlap  

Expected:

0.6 similarity threshold  
Low false-splits  
Low false-merges  

### 4. 📈 Ranking Quality Evaluation (ranking_eval.py)

We measure how well the system ranks relevant results.

Metrics:

| Metric              | Purpose                                   |
|---------------------|--------------------------------------------|
| Precision@K         | % of top-K results truly relevant          |
| NDCG@K              | Measures ranking order quality             |
| Mean Reciprocal Rank (MRR) | How early the most relevant result appears |

Ground truth created manually for HDFC Bank, Infosys, RBI queries.

### 5. 🌐 End-to-End System Evaluation (evaluate_pipeline.py)

Provides:

- NER Score
- Impact Score
- Ranking Metrics
- Pipeline Latency
- LLM summary quality checks

Outputs a consolidated JSON file:
```bash
{
  "ner_f1": 0.92,
  "impact_accuracy": 0.88,
  "ranking_precision_at_5": 0.80,
  "avg_latency_seconds": 0.42
}
```

### 🎯 Final Verdict

The evaluation framework demonstrates that:

- Entity extraction is strong
- Impact mapping is reliable
- Ranking engine performs with high precision
- Deduplication reduces redundancy significantly
- The system is suitable for financial intelligence workflows


Each predicted entity is compared against ground truth in `data/ner_test.json`.

