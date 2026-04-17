#!/bin/bash
# playwright_cli_routes.sh — Declarative route test data for playwright-cli
# Sourced by run_playwright_cli_tests.sh
#
# Format: "route|expected_title_contains|priority"
# Priority: P0 (critical), P1 (high), P2 (nav), P3 (feature), P6 (system), P7 (error)

ROUTES=(
  "login|Login|P0"
  "dashboard|交易室|P1"
  "market/realtime|实时行情|P3"
  "market/technical|K线分析|P3"
  "market/lhb|龙虎榜|P3"
  "data/industry|板块动向|P2"
  "data/concept|概念动向|P2"
  "data/fund-flow|资金流向|P2"
  "data/indicator|指标分析|P2"
  "watchlist/manage|组合管理|P4"
  "watchlist/signals|信号雷达|P4"
  "watchlist/screener|策略选股|P4"
  "strategy/repo|策略仓库|P5"
  "strategy/backtest|回测引擎|P5"
  "trade/terminal|交易操作|P5"
  "risk/overview|风险概览|P6"
  "risk/alerts|告警中心|P6"
  "system/health|健康矩阵|P6"
  "system/config|系统配置|P6"
  "nonexistent-test-page|Page Not Found|P7"
)

# Priority groups for different test modes
PRIORITY_QUICK="P0 P1"
PRIORITY_SMOKE="P0 P1 P2 P3"
PRIORITY_FULL="P0 P1 P2 P3 P4 P5 P6 P7"
