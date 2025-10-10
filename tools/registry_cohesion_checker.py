#!/usr/bin/env python3
import sys, json, argparse, yaml

def load_json(p): 
    import json, pathlib
    obj=json.load(open(p,"r",encoding="utf-8"))
    # flatten top-level required+properties keys for simple isomorphism check
    req=set(obj.get("required",[]))
    props=set((obj.get("properties") or {}).keys())
    return {"required":req, "props":props}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, help="ontology/registry.yaml (SSOT)")
    ap.add_argument("--schema", required=True, action="append", help="*.schema.json (repeatable)")
    ap.add_argument("--out", default="registry_cohesion_report.json")
    args=ap.parse_args()

    reg = yaml.safe_load(open(args.registry,"r",encoding="utf-8"))
    # expect reg["entities"][name]["required"/"properties"]
    entities = reg.get("entities",{})

    report={"diffs":[],"ok":True}
    for spath in args.schema:
        s = load_json(spath)
        name = (json.load(open(spath,"r",encoding="utf-8"))).get("title")
        ent = entities.get(name,{})
        rset=set(ent.get("required",[]) or [])
        pset=set(ent.get("properties",[]) or [])
        d = {
          "schema": spath,
          "entity": name,
          "missing_in_registry_required": sorted(s["required"]-rset),
          "missing_in_registry_props": sorted(s["props"]-pset),
          "missing_in_schema_required": sorted(rset - s["required"]),
          "missing_in_schema_props": sorted(pset - s["props"])
        }
        if any([d["missing_in_registry_required"], d["missing_in_registry_props"], d["missing_in_schema_required"], d["missing_in_schema_props"]]):
            report["ok"]=False
            report["diffs"].append(d)

    import json
    with open(args.out,"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)

    if not report["ok"]:
        sys.exit(3)

if __name__=="__main__":
    main()