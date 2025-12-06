# evaluation/evaluate_pipeline.py
"""
Run all evaluation scripts and merge results into evaluation/evaluation_results.json
"""
import subprocess, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
results = {}

scripts = ["ner_eval.py", "dedupe_eval.py", "impact_eval.py", "ranking_eval.py"]

for s in scripts:
    print("Running", s)
    path = os.path.join(ROOT, s)
    # run in-process to get returned dict if possible, else run subprocess
    try:
        ns = {}
        with open(path, "r", encoding="utf-8") as fh:
            code = compile(fh.read(), path, "exec")
            exec(code, ns, ns)
        # try to get 'run' return value
        if "run" in ns:
            try:
                r = ns["run"]()
                # merge r into results
                results.update(r)
            except Exception as e:
                print(f"Script {s} run() failed: {e}")
    except Exception as e:
        print(f"in-process exec failed for {s}: {e}")
        # fallback to subprocess
        try:
            out = subprocess.check_output([sys.executable, path], cwd=ROOT, stderr=subprocess.STDOUT, text=True, timeout=120)
            print(out)
            # attempt to read evaluation_results.json written by the script
            p = os.path.join(ROOT, "evaluation_results.json")
            if os.path.exists(p):
                data = json.load(open(p, "r", encoding="utf-8"))
                results.update(data)
        except Exception as e2:
            print(f"Subprocess failed for {s}: {e2}")

# final write
outpath = os.path.join(ROOT, "evaluation_results.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("All done. Results saved to", outpath)
