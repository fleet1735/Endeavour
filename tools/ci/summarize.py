#!/usr/bin/env python3
import json, sys, pathlib, os

ART = pathlib.Path("artifacts")
F101 = ART / "cf_101.json"
F201 = ART / "cf_201.json"

def load_json(p: pathlib.Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def main():
    # branch name comes from GitHub Actions; default 'unknown'
    ref_name = os.environ.get("GITHUB_REF_NAME","unknown")
    # test-only flag: allowed only when branch != main
    force_flag_allowed = (ref_name != "main")
    force_flag = force_flag_allowed and pathlib.Path("force_gate_fail.flag").exists()

    a = load_json(F101)
    b = load_json(F201)

    # require both validator outputs present & parseable
    have_both = (a is not None) and (b is not None)
    both_pass = False
    if have_both:
        both_pass = bool(a.get("pass")) and bool(b.get("pass"))

    # if force flag (on non-main) present => override to false for demo
    if force_flag:
        summary_pass = False
    else:
        summary_pass = have_both and both_pass

    # write report files
    md = []
    md.append("# VALIDATOR_REPORT")
    md.append("")
    md.append("## cf_101.json")
    md.append(f"- present: {a is not None}")
    md.append(f"- pass: {a.get('pass') if a else 'n/a'}")
    md.append("")
    md.append("## cf_201.json")
    md.append(f"- present: {b is not None}")
    md.append(f"- pass: {b.get('pass') if b else 'n/a'}")
    md.append("")
    md.append(f"**summary.pass={str(summary_pass).lower()}**")

    pathlib.Path("VALIDATOR_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    ART.mkdir(exist_ok=True)
    (ART / "summary_line.txt").write_text(f"summary.pass={str(summary_pass).lower()}", encoding="utf-8")

    print(f"[summarize] branch={ref_name} have_both={have_both} both_pass={both_pass} summary.pass={str(summary_pass).lower()}")
    return 0 if summary_pass else 2

if __name__ == "__main__":
    sys.exit(main())
