#!/usr/bin/env bash
set -euo pipefail

MODE="report"
if [[ ${1:-} == "--strict" ]]; then
  MODE="strict"
  shift || true
fi

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

ALLOWED_ROOT_FILES=(
  "README.md"
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"
  "IFLOW.md"
  "LICENSE"
  "CHANGELOG.md"
  ".mcp.json"
  ".pre-commit-config.yaml"
  ".pre-commit-hooks.yaml"
  ".pylintrc"
  ".pylint.test.rc"
  ".coveragerc"
  ".FILE_OWNERSHIP"
  ".env.example"
  "opencode.json"
  "pyproject.toml"
  "mypy.ini"
  "pytest.ini"
  "conftest.py"
  "package.json"
  "package-lock.json"
  "pm2.config.js"
  "monitoring-stack.yml"
  "core.py"
  "data_access.py"
  "monitoring.py"
  "unified_manager.py"
  "__init__.py"
)

ALLOWED_ROOT_PATTERNS=(
  "requirements*.txt"
  "tsconfig*.json"
  "ecosystem*.config.js"
  "docker-compose*.yml"
  ".env*"
  "playwright*.config.ts"
  "playwright*.config.js"
  "playwright.config.*.ts"
  "playwright.config.*.js"
  "vitest.config.*"
)

error=0

echo "[tree-lint] Checking root files..."
while IFS= read -r file_path; do
  file_name=$(basename "$file_path")
  allowed=false
  for allowed_name in "${ALLOWED_ROOT_FILES[@]}"; do
    if [[ "$file_name" == "$allowed_name" ]]; then
      allowed=true
      break
    fi
  done

  if [[ "$allowed" == false ]]; then
    for pattern in "${ALLOWED_ROOT_PATTERNS[@]}"; do
      if [[ "$file_name" == $pattern ]]; then
        allowed=true
        break
      fi
    done
  fi

  if [[ "$allowed" == false ]]; then
    printf '  [WARN] Root file %s is not in allowlist\n' "$file_name"
    error=1
  fi
done < <(find "$PROJECT_ROOT" -maxdepth 1 -type f -not -name '.gitignore' -not -name '.gitattributes')

echo "[tree-lint] Checking scripts directory..."
if [[ -d "$PROJECT_ROOT/scripts/development" ]]; then
  echo "  [ERROR] scripts/development/ should not exist; consolidate into scripts/dev/."
  error=1
else
  echo "  [OK] scripts/development/ is absent."
fi

if [[ $error -ne 0 ]]; then
  echo "[tree-lint] Violations detected."
  if [[ "$MODE" == "strict" ]]; then
    exit 1
  fi
else
  echo "[tree-lint] No violations detected."
fi
