# -*- coding: utf-8 -*-
\"""셋업(JSON) 스키마 v1 스켈레톤.
필드:
- metadata: { name:str, version:str, notes:str? }
- indicators: [ { id:str, type:str, params:dict } ]
- entry_rules: [ { left:str, op:str, right:str } ]
- exit_rules: [ { left:str, op:str, right:str } ]
간단 유효성 검사 함수 validate_setup(json_dict) 제공.
\"""

from typing import Any, Dict, List

REQUIRED_TOP = ["metadata", "indicators", "entry_rules", "exit_rules"]

def validate_setup(d: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP if k not in d]
    if missing:
        raise ValueError(f"Missing top-level keys: {missing}")

    if not isinstance(d["indicators"], list):
        raise TypeError("indicators must be a list")
    if not isinstance(d["entry_rules"], list):
        raise TypeError("entry_rules must be a list")
    if not isinstance(d["exit_rules"], list):
        raise TypeError("exit_rules must be a list")

    # very light structural checks
    md = d["metadata"]
    if not isinstance(md, dict) or "name" not in md:
        raise ValueError("metadata.name is required")

def load_setup_from_json_path(path: str) -> Dict[str, Any]:
    import json, io
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate_setup(data)
    return data
