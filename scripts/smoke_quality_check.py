import os
import glob
import pandas as pd
import sys

# src 패키지 경로 추가 (endeavour 임포트용)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from endeavour.utils.data_quality import clean_missing_values

def main():
    cache_dir = os.path.join("data", "cache")
    files = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not files:
        print("No cache csv files found in data/cache")
        return
    path = files[0]
    ticker = os.path.basename(path).split("_")[0]
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    cleaned, rep = clean_missing_values(df, ticker)
    print(f"SMOKE[{ticker}] rows_before={rep['rows_before']} rows_after={rep['rows_after']} "
          f"dropped_non_trading={rep['dropped_non_trading_rows']} dup_idx={rep['dropped_duplicate_index']}")
    print(f"first_date={rep.get('first_date')} last_date={rep.get('last_date')}")
    print("Log -> data/logs/data_quality.log")

if __name__ == "__main__":
    main()
