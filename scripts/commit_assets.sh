#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "[INFO] Copying ontology assets into repo..."
git add src/endeavour/setups/registry.yaml
git add src/endeavour/utils/validator.py

echo "[INFO] Committing changes..."
git commit -m "feat: Ontology v1.0.1 - Deep Research Integration & Function Hardening"

echo "[INFO] Pushing to remote..."
git push

echo "[DONE] Ontology assets successfully committed."
