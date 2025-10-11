import json, glob, os

os.makedirs("runs/ci", exist_ok=True)

def validate_signal(s):
    e=[]
    if s.get("price_update_time")==s.get("signal_time"): e.append("CF-101")
    if s.get("data_delay_ms",0)>3000: e.append("CF-102")
    if s.get("confidence_score",1)<0.3: e.append("CF-103")
    if s.get("override_flag") and s.get("confidence_score",1)<0.1: e.append("CF-105")
    return e

files = sorted(set(
    glob.glob("runs/**/*.json", recursive=True) +
    glob.glob("engine/**/*.json", recursive=True) +
    glob.glob("**/signals*.json", recursive=True)
))
ok=True; details=[]
for f in files:
    try:
        obj=json.load(open(f,"r",encoding="utf-8"))
    except Exception:
        continue
    sigs=[]
    if isinstance(obj,dict):
        if obj.get("type")=="SignalEvent":
            sigs=[obj]
        elif isinstance(obj.get("signals"),list):
            sigs=obj["signals"]
    for s in sigs:
        errs=validate_signal(s)
        details.append({"file":f,"errors":errs})
        if errs: ok=False

rep={"pass":ok,"files_scanned":len(files),"details":details}
with open("runs/ci/cf_ont_101.json","w",encoding="utf-8") as f:
    json.dump(rep,f,ensure_ascii=False)
print("CF-ONT-101..105:", json.dumps(rep,ensure_ascii=False))
