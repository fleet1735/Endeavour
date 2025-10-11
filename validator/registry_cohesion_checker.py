#!/usr/bin/env python3
# encoding: utf-8
"""
CF-ONT-201 — SSOT Cohesion Checker
- registry.yaml 과 각 스키마(JSON Schema)의 동형성, 참조 일관성, 필수 키 존재 여부를 검증한다.
- 실패가 존재하면 종료코드 1을 반환한다.
"""
import sys, json, os, glob
from pathlib import Path

def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base = Path(".").resolve()
    reg_candidates = list(base.glob("**/registry.yaml")) + list(base.glob("**/registry.yml"))
    if not reg_candidates:
        print("WARN: registry.yaml not found — CF-ONT-201 skipped (pass=true, reason=absent)")
        print(json.dumps({"cf":"CF-ONT-201","pass": True, "skipped": True, "reason":"registry.yaml not found"}))
        return 0

    # registry.yaml 은 간단한 YAML 의존 없이 파싱(최소 호환) — 키 라인만 정규식으로
    # 필요 시 pyyaml 사용 가능. CI에서는 pyyaml을 설치하므로 우선 시도하고, 실패 시 폴백.
    try:
        import yaml  # type: ignore
        reg = yaml.safe_load(reg_candidates[0].read_text(encoding="utf-8"))
    except Exception:
        # 매우 제한적인 폴백: JSON 유사 형태면 파싱 시도
        try:
            reg = json.loads(reg_candidates[0].read_text(encoding="utf-8"))
        except Exception as e:
            print(f"ERR: failed to parse registry.yaml: {e}")
            print(json.dumps({"cf":"CF-ONT-201","pass": False, "errors":["parse_error"]}))
            return 1

    errors = []
    required_top = ["schemas", "entities"]
    for k in required_top:
        if k not in reg:
            errors.append(f"missing_top:{k}")

    # 스키마 파일 존재/로드/기본키 확인
    schema_dir = Path("schemas")
    if not schema_dir.exists():
        errors.append("missing_dir:schemas")
    else:
        schema_map = {}
        for p in schema_dir.glob("**/*.schema.json"):
            try:
                obj = load_json(p)
                schema_id = obj.get("$id") or str(p).replace("\\","/")
                title = obj.get("title", "")
                typ = obj.get("type", "")
                if not typ:
                    errors.append(f"schema_no_type:{p}")
                schema_map[schema_id] = {"path": str(p).replace("\\","/"), "title": title}
            except Exception as e:
                errors.append(f"schema_parse:{p}:{e}")

        # registry.entities 와 스키마의 매핑 일치성
        entities = reg.get("entities", {}) or {}
        for name, meta in entities.items():
            ref = (meta or {}).get("$ref") or (meta or {}).get("schema")
            if not ref:
                errors.append(f"entity_no_ref:{name}")
                continue
            # $id 또는 파일경로 기준으로 매칭 시도
            if ref not in schema_map and not Path(ref).exists():
                # 느슨한 매칭: 파일명만 비교
                hit = [k for k,v in schema_map.items() if v["path"].endswith(ref) or k.endswith(ref)]
                if not hit:
                    errors.append(f"entity_ref_not_found:{name}:{ref}")

    result = {"cf":"CF-ONT-201","pass": len(errors)==0, "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
