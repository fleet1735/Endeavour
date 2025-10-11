#!/usr/bin/env bash
set -euo pipefail

ALL=0
if [[ "\" == "--all" ]]; then ALL=1; fi

if [[ \ -eq 1 ]]; then
  mapfile -t FILES < <(git ls-files)
else
  mapfile -t FILES < <(git diff --cached --name-only --diff-filter=ACMRT)
fi

ALLOWED_DIR='src/endeavour/strategies/'
ALLOWED_FILES=('__init__.py' 'schema.py' 'registry.py' 'README.md')

viol=()
for f in "\"; do
  [[ -f "\" ]] || continue
  case "\" in
    *.py|*.md|*.txt|*.json|*.ps1|*.sh|*.yml|*.yaml|*.toml) ;;
    *) continue ;;
  esac
  if [[ "\" == \* ]]; then
    leaf="\"
    case "\" in __init__.py|schema.py|registry.py|README.md) continue ;; esac
  fi
  if grep -E -q '(from[[:space:]]+endeavour\.strategies|import[[:space:]]+endeavour\.strategies|endeavour\.strategies\.)' "\"; then
    viol+=("\")
  fi
done

if (( \ > 0 )); then
  echo "Found forbidden usage in:"
  for f in "\"; do echo " - \"; done
  exit 2
else
  echo "OK: no forbidden usage detected."
fi
