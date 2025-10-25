# engine_core package initializer
from .metrics import (
    cagr, mdd_positive, profit_factor, win_rate, trades_count,
    sharpe_annualized, sortino_annualized, calmar
)
from .cv import make_cv_stamp, split_purged_kfold, split_nested_walkforward
from .hashes import summary_hash_from_df, csv_sha256_from_df
from .excel_export import export_to_excel
