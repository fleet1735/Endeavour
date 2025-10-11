#!/usr/bin/env python3
import json, sys, pathlib

def load(name):
    p = pathlib.Path(f"artifacts/{name}.json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"name": name, "pass": False, "details": ["missing"]}

def main():
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
