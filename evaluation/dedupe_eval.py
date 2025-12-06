# evaluation/dedupe_eval.py
"""
Simple dedupe evaluation.
Tries to import Deduper.assign_story_id_and_update and uses it;
fallback uses rapidfuzz.ratio to simulate duplicate detection.
"""
import json

PAIRS = [
    # (text_a, text_b, is_duplicate)
    ("Company X reports 10% growth", "Company X reports ten percent growth", 1),
    ("RBI policy review tomorrow", "Earnings: Infosys Q2 results", 0),
    ("HDFC Bank appoints new CFO", "HDFC Bank appoints new chief financial officer", 1),
    ("Corona Remedies files RHP", "Corona Remedies IPO opens next week", 1),
    ("Global markets brace for central bank signals", "Local sports team wins match", 0),
]

def run():
    try:
        from src.dedupe.deduper import Deduper
        deduper = Deduper(top_k=5, threshold=0.9)
        use_deduper = True
    except Exception:
        use_deduper = False
        from rapidfuzz import fuzz

    TP = FP = FN = TN = 0
    details = []

    for a, b, gold in PAIRS:
        if use_deduper:
            r = deduper.assign_story_id_and_update({"id": 9999, "title": a, "description": b})
            # assign_story_id_and_update may return dict - we use placeholder logic:
            pred_duplicate = bool(r.get("_dedupe_info", {}).get("duplicate"))
        else:
            score = fuzz.token_sort_ratio(a, b)
            pred_duplicate = score >= 85

        if pred_duplicate and gold == 1:
            TP += 1
        elif pred_duplicate and gold == 0:
            FP += 1
        elif (not pred_duplicate) and gold == 1:
            FN += 1
        else:
            TN += 1

        details.append({"a": a, "b": b, "gold": gold, "pred": int(pred_duplicate)})

    accuracy = (TP + TN) / (TP + TN + FP + FN)
    res = {"dedupe": {"accuracy": accuracy, "TP": TP, "FP": FP, "FN": FN, "TN": TN, "details": details}}
    print("Dedupe Eval:", res["dedupe"])
    return res

if __name__ == "__main__":
    r = run()
    with open("evaluation_results.json", "w") as f:
        json.dump({"dedupe": r["dedupe"]}, f, indent=2)
    print("Saved evaluation_results.json")
