#!/bin/bash
# MyStocks Verification Quick Aliases
# Source this file in your ~/.bashrc or ~/.zshrc:
# source /opt/claude/mystocks_spec/scripts/bash_aliases.sh

# Environment Configuration
export MYSTOCKS_URL="${MYSTOCKS_URL:-http://localhost:8000}"
export MYSTOCKS_USER="${MYSTOCKS_USER:-admin}"
export MYSTOCKS_PASS="${MYSTOCKS_PASS:-admin123}"

# PostgreSQL Configuration
export MYSTOCKS_DB_HOST="${MYSTOCKS_DB_HOST:-localhost}"
export MYSTOCKS_DB_USER="${MYSTOCKS_DB_USER:-mystocks_user}"
export MYSTOCKS_DB_NAME="${MYSTOCKS_DB_NAME:-mystocks}"
export MYSTOCKS_DB_PASS="${MYSTOCKS_DB_PASS:-mystocks2025}"

# TDengine Configuration (if needed)
export TDENGINE_HOST="${TDENGINE_HOST:-192.168.123.104}"
export TDENGINE_USER="${TDENGINE_USER:-root}"
export TDENGINE_PASS="${TDENGINE_PASS:-taosdata}"

# Quick token retrieval
alias mt-token='http POST $MYSTOCKS_URL/api/auth/login username=$MYSTOCKS_USER password=$MYSTOCKS_PASS | jq -r ".access_token"'

# Quick API verification
function mt-api() {
  local endpoint=$1
  local token=$(mt-token)
  http GET "$MYSTOCKS_URL$endpoint" Authorization:"Bearer $token"
}

# Quick PostgreSQL access
alias mt-db='PGPASSWORD=$MYSTOCKS_DB_PASS pgcli -h $MYSTOCKS_DB_HOST -U $MYSTOCKS_DB_USER -d $MYSTOCKS_DB_NAME'

# Quick TDengine access
alias mt-td='taos -h $TDENGINE_HOST -u $TDENGINE_USER -p$TDENGINE_PASS'

# Helper: Test if backend is running
function mt-health() {
  echo "Testing backend health..."
  http GET "$MYSTOCKS_URL/health" 2>/dev/null || echo "❌ Backend not responding"
}

# Helper: Quick API test with data validation
function mt-test-api() {
  local endpoint=$1
  echo "Testing: $endpoint"
  mt-api "$endpoint" | jq -e '.data != null' && echo "✅ PASS" || echo "❌ FAIL"
}

# Helper: Show all verification tools status
function mt-verify-tools() {
  echo "=== MyStocks Verification Tools Status ==="
  echo ""
  echo "Backend URL: $MYSTOCKS_URL"

  echo -n "✓ Playwright: "
  if python -c "import playwright" 2>/dev/null; then
    echo "Installed"
  else
    echo "❌ Not installed"
  fi

  echo -n "✓ httpie: "
  if command -v http &> /dev/null; then
    echo "Installed ($(http --version))"
  else
    echo "❌ Not installed"
  fi

  echo -n "✓ jq: "
  if command -v jq &> /dev/null; then
    echo "Installed ($(jq --version))"
  else
    echo "❌ Not installed"
  fi

  echo -n "✓ pgcli: "
  if command -v pgcli &> /dev/null; then
    echo "Installed ($(pgcli --version))"
  else
    echo "❌ Not installed"
  fi

  echo ""
  echo "Backend health:"
  mt-health
}

echo "✅ MyStocks verification aliases loaded."
echo "Run 'mt-verify-tools' to check tool installation status."
