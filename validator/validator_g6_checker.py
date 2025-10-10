# validator/validator_g6_checker.py — AF-OMVI-202 대응 (G-6 사후 정합성 검증)
from typing import Dict, Any, List
def _require(cond: bool, code: str, msg: str, bag: List[str]):
    if not cond: bag.append(f"{code}: {msg}")
def _extract_entity(entities: List[Any], name: str) -> Dict[str, Any]:
    for e in entities:
        if isinstance(e, dict) and e.get('name') == name: return e
    return {}
def _props_as_list(entity: Dict[str, Any]) -> List[Any]:
    props = entity.get('props'); 
    if props is None: return []
    return props if isinstance(props, list) else []
def _find_prop(props: List[Any], prop_name: str):
    for p in props:
        if isinstance(p, str) and p == prop_name: return {"name": prop_name, "type":"string"}
        if isinstance(p, dict) and p.get('name') == prop_name: return p
    return None
def _is_datetime(prop: Dict[str, Any]) -> bool:
    return (prop.get('type') in ('datetime','date-time'))
def _is_int_with_bounds(prop: Dict[str, Any], lo: int, hi: int) -> bool:
    if prop.get('type') not in ('int','integer'): return False
    return (prop.get('minimum') == lo) and (prop.get('maximum') == hi)
def _is_recent_signals_array(prop: Dict[str, Any]) -> bool:
    if prop.get('type') != 'array': return False
    items = prop.get('items', {})
    if not isinstance(items, dict): return False
    if items.get('type') != 'object': return False
    req = set(items.get('required', []))
    if not {'id','timestamp'}.issubset(req): return False
    properties = items.get('properties', {})
    if not isinstance(properties, dict): return False
    ts = properties.get('timestamp', {})
    return ts.get('type') in ('datetime','date-time')
def validate_registry_schema(registry_yaml_path: str) -> None:
    try:
        import yaml
    except Exception:
        raise RuntimeError("AF-OMVI-202-MISSING_DEP: PyYAML is required. Install via `pip install pyyaml`.")
    with open(registry_yaml_path, 'r', encoding='utf-8') as f:
        try:
            reg = yaml.safe_load(f)
        except Exception as ex:
            raise ValueError(f"AF-OMVI-202-PARSE: registry.yaml parse failed: {ex}")
    errors: List[str] = []
    _require(isinstance(reg, dict), "G6-001", "root must be mapping", errors)
    entities = reg.get('entities')
    _require(isinstance(entities, list), "G6-002", "entities must be list", errors)
    if errors: raise AssertionError(" ; ".join(errors))
    se = _extract_entity(entities, 'SignalEvent')
    _require(bool(se), "G6-010", "SignalEvent entity required", errors)
    props = _props_as_list(se)
    _require(len(props) > 0, "G6-011", "SignalEvent.props missing/empty", errors)
    if errors: raise AssertionError(" ; ".join(errors))
    put = _find_prop(props, 'price_update_time')
    _require(put is not None, "G6-101", "price_update_time required", errors)
    if put: _require(_is_datetime(put), "G6-102", "price_update_time.type must be datetime", errors)
    st = _find_prop(props, 'signal_time')
    _require(st is not None, "G6-111", "signal_time required", errors)
    if st: _require(_is_datetime(st), "G6-112", "signal_time.type must be datetime", errors)
    dd = _find_prop(props, 'data_delay_ms')
    _require(dd is not None, "G6-121", "data_delay_ms required", errors)
    if dd: _require(_is_int_with_bounds(dd, 0, 5000), "G6-122", "data_delay_ms must be int with min=0,max=5000", errors)
    rs = _find_prop(props, 'recent_signals')
    _require(rs is not None, "G6-131", "recent_signals required", errors)
    if rs: _require(_is_recent_signals_array(rs), "G6-132", "recent_signals must be array of object {id, timestamp:datetime}", errors)
    if errors: raise AssertionError(" ; ".join(errors))
if __name__ == "__main__":
    import sys
    if len(sys.argv)!=2:
        print("Usage: python validator_g6_checker.py <path_to_registry.yaml>")
        raise SystemExit(2)
    validate_registry_schema(sys.argv[1])
    print("G-6 OK: registry.yaml structural consistency passed.")
