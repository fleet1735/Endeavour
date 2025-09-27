import os
import logging
from pathlib import Path
import yfinance as yf
from pykrx import stock
# ?? ??
VERSION = "data_handler FINAL FULL | 2025-09-27"
# ???? ?? (04_data ? data)
CACHE_DIR = Path("data/cache")
LOG_DIR   = Path("data/logs")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
# ?? ??
logging.basicConfig(
    filename=LOG_DIR / "data_handler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
def get_cache_path(ticker, start, end):
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"
def main():
    logging.info(f"=== Data Handler ?? (?? {VERSION}) ===")
    print(f"[INFO] Data Handler ?? (?? {VERSION})")
if __name__ == "__main__":
    main()
