param(
  [int]$N = 1000  # business days for synthetic index
)

# 1) Import smoke
@"
import importlib
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
"@ | python -

# 2) CV base vs effective vs actual split consistency
@"
from engine_core.cv import make_cv_stamp, effective_cv_stamp, split_purged_kfold, split_nested_walkforward
import pandas as pd

n = {{N}}
idx = pd.date_range("2020-01-01", periods=n, freq="B")

base = make_cv_stamp()
eff  = effective_cv_stamp(idx, base)

# Purged K-Fold: check effective folds honored
folds_eff = eff["purged_kfold"]["folds"]
emb_eff   = eff["embargo_days"]

gen = split_purged_kfold(idx, folds=base["purged_kfold"]["folds"], embargo_days=base["embargo_days"])
tr, te = next(gen)
# Rough length check: test size within expected band
expected_fold_size = max(1, len(idx)//folds_eff)
assert abs(len(te) - expected_fold_size) <= 1, f"test size off: got {len(te)}, want ~{expected_fold_size}"
print("OK: cv purged_kfold folds=", folds_eff, "embargo=", emb_eff, "lens:", len(tr), len(te))

# Nested WF: check number of WF windows realized
wf_eff = eff["nested_wf"]["windows"]
cnt = 0
for _tr, _te in split_nested_walkforward(idx, windows=base["nested_wf"]["windows"], folds=base["purged_kfold"]["folds"], embargo_days=base["embargo_days"]):
    cnt += 1
assert cnt >= wf_eff, f"nested WF count too small: {cnt} < {wf_eff}"
print("OK: cv nested_wf windows=", wf_eff, "iters:", cnt)
"@.Replace("{{N}}", "$N") | python -

# 3) vectorbt presence (non-failing either way)
@"
try:
    from engines.vectorbt_runner import run_broadcast
    print("vectorbt present")
except ImportError as e:
    print("OK: vectorbt not installed; ImportError expected:", e)
"@ | python -
