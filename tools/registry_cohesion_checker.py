#!/usr/bin/env python3
import sys, json, argparse, yaml
def load_json_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    req = set(obj.get("required", []))
    props = set((obj.get("properties") or {}).keys())
    title = obj.get("title")
    return title, {"required": req, "props": props}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--schema", action="append", required=True)
    ap.add_argument("--out", default="registry_cohesion_report.json")
    args = ap.parse_args()
    with open(args.registry, "r", encoding="utf-8") as f:
        reg = yaml.safe_load(f) or {}
    entities = reg.get("entities", {})
    report = {"diffs": [], "ok": True}
    for spath in args.schema:
        title, s = load_json_schema(spath)
        ent = entities.get(title, {})
        rset = set(ent.get("required", []) or [])
        pset = set(ent.get("properties", []) or [])
        diff = {
            "schema": spath,
            "entity": title,
            "missing_in_registry_required": sorted(s["required"] - rset),
            "missing_in_registry_props": sorted(s["props"] - pset),
            "missing_in_schema_required": sorted(rset - s["required"]),
            "missing_in_schema_props": sorted(pset - s["props"]),
        }
        if any(diff[k] for k in diff if k.startswith("missing_")):
            report["ok"] = False
            report["diffs"].append(diff)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    sys.exit(0 if report["ok"] else 3)
if __name__ == "__main__":
    main()