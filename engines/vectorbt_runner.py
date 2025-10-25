# encoding: utf-8
# SSOT v8.2 LOCK: D close signal → D+1 open fill (shift(1)); N≥30 broadcast
import pandas as pd
try:
    import vectorbt as vbt
except Exception as e:
    # Lazy import note: runtime will require vectorbt
    vbt = None

def run_broadcast(prices: pd.DataFrame, fees=0.0015, slippage=0.0005):
    """
    prices: wide DataFrame (columns = symbols, index = dates), freq="D"
    returns portfolio object (vectorbt) or raises if vectorbt missing
    """
    if vbt is None:
        raise ImportError("vectorbt is required at runtime")

    ma50  = vbt.MA.run(prices, window=50).ma
    ma200 = vbt.MA.run(prices, window=200).ma

    entries = ma50.vbt.crossed_above(ma200).shift(1)  # D signal → fill at D+1
    exits   = ma50.vbt.crossed_below(ma200).shift(1)

    pf = vbt.Portfolio.from_signals(
        prices, entries, exits,
        fees=fees, slippage=slippage, freq="D"
    )
    return pf
