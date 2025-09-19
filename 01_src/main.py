# main.py v2.4 (수정됨)
import json
import os
import shutil
import time
import logging
from datetime import date, datetime
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from pykrx import stock
import base64
import io
import hashlib
import csv

EXCESS_RETURN_COL = '초과 성과 (Portfolio - KOSPI)'

# --- 라이브러리 종속성 ---
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import seaborn as sns
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("Fatal Error: Required libraries not found. Please run: pip install matplotlib seaborn python-dateutil")
    exit()

# --- 로깅 및 Matplotlib 한글 폰트 설정 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def setup_matplotlib_font():
    if plt is None: return
    font_paths = ['C:/Windows/Fonts/malgun.ttf', '/System/Library/Fonts/Supplemental/AppleGothic.ttf']
    font_name = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            break
    if font_name:
        plt.rc('font', family=font_name)
        logging.info(f"Matplotlib 한글 폰트 설정 완료: {font_name}")
    else:
        logging.warning("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    plt.rc('axes', unicode_minus=False)

setup_matplotlib_font()

# ==============================================================================
# [v.2.0] 포트폴리오 관리 클래스 (Portfolio)
# ==============================================================================
class Portfolio:
    """모든 자산, 포지션, 거래 내역을 관리하는 중앙 허브"""
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.trade_log = []
        self.equity_curve = {}

    def update_equity(self, timestamp: pd.Timestamp, data: Dict[str, pd.DataFrame]):
        current_value = self.cash
        for ticker, info in self.positions.items():
            if ticker in data and timestamp in data[ticker].index:
                current_value += info['shares'] * data[ticker].loc[timestamp, 'Close']
        self.equity_curve[timestamp] = current_value

    def has_position(self, ticker: str) -> bool:
        return ticker in self.positions and self.positions[ticker]['shares'] > 0

    def get_average_entry_price(self, ticker: str) -> float:
        return self.positions.get(ticker, {}).get('average_price', 0)

    def execute_trade(self, timestamp: pd.Timestamp, ticker: str, trade_type: str, shares: int, price: float, reason: str) -> bool:
        trade_cost = shares * price
        if trade_type.upper() == 'BUY':
            if self.cash < trade_cost: return False
            self.cash -= trade_cost
            if not self.has_position(ticker):
                self.positions[ticker] = {'shares': shares, 'average_price': price}
            else:
                pos = self.positions[ticker]
                new_total_cost = (pos['shares'] * pos['average_price']) + trade_cost
                new_total_shares = pos['shares'] + shares
                pos['shares'] = new_total_shares
                pos['average_price'] = new_total_cost / new_total_shares
        elif trade_type.upper() == 'SELL':
            if not self.has_position(ticker) or self.positions[ticker]['shares'] < shares: return False
            self.cash += trade_cost
            self.positions[ticker]['shares'] -= shares
            if self.positions[ticker]['shares'] == 0:
                del self.positions[ticker]
        
        log_entry = {'date': timestamp, 'ticker': ticker, 'type': trade_type, 'shares': shares, 'price': price, 'reason': reason}
        self.trade_log.append(log_entry)
        return True

# ==============================================================================
# 1. 데이터 로더 (DataLoader)
# ==============================================================================
class DataLoader:
    def __init__(self, data_path='data'):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.script_dir, data_path)
        os.makedirs(self.data_path, exist_ok=True)

    def _coerce_price_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty: return pd.DataFrame()
        df.index = pd.to_datetime(df.index.astype(str), errors='coerce')
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        df = df[~df.index.isna()]
        return df

    def get_price_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        clean_ticker = ticker.split('.')[0]
        fname = os.path.join(self.data_path, f"{clean_ticker}_{start_date}_{end_date}.csv")
        if os.path.exists(fname):
            df = pd.read_csv(fname, index_col=0)
            return self._coerce_price_df(df)
        df = self._fetch_ticker_history(ticker, start_date, end_date)
        if not df.empty:
            df = self._coerce_price_df(df)
            df.to_csv(fname)
        return df

    def get_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        fname = os.path.join(self.data_path, f"BENCHMARK_{ticker}_{start_date}_{end_date}.csv")
        if os.path.exists(fname):
            df = pd.read_csv(fname, index_col=0)
            return self._coerce_price_df(df)
        try:
            df = stock.get_index_ohlcv(start_date.replace('-', ''), end_date.replace('-', ''), ticker)
            df.rename(columns={'시가':'Open','고가':'High','저가':'Low','종가':'Close','거래량':'Volume'}, inplace=True)
            df['Adj Close'] = df['Close']
            df.index.name = 'Date'
            df = self._coerce_price_df(df)
            if not df.empty: df.to_csv(fname)
            return df
        except Exception as e:
            logging.error(f"Failed to download benchmark data for {ticker}: {e}")
            return pd.DataFrame()

    def _fetch_ticker_history(self, ticker: str, start: str, end: str, max_retries=3, pause=1.0) -> pd.DataFrame:
        ticker_code = ticker.split('.')[0]
        for attempt in range(1, max_retries + 1):
            try:
                df = stock.get_market_ohlcv(start.replace('-', ''), end.replace('-', ''), ticker_code)
                if df.empty: return pd.DataFrame()
                df.rename(columns={'시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume'}, inplace=True)
                df['Adj Close'] = df['Close']
                df.index.name = 'Date'
                return self._coerce_price_df(df)
            except Exception as e:
                logging.warning(f"Download failed for {ticker} attempt {attempt}: {e}")
                time.sleep(pause * (2 ** (attempt - 1)))
        return pd.DataFrame()

    def get_ticker_metadata(self, tickers: List[str], base_date: str) -> List[str]:
        logging.info("Fetching ticker metadata for universe filtering...")
        valid_tickers = []
        try:
            all_market_tickers = set(stock.get_market_ticker_list(base_date, market="ALL"))
        except Exception as e:
            logging.error(f"Failed to get ticker lists from pykrx: {e}. Skipping filtering.")
            return tickers
        for ticker in tickers:
            clean_ticker = ticker.split('.')[0]
            if clean_ticker not in all_market_tickers:
                logging.warning(f"Ticker {ticker} is not a stock (ETF/ETN etc). Excluding.")
                continue
            try:
                df = stock.get_market_trading_value_by_date(base_date, base_date, clean_ticker)
                if df is None or df.empty:
                    logging.warning(f"No trading value data for {ticker} on {base_date}. Excluding.")
                    continue
                valid_tickers.append(ticker)
            except Exception:
                logging.warning(f"Could not verify {ticker}. Might be delisted, suspended, or admin issue. Excluding.")
                continue
        return valid_tickers

# ==============================================================================
# 2. 지표 계산기 (IndicatorCalculator)
# ==============================================================================
class IndicatorCalculator:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def calculate_all(self, strategy: Dict) -> pd.DataFrame:
        for indicator in strategy.get('indicators', []):
            self._calculate_indicator(indicator)
        return self.data

    def _calculate_indicator(self, config: Dict):
        name, type_ = config['id'], config['type'] # [수정] 'name' -> 'id'로 변경하여 IPD 원칙 준수
        params = config.get('params', {})
        try:
            if type_ == 'SMA':
                self.data[name] = self.data[params['source']].rolling(window=params['period']).mean()
            # [참고] v2.4 코드에는 MIN/MAX 로직이 누락되어 있음. 이후 버전에서 추가된 것으로 보임.
            # 이 부분은 현재 전략 파일의 MIN 지표를 처리하지 못해 오류를 발생시킬 수 있음.
            elif type_ == 'MIN':
                 self.data[name] = self.data[params['source']].rolling(window=params['period']).min()
            elif type_ == 'MAX':
                 self.data[name] = self.data[params['source']].rolling(window=params['period']).max()
            elif type_ == 'CALCULATION':
                self.data[name] = eval(params['formula'], {"__builtins__": None}, {"pd": pd, **self.data.to_dict('series')})
        except Exception as e:
            logging.error(f"Error evaluating indicator '{name}': {e}")

# ==============================================================================
# 3. 백테스팅 엔진 (Backtester)
# ==============================================================================
class Backtester:
    def __init__(self, data_with_indicators: pd.DataFrame, strategy: Dict, initial_capital: float, ticker: str):
        self.data = data_with_indicators
        self.strategy = strategy
        self.ticker = ticker
        self.portfolio = Portfolio(initial_capital)

    def run_backtest(self, position_sizing_pct=0.95):
        if self.data.empty or len(self.data) < 3:
            return self.get_final_results([])
        
        self.portfolio.equity_curve[self.data.index[0]] = self.portfolio.initial_capital
        closed_trades = []
        
        for i in range(2, len(self.data)):
            current_timestamp = self.data.index[i]
            day_before_prev_row, prev_row, row = self.data.iloc[i-2], self.data.iloc[i-1], self.data.iloc[i]

            if self.portfolio.has_position(self.ticker):
                exit_rules = self.strategy.get('exit_rules', {})
                # [참고] v2.4 코드는 복합적인 청산 규칙(TP/SL)을 지원하지 않음. 
                # IPD v2.5(통합 최적화 시스템)에서 고도화된 것으로 보임.
                if self._check_condition_recursive(row, prev_row, day_before_prev_row, exit_rules):
                    shares_to_sell = self.portfolio.positions[self.ticker]['shares']
                    sell_price = row['Open']
                    avg_buy_price = self.portfolio.get_average_entry_price(self.ticker)
                    profit_pct = (sell_price - avg_buy_price) / avg_buy_price if avg_buy_price > 0 else 0
                    closed_trades.append({'profit_pct': profit_pct})
                    self.portfolio.execute_trade(current_timestamp, self.ticker, 'SELL', shares_to_sell, sell_price, exit_rules.get('name', 'ExitRule'))
            else:
                entry_rules = self.strategy.get('entry_rules', {})
                if self._check_condition_recursive(row, prev_row, day_before_prev_row, entry_rules):
                    buy_price = row['Open']
                    capital_for_trade = self.portfolio.cash * position_sizing_pct
                    shares_to_buy = int(capital_for_trade / buy_price)
                    if shares_to_buy > 0:
                        self.portfolio.execute_trade(current_timestamp, self.ticker, 'BUY', shares_to_buy, buy_price, entry_rules.get('name', 'EntryRule'))
            
            self.portfolio.update_equity(current_timestamp, {self.ticker: self.data})

        return self.get_final_results(closed_trades)

    def get_final_results(self, closed_trades: List[Dict]) -> Dict:
        equity_series = pd.Series(self.portfolio.equity_curve).sort_index()
        final_equity = equity_series.iloc[-1] if not equity_series.empty else self.portfolio.initial_capital
        return {
            'final_value': final_equity, 'initial_capital': self.portfolio.initial_capital,
            'trades': closed_trades, 'raw_trade_log': self.portfolio.trade_log,
            'equity_curve': equity_series
        }

    def _check_condition_recursive(self, current_row: pd.Series, prev_row: pd.Series, day_before_prev_row: pd.Series, cond_group: Dict) -> bool:
        if not cond_group or 'conditions' not in cond_group: return False
        logic = cond_group.get('logic', 'AND').upper()
        results = []
        for cond in cond_group.get('conditions', []):
            if 'logic' in cond:
                results.append(self._check_condition_recursive(current_row, prev_row, day_before_prev_row, cond))
            else:
                op, left_key, right_str = cond.get('op'), cond.get('left'), cond.get('right')
                is_true = False
                if op == 'crosses_above':
                    left_prev, right_prev = prev_row.get(left_key), prev_row.get(right_str)
                    left_before, right_before = day_before_prev_row.get(left_key), day_before_prev_row.get(right_str)
                    if not pd.isna([left_prev, right_prev, left_before, right_before]).any():
                        if (left_before <= right_before) and (left_prev > right_prev): is_true = True
                elif op == 'crosses_below':
                    left_prev, right_prev = prev_row.get(left_key), prev_row.get(right_str)
                    left_before, right_before = day_before_prev_row.get(left_key), day_before_prev_row.get(right_str)
                    if not pd.isna([left_prev, right_prev, left_before, right_before]).any():
                        if (left_before >= right_before) and (left_prev < right_prev): is_true = True
                else: 
                    row_to_use = prev_row # 진입/청산 평가는 항상 어제 종가 기준
                    left_val = row_to_use.get(left_key)
                    # `right`는 다른 지표(str)이거나 상수(float/int)일 수 있음
                    right_val = row_to_use.get(right_str, pd.NA) 
                    if pd.isna(right_val):
                        try: right_val = float(right_str)
                        except (ValueError, TypeError): right_val = pd.NA

                    if not pd.isna(left_val) and not pd.isna(right_val):
                        try:
                            op_map = {'<': left_val < right_val, '>': left_val > right_val, '<=': left_val <= right_val, '>=': left_val >= right_val, '==': left_val == right_val, '!=': left_val != right_val}
                            is_true = op_map.get(op, False)
                        except TypeError: is_true = False
                results.append(is_true)
        if not results: return False
        return all(results) if logic == 'AND' else any(results)

# ==============================================================================
# 4. 최적화 엔진 (Optimizer)
# ==============================================================================
class Optimizer:
    def __init__(self, data_with_indicators: pd.DataFrame, strategy: Dict, initial_capital: float, ticker: str):
        self.data = data_with_indicators
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.ticker = ticker

    def run_optimization(self):
        logging.info(f"Running single backtest for {self.ticker} (v2.4 strategy).")
        backtester = Backtester(self.data, self.strategy, self.initial_capital, self.ticker)
        performance = backtester.run_backtest()
        # [참고] v2.4 버전에서는 단일 실행만 가정, 복잡한 최적화 로직은 없음
        performance['Trades'] = len(performance['trades'])
        return [performance]

# ==============================================================================
# 5. 성과 분석기 (PerformanceAnalyzer)
# ==============================================================================
class PerformanceAnalyzer:
    @staticmethod
    def calculate_all_metrics(result: Dict, equity_curve: pd.Series = None) -> Dict:
        if equity_curve is None: equity_curve = result.get('equity_curve')
        metrics = {}
        if equity_curve is not None and not equity_curve.empty and len(equity_curve) > 1:
            start_val, end_val = equity_curve.iloc[0], equity_curve.iloc[-1]
            days = (equity_curve.index[-1] - equity_curve.index[0]).days
            metrics['CAGR'] = ((end_val/start_val)**(365.0/days)-1)*100 if days>0 and start_val>0 else 0
            peak = equity_curve.cummax()
            dd = (equity_curve / peak - 1)
            metrics['MDD'] = dd.min() * 100
            rets = equity_curve.pct_change().dropna()
            metrics['Sharpe'] = (rets.mean()/rets.std()*np.sqrt(252)) if not rets.empty and rets.std()!=0 else 0
            metrics['Final P/L %'] = (end_val/start_val - 1)*100 if start_val > 0 else 0
        else:
            metrics.update({'CAGR': 0, 'MDD': 0, 'Sharpe': 0, 'Final P/L %': 0})

        trades = result.get('trades', [])
        metrics['Num Trades'] = len(trades)
        if trades:
            wins = [t for t in trades if t.get('profit_pct', 0) > 0]
            metrics['WinRate'] = (len(wins)/len(trades))*100 if trades else 0.0
            gross_profit = sum(t.get('profit_pct', 0) for t in wins)
            gross_loss = abs(sum(t.get('profit_pct', 0) for t in trades if t.get('profit_pct', 0) <= 0))
            metrics['ProfitFactor'] = gross_profit/gross_loss if gross_loss > 0 else float('inf')
        else:
            metrics['WinRate'], metrics['ProfitFactor'] = 0.0, "N/A"
        return metrics

# ==============================================================================
# 6. 리포트 생성기 (ReportGenerator)
# ==============================================================================
class ReportGenerator:
    def __init__(self, reports_path='reports'):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.reports_path = os.path.join(self.script_dir, reports_path)
        os.makedirs(self.reports_path, exist_ok=True)
        
    def _convert_fig_to_base64(self, fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def generate_html_report(self, ticker: str, all_results: List[Dict], best_result: Dict, metrics: Dict, benchmark: pd.DataFrame, strategy: Dict):
        equity_curve = best_result['equity_curve']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(equity_curve.index, equity_curve.values, label='Strategy Equity', color='blue')
        if not benchmark.empty:
            bench_curve = benchmark['Close']/benchmark['Close'].iloc[0]*equity_curve.iloc[0]
            ax.plot(bench_curve.index, bench_curve.values, label='Benchmark (KOSPI)', color='grey', linestyle='--')
        ax.set_title(f'Performance Report: {ticker}')
        ax.legend()
        img_base64 = self._convert_fig_to_base64(fig)
        
        metrics_map = {'CAGR': 'CAGR (%, 연)', 'MDD': 'MDD (%)', 'Sharpe': 'Sharpe Ratio', 'WinRate': '승률 (%)', 'ProfitFactor': '손익비', 'Num Trades': '총 거래 횟수'}
        metrics_table_html = "<table><tr><th>지표</th><th>값</th></tr>"
        for key, name in metrics_map.items():
            value = metrics.get(key)
            if isinstance(value, float):
                metrics_table_html += f"<tr><td>{name}</td><td>{value:.2f}</td></tr>"
            else:
                metrics_table_html += f"<tr><td>{name}</td><td>{value}</td></tr>"
        metrics_table_html += "</table>"

        html = f"""
        <html><head><meta charset='utf-8'><title>Report {ticker}</title>
        <style>body{{font-family:sans-serif;}} table{{border-collapse:collapse;}} th,td{{padding:8px;border:1px solid #ddd;}}</style>
        </head><body>
        <h1>성과 리포트: {ticker}</h1>
        <h2>전략: {strategy.get('strategy_name')}</h2>
        <h2>핵심 지표</h2>{metrics_table_html}
        <h2>자산 곡선 (Equity Curve)</h2><img src="data:image/png;base64,{img_base64}" />
        </body></html>
        """
        out_path = os.path.join(self.reports_path, f"{ticker}_report.html")
        with open(out_path,'w',encoding='utf-8') as f: f.write(html)
        logging.info(f"Report generated: {out_path}")

    def generate_trade_log_csv(self, ticker: str, raw_trade_log: List[Dict]):
        if not raw_trade_log: return
        out_path = os.path.join(self.reports_path, f"{ticker}_tradelog.csv")
        try:
            with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=raw_trade_log[0].keys())
                writer.writeheader()
                writer.writerows(raw_trade_log)
            logging.info(f"Trade log saved: {out_path}")
        except Exception as e:
            logging.error(f"Failed to save trade log for {ticker}: {e}")
        
    def generate_portfolio_summary_report(self, portfolio_metrics: Dict, portfolio_equity: pd.Series, individual_results: List[Dict], benchmark: pd.DataFrame, annual_df: pd.DataFrame):
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(portfolio_equity.index, portfolio_equity.values, label='Portfolio Equity')
        bench_equity = benchmark['Close'] / benchmark['Close'].iloc[0] * portfolio_equity.iloc[0]
        ax1.plot(bench_equity.index, bench_equity.values, label='Benchmark (KOSPI)', linestyle='--')
        ax1.set_title('포트폴리오 누적 수익률 곡선 (Portfolio vs KOSPI)')
        ax1.legend()
        img1_b64 = self._convert_fig_to_base64(fig1)

        metrics_map = {'CAGR': 'CAGR (%, 연)', 'MDD': 'MDD (%)', 'Sharpe': 'Sharpe Ratio', 'WinRate': '승률 (%)', 'ProfitFactor': '손익비 (전체 거래 기준)', 'Final P/L %': '누적 수익률 (%)', 'Num Trades': '총 거래 횟수'}
        metrics_html = "<table><tr><th>지표</th><th>값</th></tr>"
        for key, name in metrics_map.items():
            value = portfolio_metrics.get(key)
            if isinstance(value, float):
                 metrics_html += f"<tr><td>{name}</td><td>{value:.2f}</td></tr>"
            else:
                metrics_html += f"<tr><td>{name}</td><td>{value}</td></tr>"
        metrics_html += "</table>"
        desc_html = "<p style='font-size: smaller; color: grey;'><i>포트폴리오 성과는 개별 종목 자산 곡선의 일일 수익률 평균 기준입니다.</i></p>"

        def style_excess_return(val):
            color = '#0000FF' if val > 0 else '#FF0000' if val < 0 else 'black'
            return f'color: {color}'
        
        annual_html = ""
        if not annual_df.empty:
            annual_styled = annual_df.style.format('{:+.2f}%').map(style_excess_return, subset=[EXCESS_RETURN_COL])
            annual_html = annual_styled.to_html().replace('<table border="1" class="dataframe">','<table>')
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        if not annual_df.empty:
            annual_df.plot(kind='bar', y=['Portfolio', 'Benchmark'], ax=ax2)
            ax2.set_title('연도별 수익률 비교 (Annual Returns)')
            ax2.set_ylabel('Return (%)')
            ax2.tick_params(axis='x', rotation=45)
        img2_b64 = self._convert_fig_to_base64(fig2)
        
        individual_html = "<table><tr><th>종목</th><th>CAGR(%)</th><th>MDD(%)</th><th>Sharpe</th><th>거래 수</th></tr>"
        for res in sorted(individual_results, key=lambda x: x['metrics']['CAGR'], reverse=True):
            individual_html += f"""
            <tr><td>{res['ticker']}</td><td>{res['metrics']['CAGR']:.2f}</td><td>{res['metrics']['MDD']:.2f}</td>
            <td>{res['metrics']['Sharpe']:.2f}</td><td>{res['metrics']['Num Trades']}</td></tr>
            """
        individual_html += "</table>"
        
        html = f"""
        <html><head><meta charset='utf-8'><title>Portfolio Summary</title>
        <style>body{{font-family:sans-serif;}} table{{border-collapse:collapse; margin-bottom: 20px;}} th,td{{padding:8px;border:1px solid #ddd; text-align:left;}}</style>
        </head><body>
        <h1>포트폴리오 종합 성과 리포트</h1><h2>Part 1: 종합 성과</h2>{metrics_html}{desc_html}
        <img src="data:image/png;base64,{img1_b64}" width="800"/>
        <h2>Part 2: 연도별 성과</h2>{annual_html}
        <img src="data:image/png;base64,{img2_b64}" width="800"/>
        <h2>Part 3: 개별 종목 요약</h2>{individual_html}</body></html>
        """
        out_path = os.path.join(self.reports_path, "_Portfolio_Summary_Report.html")
        with open(out_path, 'w', encoding='utf-8') as f: f.write(html)
        logging.info(f"Portfolio summary report generated: {out_path}")

    @staticmethod
    def print_terminal_summary(portfolio_metrics: Dict):
        print("\n" + "="*50 + "\n          PORTFOLIO SUMMARY REPORT\n" + "="*50)
        metrics_map = {'CAGR': 'CAGR (%, 연)', 'MDD': 'MDD (%)', 'Sharpe': 'Sharpe Ratio', 'WinRate': '승률 (%)', 'ProfitFactor': '손익비', 'Num Trades': '총 거래 횟수'}
        display_data = {name: (f"{portfolio_metrics.get(key):.2f}" if isinstance(portfolio_metrics.get(key), float) else portfolio_metrics.get(key)) for key, name in metrics_map.items()}
        df = pd.DataFrame.from_dict(display_data, orient='index', columns=['Value'])
        print(df)
        print("="*50)

    @staticmethod
    def generate_ai_commentary(portfolio_metrics: Dict, benchmark_metrics: Dict, annual_df: pd.DataFrame, individual_results: List[Dict]) -> str:
        final_comment = ["[AI 종합 분석 코멘트]"]
        part1_comments, part2_comments, part3_comments = ["- [종합 성과]"], ["- [연도별 성과 분석]"], ["- [개별 종목 성과 요약]"]
        cagr_p, cagr_b = portfolio_metrics.get('CAGR', 0), benchmark_metrics.get('CAGR', 0)
        mdd_p, sharpe_p = portfolio_metrics.get('MDD', 0), portfolio_metrics.get('Sharpe', 0)
        part1_comments.append(f"포트폴리오의 CAGR은 {cagr_p:.2f}%로, 벤치마크({cagr_b:.2f}%) 대비 {'우수한' if cagr_p > cagr_b else '부진한'} 성과를 보였습니다.")
        if sharpe_p > 1.0: part1_comments.append(f"샤프 지수가 {sharpe_p:.2f}로 높아, 효율적인 위험 관리가 이루어졌음을 시사합니다.")
        if mdd_p < -20: part1_comments.append(f"최대 낙폭(MDD)은 {mdd_p:.2f}%로, 상당한 리스크가 존재할 수 있음을 인지해야 합니다.")
        final_comment.append("\n".join(part1_comments))
        if not annual_df.empty:
            outperform_years = (annual_df[EXCESS_RETURN_COL] > 0).sum()
            part2_comments.append(f"총 {len(annual_df)}년 중 {outperform_years}년 동안 벤치마크를 상회했습니다.")
        final_comment.append("\n".join(part2_comments))
        if individual_results:
            sorted_by_cagr = sorted(individual_results, key=lambda x: x['metrics'].get('CAGR', -np.inf), reverse=True)
            if sorted_by_cagr:
                part3_comments.append(f"'{sorted_by_cagr[0]['ticker']}' 종목이 CAGR {sorted_by_cagr[0]['metrics']['CAGR']:.2f}%로 최고의 성과를 보였습니다.")
        final_comment.append("\n".join(part3_comments))
        disclaimer = "\n\n[법적 고지 사항]\n본 분석은 과거 데이터를 기반으로 한 시뮬레이션 결과이며, 미래의 수익을 보장하지 않습니다."
        return "\n\n".join(final_comment) + disclaimer
    
# ==============================================================================
# 7. 테스트 이력 관리 (History Manager)
# ==============================================================================
class HistoryManager:
    def __init__(self, history_file='test_history.csv'):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(self.script_dir, history_file)
        self.headers = ['Timestamp', 'Strategy File', 'Strategy Hash', 'Tickers', 'Portfolio CAGR', 'Portfolio MDD', 'Portfolio Sharpe']
    def _get_strategy_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f: hasher.update(f.read())
        return hasher.hexdigest()
    def update_history(self, strategy_file_path: str, tickers: List[str], portfolio_metrics: Dict):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.headers)
        new_row = {'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Strategy File': os.path.basename(strategy_file_path), 'Strategy Hash': self._get_strategy_hash(strategy_file_path), 'Tickers': ', '.join(tickers), 'Portfolio CAGR': f"{portfolio_metrics.get('CAGR', 0):.2f}", 'Portfolio MDD': f"{portfolio_metrics.get('MDD', 0):.2f}", 'Portfolio Sharpe': f"{portfolio_metrics.get('Sharpe', 0):.2f}"}
        with open(self.history_file, 'a', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, fieldnames=self.headers).writerow(new_row)
        logging.info(f"Test history updated in {self.history_file}")

# ==============================================================================
# 메인 실행 블록
# ==============================================================================
if __name__ == "__main__":
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. 전략 파일 로드
        strategy_filename = input(">>> 실행할 전략 파일명을 입력하세요 (예: Advanced_Pullback_Strategy_v1.json): ")
        strategy_file_path = os.path.join(base_dir, 'strategies', strategy_filename)
        if not os.path.exists(strategy_file_path):
            logging.error(f"전략 파일을 찾을 수 없습니다: {strategy_file_path}"); exit()
        try:
            with open(strategy_file_path, 'r', encoding='utf-8') as f: strategy_config = json.load(f)
            logging.info(f"전략 파일 로드 성공: {strategy_filename}")
        except json.JSONDecodeError:
            logging.error(f"전략 파일이 올바른 JSON 형식이 아닙니다: {strategy_file_path}"); exit()

        # 2. 설정 파일 로드
        config_path = os.path.join(base_dir,'config.json')
        with open(config_path,'r',encoding='utf-8') as f: app_config = json.load(f)
        
        # 3. 날짜 및 종목 설정
        tickers = app_config.get('tickers',[])
        initial_capital = app_config.get('initial_capital', 1e8)
        end_date_obj = date.today() if app_config.get('end_date')=='today' else date.fromisoformat(app_config['end_date'])
        start_date_obj = end_date_obj - relativedelta(years=5) if relativedelta and app_config.get('start_date')=='5_years_ago' else date.fromisoformat(app_config['start_date'])
        start_date, end_date = start_date_obj.isoformat(), end_date_obj.isoformat()
        
        # 4. 모듈 인스턴스화
        data_loader = DataLoader()
        report_gen = ReportGenerator()
        history_manager = HistoryManager()

        # 5. [v2.5 수정] 유니버스 필터링 기준일 보정 및 실행
        if strategy_config.get('universe_filters'):
            latest_business_day = stock.get_nearest_business_day_in_a_week(end_date.replace("-", ""))
            logging.info(f"Universe filtering base date adjusted to the last business day: {latest_business_day}")
            filtered_tickers = data_loader.get_ticker_metadata(tickers, latest_business_day)
        else:
            filtered_tickers = tickers
        logging.info(f"Filtered Universe: {len(filtered_tickers)} tickers to be tested -> {filtered_tickers}")
        
        # 6. 벤치마크 데이터 로드
        benchmark_data = data_loader.get_benchmark_data('1001', start_date, end_date)

        # 7. 백테스팅 실행
        all_individual_results = []
        for ticker in filtered_tickers:
            logging.info(f"--- 분석 시작: {ticker} ---")
            price_data = data_loader.get_price_data(ticker, start_date, end_date)
            if price_data.empty or len(price_data) < 60:
                logging.warning(f"Not enough data for {ticker}, skipping."); continue
            
            indicator_calc = IndicatorCalculator(price_data)
            data_with_ind = indicator_calc.calculate_all(strategy_config)
            
            optimizer = Optimizer(data_with_ind, strategy_config, initial_capital, ticker)
            results = optimizer.run_optimization()
            
            if not results:
                logging.warning(f"Backtest yielded no results for {ticker}, skipping."); continue
            
            best_result = results[0]
            metrics = PerformanceAnalyzer.calculate_all_metrics(best_result)
            all_individual_results.append({
                'ticker': ticker, 'best_result': best_result,
                'metrics': metrics, 'equity_curve': best_result['equity_curve']
            })
            report_gen.generate_html_report(ticker, results, best_result, metrics, benchmark_data, strategy_config)
            
            if 'raw_trade_log' in best_result and best_result['raw_trade_log']:
                report_gen.generate_trade_log_csv(ticker, best_result['raw_trade_log'])

        # 8. 포트폴리오 분석 및 리포팅
        if all_individual_results:
            all_daily_returns = []
            for res in all_individual_results:
                if res['equity_curve'] is not None and not res['equity_curve'].empty:
                    all_daily_returns.append(res['equity_curve'].pct_change().fillna(0))
            
            if all_daily_returns:
                portfolio_daily_returns = pd.concat(all_daily_returns, axis=1).mean(axis=1)
                portfolio_equity_curve = (1 + portfolio_daily_returns).cumprod() * initial_capital
                
                all_trades = [trade for res in all_individual_results for trade in res['best_result']['trades']]
                portfolio_metrics = PerformanceAnalyzer.calculate_all_metrics({'trades': all_trades}, equity_curve=portfolio_equity_curve)
                benchmark_metrics = PerformanceAnalyzer.calculate_all_metrics({'trades': []}, equity_curve=benchmark_data['Close'])

                bench_equity = benchmark_data['Close'] / benchmark_data['Close'].iloc[0] * portfolio_equity_curve.iloc[0]
                portfolio_annual = portfolio_equity_curve.resample('YE').last().pct_change().dropna() * 100
                benchmark_annual = bench_equity.resample('YE').last().pct_change().dropna() * 100
                annual_df = pd.DataFrame({'Portfolio': portfolio_annual, 'Benchmark': benchmark_annual})
                if not annual_df.empty:
                    annual_df.index = annual_df.index.year
                    annual_df[EXCESS_RETURN_COL] = annual_df['Portfolio'] - annual_df['Benchmark']
                
                report_gen.generate_portfolio_summary_report(portfolio_metrics, portfolio_equity_curve, all_individual_results, benchmark_data, annual_df)
                report_gen.print_terminal_summary(portfolio_metrics)
                ai_comment = report_gen.generate_ai_commentary(portfolio_metrics, benchmark_metrics, annual_df, all_individual_results)
                print(ai_comment)
                history_manager.update_history(strategy_file_path, tickers, portfolio_metrics)
            else:
                logging.warning("All backtests resulted in empty equity curves. Skipping portfolio analysis.")
        else:
            logging.warning("No successful backtests were run. Skipping portfolio analysis.")

    except Exception as e:
        logging.error(f"Fatal error in main execution: {e}", exc_info=True)