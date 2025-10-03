import os, glob, sys
import pandas as pd

# src 모듈 경로 보장
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from endeavour.utils.runtime_clean import runtime_clean
from endeavour.utils.cache_validator import validate_cache

def main():
    cache_dir = os.path.join("data", "cache")
    files = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not files:
        print("No cache files found.")
        return

    path = files[0]
    ticker = os.path.basename(path).split("_")[0]
    print(f"=== MINI TEST START [{ticker}] ===")

    # 1) 캐시 유효성 검사
    rep = validate_cache(path)
    print("Cache check:", rep)

    # 2) 데이터 로드 + 런타임 정리
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df2 = runtime_clean(df, ticker)
    print(f"Runtime clean: rows_before={len(df)}, rows_after={len(df2)}")

    if len(df2) > 0:
        print(f"Date range after clean: {df2.index.min().date()} → {df2.index.max().date()}")

    print("=== MINI TEST END ===")

if __name__ == "__main__":
    main()
