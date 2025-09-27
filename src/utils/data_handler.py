import os
import logging
from pathlib import Path
from datetime import date, timedelta
import yfinance as yf
from pykrx import stock
import pandas as pd
import holidays

# =============================
# 버전 정보
# =============================
VERSION = "data_handler FINAL FULL | 2025-09-27 (Stable ~300 lines, business-grade)"

# =============================
# 디렉토리 설정
# =============================
CACHE_DIR = Path("data/cache")
LOG_DIR   = Path("data/logs")
REPORT_DIR = Path("reports/data_quality")
for d in [CACHE_DIR, LOG_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# =============================
# 로깅 설정
# =============================
logging.basicConfig(
    filename=LOG_DIR / "data_handler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

# =============================
# 보조 함수: 최종 영업일 (T-1)
# =============================
def get_last_business_day_from_yesterday():
    """어제를 기준으로, 어제가 휴일(주말/공휴일)이면 직전 영업일 반환"""
    check_date = date.today() - timedelta(days=1)
    kr_holidays = holidays.KR(years=[check_date.year, check_date.year - 1])
    while True:
        is_weekend = check_date.isoweekday() in [6, 7]
        is_holiday = check_date in kr_holidays
        if not is_weekend and not is_holiday:
            return check_date
        check_date -= timedelta(days=1)

# =============================
# 캐시 경로
# =============================
def get_cache_path(ticker, start, end):
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"

# =============================
# 데이터 수집 - yfinance
# =============================
def fetch_yfinance(ticker, start, end):
    try:
        df = yf.download(str(ticker), start=start, end=end, progress=False)
        if df.empty:
            raise ValueError("No data from yfinance")
        df.reset_index(inplace=True)
        df = df.rename(columns={
            "Date": "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Adj Close": "Close",
            "Volume": "Volume"
        })[["Date", "Open", "High", "Low", "Close", "Volume"]]
        return df
    except Exception as e:
        logging.error(f"[yfinance error] {ticker}: {e}")
        return None

# =============================
# 데이터 수집 - pykrx
# =============================
def fetch_pykrx(ticker, start, end):
    try:
        code = ticker.replace(".KS", "").replace(".KQ", "")
        df = stock.get_market_ohlcv_by_date(start.replace("-", ""), end.replace("-", ""), code)
        if df.empty:
            raise ValueError("No data from pykrx")
        df.reset_index(inplace=True)
        df = df.rename(columns={
            "날짜": "Date",
            "시가": "Open",
            "고가": "High",
            "저가": "Low",
            "종가": "Close",
            "거래량": "Volume"
        })[["Date", "Open", "High", "Low", "Close", "Volume"]]
        return df
    except Exception as e:
        logging.error(f"[pykrx error] {ticker}: {e}")
        return None

# =============================
# 데이터 검증 함수
# =============================
def _validate_df(df: pd.DataFrame, start: str, end: str):
    """데이터 프레임 품질 검증"""
    result = {
        "Rows": len(df),
        "MissingDays": None,
        "NaNRatio": None,
        "NaNStreak": None,
        "AbnormalClose": False,
        "Result": "OK"
    }
    try:
        dfx = df.copy()
        dfx = dfx.drop_duplicates(subset=["Date"]).sort_values("Date")

        # 전체 영업일 계산
        all_days = pd.bdate_range(start=start, end=end)
        missing_days = set(all_days.date) - set(pd.to_datetime(dfx["Date"]).dt.date)
        result["MissingDays"] = len(missing_days)

        # NaN 비율
        nan_ratio = dfx.isna().mean().max()
        result["NaNRatio"] = round(float(nan_ratio), 4)

        # NaN 연속 구간
        nan_streak = (dfx.isna().any(axis=1).astype(int)
                      .groupby(dfx["Date"].notna().cumsum()).cumsum().max())
        result["NaNStreak"] = int(nan_streak) if pd.notna(nan_streak) else 0

        # 종가 이상치 검사 (0 또는 음수)
        if (dfx["Close"] <= 0).any():
            result["AbnormalClose"] = True

        # 결과 요약
        if result["MissingDays"] > 0 or result["NaNRatio"] > 0 or result["AbnormalClose"]:
            result["Result"] = "WARN_MISSING"

    except Exception as e:
        result["Result"] = f"ERROR: {e}"

    return result

# =============================
# 메인 로직 - 데이터 로드
# =============================
def load_price_data(ticker, start, end):
    cache_file = get_cache_path(ticker, start, end)
    if cache_file.exists():
        logging.info(f"[CACHE] hit: {cache_file}")
        df = pd.read_csv(cache_file, parse_dates=["Date"])
    else:
        df = fetch_yfinance(ticker, start, end)
        if df is None:
            df = fetch_pykrx(ticker, start, end)
        if df is not None:
            df.to_csv(cache_file, index=False, encoding="utf-8-sig")
            logging.info(f"[CACHE] saved: {cache_file}")

    if df is None:
        logging.error(f"[FAIL] {ticker}")
        return None, None

    # 검증
    report = _validate_df(df, start, end)
    return df, report

# =============================
# 리포트 저장
# =============================
def save_validation_report(results, tag: str):
    report_file = REPORT_DIR / f"validation_{tag}.csv"
    pd.DataFrame(results).to_csv(report_file, index=False, encoding="utf-8-sig")
    logging.info(f"[REPORT] Saved validation report → {report_file}")

# =============================
# main
# =============================
def main():
    last_bday = get_last_business_day_from_yesterday()
    start = "2020-01-01"
    end   = last_bday.strftime("%Y-%m-%d")
    tickers = ["005930.KS", "000660.KS", "035720.KS"]

    logging.info(f"=== Data Handler 실행 (버전 {VERSION}) ===")
    logging.info(f"기간: {start} ~ {end}")
    print(f"[INFO] Data Handler 실행 (버전 {VERSION})")
    print(f"[INFO] 기간: {start} ~ {end}")

    results = []
    for t in tickers:
        df, report = load_price_data(t, start, end)
        if df is not None:
            print(f"[OK] {t} rows={len(df)}")
            logging.info(f"[OK] {t} rows={len(df)}")
        else:
            print(f"[FAIL] {t}")
            logging.error(f"[FAIL] {t}")

        if report:
            report["Ticker"] = t
            results.append(report)

    # 리포트 저장
    if results:
        tag = date.today().strftime("%Y%m%d")
        save_validation_report(results, tag)

if __name__ == "__main__":
    main()
