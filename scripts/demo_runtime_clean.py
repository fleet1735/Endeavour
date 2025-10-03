import os, glob, sys
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from endeavour.utils.runtime_clean import runtime_clean

def main():
    cache_dir = os.path.join("data", "cache")
    files = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not files:
        print("No cache csv files found in data/cache")
        return
    path = files[0]
    ticker = os.path.basename(path).split("_")[0]
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df2 = runtime_clean(df, ticker)

    print(f"RUNTIME[{ticker}] rows_before={len(df)} rows_after={len(df2)}")
    if len(df2) > 0:
        print(f"first_date={df2.index.min().date()} last_date={df2.index.max().date()}")
    print("cache untouched ✓")

if __name__ == "__main__":
    main()
