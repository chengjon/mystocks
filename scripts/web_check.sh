#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/web/frontend"

declare -a STEP_NAMES=()
declare -a STEP_RESULTS=()

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

run_step() {
  local name="$1"
  local cmd="$2"

  STEP_NAMES+=("$name")

  echo -e "${BLUE}==> $name${NC}"
  echo -e "${YELLOW}CMD:${NC} $cmd"

  if eval "$cmd"; then
    STEP_RESULTS+=("PASS")
    echo -e "${GREEN}[PASS]${NC} $name"
  else
    local exit_code=$?
    STEP_RESULTS+=("FAIL($exit_code)")
    echo -e "${RED}[FAIL]${NC} $name (exit $exit_code)"
  fi

  echo
}

print_summary() {
  local has_fail=0
  echo "==================== SUMMARY ===================="
  for i in "${!STEP_NAMES[@]}"; do
    local name="${STEP_NAMES[$i]}"
    local result="${STEP_RESULTS[$i]}"
    if [[ "$result" == PASS ]]; then
      echo -e "${GREEN}- $name: $result${NC}"
    else
      echo -e "${RED}- $name: $result${NC}"
      has_fail=1
    fi
  done
  echo "================================================="

  if [[ $has_fail -eq 1 ]]; then
    echo -e "${RED}Web check completed with failures.${NC}"
    return 1
  fi

  echo -e "${GREEN}Web check completed successfully.${NC}"
  return 0
}

main() {
  echo "Project root: $ROOT_DIR"
  echo

  if [[ ! -d "$FRONTEND_DIR" ]]; then
    echo -e "${RED}Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 2
  fi

  run_step "Frontend lint" "cd '$FRONTEND_DIR' && npm run lint"

  if grep -q '"type-check"' "$FRONTEND_DIR/package.json"; then
    run_step "Frontend type-check" "cd '$FRONTEND_DIR' && npm run type-check"
  else
    STEP_NAMES+=("Frontend type-check")
    STEP_RESULTS+=("SKIP(no-script)")
    echo -e "${YELLOW}[SKIP]${NC} Frontend type-check (script not found)"
    echo
  fi

  run_step "E2E tests" "cd '$ROOT_DIR' && npm run test:e2e"

  if [[ -d "$ROOT_DIR/tests/integration" ]]; then
    run_step "Integration tests" "cd '$ROOT_DIR' && pytest tests/integration/ -v"
  else
    STEP_NAMES+=("Integration tests")
    STEP_RESULTS+=("SKIP(no-dir)")
    echo -e "${YELLOW}[SKIP]${NC} Integration tests (directory not found)"
    echo
  fi

  if [[ -d "$ROOT_DIR/tests/contract" ]]; then
    run_step "Contract tests" "cd '$ROOT_DIR' && pytest tests/contract/ -v"
  else
    STEP_NAMES+=("Contract tests")
    STEP_RESULTS+=("SKIP(no-dir)")
    echo -e "${YELLOW}[SKIP]${NC} Contract tests (directory not found)"
    echo
  fi

  if print_summary; then
    exit 0
  else
    exit 1
  fi
}

main "$@"
