#!/usr/bin/env python3
import json, sys, pathlib, yaml

def check_registry(p: pathlib.Path):
    if not p.exists():
        return (False, ["registry.yaml missing"])
    try:
        obj = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as e:
        return (False, [f"yaml parse error: {e}"])
    if not isinstance(obj, dict):
        return (False, ["registry root must be a mapping"])
    missing = [k for k in ("name","version","entities") if k not in obj]
    if missing:
        return (False, [f"missing keys: {','.join(missing)}"])
    # entities type check (minimal)
    ents = obj.get("entities")
    if not isinstance(ents, (list, dict)):
        return (False, ["entities must be list or mapping"])
    return (True, ["OK"])

def main():
    ok, details = check_registry(pathlib.Path("registry.yaml"))
    report = {"name":"cf_201","checks":["registry_minimal_presence"],"pass": ok, "details": details}
    pathlib.Path("artifacts").mkdir(exist_ok=True)
    pathlib.Path("artifacts/cf_201.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[cf_201] {'PASS' if ok else 'FAIL'} — {details}")
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
