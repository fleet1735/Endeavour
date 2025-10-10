#!/usr/bin/env python3
import sys, json, argparse, csv, uuid, hashlib
from datetime import datetime, timezone

def jloadl(path):
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            yield json.loads(line)

def read_prices_csv(path):
    # DataSnapshot: date, open, high, low, close
    data=[]
    with open(path,"r",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            data.append({"date": r["date"], "open": float(r["open"]), "close": float(r["close"])})
    return data

def run_id(): return datetime.utcnow().strftime("run_%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]

def sma(arr, n):
    out=[]
    s=0.0
    for i,x in enumerate(arr):
        s += x
        if i>=n: s -= arr[i-n]
        out.append(s/n if i>=n-1 else None)
    return out

def engine(signal_events_path, data_csv_path, out_dir, setup_ref="MA_Crossover", fast=5, slow=20, engine_version="skel-1.0"):
    rid = run_id()
    prices = read_prices_csv(data_csv_path)
    closes = [p["close"] for p in prices]
    fast_sma = sma(closes, fast)
    slow_sma = sma(closes, slow)

    # consume SignalEvents (e.g., "CROSS_UP"/"CROSS_DOWN" prepared by DSL)
    events = list(jloadl(signal_events_path))

    trades=[]
    pos=None
    for idx, p in enumerate(prices[:-1]): # T+1 execution at next day open
        t = prices[idx+1]
        ts_exec = t["date"] + "T00:00:00Z"
        # derive intent from SignalEvent at current index if any
        # naive alignment by date; in practice, map event.ts_event to price index
        todays = [e for e in events if e.get("payload",{}).get("date")==p["date"]]
        side=None
        for ev in todays:
            if ev.get("payload",{}).get("signal")=="CROSS_UP": side="BUY"
            elif ev.get("payload",{}).get("signal")=="CROSS_DOWN": side="SELL"

        # fallback: crossover from SMA (only if no explicit SignalEvent provided)
        if side is None and fast_sma[idx] is not None and slow_sma[idx] is not None:
            if fast_sma[idx] > slow_sma[idx]: side="BUY"
            elif fast_sma[idx] < slow_sma[idx]: side="SELL"

        if side is None: continue
        if side=="BUY" and pos is None:
            pos={"qty":1.0,"entry":t["open"],"ts":ts_exec}
            trades.append({"ontology_version":"1.0.1","entity":"Trade","trade_id":uuid.uuid4().hex,
                           "run_id":rid,"side":"BUY","qty":1.0,"price":t["open"],"ts_exec":ts_exec,
                           "signal_event_ref": (todays[0].get("event_id") if todays else None)})
        elif side=="SELL" and pos is not None:
            pnl=(t["open"]-pos["entry"])*pos["qty"]
            trades.append({"ontology_version":"1.0.1","entity":"Trade","trade_id":uuid.uuid4().hex,
                           "run_id":rid,"side":"SELL","qty":pos["qty"],"price":t["open"],"ts_exec":ts_exec,
                           "signal_event_ref": (todays[0].get("event_id") if todays else None)})
            pos=None

    pnl=sum([ (trades[i+1]["price"]-trades[i]["price"]) for i in range(0,len(trades)-1,2) ]) if len(trades)>=2 else 0.0
    metrics={"ontology_version":"1.0.1","entity":"MetricSummary","run_id":rid,
             "setup_ref":setup_ref,"engine_version":engine_version,
             "totals":{"pnl":pnl,"mdd":0.0,"hit_ratio":0.0,"sharpe":0.0,"turnover":0.0,"exposure":0.0},
             "hashes":{}}

    import os, json
    os.makedirs(out_dir, exist_ok=True)
    trades_path = os.path.join(out_dir,"trades.jsonl")
    metrics_path= os.path.join(out_dir,"metrics.json")
    with open(trades_path,"w",encoding="utf-8") as f:
        for t in trades: f.write(json.dumps(t, ensure_ascii=False)+"\n")
    with open(metrics_path,"w",encoding="utf-8") as f:
        json.dump(metrics,f,ensure_ascii=False,indent=2)
    return rid, trades_path, metrics_path

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("signal_events_jsonl")
    ap.add_argument("data_snapshot_csv")
    ap.add_argument("out_dir")
    ap.add_argument("--setup-ref", default="MA_Crossover")
    args=ap.parse_args()
    rid, tp, mp = engine(args.signal_events_jsonl, args.data_snapshot_csv, args.out_dir, args.setup_ref)
    print(json.dumps({"run_id":rid,"trades":tp,"metrics":mp}, ensure_ascii=False))

if __name__=="__main__":
    main()