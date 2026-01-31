#!/bin/bash

# MyStocks 前端页面验证脚本
# 用于系统化验证所有页面的功能和性能

echo "=========================================="
echo "  MyStocks 前端页面验证"
echo "=========================================="
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "验证地址: http://localhost:3020"
echo ""

# 页面列表
pages=(
  "/"
  "/dashboard"
  "/market"
  "/stocks"
  "/analysis"
  "/risk"
  "/trading"
  "/strategy"
  "/artdeco/dashboard"
  "/artdeco/risk"
  "/artdeco/trading"
  "/artdeco/backtest"
  "/artdeco/monitor"
  "/artdeco/strategy"
  "/artdeco/settings"
  "/artdeco/community"
)

# 统计变量
total_pages=${#pages[@]}
passed_pages=0
failed_pages=0
issues_found=()

# 颜色定义
RED='\033[0;31m'  # 失败
GREEN='\033[0;32m'  # 通过
YELLOW='\033[0;33m'  # 警告

# 创建验证报告目录
REPORT_DIR="/tmp/mystocks-page-verification-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

# 函数：验证页面
verify_page() {
  local page=$1
  local url="http://localhost:3020$page"
  local page_name=$2
  local status="unknown"
  local http_code=""
  local console_errors=()
  local load_time=""
  local issue_description=""
  
  echo ""
  echo "----------------------------------------"
  echo "验证页面: $page_name"
  echo "URL: $url"
  echo "----------------------------------------"
  
  # 使用curl检查HTTP状态
  response=$(curl -s -w "\nHTTP Status: %{http_code}\n" --connect-timeout 5 "$url" 2>&1)
  http_code=$(echo "$response" | grep -o "HTTP Status:" | sed 's/.*HTTP Status: \([0-9]*\)/\1/' | head -1)
  
  if [ "$http_code" = "200" ]; then
    echo -e "\033[0;32mHTTP状态: $GREEN HTTP 200 ✓\033[0m"
    status="passed"
  else
    echo -e "\033[0;31mHTTP状态: $RED HTTP $http_code ✗\033[0m"
    status="failed"
    http_code="$http_code"
    
    if [ "$status" = "passed" ]; then
      ((passed_pages++))
    else
      ((failed_pages++))
      
      issue_description="HTTP状态码: $http_code"
      issues_found+=("$page_name: $issue_description")
    fi
  
  echo "HTTP状态: $http_code"
  echo ""
  
  # 检查页面加载时间（使用curl -w测量TTFB）
  start_time=$(date +%s)
  response=$(curl -s -w "\nTime-Total: %{time_total}\n" --connect-timeout 10 "$url" 2>&1)
  time_total=$(echo "$response" | grep -o "Time-Total:" | sed 's/.*Time-Total: \([0-9.]*\)/\1/' | head -1)
  end_time=$(date +%s)
  load_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null)
  
  echo "页面加载时间: ${load_time}s"
  
  if (( $(echo "$load_time < 3.00" | bc -l 2>/dev/null)); then
    echo -e "\033[0;32m加载时间: $GREEN ${load_time}s ✓\033[0m"
    if [ "$status" = "passed" ]; then
      ((passed_pages++))
    else
      ((failed_pages++))
      warning="页面加载超时（>3秒）"
      issues_found+=("$page_name: $warning")
    fi
  else
    echo -e "\033[0;31m加载时间测量失败\033[0m"
    status="failed"
  fi
  
  echo ""
}

# 主验证流程
echo "开始验证所有页面..."
echo ""

for page in "${pages[@]}"; do
  verify_page "$page" "$url"
  echo ""
done

# 生成验证报告
echo ""
echo "=========================================="
echo "  验证报告总结"
echo "=========================================="
echo "总页面数: $total_pages"
echo "通过页面: $passed_pages"
echo "失败页面: $failed_pages"
echo "通过率: $(echo "scale=2; $passed_pages * 100 / $total_pages" | bc -l)"
echo ""

if [ $failed_pages -gt 0 ]; then
  echo -e "\033[0;31m⚠️ 发现 $failed_pages 个页面有问题\033[0m"
  echo ""
  echo "发现的问题:"
  for issue in "${issues_found[@]}"; do
    echo "  - $issue"
  done
else
  echo -e "\033[0;32m✅ 所有页面验证通过！\033[0m"
fi

echo ""
echo "验证报告保存在: $REPORT_DIR"
echo "详细报告文件: $REPORT_DIR/page-verification-report.txt"
echo ""

# 保存完整报告到文件
{
  "verification_time": "$(date '+%Y-%m-%d %H:%M:%S')",
  "base_url": "http://localhost:3020",
  "total_pages": "$total_pages",
  "passed_pages": "$passed_pages",
  "failed_pages": "$failed_pages",
  "pass_rate": "$(echo "scale=2; $passed_pages * 100 / $total_pages" | bc -l)",
  "issues_found": "${issues_found[@]}"
} | tee "$REPORT_DIR/verification-summary.json"
echo "" | tee "$REPORT_DIR/page-verification-report.txt"
echo "报告已生成完毕"