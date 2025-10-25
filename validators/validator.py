"""
validator.py — validates last ledger and writes report to audit/logs
"""
import os, json, glob, sys
AUDIT_DIR = r"D:\GoogleDrive\Endeavour_Gov\audit"
os.makedirs(AUDIT_DIR, exist_ok=True)
def validate(path:str)->dict:
    with open(path,"r",encoding="utf-8") as f: data=json.load(f)
    ok=all("summary_hash" in x for x in data)
    rep={"ok":ok,"count":len(data),"path":path}
    p=os.path.join(AUDIT_DIR,"validator_report.json")
    with open(p,"w",encoding="utf-8") as f: json.dump(rep,f,ensure_ascii=False,indent=2)
    print(f"[validator] ok={ok} count={len(data)} → {p}")
    return rep
if __name__=="__main__":
    ledgers=sorted(glob.glob(os.path.join(r"D:\GoogleDrive\Endeavour_Gov\audit","ledgers","ledger_*.json")))
    if not ledgers:
        print("[validator] no ledgers found"); sys.exit(1)
    validate(ledgers[-1])
