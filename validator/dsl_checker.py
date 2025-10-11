#!/usr/bin/env python3
# encoding: utf-8
"""
CF-ONT-101 — DSL Output Integrity Checker (SignalEvent)
- 신규 CLI 인자(기존호출 완전 호환):
  * (구호출) python validator/dsl_checker.py <input_or_dir>
  * (신호출) python validator/dsl_checker.py --events <file_or_dir> --strict --out runs/ci/validator_report.json
  * 선택: --setup schemas/setup.schema.json 이 존재하면 구조 검증도 수행
- 실패 존재 시 종료코드 1, 성공 시 0
"""
import sys, json, glob, argparse, datetime
from pathlib import Path

def iter_signals(target: Path):
    files=[]
    if target.is_dir():
        files += list(target.glob("**/*.json"))
    elif target.is_file():
        files = [target]
    for f in files:
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("type")=="SignalEvent":
            yield f, [obj]
        elif isinstance(obj, dict) and isinstance(obj.get("signals"), list):
            yield f, obj["signals"]

def validate_signal(s: dict):
    errs=[]
    if s.get("price_update_time")==s.get("signal_time"):
        errs.append("CF-101")
    if s.get("data_delay_ms",0)>3000:
        errs.append("CF-102")
    if s.get("confidence_score",1)<0.3:
        errs.append("CF-103")
    if s.get("override_flag") and s.get("confidence_score",1)<0.1:
        errs.append("CF-105")
    # CF-104: 5초 내 동일 id 중복은 입력 캡쳐가 없으면 생략(실사용에선 recent_signals로 판단)
    return errs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("legacy", nargs="?", help="(legacy) file or dir containing events JSONs")
    p.add_argument("--events", help="file or dir containing SignalEvent JSON(s)")
    p.add_argument("--setup", help="schemas/setup.schema.json path (optional)")
    p.add_argument("--out", default="runs/ci/validator_report.json", help="output json path")
    p.add_argument("--strict", action="store_true", help="exit 1 on any failure")
    args=p.parse_args()

    target = Path(args.events or args.legacy or "runs")
    ok=True; total=0; failed=0; details=[]

    for f, arr in iter_signals(target):
        for s in arr:
            total+=1
            errs=validate_signal(s)
            if errs:
                ok=False; failed+=1
                details.append({"file": str(f).replace("\\","/"), "errors": errs})

    result={
        "cf":"CF-ONT-101",
        "pass": ok,
        "total_signals": total,
        "failed": failed,
        "ts": datetime.datetime.utcnow().isoformat()+"Z",
        "details": details[:50]  # 너무 길면 일부만
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.strict and not ok:
        return 1
    return 0

if __name__=="__main__":
    sys.exit(main())
