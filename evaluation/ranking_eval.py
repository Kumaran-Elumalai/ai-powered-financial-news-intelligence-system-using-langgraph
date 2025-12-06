# evaluation/ranking_eval.py
"""
Ranking evaluation using QueryEngine.search.
Test queries map to expected top-1 title (or keywords).
Computes Hit@1 and Hit@3.
Falls back to title matching if QueryEngine unavailable.
"""
import json

TESTS = [
    {"query": "Show me news affecting HDFC Bank", "expected_keywords": ["HDFC Bank", "HDFC"]},
    {"query": "RBI MPC meeting rate cut", "expected_keywords": ["RBI", "rate cut", "RBI MPC"]},
    {"query": "Corona Remedies IPO details", "expected_keywords": ["Corona Remedies", "IPO"]},
]

def _contains_expected(title, keywords):
    t = (title or "").lower()
    return any(k.lower() in t for k in keywords)

def run():
    try:
        from src.query.query_engine import QueryEngine
        engine = QueryEngine()
        use_engine = True
    except Exception as e:
        print("QueryEngine unavailable, fallback to metadata search. Error:", e)
        engine = None
        use_engine = False

    hit1 = 0
    hit3 = 0
    details = []

    for t in TESTS:
        q = t["query"]
        kw = t["expected_keywords"]
        try:
            if use_engine:
                res = engine.search(q, top_k=10)
                titles = [r["title"] or "" for r in res["results"]]
            else:
                # fallback: find any article in news_final_enriched.json with expected keywords
                import os, json as _json
                p = os.path.join("data", "news_final_enriched.json")
                titles = []
                if os.path.exists(p):
                    dataset = _json.load(open(p, "r", encoding="utf-8"))
                    for a in dataset[:200]:
                        titles.append(a.get("title",""))
            # evaluate
            top1 = titles[0] if titles else ""
            top3 = titles[:3]
            is_hit1 = _contains_expected(top1, kw)
            is_hit3 = any(_contains_expected(ti, kw) for ti in top3)
            if is_hit1: hit1 += 1
            if is_hit3: hit3 += 1
            details.append({"query": q, "top1": top1, "top3": top3, "is_hit1": is_hit1, "is_hit3": is_hit3})
        except Exception as ex:
            details.append({"query": q, "error": str(ex)})
    total = len(TESTS)
    res = {"ranking": {"hit1": hit1/total, "hit3": hit3/total, "details": details}}
    print("Ranking Eval:", res["ranking"])
    return res

if __name__ == "__main__":
    r = run()
    with open("evaluation_results.json", "w") as f:
        json.dump({"ranking": r["ranking"]}, f, indent=2)
    print("Saved evaluation_results.json")
