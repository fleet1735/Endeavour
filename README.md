# Endeavour Prototype (Parallel Backtesting)

## Setup
```bash
pip install -r requirements.txt
```

## Run
From project root:
```bash
python 01_src/engines/parallel_runner.py
```

Ensure:
- Universe CSV: `02_docs/universe/target_tickers.csv`
- Approved strategies: `01_src/strategies/approved/*.json`
- Results saved under `03_reports/strategy_runs/{strategy_id}/`
```