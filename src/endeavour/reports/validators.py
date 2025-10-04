"""
cache_validator.py
- 캐시 CSV 파일 유효성 검사
- 캐시 파일이 비었거나, 날짜 인덱스가 잘못됐거나, 행 수가 너무 적으면 로그 경고
"""
import os
import logging
import pandas as pd

LOG_PATH = os.path.join("data","logs","cache_validator.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

_logger = logging.getLogger("cache_validator")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    _fh.setFormatter(_fmt)
    _logger.addHandler(_fh)

def validate_cache(path: str, min_rows: int = 10) -> dict:
    report = {"path": path, "exists": False, "valid": False}
    if not os.path.exists(path):
        _logger.error("Cache not found: %s", path)
        return report

    report["exists"] = True
    try:
        df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    except Exception as e:
        _logger.error("Cache read failed: %s (%s)", path, e)
        return report

    nrows = len(df)
    report["rows"] = nrows
    if nrows < min_rows:
        _logger.warning("Cache too small: %s (%d rows)", path, nrows)
        return report

    if not isinstance(df.index, pd.DatetimeIndex):
        _logger.warning("Cache index not datetime: %s", path)
        return report

    report["first_date"] = str(df.index.min().date())
    report["last_date"] = str(df.index.max().date())
    report["valid"] = True
    _logger.info("Cache valid: %s rows=%d range=%s→%s", path, nrows, report["first_date"], report["last_date"])
    return report
