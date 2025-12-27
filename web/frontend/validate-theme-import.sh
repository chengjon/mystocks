#!/bin/bash

# Phase 1 Task 1.3 - Theme Import Validation Script
# 验证深色主题系统导入是否成功

echo "=================================================="
echo "MyStocks Frontend - Theme Import Validation"
echo "MyStocks 前端 - 主题导入验证"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
print_result() {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}: $2"
    ((PASSED++))
  else
    echo -e "${RED}✗ FAIL${NC}: $2"
    ((FAILED++))
  fi
}

echo "1. Checking main.js file existence..."
if [ -f "src/main.js" ]; then
  print_result 0 "main.js file exists"
else
  print_result 1 "main.js file not found"
  exit 1
fi

echo ""
echo "2. Checking theme-dark.scss file existence..."
if [ -f "src/styles/theme-dark.scss" ]; then
  print_result 0 "theme-dark.scss file exists"
else
  print_result 1 "theme-dark.scss file not found"
  exit 1
fi

echo ""
echo "3. Verifying Element Plus dark theme CSS import..."
if grep -q "element-plus/theme-chalk/dark/css-vars.css" src/main.js; then
  print_result 0 "Element Plus dark theme import found"
else
  print_result 1 "Element Plus dark theme import not found"
fi

echo ""
echo "4. Verifying custom theme import..."
if grep -q "theme-dark.scss" src/main.js; then
  print_result 0 "Custom theme-dark.scss import found"
else
  print_result 1 "Custom theme-dark.scss import not found"
fi

echo ""
echo "5. Verifying import order..."
IMPORTS=$(grep -n "^import.*css\|^import.*scss" src/main.js | awk '{print $1}')

# Check order: Element Plus default -> Element Plus dark -> Custom theme -> Global styles
EL_PLUS_LINE=$(grep -n "element-plus/dist/index.css" src/main.js | cut -d: -f1)
EL_PLUS_DARK_LINE=$(grep -n "element-plus/theme-chalk/dark/css-vars.css" src/main.js | cut -d: -f1)
CUSTOM_THEME_LINE=$(grep -n "theme-dark.scss" src/main.js | cut -d: -f1)
GLOBAL_STYLES_LINE=$(grep -n "index.scss" src/main.js | cut -d: -f1)

if [ $EL_PLUS_LINE -lt $EL_PLUS_DARK_LINE ] && \
   [ $EL_PLUS_DARK_LINE -lt $CUSTOM_THEME_LINE ] && \
   [ $CUSTOM_THEME_LINE -lt $GLOBAL_STYLES_LINE ]; then
  print_result 0 "Import order is correct"
else
  print_result 1 "Import order is incorrect"
fi

echo ""
echo "6. Verifying theme CSS variables..."
CSS_VARS=$(grep -c "color-up\|color-down\|color-flat\|bg-primary" src/styles/theme-dark.scss)
if [ $CSS_VARS -ge 4 ]; then
  print_result 0 "Theme CSS variables found ($CSS_VARS key variables)"
else
  print_result 1 "Theme CSS variables missing (only found $CSS_VARS)"
fi

echo ""
echo "7. Checking theme documentation..."
if [ -f "src/styles/theme-dark.scss" ]; then
  if grep -q "A-SHARE MARKET COLOR CONVENTION" src/styles/theme-dark.scss || \
     grep -q "A股市场颜色约定" src/styles/theme-dark.scss; then
    print_result 0 "Theme documentation found"
  else
    print_result 1 "Theme documentation missing"
  fi
fi

echo ""
echo "8. Verifying Element Plus integration..."
if grep -q "Element Plus" src/styles/theme-dark.scss; then
  print_result 0 "Element Plus override styles found"
else
  print_result 1 "Element Plus override styles not found"
fi

echo ""
echo "=================================================="
echo "Validation Summary"
echo "验证摘要"
echo "=================================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}All tests passed! Theme import is correctly configured.${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Run 'npm run dev' to start the development server"
  echo "2. Open browser and verify the dark theme is applied"
  echo "3. Check browser console for any CSS-related errors"
  echo ""
  exit 0
else
  echo -e "${RED}Some tests failed. Please review the issues above.${NC}"
  echo ""
  exit 1
fi
