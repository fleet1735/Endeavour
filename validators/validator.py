"""
validator.py — Handshake validator for Endeavour
- Reads latest ledger_*.json
- Verifies presence of summary_hash and minimal fields
- Emits validator_report.json
"""
import os, json, glob, sys

REQ_FIELDS = ["name","params","cv","seed","metrics","summary_hash"]
def validate_ledger(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        arr = json.load(f)
    ok = True; reasons=[]
    for i, row in enumerate(arr):
        for k in REQ_FIELDS:
            if k not in row:
                ok=False; reasons.append(f"row#{i} missing {k}")
    rep = {"ok": ok, "reasons": reasons, "count": len(arr), "path": path}
    return rep

def main():
    ledgers = sorted(glob.glob(os.path.join("ledgers", "ledger_*.json")))
    if not ledgers:
        print("[validator] no ledger files"); sys.exit(2)
    rep = validate_ledger(ledgers[-1])
    with open("validator_report.json","w",encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(f"[validator] ok={rep['ok']} count={rep['count']} → validator_report.json")

if __name__ == "__main__":
    main()
