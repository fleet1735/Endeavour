# 01_src/engines/parallel_runner.py

import os
import sys
import concurrent.futures
import traceback
import json
import pandas as pd
from backtesting import Backtest

# ✅ 어디서 실행해도 utils 경로를 찾도록 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from utils.data_handler import load_universe, fetch_ohlcv, save_to_cache, load_cached_csv
from utils.strategy_builder import build_strategy_from_json as build_strategy

# 📂 캐시 및 리포트 경로
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "04_data", "cache"))
REPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "04_data", "reports"))
STRATEGY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "strategies", "approved"))

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def run_backtest(ticker: str, strategy_config: dict, start: str = None, end: str = None):
    try:
        df = fetch_ohlcv(ticker, start=start, end=end)

        if df is None or df.empty:
            print(f"[WARN] {ticker}: 데이터가 비어 있습니다.")
            return ticker, None

        # 전략 클래스 생성
        StrategyClass = build_strategy(strategy_config)

        bt = Backtest(
            df,
            StrategyClass,
            cash=10_000_000,
            commission=.001,
            trade_on_close=True
        )
        stats = bt.run()
        return ticker, stats

    except Exception as e:
        print(f"Task failed for {ticker}: {e}")
        traceback.print_exc()
        return ticker, None


def main():
    # 📌 유니버스 로드
    tickers = load_universe()
    print(f"[INFO] Universe 로드 완료: {len(tickers)} tickers")

    # 📌 전략 JSON 로드 (샘플)
    strategy_file = os.path.join(STRATEGY_DIR, "sample_strategy.json")
    with open(strategy_file, "r", encoding="utf-8") as f:
        strategy_config = json.load(f)

    results = {}

    # 병렬 실행
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(run_backtest, ticker, strategy_config): ticker
            for ticker in tickers
        }

        for future in concurrent.futures.as_completed(futures):
            ticker, stats = future.result()
            if stats is not None:
                results[ticker] = stats

    # 📊 리포트 저장
    report_file = os.path.join(REPORT_DIR, "backtest_results.csv")
    if results:
        df_report = pd.DataFrame(results).T
        df_report.to_csv(report_file, encoding="utf-8-sig")
        print(f"[INFO] 리포트 저장 완료: {report_file}")
    else:
        print("[WARN] 저장할 결과가 없습니다.")


if __name__ == "__main__":
    main()
