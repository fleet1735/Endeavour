import json
import pandas as pd
from backtesting import Strategy
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator

# === 지표 매핑 사전 ===
INDICATOR_MAP = {
    "sma_indicator": (SMAIndicator, "sma_indicator"),
    "ema_indicator": (EMAIndicator, "ema_indicator"),
    "macd": (MACD, "macd"),
    "rsi": (RSIIndicator, "rsi"),
}


class JSONStrategy(Strategy):
    """
    JSON 기반으로 동적으로 전략을 생성하는 클래스
    """

    def init(self):
        # JSON 전략 불러오기
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.config = config
        self.indicator_values = {}

        # === 인디케이터 생성 ===
        for ind in config.get("indicators", []):
            name = ind["name"]
            func_name = ind["function"]

            if func_name not in INDICATOR_MAP:
                raise ValueError(f"Indicator function {func_name} not found")

            cls, method = INDICATOR_MAP[func_name]
            params = ind.get("params", {})

            # --- wrapper 정의 (data_close를 pandas.Series로 변환) ---
            def wrapper(data_close, cls=cls, method=method, params=params):
                series = pd.Series(data_close)  # numpy array → pandas Series
                if isinstance(params, dict):
                    obj = cls(close=series, **params)
                else:
                    obj = cls(series, *params)
                return getattr(obj, method)()

            # Backtesting 프레임워크에 등록
            self.indicator_values[name] = self.I(wrapper, self.data.Close)

    def next(self):
        """
        매 시점마다 entry_rules, exit_rules 실행
        """
        cfg = self.config

        # === 진입 규칙 ===
        for rule in cfg.get("entry_rules", []):
            left_val = self.indicator_values[rule["left"]][-1]
            right_val = self.indicator_values[rule["right"]][-1]
            op = rule["operator"]

            if op == ">" and left_val > right_val:
                if not self.position:
                    self.buy()
            elif op == "<" and left_val < right_val:
                if not self.position:
                    self.buy()

        # === 청산 규칙 ===
        for rule in cfg.get("exit_rules", []):
            left_val = self.indicator_values[rule["left"]][-1]
            right_val = self.indicator_values[rule["right"]][-1]
            op = rule["operator"]

            if op == ">" and left_val > right_val:
                if self.position:
                    self.position.close()
            elif op == "<" and left_val < right_val:
                if self.position:
                    self.position.close()
