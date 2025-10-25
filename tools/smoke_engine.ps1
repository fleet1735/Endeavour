param(
  [int]$N = 1000,
  [string]$BASE = "D:\Endeavour_Dev"
)

# 보강: 프로젝트 루트로 이동 + PYTHONPATH 삽입
Set-Location "D:\Endeavour_Dev"
if ($env:PYTHONPATH) { $env:PYTHONPATH = "D:\Endeavour_Dev;$env:PYTHONPATH" } else { $env:PYTHONPATH = "D:\Endeavour_Dev" }

# 1) Import smoke
@'
import importlib, sys, os
# 추가 안전망: 런타임에서도 sys.path에 BASE 주입
base = os.getenv("PYTHONPATH","").split(";")[0]
if base and base not in sys.path: sys.path.insert(0, base)
mods = [
    "engine_core",
    "engine_core.cv",
    "engine_core.metrics",
    "engine_core.hashes",
    "engine_core.excel_export",
    "engines",
    "engines.vectorbt_runner",
]
for m in mods:
    importlib.import_module(m)
print("OK: imports")
'@ | python -

# 2) CV base vs effective vs actual split consistency
@'
from engine_core.cv import make_cv_stamp, effective_cv_stamp, split_purged_kfold, split_nested_walkforward
import pandas as pd, os, sys
base = os.getenv("PYTHONPATH","").split(";")[0]
if base and base not in sys.path: sys.path.insert(0, base)

n = 1000
idx = pd.date_range("2020-01-01", periods=n, freq="B")

base_stamp = make_cv_stamp()
eff        = effective_cv_stamp(idx, base_stamp)

folds_eff = eff["purged_kfold"]["folds"]
emb_eff   = eff["embargo_days"]

gen = split_purged_kfold(idx, folds=base_stamp["purged_kfold"]["folds"], embargo_days=base_stamp["embargo_days"])
tr, te = next(gen)
expected_fold_size = max(1, len(idx)//folds_eff)
assert abs(len(te) - expected_fold_size) <= 1, f"test size off: got {len(te)}, want ~{expected_fold_size}"
print("OK: cv purged_kfold folds=", folds_eff, "embargo=", emb_eff, "lens:", len(tr), len(te))

wf_eff = eff["nested_wf"]["windows"]
cnt = 0
for _tr, _te in split_nested_walkforward(idx, windows=base_stamp["nested_wf"]["windows"], folds=base_stamp["purged_kfold"]["folds"], embargo_days=base_stamp["embargo_days"]):
    cnt += 1
assert cnt >= wf_eff, f"nested WF count too small: {cnt} < {wf_eff}"
print("OK: cv nested_wf windows=", wf_eff, "iters:", cnt)
'@ | python -

# 3) vectorbt presence
@'
try:
    from engines.vectorbt_runner import run_broadcast
    print("vectorbt present")
except ImportError as e:
    print("OK: vectorbt not installed; ImportError expected:", e)
'@ | python -
