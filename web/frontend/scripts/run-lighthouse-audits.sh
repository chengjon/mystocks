#!/bin/bash

# Lighthouse Performance Audit Script
# This script runs Lighthouse audits on key pages of the MyStocks application

set -e

# Configuration
BASE_URL="http://localhost:3020"
REPORT_DIR="./reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create reports directory
mkdir -p "$REPORT_DIR"

# Array of pages to audit
# Format: "route|report_name|description"
declare -a PAGES=(
  "/dashboard|dashboard|Dashboard - Main landing page"
  "/analysis|analysis|Analysis page"
  "/settings|settings|Settings page"
  "/market/list|market-list|Market list page"
  "/market/realtime|market-realtime|Real-time market data"
  "/market-data/fund-flow|fund-flow|Fund flow analysis"
  "/market-data/longhubang|longhubang|Longhubang data"
  "/risk-monitor/overview|risk-overview|Risk monitoring overview"
  "/strategy-hub/management|strategy-management|Strategy management hub"
)

echo "========================================"
echo "Lighthouse Performance Audit Script"
echo "========================================"
echo "Base URL: $BASE_URL"
echo "Report Directory: $REPORT_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check if dev server is running
echo "Checking if dev server is running..."
if ! lsof -i :3020 > /dev/null 2>&1; then
  echo "ERROR: Dev server is not running on port 3020"
  echo "Please start it with: npm run dev"
  exit 1
fi
echo "✓ Dev server is running"
echo ""

# Function to run Lighthouse audit
run_audit() {
  local route=$1
  local report_name=$2
  local description=$3
  local url="${BASE_URL}${route}"

  echo "Auditing: $description"
  echo "URL: $url"

  # Run Lighthouse with only Performance metrics (faster)
  npx lighthouse "$url" \
    --output=html \
    --output=json \
    --output-path="$REPORT_DIR/lighthouse-${report_name}-${TIMESTAMP}" \
    --only-categories=performance,accessibility,best-practices,seo \
    --chrome-flags="--headless" \
    --quiet

  if [ $? -eq 0 ]; then
    echo "✓ Completed: $description"
  else
    echo "✗ Failed: $description"
  fi
  echo ""
}

# Count total pages
TOTAL=${#PAGES[@]}
CURRENT=0

# Run audits for each page
echo "Starting audits for $TOTAL pages..."
echo ""

for page in "${PAGES[@]}"; do
  IFS='|' read -r route report_name description <<< "$page"

  CURRENT=$((CURRENT + 1))
  echo "[$CURRENT/$TOTAL] Processing: $description"

  run_audit "$route" "$report_name" "$description"
done

echo "========================================"
echo "All audits completed!"
echo "========================================"
echo ""
echo "Reports saved to: $REPORT_DIR"
echo "Pattern: lighthouse-*-${TIMESTAMP}.{html,json}"
echo ""

# Create summary report
echo "Generating summary report..."
node scripts/summarize-lighthouse-reports.js "$REPORT_DIR" "$TIMESTAMP"

echo "✓ Summary report generated"
echo ""
echo "To view reports:"
echo "  - Open HTML files in your browser"
echo "  - Check summary for aggregated results"
echo ""
