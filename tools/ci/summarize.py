#!/usr/bin/env python3
import json, sys, pathlib

def load(name):
    p = pathlib.Path(f"artifacts/{name}.json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"name": name, "pass": False, "details": ["missing"]}

def main():
    import os, pathlib
    # Gate FAIL 강제용: repo 루트의 flag 파일이 있으면 summary.pass=false
    if os.path.exists("force_gate_fail.flag") or os.environ.get("GATE_FORCE_FALSE") == "1":
        a = {"name":"cf_101","pass": True, "details":["forced context"]}
        b = {"name":"cf_201","pass": True, "details":["forced context"]}
        all_ok = False
        md = ["# VALIDATOR_REPORT","", "## cf_101","- pass: True","- details: [\"forced context\"]","",
              "## cf_201","- pass: True","- details: [\"forced context\"]","",
              "**summary.pass=false**"]
        pathlib.Path("VALIDATOR_REPORT.md").write_text("\n".join(md), encoding="utf-8")
        pathlib.Path("artifacts").mkdir(exist_ok=True)
        pathlib.Path("artifacts/summary_line.txt").write_text("summary.pass=false", encoding="utf-8")
        print("[summarize] forced gate failure via flag")
        return 0
    a = load("cf_101")
    b = load("cf_201")
    all_ok = a.get("pass") and b.get("pass")
    md = []
    md.append("# VALIDATOR_REPORT")
    md.append("")
    for r in (a,b):
        md.append(f"## {r.get('name')}")
        md.append(f"- pass: {r.get('pass')}")
        md.append(f"- details: {r.get('details')}")
        md.append("")
    md.append(f"**summary.pass={str(all_ok).lower()}**")
    pathlib.Path("VALIDATOR_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    # Also write a one-line status for CI step summary (runner side will append)
    pathlib.Path("artifacts/summary_line.txt").write_text(f"summary.pass={str(all_ok).lower()}", encoding="utf-8")
    print(f"[summarize] summary.pass={str(all_ok).lower()}")
    return 0 if all_ok else 2

if __name__ == "__main__":
    sys.exit(main())

