#!/usr/bin/env python3
import json, sys, pathlib, os

def main():
    ok = True
    details = []
    # Minimal cohesion: schemas/setup.schema.json exists
    if not pathlib.Path("schemas/setup.schema.json").exists():
        ok = False
        details.append("schemas/setup.schema.json missing")

    report = {
        "name": "cf_201",
        "checks": ["ssot_registry_cohesion_minimal"],
        "pass": ok,
        "details": details or ["OK"]
    }
    pathlib.Path("artifacts").mkdir(exist_ok=True)
    pathlib.Path("artifacts/cf_201.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[cf_201] {'PASS' if ok else 'FAIL'}")
    return 2

if __name__ == "__main__":
    sys.exit(main())

