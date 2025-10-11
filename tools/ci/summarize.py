import json, os, sys

rep={}
for fn in ("runs/ci/cf_ont_101.json","runs/ci/cf_ont_201.json"):
    if os.path.exists(fn):
        with open(fn,"r",encoding="utf-8") as f:
            rep[os.path.basename(fn)]=json.load(f)

rep["summary"]={"pass": all(v.get("pass",False) for v in rep.values()) if rep else False}
txt=json.dumps(rep,ensure_ascii=False)
print("VALIDATOR_REPORT:", txt)

summ=os.environ.get("GITHUB_STEP_SUMMARY")
if summ:
    with open(summ,"a",encoding="utf-8") as f:
        f.write("### VALIDATOR_REPORT\n\n```\n"+txt+"\n```\n")

sys.exit(0 if rep["summary"].get("pass",False) else 1)
