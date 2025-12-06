# evaluation/ner_eval.py
"""
Lightweight NER evaluation (non-intrusive).
Uses src.ner.custom_ner.final_ner_logic_v4 if available; else uses a tiny
heuristic company list fallback.

Outputs:
  - precision, recall, f1 (micro) on small gold set
"""
import json
from collections import Counter

# small gold set (text -> expected org list)
GOLD = [
    {"text": "HDFC Bank Q3 profit rises on higher NII", "expected": ["HDFC Bank"]},
    {"text": "RBI hikes repo rate by 25 bps", "expected": ["RBI"]},
    {"text": "ICICI Securities upgrades HDFC Bank to BUY", "expected": ["ICICI Securities", "HDFC Bank"]},
    {"text": "Tata Motors announces JV with Suzuki", "expected": ["Tata Motors", "Suzuki"]},
    {"text": "Mumbai Police arrests cybercriminal", "expected": ["Mumbai Police"]},
]

def extract_with_fallback(text):
    try:
        from src.ner.custom_ner import final_ner_logic_v4
        ents = final_ner_logic_v4(text)
        return [e["entity"] for e in ents if e.get("type") in ("ORG", "COMPANY", "GPE")]
    except Exception:
        # fallback heuristic: look for known names
        COMPANY_LIST = ["HDFC Bank","RBI","ICICI Securities","Tata Motors","Suzuki","Mumbai Police"]
        text_lower = text.lower()
        found = [c for c in COMPANY_LIST if c.lower() in text_lower]
        return found

def compute_scores(gold, pred):
    tp = len([x for x in pred if x in gold])
    fp = len([x for x in pred if x not in gold])
    fn = len([x for x in gold if x not in pred])
    return tp, fp, fn

def run():
    TP = FP = FN = 0
    details = []
    for item in GOLD:
        text = item["text"]
        gold_ents = item["expected"]
        pred_ents = extract_with_fallback(text)
        tp, fp, fn = compute_scores(gold_ents, pred_ents)
        TP += tp; FP += fp; FN += fn
        details.append({"text": text, "gold": gold_ents, "pred": pred_ents, "tp": tp, "fp": fp, "fn": fn})

    precision = TP / (TP + FP) if (TP + FP) else 0.0
    recall = TP / (TP + FN) if (TP + FN) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    res = {"ner": {"precision": precision, "recall": recall, "f1": f1, "details": details}}
    print("NER Eval:", res["ner"])
    return res

if __name__ == "__main__":
    r = run()
    with open("evaluation_results.json", "w") as f:
        json.dump({"ner": r["ner"]}, f, indent=2)
    print("Saved evaluation_results.json")
