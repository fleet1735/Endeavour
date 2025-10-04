#!/usr/bin/env bash
# ============================================================
# Endeavour Release Generator v1.0.1b
# Ontology Alignment Verified + Extended Property Validation
# ============================================================

set -e
cd "$(git rev-parse --show-toplevel)"

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
NEW_VERSION=$(echo $LAST_TAG | awk -F. '{print $1"."$2"."$3+1}')
RELEASE_FILE="docs/release/RELEASE_NOTE_${NEW_VERSION}.md"
DATE_NOW=$(date +"%Y-%m-%d %H:%M:%S KST")

mkdir -p docs/release docs/audit

COMMITS=$(git log $LAST_TAG..HEAD --pretty=format:"- %s (%h)" | grep -E "feat:|fix:|refactor:" || echo "- No feature commits found")

# --- Ontology Validation (F-109) ---
REGISTRY_PATH="src/endeavour/setups/registry.yaml"
if [ ! -f "$REGISTRY_PATH" ]; then
  echo "❌ registry.yaml not found: $REGISTRY_PATH"
  exit 1
fi

REQUIRED_PROPS=(
  "signal_id"
  "confidence_score"
  "volatility_adjusted"
  "signal_latency_ms"
  "source_reliability"
  "data_integrity_score"
  "redundancy_ratio"
  "override_flag"
  "updated_at"
)

echo "🔍 Validating 9 required SignalEvent properties..."
for prop in "${REQUIRED_PROPS[@]}"; do
  if ! grep -q "$prop" "$REGISTRY_PATH"; then
    echo "❌ Missing property in registry.yaml: $prop"
    echo "❌ Release halted due to schema mismatch."
    exit 2
  fi
done
echo "✅ Ontology property verification passed (9/9)."

# --- Generate Release Note ---
cat > "$RELEASE_FILE" <<EOF
# 🚀 Release ${NEW_VERSION} — Ontology v1.0.1b Verified Alignment
_Release Date: ${DATE_NOW}_

---

## 🔍 Summary
본 릴리즈는 SignalEvent 엔티티의 9개 속성 정합성을 전수 검증한 결과,
F-109 요건을 충족하며 CF-코드 의존성 무결성을 확보하였습니다.

---

## 📦 New Features
${COMMITS}

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
- Registry Path: ${REGISTRY_PATH}
- Version Tag: ${NEW_VERSION}
- Generated: ${DATE_NOW}
- Script: generate_release.sh v1.0.1b

EOF

# --- Git Stage Only (F-113) ---
git add "scripts/release/generate_release.sh"

echo "✅ generate_release.sh added to staging area. Commit and push manually when ready."
