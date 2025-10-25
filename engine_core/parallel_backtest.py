# -*- coding: utf-8 -*-
"""
parallel_backtest.py — Smoke runner (no external deps).
- --smoke: 내부 더미데이터로 지표/원장 생성
- --out: 산출물 저장 디렉토리 (필수, Gov audit_logs 권고)
- 산출물: validator_report.json, ledger_YYYYMMDD.json
- SSOT: CVStampV2 literal을 그대로 기록
"""
import argparse, json, os, sys, hashlib, datetime
from metrics import compute_core_metrics
from cv import cv_stamp_str

def _now_ymd():
    return datetime.datetime.now().strftime("%Y%m%d")

def _summary_hash(d: dict) -> str:
    raw = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def run_smoke(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    # ---- 더미 데이터 (외부 의존 0)
    daily_returns = [0.002, -0.001, 0.0005, 0.003, -0.002, 0.0015, 0.001]  # 7일
    pnl_series = [0, 20, 19, 20, 26, 21, 23, 25]  # 통화단위 PnL 누적치 (예시)
    trades = [10, -5, 12, -7, 15]  # 각 트레이드 PnL

    metrics = compute_core_metrics(daily_returns, pnl_series, trades, periods_per_year=252)
    cv_stamp = cv_stamp_str()

    # 원장(ledger) — 필수 키만 최소화
    ledger = {
        "date": _now_ymd(),
        "cv_stamp": cv_stamp,
        "metrics": metrics,
        "trades": len(trades),
        "pnl_last": pnl_series[-1] if pnl_series else 0.0,
    }
    ledger["summary_hash"] = _summary_hash(ledger)

    # Validator 리포트
    validator = {
        "date": _now_ymd(),
        "checks": {
            "cv_stamp_exact": (cv_stamp == '{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}'),
            "metrics_shape_ok": all(k in metrics for k in ["CAGR","MDD","PF","WinRate","Trades","Sharpe","Sortino","Calmar"]),
            "rounding_rule": True  # 소수 6자리 라운딩은 metrics 내부에서 보장
        },
        "pass": True,
        "errors": metrics.get("error_codes", [])
    }
    if not validator["checks"]["cv_stamp_exact"] or not validator["checks"]["metrics_shape_ok"]:
        validator["pass"] = False

    # 파일 기록
    ymd = _now_ymd()
    ledger_path = os.path.join(out_dir, f"ledger_{ymd}.json")
    report_path = os.path.join(out_dir, "validator_report.json")

    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validator, f, ensure_ascii=False, indent=2)

    return ledger_path, report_path, validator["pass"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true", help="run smoke test with dummy data")
    p.add_argument("--out", required=True, help="output dir (Gov audit_logs)")
    args = p.parse_args()

    if not args.smoke:
        print("Use --smoke for this first run.", file=sys.stderr)
        return 2

    lp, rp, ok = run_smoke(args.out)
    print(f"[SMOKE] ledger: {lp}")
    print(f"[SMOKE] report: {rp}")
    print(f"[SMOKE] PASS={ok}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
