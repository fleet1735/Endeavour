import json, os, yaml

os.makedirs("runs/ci", exist_ok=True)
status={"pass": True, "checks":[]}
path=None
for c in ("registry.yaml","registry.yml"):
    if os.path.exists(c):
        path=c; break

if not path:
    status["pass"]=False
    status["checks"].append({"id":"REG-001","msg":"registry not found"})
else:
    try:
        data=yaml.safe_load(open(path,"r",encoding="utf-8"))
        if not isinstance(data,dict):
            status["pass"]=False
            status["checks"].append({"id":"REG-002","msg":"root must be mapping"})
    except Exception as e:
        status["pass"]=False
        status["checks"].append({"id":"REG-003","msg":f"YAML error: {e}"})

with open("runs/ci/cf_ont_201.json","w",encoding="utf-8") as f:
    json.dump(status,f,ensure_ascii=False)
print("CF-ONT-201:", json.dumps(status,ensure_ascii=False))
