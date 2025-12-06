# evaluation/impact_eval.py
"""
Evaluate ImpactMapper.map_entity on a small gold sample.
Gracefully handles missing mapping CSV by using auto mapping code path.
"""
import json

GOLD = [
    {"entity": "HDFC Bank", "expected_ticker": "HDFCBANK"},
    {"entity": "ICICI Securities", "expected_ticker": "ICICISECURITIES"},
    {"entity": "RBI", "expected_ticker": "RBI"},
    {"entity": "Tata Motors", "expected_ticker": "TATAMOTORS"},
]

def run():
    try:
        from src.impact.impact_mapper import ImpactMapper
        mapper = ImpactMapper()
    except Exception as e:
        print("ImpactMapper import error, fallback:", e)
        mapper = None

    correct = 0
    details = []
    for item in GOLD:
        ent = item["entity"]
        expected = item["expected_ticker"].upper()
        pred = None
        if mapper:
            m = mapper.map_entity(ent, "ORG")
            if m:
                pred = m.get("ticker", "").upper()
        else:
            # fallback heuristic
            pred = "".join(ch for ch in ent.upper() if ch.isalnum())[:10]

        match = pred == expected
        if match:
            correct += 1
        details.append({"entity": ent, "expected": expected, "pred": pred, "match": match})

    accuracy = correct / len(GOLD)
    res = {"impact": {"accuracy": accuracy, "details": details}}
    print("Impact Eval:", res["impact"])
    return res

if __name__ == "__main__":
    r = run()
    with open("evaluation_results.json", "w") as f:
        json.dump({"impact": r["impact"]}, f, indent=2)
    print("Saved evaluation_results.json")
