#!/usr/bin/env python3
import sys, json, argparse, yaml

def load_json(p):
    obj=json.load(open(p,"r",encoding="utf-8"))
    # flatten top-level required+properties keys for simple isomorphism check
    req=set(obj.get("required",[]))
    props=set((obj.get("properties") or {}).keys())
    return {"required":req, "props":props}

def main():

with open(args.out,"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)

    if not report["ok"]:
        sys.exit(3)

if __name__=="__main__":
    main()