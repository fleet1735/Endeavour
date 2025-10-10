#!/usr/bin/env python3
import sys, json, argparse, hashlib
from datetime import datetime, timezone

def jloadl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            yield json.loads(line)

def iso2dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def cf_101_concurrency(events):
    # event_id uniqueness
    seen = set(); dups=[]
    for e in events:
        eid = e.get("event_id")
        if eid in seen: dups.append(eid)
        else: seen.add(eid)
    ok = (len(dups)==0)
    return ok, {"dup_event_ids": dups, "count": len(dups)}

def cf_102_latency(events, max_lag_sec):
    viol=[]
    for e in events:
        te = e.get("ts_event"); ts = e.get("ts_signal") or te
        if not te: continue
        dte = iso2dt(te); dts = iso2dt(ts)
        lag = (dts - dte).total_seconds()
        if lag > max_lag_sec:
            viol.append({"event_id": e.get("event_id"), "lag_sec": lag})
    ok = (len(viol)==0)
    return ok, {"violations": viol, "count": len(viol)}

def cf_103_time_order(events):
    # ensure non-decreasing ts_event
    prev=None; viol=[]
    for e in events:
        te = e.get("ts_event"); 
        if not te: continue
        dte = iso2dt(te)
        if prev and dte < prev:
            viol.append({"event_id": e.get("event_id")})
        prev = dte
    ok = (len(viol)==0)
    return ok, {"disorder": viol, "count": len(viol)}

def cf_104_idempotency(events):
    # content hash signature idempotency
    seen=set(); dups=[]
    for e in events:
        key = sha(json.dumps({"setup_ref":e.get("setup_ref"),
                              "instrument_ref":e.get("instrument_ref"),
                              "ts_event":e.get("ts_event"),
                              "payload":e.get("payload")}, sort_keys=True))
        if key in seen: dups.append(e.get("event_id"))
        else: seen.add(key)
    ok = (len(dups)==0)
    return ok, {"dup_content_events": dups, "count": len(dups)}

def cf_105_referential(events):
    viol=[]
    for e in events:
        for k in ("setup_ref","instrument_ref","ts_event","payload"):
            if not e.get(k): viol.append({"event_id": e.get("event_id"), "missing": k})
    ok = (len(viol)==0)
    return ok, {"missing_refs": viol, "count": len(viol)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events_jsonl", help="SignalEvent stream (.jsonl)")
    ap.add_argument("--max-lag-sec", type=int, default=3600) # 1h default
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--report", default="validator_report.json")
    args = ap.parse_args()

    events = list(jloadl(args.events_jsonl))

    results = {}
    oks = []

    ok, detail = cf_101_concurrency(events); results["CF-101"] = detail; oks.append(ok)
    ok, detail = cf_102_latency(events, args.max_lag_sec); results["CF-102"] = detail; oks.append(ok)
    ok, detail = cf_103_time_order(events); results["CF-103"] = detail; oks.append(ok)
    ok, detail = cf_104_idempotency(events); results["CF-104"] = detail; oks.append(ok)
    ok, detail = cf_105_referential(events); results["CF-105"] = detail; oks.append(ok)

    summary = {
        "ontology_version": "1.0.1",
        "checked": ["CF-101","CF-102","CF-103","CF-104","CF-105"],
        "strict": args.strict,
        "ts": datetime.now(timezone.utc).isoformat()+"Z",
        "counts": {k:v.get("count",0) for k,v in results.items()},
        "pass": all(oks)
    }
    out = {"summary": summary, "details": results}
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    if not summary["pass"]:
        sys.exit(2 if args.strict else 0)

if __name__ == "__main__":
    main()