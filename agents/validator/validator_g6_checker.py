from typing import Dict, Any, List
def _require(c, code, msg, bag): 
    if not c: bag.append(f"{code}: {msg}")
def _extract_entity(entities, name):
    for e in entities:
        if isinstance(e, dict) and e.get("name")==name: return e
    return {}
def _props_as_list(entity):
    p = entity.get("props")
    if p is None: return []
    return p if isinstance(p, list) else []
def _find_prop(props, name):
    for p in props:
        if isinstance(p,str) and p==name: return {"name":name,"type":"string"}
        if isinstance(p,dict) and p.get("name")==name: return p
    return None
def _is_dt(p): return p.get("type") in ("datetime","date-time")
def _is_int_bounds(p,lo,hi): 
    return p.get("type") in ("int","integer") and p.get("minimum")==lo and p.get("maximum")==hi
def _is_recent_arr(p):
    if p.get("type")!="array": return False
    it=p.get("items",{})
    if not isinstance(it,dict): return False
    if it.get("type")!="object": return False
    req=set(it.get("required",[]))
    if not {"id","timestamp"}.issubset(req): return False
    ts=(it.get("properties") or {}).get("timestamp",{})
    return ts.get("type") in ("datetime","date-time")
def validate_registry_schema(registry_yaml_path:str)->None:
    try:
        import yaml
    except Exception:
        raise RuntimeError("AF-OMVI-202-MISSING_DEP: PyYAML required (pip install pyyaml)")
    import io
    with io.open(registry_yaml_path,"r",encoding="utf-8") as f:
        try:
            reg = __import__("yaml").safe_load(f)
        except Exception as ex:
            raise ValueError(f"AF-OMVI-202-PARSE: registry.yaml parse failed: {ex}")
    errors=[]
    _require(isinstance(reg,dict),"G6-001","root must be mapping",errors)
    ents=reg.get("entities"); _require(isinstance(ents,list),"G6-002","entities must be list",errors)
    if errors: raise AssertionError(" ; ".join(errors))
    se=_extract_entity(ents,"SignalEvent"); _require(bool(se),"G6-010","SignalEvent required",errors)
    props=_props_as_list(se); _require(len(props)>0,"G6-011","SignalEvent.props missing/empty",errors)
    put=_find_prop(props,"price_update_time"); _require(put is not None,"G6-101","price_update_time required",errors)
    if put: _require(_is_dt(put),"G6-102","price_update_time.type must be datetime",errors)
    st=_find_prop(props,"signal_time"); _require(st is not None,"G6-111","signal_time required",errors)
    if st: _require(_is_dt(st),"G6-112","signal_time.type must be datetime",errors)
    dd=_find_prop(props,"data_delay_ms"); _require(dd is not None,"G6-121","data_delay_ms required",errors)
    if dd: _require(_is_int_bounds(dd,0,5000),"G6-122","data_delay_ms must be int(min=0,max=5000)",errors)
    rs=_find_prop(props,"recent_signals"); _require(rs is not None,"G6-131","recent_signals required",errors)
    if rs: _require(_is_recent_arr(rs),"G6-132","recent_signals must be array of {id, timestamp:datetime}",errors)
    if errors: raise AssertionError(" ; ".join(errors))
if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:
        print("Usage: python validator_g6_checker.py <path_to_registry.yaml>")
        raise SystemExit(2)
    validate_registry_schema(sys.argv[1])
    print("G-6 OK: registry.yaml structural consistency passed.")