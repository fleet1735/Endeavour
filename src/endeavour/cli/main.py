# -*- coding: utf-8 -*-
import argparse
import sys

def cmd_ingest(args):
    from endeavour.data.loader import main as ingest_main
    return ingest_main(args=args)

def cmd_backtest(args):
    from endeavour.engines.parallel_runner import main as pr_main
    return pr_main(args=args)

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="endeavour", description="Endeavour CLI (Phase 2)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp1 = sub.add_parser("ingest", help="Fetch/cache data for universe")
    sp1.add_argument("--universe", required=False, default="docs/universe/target_tickers.csv")
    sp1.add_argument("--source", required=False, default="yfinance", choices=["yfinance","pykrx"])
    sp1.set_defaults(func=cmd_ingest)

    sp2 = sub.add_parser("backtest", help="Run parallel backtests")
    sp2.add_argument("--strategy", required=False, default="docs/setup_examples/sma_cross.json")
    sp2.add_argument("--universe", required=False, default="docs/universe/target_tickers.csv")
    sp2.set_defaults(func=cmd_backtest)

    args = p.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())

