import os, json, datetime, hashlib
from pathlib import Path
try:
  import pandas as pd
  HAVE_PANDAS = True
except Exception:
  HAVE_PANDAS = False

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO/"runs"; RUNS.mkdir(parents=True, exist_ok=True)
STAGE = REPO/"ci_out"; STAGE.mkdir(parents=True, exist_ok=True)
AUDIT = STAGE/"audit_logs"; AUDIT.mkdir(parents=True, exist_ok=True)
PROMO = STAGE/"promotion_checklist.md"

LEDGER_JSONL = RUNS/"ledger.jsonl"
LEDGER_PARQUET = RUNS/"ledger.parquet"
SAMPLES = REPO/"samples"
DATASETS = REPO/"datasets"/"registry.json"

def now_iso(): return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

def read_json(p:Path):
  with p.open("r", encoding="utf-8") as f: return json.load(f)

pe = read_json(SAMPLES/"promotion_event.sample.json")
ca = read_json(SAMPLES/"compliance_audit.sample.json")
se = read_json(SAMPLES/"signal_event.sample.json")
reg = read_json(Path(DATASETS))
ds = next((d for d in reg.get("datasets",[]) if d.get("dataset_id")==se.get("dataset_id")), None)

event = {
  "ts": now_iso(),
  "type": "PromotionFinalize",
  "promotion_event": pe,
  "compliance_audit": ca,
  "signal_event": se,
  "dataset_ref": ds,
  "integrity": {
    "dq_snapshot_score": (ds or {}).get("dq_snapshot_score"),
    "links_ok": pe.get("compliance_audit_id")==ca.get("compliance_audit_id")
  }
}

# Append-only ledger (jsonl)
LEDGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
with LEDGER_JSONL.open("a", encoding="utf-8") as f:
  f.write(json.dumps(event, ensure_ascii=False)+"\n")

# Parquet snapshot
if HAVE_PANDAS and LEDGER_JSONL.exists():
  rows=[]
  with LEDGER_JSONL.open("r", encoding="utf-8") as f:
    for line in f:
      line=line.strip()
      if line: rows.append(json.loads(line))
  if rows:
    import pandas as pd
    pd.json_normalize(rows, sep=".").to_parquet(LEDGER_PARQUET, index=False)

# Stage-only docs (no repo/docs write)
stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
daily = AUDIT/(datetime.date.today().strftime("%Y-%m-%d")+".md")
section = [
  f"## Promotion Finalized — {stamp}",
  f"- promotion_event_id: {pe.get('promotion_event_id')}",
  f"- compliance_audit_id: {ca.get('compliance_audit_id')}",
  f"- setup_id: {pe.get('target_setup_id')}",
  f"- dataset_id: {se.get('dataset_id')}",
  f"- dq_snapshot_score: {(ds or {}).get('dq_snapshot_score')}",
  f"- links_ok: {pe.get('compliance_audit_id')==ca.get('compliance_audit_id')}",
  ""
]
content="\n".join(section)+"\n"
if daily.exists(): daily.write_text(content + "\n" + daily.read_text(encoding="utf-8"), encoding="utf-8")
else: daily.write_text("# Audit Log (staged)\n\n"+content, encoding="utf-8")

line = f"- [{stamp}] {pe.get('target_setup_id')} → audit:{ca.get('compliance_audit_id')} (DQ={(ds or {}).get('dq_snapshot_score')}, link_ok={pe.get('compliance_audit_id')==ca.get('compliance_audit_id')})\n"
if PROMO.exists(): PROMO.write_text(PROMO.read_text(encoding="utf-8")+line, encoding="utf-8")
else: PROMO.write_text("# Promotion Checklist (staged)\n\n"+line, encoding="utf-8")

print("Finalize staged: runs/ledger.*, ci_out/audit_logs, ci_out/promotion_checklist.md")