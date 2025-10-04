# 🚀 Release v1.0.1 — Ontology v1.0.1b Verified Alignment
_Release Date: 2025-10-05 03:19:22 KST_

---

## 🔍 Summary
본 릴리즈는 SignalEvent 엔티티의 9개 속성 정합성을 전수 검증한 결과,
F-109 요건을 충족하며 CF-코드 의존성 무결성을 확보하였습니다.

---

## 📦 New Features
- No feature commits found

---

## 🧩 Ontology Changes (Aligned with v1.0.1b)
### Verified SignalEvent Properties
| 속성명 | 타입 | 상태 |
|--------|------|------|
| signal_id | string | 유지 |
| confidence_score | float(0~1) | 유지 |
| volatility_adjusted | bool | 유지 |
| signal_latency_ms | int(0~10000) | 유지 |
| source_reliability | float(0~1) | 유지 |
| data_integrity_score | float(0~1) | 유지 |
| redundancy_ratio | float(0~1) | 유지 |
| override_flag | bool | 유지 |
| updated_at | datetime | 유지 |

---

## 🧠 Technical Notes
- Registry Path: src/endeavour/setups/registry.yaml
- Version Tag: v1.0.1
- Generated: 2025-10-05 03:19:22 KST
- Script: generate_release.sh v1.0.1b

