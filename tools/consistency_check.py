import sys, json
from typing import Any, Dict
try:
    import yaml
except Exception:
    print("ERR: PyYAML required. pip install pyyaml"); sys.exit(2)
def load_yaml(p:str)->Dict[str,Any]:
    import io; 
    with io.open(p,"r",encoding="utf-8") as f: 
        return yaml.safe_load(f)
def load_json(p:str)->Dict[str,Any]:
    import io, json as j
    with io.open(p,"r",encoding="utf-8") as f:
        return j.load(f)
def has_entity(reg:Dict[str,Any], name:str)->bool:
    for e in reg.get("entities",[]):
        if isinstance(e,dict) and e.get("name")==name: return True
    return False
def main(reg_path:str, schema_path:str)->None:
    reg=load_yaml(reg_path); sch=load_json(schema_path)
    need=["Setup","SignalEvent","BacktestRun","Metric"]
    miss=[n for n in need if not has_entity(reg,n)]
    if miss: raise AssertionError(f"G6-PRE-101: registry missing entities: {miss}")
    props=sch.get("properties",{})
    for k in ["name","indicators","entry","exit"]:
        if k not in props: raise AssertionError(f"G6-PRE-201: setup.schema.json missing '{k}'")
    print("G-6 PRECHECK OK: registry.yaml & setup.schema.json minimal consistency passed.")
if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: python consistency_check.py <registry.yaml> <setup.schema.json>")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])