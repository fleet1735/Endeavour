import os
import logging
from pathlib import Path
from datetime import date, timedelta
import yfinance as yf
from pykrx import stock
import holidays
# ?? ??
VERSION = "data_handler FINAL FULL | 2025-09-27 (last business day = yesterday)"
# ???? ??
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
def get_last_business_day_from_yesterday():
    \"\"\"??? ????, ??? ??(?? ?? ???)?? ?? ??? ??\"\"\"
    check_date = date.today() - timedelta(days=1)
    kr_holidays = holidays.KR(years=[check_date.year, check_date.year - 1])
    while True:
        is_weekend = check_date.isoweekday() in [6, 7]  # ?=6, ?=7
        is_holiday = check_date in kr_holidays
        if not is_weekend and not is_holiday:
            return check_date
        check_date -= timedelta(days=1)
def main():
    last_bday = get_last_business_day_from_yesterday()
    logging.info(f"=== Data Handler ?? (?? {VERSION}) ===")
    logging.info(f"???: {last_bday}")
    print(f"[INFO] Data Handler ?? (?? {VERSION}) | ???: {last_bday}")
if __name__ == "__main__":
    main()
