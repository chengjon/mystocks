# MyStocks API 目录

**生成时间**: 2025-12-30
**数据来源**: FastAPI OpenAPI (localhost:8000)
**API总数**: 285

## 目录
## 优先级分布
- **P2**: 134 个（辅助功能）
- **P1**: 83 个（重要业务）
- **P0**: 68 个（核心业务）


- [SSE实时推送](#SSE实时推送)
- [announcement](#announcement)
- [api](#api)
- [auth](#auth)
- [cache](#cache)
- [contract-management](#contract-management)
- [dashboard](#dashboard)
- [data](#data)
- [data-quality](#data-quality)
- [gpu-monitoring](#gpu-monitoring)
- [health](#health)
- [indicators](#indicators)
- [industry-concept-analysis](#industry-concept-analysis)
- [machine-learning](#machine-learning)
- [market](#market)
- [market-v2](#market-v2)
- [metrics](#metrics)
- [monitoring](#monitoring)
- [multi-source](#multi-source)
- [notification](#notification)
- [pool-monitoring](#pool-monitoring)
- [stock-search](#stock-search)
- [strategy](#strategy)
- [strategy-mgmt](#strategy-mgmt)
- [system](#system)
- [tasks](#tasks)
- [tdx](#tdx)
- [technical-analysis](#technical-analysis)
- [trade](#trade)
- [tradingview](#tradingview)
- [watchlist](#watchlist)
- [wencai](#wencai)
- [策略管理-Week1](#策略管理-Week1)
- [风险管理-Week1](#风险管理-Week1)

---

## SSE实时推送

### P2 - 辅助功能API

#### GET /api/v1/sse/alerts

**描述**: Sse Alerts Stream

- **API ID**: `SSE实时推送_get_api_v1_sse_alerts`
- **标签**: SSE实时推送
- **参数**: 1 个

#### GET /api/v1/sse/backtest

**描述**: Sse Backtest Stream

- **API ID**: `SSE实时推送_get_api_v1_sse_backtest`
- **标签**: SSE实时推送
- **参数**: 1 个

#### GET /api/v1/sse/dashboard

**描述**: Sse Dashboard Stream

- **API ID**: `SSE实时推送_get_api_v1_sse_dashboard`
- **标签**: SSE实时推送
- **参数**: 1 个

#### GET /api/v1/sse/status

**描述**: Sse Status

- **API ID**: `SSE实时推送_get_api_v1_sse_status`
- **标签**: SSE实时推送

#### GET /api/v1/sse/training

**描述**: Sse Training Stream

- **API ID**: `SSE实时推送_get_api_v1_sse_training`
- **标签**: SSE实时推送
- **参数**: 1 个

---

## announcement

### P2 - 辅助功能API

#### DELETE /api/announcement/monitor-rules/{rule_id}

**描述**: Delete Monitor Rule

- **API ID**: `announcement_delete_api_announcement_monitor_rules_rule_id`
- **标签**: announcement
- **参数**: 1 个

#### GET /api/announcement/health

**描述**: Health Check

- **API ID**: `announcement_get_api_announcement_health`
- **标签**: announcement

#### GET /api/announcement/important

**描述**: Get Important Announcements

- **API ID**: `announcement_get_api_announcement_important`
- **标签**: announcement
- **参数**: 2 个

#### GET /api/announcement/list

**描述**: Get Announcements

- **API ID**: `announcement_get_api_announcement_list`
- **标签**: announcement
- **参数**: 7 个

#### GET /api/announcement/monitor-rules

**描述**: Get Monitor Rules

- **API ID**: `announcement_get_api_announcement_monitor_rules`
- **标签**: announcement

#### GET /api/announcement/stats

**描述**: Get Announcement Stats

- **API ID**: `announcement_get_api_announcement_stats`
- **标签**: announcement

#### GET /api/announcement/status

**描述**: Get Status

- **API ID**: `announcement_get_api_announcement_status`
- **标签**: announcement

#### GET /api/announcement/today

**描述**: Get Today Announcements

- **API ID**: `announcement_get_api_announcement_today`
- **标签**: announcement
- **参数**: 1 个

#### GET /api/announcement/triggered-records

**描述**: Get Triggered Records

- **API ID**: `announcement_get_api_announcement_triggered_records`
- **标签**: announcement
- **参数**: 4 个

#### POST /api/announcement/analyze

**描述**: Analyze Data

- **API ID**: `announcement_post_api_announcement_analyze`
- **标签**: announcement
- **参数**: 1 个

#### POST /api/announcement/fetch

**描述**: Fetch Announcements

- **API ID**: `announcement_post_api_announcement_fetch`
- **标签**: announcement
- **参数**: 4 个

#### POST /api/announcement/monitor-rules

**描述**: Create Monitor Rule

- **API ID**: `announcement_post_api_announcement_monitor_rules`
- **标签**: announcement
- **参数**: 1 个

#### POST /api/announcement/monitor/evaluate

**描述**: Evaluate Monitor Rules

- **API ID**: `announcement_post_api_announcement_monitor_evaluate`
- **标签**: announcement

#### PUT /api/announcement/monitor-rules/{rule_id}

**描述**: Update Monitor Rule

- **API ID**: `announcement_put_api_announcement_monitor_rules_rule_id`
- **标签**: announcement
- **参数**: 2 个

---

## api

### P2 - 辅助功能API

#### GET /

**描述**: Root

- **API ID**: `api_get_root`
- **标签**: 

#### GET /api/csrf-token

**描述**: Get Csrf Token

- **API ID**: `api_get_api_csrf_token`
- **标签**: 

#### GET /api/socketio-status

**描述**: Socketio Status

- **API ID**: `api_get_api_socketio_status`
- **标签**: 

#### GET /health

**描述**: Health Check

- **API ID**: `api_get_health`
- **标签**: 

---

## auth

### P0 - 核心业务API

#### GET /api/v1/auth/csrf/token

**描述**: Get Csrf Token

- **API ID**: `auth_get_api_v1_auth_csrf_token`
- **标签**: auth

#### GET /api/v1/auth/me

**描述**: Read Users Me

- **API ID**: `auth_get_api_v1_auth_me`
- **标签**: auth

#### GET /api/v1/auth/users

**描述**: Get Users

- **API ID**: `auth_get_api_v1_auth_users`
- **标签**: auth

#### POST /api/v1/auth/login

**描述**: Login For Access Token

- **API ID**: `auth_post_api_v1_auth_login`
- **标签**: auth

#### POST /api/v1/auth/logout

**描述**: Logout

- **API ID**: `auth_post_api_v1_auth_logout`
- **标签**: auth

#### POST /api/v1/auth/refresh

**描述**: Refresh Token

- **API ID**: `auth_post_api_v1_auth_refresh`
- **标签**: auth

---

## cache

### P1 - 重要业务API

#### DELETE /api/cache

**描述**: Clear All Cache

- **API ID**: `cache_delete_api_cache`
- **标签**: cache, cache
- **参数**: 1 个

#### DELETE /api/cache/{symbol}

**描述**: Invalidate Symbol Cache

- **API ID**: `cache_delete_api_cache_symbol`
- **标签**: cache, cache
- **参数**: 1 个

#### GET /api/cache/eviction/stats

**描述**: Get Eviction Statistics

- **API ID**: `cache_get_api_cache_eviction_stats`
- **标签**: cache, cache

#### GET /api/cache/monitoring/health

**描述**: Get Cache Health Status

- **API ID**: `cache_get_api_cache_monitoring_health`
- **标签**: cache, cache

#### GET /api/cache/monitoring/metrics

**描述**: Get Cache Monitoring Metrics

- **API ID**: `cache_get_api_cache_monitoring_metrics`
- **标签**: cache, cache

#### GET /api/cache/prewarming/status

**描述**: Get Prewarming Status

- **API ID**: `cache_get_api_cache_prewarming_status`
- **标签**: cache, cache

#### GET /api/cache/status

**描述**: Get Cache Status

- **API ID**: `cache_get_api_cache_status`
- **标签**: cache, cache

#### GET /api/cache/{symbol}/{data_type}

**描述**: Get Cached Data

- **API ID**: `cache_get_api_cache_symbol_data_type`
- **标签**: cache, cache
- **参数**: 3 个

#### GET /api/cache/{symbol}/{data_type}/fresh

**描述**: Check Cache Freshness

- **API ID**: `cache_get_api_cache_symbol_data_type_fresh`
- **标签**: cache, cache
- **参数**: 3 个

#### POST /api/cache/evict/manual

**描述**: Manual Cache Eviction

- **API ID**: `cache_post_api_cache_evict_manual`
- **标签**: cache, cache

#### POST /api/cache/prewarming/trigger

**描述**: Trigger Cache Prewarming

- **API ID**: `cache_post_api_cache_prewarming_trigger`
- **标签**: cache, cache

#### POST /api/cache/{symbol}/{data_type}

**描述**: Write Cache Data

- **API ID**: `cache_post_api_cache_symbol_data_type`
- **标签**: cache, cache
- **参数**: 5 个

---

## contract-management

### P2 - 辅助功能API

#### DELETE /api/contracts/versions/{version_id}

**描述**: Delete Version

- **API ID**: `contract_management_delete_api_contracts_versions_version_id`
- **标签**: contract-management
- **参数**: 1 个

#### GET /api/contracts/contracts

**描述**: List Contracts

- **API ID**: `contract_management_get_api_contracts_contracts`
- **标签**: contract-management

#### GET /api/contracts/versions

**描述**: List Versions

- **API ID**: `contract_management_get_api_contracts_versions`
- **标签**: contract-management
- **参数**: 3 个

#### GET /api/contracts/versions/{name}/active

**描述**: Get Active Version

- **API ID**: `contract_management_get_api_contracts_versions_name_active`
- **标签**: contract-management
- **参数**: 1 个

#### GET /api/contracts/versions/{version_id}

**描述**: Get Version

- **API ID**: `contract_management_get_api_contracts_versions_version_id`
- **标签**: contract-management
- **参数**: 1 个

#### POST /api/contracts/diff

**描述**: Compare Versions

- **API ID**: `contract_management_post_api_contracts_diff`
- **标签**: contract-management
- **参数**: 1 个

#### POST /api/contracts/sync

**描述**: Sync Contract

- **API ID**: `contract_management_post_api_contracts_sync`
- **标签**: contract-management
- **参数**: 1 个

#### POST /api/contracts/validate

**描述**: Validate Contract

- **API ID**: `contract_management_post_api_contracts_validate`
- **标签**: contract-management
- **参数**: 1 个

#### POST /api/contracts/versions

**描述**: Create Version

- **API ID**: `contract_management_post_api_contracts_versions`
- **标签**: contract-management
- **参数**: 1 个

#### POST /api/contracts/versions/{version_id}/activate

**描述**: Activate Version

- **API ID**: `contract_management_post_api_contracts_versions_version_id_activate`
- **标签**: contract-management
- **参数**: 1 个

#### PUT /api/contracts/versions/{version_id}

**描述**: Update Version

- **API ID**: `contract_management_put_api_contracts_versions_version_id`
- **标签**: contract-management
- **参数**: 2 个

---

## dashboard

### P1 - 重要业务API

#### GET /api/dashboard/health

**描述**: 仪表盘健康检查

- **API ID**: `dashboard_get_api_dashboard_health`
- **标签**: dashboard, dashboard, health

#### GET /api/dashboard/market-overview

**描述**: 获取市场概览

- **API ID**: `dashboard_get_api_dashboard_market_overview`
- **标签**: dashboard, dashboard
- **参数**: 1 个

#### GET /api/dashboard/summary

**描述**: 获取仪表盘汇总数据

- **API ID**: `dashboard_get_api_dashboard_summary`
- **标签**: dashboard, dashboard
- **参数**: 7 个

---

## data

### P0 - 核心业务API

#### GET /api/data/financial

**描述**: Get Financial Data

- **API ID**: `data_get_api_data_financial`
- **标签**: data
- **参数**: 4 个

#### GET /api/data/kline

**描述**: Get Kline

- **API ID**: `data_get_api_data_kline`
- **标签**: data
- **参数**: 4 个

#### GET /api/data/markets/hot-concepts

**描述**: Get Hot Concepts

- **API ID**: `data_get_api_data_markets_hot_concepts`
- **标签**: data
- **参数**: 1 个

#### GET /api/data/markets/hot-industries

**描述**: Get Hot Industries

- **API ID**: `data_get_api_data_markets_hot_industries`
- **标签**: data
- **参数**: 1 个

#### GET /api/data/markets/overview

**描述**: Get Market Overview

- **API ID**: `data_get_api_data_markets_overview`
- **标签**: data

#### GET /api/data/markets/price-distribution

**描述**: Get Price Distribution

- **API ID**: `data_get_api_data_markets_price_distribution`
- **标签**: data

#### GET /api/data/stocks/basic

**描述**: Get Stocks Basic

- **API ID**: `data_get_api_data_stocks_basic`
- **标签**: data
- **参数**: 8 个

#### GET /api/data/stocks/concepts

**描述**: Get Stocks Concepts

- **API ID**: `data_get_api_data_stocks_concepts`
- **标签**: data

#### GET /api/data/stocks/daily

**描述**: Get Daily Kline

- **API ID**: `data_get_api_data_stocks_daily`
- **标签**: data
- **参数**: 4 个

#### GET /api/data/stocks/industries

**描述**: Get Stocks Industries

- **API ID**: `data_get_api_data_stocks_industries`
- **标签**: data

#### GET /api/data/stocks/intraday

**描述**: Get Intraday Data

- **API ID**: `data_get_api_data_stocks_intraday`
- **标签**: data
- **参数**: 2 个

#### GET /api/data/stocks/kline

**描述**: Get Kline Data

- **API ID**: `data_get_api_data_stocks_kline`
- **标签**: data
- **参数**: 4 个

#### GET /api/data/stocks/search

**描述**: Search Stocks

- **API ID**: `data_get_api_data_stocks_search`
- **标签**: data
- **参数**: 2 个

#### GET /api/data/stocks/{symbol}/detail

**描述**: Get Stock Detail

- **API ID**: `data_get_api_data_stocks_symbol_detail`
- **标签**: data
- **参数**: 1 个

#### GET /api/data/stocks/{symbol}/trading-summary

**描述**: Get Trading Summary

- **API ID**: `data_get_api_data_stocks_symbol_trading_summary`
- **标签**: data
- **参数**: 2 个

#### GET /api/data/test/factory

**描述**: Test Data Source Factory

- **API ID**: `data_get_api_data_test_factory`
- **标签**: data
- **参数**: 1 个

---

## data-quality

### P1 - 重要业务API

#### GET /api/data-quality/alerts

**描述**: Get Active Alerts

- **API ID**: `data_quality_get_api_data_quality_alerts`
- **标签**: data-quality, data-quality
- **参数**: 3 个

#### GET /api/data-quality/config/mode

**描述**: Get Data Source Mode

- **API ID**: `data_quality_get_api_data_quality_config_mode`
- **标签**: data-quality, data-quality

#### GET /api/data-quality/health

**描述**: Get Sources Health

- **API ID**: `data_quality_get_api_data_quality_health`
- **标签**: data-quality, data-quality

#### GET /api/data-quality/metrics

**描述**: Get Data Quality Metrics

- **API ID**: `data_quality_get_api_data_quality_metrics`
- **标签**: data-quality, data-quality
- **参数**: 1 个

#### GET /api/data-quality/metrics/trends

**描述**: Get Quality Trends

- **API ID**: `data_quality_get_api_data_quality_metrics_trends`
- **标签**: data-quality, data-quality
- **参数**: 2 个

#### GET /api/data-quality/status/overview

**描述**: Get System Status Overview

- **API ID**: `data_quality_get_api_data_quality_status_overview`
- **标签**: data-quality, data-quality

#### POST /api/data-quality/alerts/{alert_id}/acknowledge

**描述**: Acknowledge Alert

- **API ID**: `data_quality_post_api_data_quality_alerts_alert_id_acknowledge`
- **标签**: data-quality, data-quality
- **参数**: 1 个

#### POST /api/data-quality/alerts/{alert_id}/resolve

**描述**: Resolve Alert

- **API ID**: `data_quality_post_api_data_quality_alerts_alert_id_resolve`
- **标签**: data-quality, data-quality
- **参数**: 1 个

#### POST /api/data-quality/test/quality

**描述**: Test Data Quality

- **API ID**: `data_quality_post_api_data_quality_test_quality`
- **标签**: data-quality, data-quality
- **参数**: 2 个

---

## gpu-monitoring

### P2 - 辅助功能API

#### GET /api/gpu/history

**描述**: Get Gpu History

- **API ID**: `gpu_monitoring_get_api_gpu_history`
- **标签**: gpu-monitoring, gpu-monitoring
- **参数**: 4 个

#### GET /api/gpu/metrics

**描述**: Get Prometheus Metrics

- **API ID**: `gpu_monitoring_get_api_gpu_metrics`
- **标签**: gpu-monitoring, gpu-monitoring

#### GET /api/gpu/performance

**描述**: Get Gpu Performance

- **API ID**: `gpu_monitoring_get_api_gpu_performance`
- **标签**: gpu-monitoring, gpu-monitoring
- **参数**: 1 个

#### GET /api/gpu/status

**描述**: Get Gpu Status

- **API ID**: `gpu_monitoring_get_api_gpu_status`
- **标签**: gpu-monitoring, gpu-monitoring
- **参数**: 1 个

---

## health

### P2 - 辅助功能API

#### GET /api/health

**描述**: Check System Health

- **API ID**: `health_get_api_health`
- **标签**: health

#### GET /api/health/detailed

**描述**: Detailed Health Check

- **API ID**: `health_get_api_health_detailed`
- **标签**: health

#### GET /api/reports/health/{timestamp}

**描述**: Get Health Report

- **API ID**: `health_get_api_reports_health_timestamp`
- **标签**: health
- **参数**: 1 个

---

## indicators

### P1 - 重要业务API

#### DELETE /api/indicators/configs/{config_id}

**描述**: Delete Indicator Config

- **API ID**: `indicators_delete_api_indicators_configs_config_id`
- **标签**: indicators
- **参数**: 1 个

#### GET /api/indicators/cache/stats

**描述**: Get Cache Statistics

- **API ID**: `indicators_get_api_indicators_cache_stats`
- **标签**: indicators

#### GET /api/indicators/configs

**描述**: List Indicator Configs

- **API ID**: `indicators_get_api_indicators_configs`
- **标签**: indicators

#### GET /api/indicators/configs/{config_id}

**描述**: Get Indicator Config

- **API ID**: `indicators_get_api_indicators_configs_config_id`
- **标签**: indicators
- **参数**: 1 个

#### GET /api/indicators/registry

**描述**: Get Indicator Registry Endpoint

- **API ID**: `indicators_get_api_indicators_registry`
- **标签**: indicators
- **参数**: 3 个

#### GET /api/indicators/registry/{category}

**描述**: Get Indicators By Category

- **API ID**: `indicators_get_api_indicators_registry_category`
- **标签**: indicators
- **参数**: 1 个

#### POST /api/indicators/cache/clear

**描述**: Clear Cache

- **API ID**: `indicators_post_api_indicators_cache_clear`
- **标签**: indicators
- **参数**: 1 个

#### POST /api/indicators/calculate

**描述**: Calculate Indicators

- **API ID**: `indicators_post_api_indicators_calculate`
- **标签**: indicators
- **参数**: 1 个

#### POST /api/indicators/calculate/batch

**描述**: Calculate Indicators Batch

- **API ID**: `indicators_post_api_indicators_calculate_batch`
- **标签**: indicators
- **参数**: 1 个

#### POST /api/indicators/configs

**描述**: Create Indicator Config

- **API ID**: `indicators_post_api_indicators_configs`
- **标签**: indicators
- **参数**: 1 个

#### PUT /api/indicators/configs/{config_id}

**描述**: Update Indicator Config

- **API ID**: `indicators_put_api_indicators_configs_config_id`
- **标签**: indicators
- **参数**: 2 个

---

## industry-concept-analysis

### P2 - 辅助功能API

#### GET /api/analysis/concept/list

**描述**: Get Concept List

- **API ID**: `industry_concept_analysis_get_api_analysis_concept_list`
- **标签**: industry-concept-analysis

#### GET /api/analysis/concept/stocks

**描述**: Get Concept Stocks

- **API ID**: `industry_concept_analysis_get_api_analysis_concept_stocks`
- **标签**: industry-concept-analysis
- **参数**: 2 个

#### GET /api/analysis/industry/list

**描述**: Get Industry List

- **API ID**: `industry_concept_analysis_get_api_analysis_industry_list`
- **标签**: industry-concept-analysis

#### GET /api/analysis/industry/performance

**描述**: Get Industry Performance

- **API ID**: `industry_concept_analysis_get_api_analysis_industry_performance`
- **标签**: industry-concept-analysis
- **参数**: 1 个

#### GET /api/analysis/industry/stocks

**描述**: Get Industry Stocks

- **API ID**: `industry_concept_analysis_get_api_analysis_industry_stocks`
- **标签**: industry-concept-analysis
- **参数**: 2 个

---

## machine-learning

### P2 - 辅助功能API

#### GET /api/ml/models

**描述**: List Models

- **API ID**: `machine_learning_get_api_ml_models`
- **标签**: machine-learning, Machine Learning

#### GET /api/ml/models/{model_name}

**描述**: Get Model Detail

- **API ID**: `machine_learning_get_api_ml_models_model_name`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### GET /api/ml/tdx/stocks/{market}

**描述**: List Tdx Stocks

- **API ID**: `machine_learning_get_api_ml_tdx_stocks_market`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/features/generate

**描述**: Generate Features

- **API ID**: `machine_learning_post_api_ml_features_generate`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/models/evaluate

**描述**: Evaluate Model

- **API ID**: `machine_learning_post_api_ml_models_evaluate`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/models/hyperparameter-search

**描述**: Hyperparameter Search

- **API ID**: `machine_learning_post_api_ml_models_hyperparameter_search`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/models/predict

**描述**: Predict With Model

- **API ID**: `machine_learning_post_api_ml_models_predict`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/models/train

**描述**: Train Model

- **API ID**: `machine_learning_post_api_ml_models_train`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

#### POST /api/ml/tdx/data

**描述**: Get Tdx Data

- **API ID**: `machine_learning_post_api_ml_tdx_data`
- **标签**: machine-learning, Machine Learning
- **参数**: 1 个

---

## market

### P0 - 核心业务API

#### GET /api/market/chip-race

**描述**: 查询竞价抢筹

- **API ID**: `market_get_api_market_chip_race`
- **标签**: market, 市场数据
- **参数**: 4 个

#### GET /api/market/etf/list

**描述**: 查询ETF列表

- **API ID**: `market_get_api_market_etf_list`
- **标签**: market, 市场数据
- **参数**: 6 个

#### GET /api/market/fund-flow

**描述**: 查询资金流向

- **API ID**: `market_get_api_market_fund_flow`
- **标签**: market, 市场数据
- **参数**: 4 个

#### GET /api/market/health

**描述**: 市场数据 API 健康检查

- **API ID**: `market_get_api_market_health`
- **标签**: market, 市场数据, health

#### GET /api/market/heatmap

**描述**: 获取市场热力图数据

- **API ID**: `market_get_api_market_heatmap`
- **标签**: market, 市场数据
- **参数**: 2 个

#### GET /api/market/kline

**描述**: 查询K线数据

- **API ID**: `market_get_api_market_kline`
- **标签**: market, 市场数据
- **参数**: 5 个

#### GET /api/market/lhb

**描述**: 查询龙虎榜

- **API ID**: `market_get_api_market_lhb`
- **标签**: market, 市场数据
- **参数**: 5 个

#### GET /api/market/quotes

**描述**: 查询实时行情

- **API ID**: `market_get_api_market_quotes`
- **标签**: market, 市场数据
- **参数**: 1 个

#### GET /api/market/stocks

**描述**: 查询股票列表

- **API ID**: `market_get_api_market_stocks`
- **标签**: market, 市场数据
- **参数**: 4 个

#### POST /api/market/chip-race/refresh

**描述**: 刷新抢筹数据

- **API ID**: `market_post_api_market_chip_race_refresh`
- **标签**: market, 市场数据
- **参数**: 2 个

#### POST /api/market/etf/refresh

**描述**: 刷新ETF数据

- **API ID**: `market_post_api_market_etf_refresh`
- **标签**: market, 市场数据

#### POST /api/market/fund-flow/refresh

**描述**: 刷新资金流向

- **API ID**: `market_post_api_market_fund_flow_refresh`
- **标签**: market, 市场数据
- **参数**: 2 个

#### POST /api/market/lhb/refresh

**描述**: 刷新龙虎榜

- **API ID**: `market_post_api_market_lhb_refresh`
- **标签**: market, 市场数据
- **参数**: 1 个

---

## market-v2

### P0 - 核心业务API

#### GET /api/market/v2/blocktrade

**描述**: 查询股票大宗交易

- **API ID**: `market_v2_get_api_market_v2_blocktrade`
- **标签**: market-v2, 市场数据V2
- **参数**: 4 个

#### GET /api/market/v2/dividend

**描述**: 查询股票分红配送

- **API ID**: `market_v2_get_api_market_v2_dividend`
- **标签**: market-v2, 市场数据V2
- **参数**: 2 个

#### GET /api/market/v2/etf/list

**描述**: 查询ETF列表

- **API ID**: `market_v2_get_api_market_v2_etf_list`
- **标签**: market-v2, 市场数据V2
- **参数**: 3 个

#### GET /api/market/v2/fund-flow

**描述**: 查询个股资金流向

- **API ID**: `market_v2_get_api_market_v2_fund_flow`
- **标签**: market-v2, 市场数据V2
- **参数**: 4 个

#### GET /api/market/v2/lhb

**描述**: 查询龙虎榜

- **API ID**: `market_v2_get_api_market_v2_lhb`
- **标签**: market-v2, 市场数据V2
- **参数**: 5 个

#### GET /api/market/v2/sector/fund-flow

**描述**: 查询行业/概念资金流向

- **API ID**: `market_v2_get_api_market_v2_sector_fund_flow`
- **标签**: market-v2, 市场数据V2
- **参数**: 3 个

#### POST /api/market/v2/blocktrade/refresh

**描述**: 刷新股票大宗交易数据

- **API ID**: `market_v2_post_api_market_v2_blocktrade_refresh`
- **标签**: market-v2, 市场数据V2
- **参数**: 1 个

#### POST /api/market/v2/dividend/refresh

**描述**: 刷新股票分红配送数据

- **API ID**: `market_v2_post_api_market_v2_dividend_refresh`
- **标签**: market-v2, 市场数据V2
- **参数**: 1 个

#### POST /api/market/v2/etf/refresh

**描述**: 刷新ETF数据

- **API ID**: `market_v2_post_api_market_v2_etf_refresh`
- **标签**: market-v2, 市场数据V2

#### POST /api/market/v2/fund-flow/refresh

**描述**: 刷新资金流向数据

- **API ID**: `market_v2_post_api_market_v2_fund_flow_refresh`
- **标签**: market-v2, 市场数据V2
- **参数**: 2 个

#### POST /api/market/v2/lhb/refresh

**描述**: 刷新龙虎榜数据

- **API ID**: `market_v2_post_api_market_v2_lhb_refresh`
- **标签**: market-v2, 市场数据V2
- **参数**: 1 个

#### POST /api/market/v2/refresh-all

**描述**: 批量刷新所有市场数据

- **API ID**: `market_v2_post_api_market_v2_refresh_all`
- **标签**: market-v2, 市场数据V2

#### POST /api/market/v2/sector/fund-flow/refresh

**描述**: 刷新行业/概念资金流向

- **API ID**: `market_v2_post_api_market_v2_sector_fund_flow_refresh`
- **标签**: market-v2, 市场数据V2
- **参数**: 2 个

---

## metrics

### P2 - 辅助功能API

#### GET /api/basic

**描述**: Basic Metrics

- **API ID**: `metrics_get_api_basic`
- **标签**: metrics

#### GET /api/detailed

**描述**: Detailed Metrics

- **API ID**: `metrics_get_api_detailed`
- **标签**: metrics

#### GET /api/metrics

**描述**: Prometheus Metrics

- **API ID**: `metrics_get_api_metrics`
- **标签**: metrics

#### GET /api/performance

**描述**: Performance Metrics

- **API ID**: `metrics_get_api_performance`
- **标签**: metrics

#### GET /api/status

**描述**: Basic Status

- **API ID**: `metrics_get_api_status`
- **标签**: metrics

#### POST /api/reset

**描述**: Reset Metrics

- **API ID**: `metrics_post_api_reset`
- **标签**: metrics

---

## monitoring

### P2 - 辅助功能API

#### GET /monitoring/health

**描述**: Health Check

- **API ID**: `monitoring_get_monitoring_health`
- **标签**: monitoring

#### GET /monitoring/status

**描述**: Get Status

- **API ID**: `monitoring_get_monitoring_status`
- **标签**: monitoring

#### POST /monitoring/analyze

**描述**: Analyze Data

- **API ID**: `monitoring_post_monitoring_analyze`
- **标签**: monitoring
- **参数**: 1 个

---

## multi-source

### P2 - 辅助功能API

#### GET /multi_source/health

**描述**: Health Check

- **API ID**: `multi_source_get_multi_source_health`
- **标签**: multi-source

#### GET /multi_source/status

**描述**: Get Status

- **API ID**: `multi_source_get_multi_source_status`
- **标签**: multi-source

#### POST /multi_source/analyze

**描述**: Analyze Data

- **API ID**: `multi_source_post_multi_source_analyze`
- **标签**: multi-source
- **参数**: 1 个

---

## notification

### P1 - 重要业务API

#### GET /api/notification/preferences

**描述**: Get Notification Preferences

- **API ID**: `notification_get_api_notification_preferences`
- **标签**: notification

#### GET /api/notification/status

**描述**: Get Email Service Status

- **API ID**: `notification_get_api_notification_status`
- **标签**: notification

#### POST /api/notification/email/newsletter

**描述**: Send Daily Newsletter

- **API ID**: `notification_post_api_notification_email_newsletter`
- **标签**: notification
- **参数**: 1 个

#### POST /api/notification/email/price-alert

**描述**: Send Price Alert

- **API ID**: `notification_post_api_notification_email_price_alert`
- **标签**: notification
- **参数**: 1 个

#### POST /api/notification/email/send

**描述**: Send Email

- **API ID**: `notification_post_api_notification_email_send`
- **标签**: notification
- **参数**: 1 个

#### POST /api/notification/email/welcome

**描述**: Send Welcome Email

- **API ID**: `notification_post_api_notification_email_welcome`
- **标签**: notification
- **参数**: 1 个

#### POST /api/notification/preferences

**描述**: Update Notification Preferences

- **API ID**: `notification_post_api_notification_preferences`
- **标签**: notification
- **参数**: 1 个

#### POST /api/notification/test-email

**描述**: Send Test Email

- **API ID**: `notification_post_api_notification_test_email`
- **标签**: notification

---

## pool-monitoring

### P2 - 辅助功能API

#### GET /api/pool-monitoring/alerts

**描述**: 连接池告警检测

- **API ID**: `pool_monitoring_get_api_pool_monitoring_alerts`
- **标签**: pool-monitoring, Connection Pool Monitoring

#### GET /api/pool-monitoring/health

**描述**: 连接池综合健康检查

- **API ID**: `pool_monitoring_get_api_pool_monitoring_health`
- **标签**: pool-monitoring, Connection Pool Monitoring

#### GET /api/pool-monitoring/postgresql/stats

**描述**: PostgreSQL连接池统计

- **API ID**: `pool_monitoring_get_api_pool_monitoring_postgresql_stats`
- **标签**: pool-monitoring, Connection Pool Monitoring

#### GET /api/pool-monitoring/tdengine/stats

**描述**: TDengine连接池统计

- **API ID**: `pool_monitoring_get_api_pool_monitoring_tdengine_stats`
- **标签**: pool-monitoring, Connection Pool Monitoring

---

## stock-search

### P1 - 重要业务API

#### GET /api/stock-search/analytics/searches

**描述**: Get Search Analytics

- **API ID**: `stock_search_get_api_stock_search_analytics_searches`
- **标签**: stock-search
- **参数**: 3 个

#### GET /api/stock-search/news/market/{category}

**描述**: Get Market News

- **API ID**: `stock_search_get_api_stock_search_news_market_category`
- **标签**: stock-search
- **参数**: 2 个

#### GET /api/stock-search/news/{symbol}

**描述**: Get Stock News

- **API ID**: `stock_search_get_api_stock_search_news_symbol`
- **标签**: stock-search
- **参数**: 3 个

#### GET /api/stock-search/profile/{symbol}

**描述**: Get Company Profile

- **API ID**: `stock_search_get_api_stock_search_profile_symbol`
- **标签**: stock-search
- **参数**: 2 个

#### GET /api/stock-search/quote/{symbol}

**描述**: Get Stock Quote

- **API ID**: `stock_search_get_api_stock_search_quote_symbol`
- **标签**: stock-search
- **参数**: 2 个

#### GET /api/stock-search/rate-limits/status

**描述**: Get Rate Limits Status

- **API ID**: `stock_search_get_api_stock_search_rate_limits_status`
- **标签**: stock-search
- **参数**: 1 个

#### GET /api/stock-search/recommendation/{symbol}

**描述**: Get Recommendation Trends

- **API ID**: `stock_search_get_api_stock_search_recommendation_symbol`
- **标签**: stock-search
- **参数**: 1 个

#### GET /api/stock-search/search

**描述**: Search Stocks

- **API ID**: `stock_search_get_api_stock_search_search`
- **标签**: stock-search
- **参数**: 6 个

#### POST /api/stock-search/analytics/cleanup

**描述**: Cleanup Search Analytics

- **API ID**: `stock_search_post_api_stock_search_analytics_cleanup`
- **标签**: stock-search
- **参数**: 1 个

#### POST /api/stock-search/cache/clear

**描述**: Clear Search Cache

- **API ID**: `stock_search_post_api_stock_search_cache_clear`
- **标签**: stock-search

---

## strategy

### P0 - 核心业务API

#### GET /api/strategy/definitions

**描述**: Get Strategy Definitions

- **API ID**: `strategy_get_api_strategy_definitions`
- **标签**: strategy, strategy

#### GET /api/strategy/matched-stocks

**描述**: Get Matched Stocks

- **API ID**: `strategy_get_api_strategy_matched_stocks`
- **标签**: strategy, strategy
- **参数**: 3 个

#### GET /api/strategy/results

**描述**: Query Strategy Results

- **API ID**: `strategy_get_api_strategy_results`
- **标签**: strategy, strategy
- **参数**: 6 个

#### GET /api/strategy/stats/summary

**描述**: Get Strategy Summary

- **API ID**: `strategy_get_api_strategy_stats_summary`
- **标签**: strategy, strategy
- **参数**: 1 个

#### POST /api/strategy/run/batch

**描述**: Run Strategy Batch

- **API ID**: `strategy_post_api_strategy_run_batch`
- **标签**: strategy, strategy
- **参数**: 5 个

#### POST /api/strategy/run/single

**描述**: Run Strategy Single

- **API ID**: `strategy_post_api_strategy_run_single`
- **标签**: strategy, strategy
- **参数**: 4 个

---

## strategy-mgmt

### P2 - 辅助功能API

#### DELETE /api/strategy-mgmt/strategies/{strategy_id}

**描述**: 删除策略

- **API ID**: `strategy_mgmt_delete_api_strategy_mgmt_strategies_strategy_id`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### GET /api/strategy-mgmt/backtest/results

**描述**: 获取回测列表

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_backtest_results`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 4 个

#### GET /api/strategy-mgmt/backtest/results/{backtest_id}

**描述**: 获取回测结果

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_backtest_results_backtest_id`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### GET /api/strategy-mgmt/backtest/status/{backtest_id}

**描述**: 获取回测任务状态

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_backtest_status_backtest_id`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### GET /api/strategy-mgmt/health

**描述**: 健康检查

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_health`
- **标签**: strategy-mgmt, strategy-mgmt

#### GET /api/strategy-mgmt/strategies

**描述**: 获取策略列表

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_strategies`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 4 个

#### GET /api/strategy-mgmt/strategies/{strategy_id}

**描述**: 获取策略详情

- **API ID**: `strategy_mgmt_get_api_strategy_mgmt_strategies_strategy_id`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### POST /api/strategy-mgmt/backtest/execute

**描述**: 执行回测

- **API ID**: `strategy_mgmt_post_api_strategy_mgmt_backtest_execute`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### POST /api/strategy-mgmt/strategies

**描述**: 创建新策略

- **API ID**: `strategy_mgmt_post_api_strategy_mgmt_strategies`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 1 个

#### PUT /api/strategy-mgmt/strategies/{strategy_id}

**描述**: 更新策略

- **API ID**: `strategy_mgmt_put_api_strategy_mgmt_strategies_strategy_id`
- **标签**: strategy-mgmt, strategy-mgmt
- **参数**: 2 个

---

## system

### P2 - 辅助功能API

#### GET /api/system/adapters/health

**描述**: Get Adapters Health

- **API ID**: `system_get_api_system_adapters_health`
- **标签**: system

#### GET /api/system/architecture

**描述**: Get System Architecture

- **API ID**: `system_get_api_system_architecture`
- **标签**: system

#### GET /api/system/database/health

**描述**: Database Health

- **API ID**: `system_get_api_system_database_health`
- **标签**: system

#### GET /api/system/database/stats

**描述**: Database Stats

- **API ID**: `system_get_api_system_database_stats`
- **标签**: system

#### GET /api/system/datasources

**描述**: Get Datasources

- **API ID**: `system_get_api_system_datasources`
- **标签**: system

#### GET /api/system/health

**描述**: System Health

- **API ID**: `system_get_api_system_health`
- **标签**: system

#### GET /api/system/logs

**描述**: Get System Logs

- **API ID**: `system_get_api_system_logs`
- **标签**: system
- **参数**: 5 个

#### GET /api/system/logs/summary

**描述**: Get Logs Summary

- **API ID**: `system_get_api_system_logs_summary`
- **标签**: system

#### POST /api/system/test-connection

**描述**: Test Database Connection

- **API ID**: `system_post_api_system_test_connection`
- **标签**: system
- **参数**: 1 个

---

## tasks

### P2 - 辅助功能API

#### DELETE /api/tasks/executions/cleanup

**描述**: Cleanup Executions

- **API ID**: `tasks_delete_api_tasks_executions_cleanup`
- **标签**: tasks, tasks
- **参数**: 1 个

#### DELETE /api/tasks/{task_id}

**描述**: Unregister Task

- **API ID**: `tasks_delete_api_tasks_task_id`
- **标签**: tasks, tasks
- **参数**: 1 个

#### GET /api/tasks/

**描述**: List Tasks

- **API ID**: `tasks_get_api_tasks`
- **标签**: tasks, tasks
- **参数**: 6 个

#### GET /api/tasks/audit/logs

**描述**: Get Audit Logs

- **API ID**: `tasks_get_api_tasks_audit_logs`
- **标签**: tasks, tasks
- **参数**: 3 个

#### GET /api/tasks/executions/

**描述**: List Task Executions

- **API ID**: `tasks_get_api_tasks_executions`
- **标签**: tasks, tasks
- **参数**: 2 个

#### GET /api/tasks/executions/{execution_id}

**描述**: Get Execution

- **API ID**: `tasks_get_api_tasks_executions_execution_id`
- **标签**: tasks, tasks
- **参数**: 1 个

#### GET /api/tasks/health

**描述**: 任务管理健康检查

- **API ID**: `tasks_get_api_tasks_health`
- **标签**: tasks, tasks, health

#### GET /api/tasks/statistics/

**描述**: Get Task Statistics

- **API ID**: `tasks_get_api_tasks_statistics`
- **标签**: tasks, tasks

#### GET /api/tasks/{task_id}

**描述**: Get Task

- **API ID**: `tasks_get_api_tasks_task_id`
- **标签**: tasks, tasks
- **参数**: 1 个

#### POST /api/tasks/cleanup/audit

**描述**: Cleanup Audit Logs

- **API ID**: `tasks_post_api_tasks_cleanup_audit`
- **标签**: tasks, tasks
- **参数**: 1 个

#### POST /api/tasks/export

**描述**: Export Config

- **API ID**: `tasks_post_api_tasks_export`
- **标签**: tasks, tasks
- **参数**: 1 个

#### POST /api/tasks/import

**描述**: Import Config

- **API ID**: `tasks_post_api_tasks_import`
- **标签**: tasks, tasks
- **参数**: 1 个

#### POST /api/tasks/register

**描述**: Register Task

- **API ID**: `tasks_post_api_tasks_register`
- **标签**: tasks, tasks
- **参数**: 1 个

#### POST /api/tasks/{task_id}/start

**描述**: Start Task

- **API ID**: `tasks_post_api_tasks_task_id_start`
- **标签**: tasks, tasks
- **参数**: 2 个

#### POST /api/tasks/{task_id}/stop

**描述**: Stop Task

- **API ID**: `tasks_post_api_tasks_task_id_stop`
- **标签**: tasks, tasks
- **参数**: 1 个

---

## tdx

### P2 - 辅助功能API

#### GET /api/tdx/health

**描述**: TDX服务健康检查

- **API ID**: `tdx_get_api_tdx_health`
- **标签**: tdx, TDX行情数据

#### GET /api/tdx/index/kline

**描述**: 获取指数K线数据

- **API ID**: `tdx_get_api_tdx_index_kline`
- **标签**: tdx, TDX行情数据
- **参数**: 4 个

#### GET /api/tdx/index/quote/{symbol}

**描述**: 获取指数实时行情

- **API ID**: `tdx_get_api_tdx_index_quote_symbol`
- **标签**: tdx, TDX行情数据
- **参数**: 1 个

#### GET /api/tdx/kline

**描述**: 获取股票K线数据

- **API ID**: `tdx_get_api_tdx_kline`
- **标签**: tdx, TDX行情数据
- **参数**: 4 个

#### GET /api/tdx/quote/{symbol}

**描述**: 获取股票实时行情

- **API ID**: `tdx_get_api_tdx_quote_symbol`
- **标签**: tdx, TDX行情数据
- **参数**: 1 个

---

## technical-analysis

### P1 - 重要业务API

#### GET /api/technical/patterns/{symbol}

**描述**: Detect Patterns

- **API ID**: `technical_analysis_get_api_technical_patterns_symbol`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

#### GET /api/technical/{symbol}/history

**描述**: Get Stock History

- **API ID**: `technical_analysis_get_api_technical_symbol_history`
- **标签**: technical-analysis, technical-analysis
- **参数**: 5 个

#### GET /api/technical/{symbol}/indicators

**描述**: Get All Indicators

- **API ID**: `technical_analysis_get_api_technical_symbol_indicators`
- **标签**: technical-analysis, technical-analysis
- **参数**: 5 个

#### GET /api/technical/{symbol}/momentum

**描述**: Get Momentum Indicators

- **API ID**: `technical_analysis_get_api_technical_symbol_momentum`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

#### GET /api/technical/{symbol}/signals

**描述**: Get Trading Signals

- **API ID**: `technical_analysis_get_api_technical_symbol_signals`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

#### GET /api/technical/{symbol}/trend

**描述**: 获取趋势指标

- **API ID**: `technical_analysis_get_api_technical_symbol_trend`
- **标签**: technical-analysis, technical-analysis
- **参数**: 3 个

#### GET /api/technical/{symbol}/volatility

**描述**: Get Volatility Indicators

- **API ID**: `technical_analysis_get_api_technical_symbol_volatility`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

#### GET /api/technical/{symbol}/volume

**描述**: Get Volume Indicators

- **API ID**: `technical_analysis_get_api_technical_symbol_volume`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

#### POST /api/technical/batch/indicators

**描述**: Get Batch Indicators

- **API ID**: `technical_analysis_post_api_technical_batch_indicators`
- **标签**: technical-analysis, technical-analysis
- **参数**: 2 个

---

## trade

### P0 - 核心业务API

#### GET /api/trade/health

**描述**: Health Check

- **API ID**: `trade_get_api_trade_health`
- **标签**: trade, 交易执行

#### GET /api/trade/portfolio

**描述**: Get Portfolio

- **API ID**: `trade_get_api_trade_portfolio`
- **标签**: trade, 交易执行

#### GET /api/trade/positions

**描述**: Get Positions

- **API ID**: `trade_get_api_trade_positions`
- **标签**: trade, 交易执行

#### GET /api/trade/statistics

**描述**: Get Statistics

- **API ID**: `trade_get_api_trade_statistics`
- **标签**: trade, 交易执行

#### GET /api/trade/trades

**描述**: Get Trades

- **API ID**: `trade_get_api_trade_trades`
- **标签**: trade, 交易执行
- **参数**: 5 个

#### POST /api/trade/execute

**描述**: Execute Trade

- **API ID**: `trade_post_api_trade_execute`
- **标签**: trade, 交易执行
- **参数**: 1 个

---

## tradingview

### P1 - 重要业务API

#### GET /api/tradingview/market-overview/config

**描述**: Get Market Overview Config

- **API ID**: `tradingview_get_api_tradingview_market_overview_config`
- **标签**: tradingview
- **参数**: 4 个

#### GET /api/tradingview/screener/config

**描述**: Get Screener Config

- **API ID**: `tradingview_get_api_tradingview_screener_config`
- **标签**: tradingview
- **参数**: 4 个

#### GET /api/tradingview/symbol/convert

**描述**: Convert Symbol

- **API ID**: `tradingview_get_api_tradingview_symbol_convert`
- **标签**: tradingview
- **参数**: 2 个

#### POST /api/tradingview/chart/config

**描述**: Get Chart Config

- **API ID**: `tradingview_post_api_tradingview_chart_config`
- **标签**: tradingview
- **参数**: 1 个

#### POST /api/tradingview/mini-chart/config

**描述**: Get Mini Chart Config

- **API ID**: `tradingview_post_api_tradingview_mini_chart_config`
- **标签**: tradingview
- **参数**: 5 个

#### POST /api/tradingview/ticker-tape/config

**描述**: Get Ticker Tape Config

- **API ID**: `tradingview_post_api_tradingview_ticker_tape_config`
- **标签**: tradingview
- **参数**: 1 个

---

## watchlist

### P1 - 重要业务API

#### DELETE /api/watchlist/clear

**描述**: Clear Watchlist

- **API ID**: `watchlist_delete_api_watchlist_clear`
- **标签**: watchlist

#### DELETE /api/watchlist/groups/{group_id}

**描述**: Delete Group

- **API ID**: `watchlist_delete_api_watchlist_groups_group_id`
- **标签**: watchlist
- **参数**: 1 个

#### DELETE /api/watchlist/remove/{symbol}

**描述**: Remove From Watchlist

- **API ID**: `watchlist_delete_api_watchlist_remove_symbol`
- **标签**: watchlist
- **参数**: 1 个

#### GET /api/watchlist/

**描述**: Get My Watchlist

- **API ID**: `watchlist_get_api_watchlist`
- **标签**: watchlist

#### GET /api/watchlist/check/{symbol}

**描述**: Check In Watchlist

- **API ID**: `watchlist_get_api_watchlist_check_symbol`
- **标签**: watchlist
- **参数**: 1 个

#### GET /api/watchlist/count

**描述**: Get Watchlist Count

- **API ID**: `watchlist_get_api_watchlist_count`
- **标签**: watchlist

#### GET /api/watchlist/group/{group_id}

**描述**: Get Watchlist By Group

- **API ID**: `watchlist_get_api_watchlist_group_group_id`
- **标签**: watchlist
- **参数**: 1 个

#### GET /api/watchlist/groups

**描述**: Get User Groups

- **API ID**: `watchlist_get_api_watchlist_groups`
- **标签**: watchlist

#### GET /api/watchlist/symbols

**描述**: Get My Watchlist Symbols

- **API ID**: `watchlist_get_api_watchlist_symbols`
- **标签**: watchlist

#### GET /api/watchlist/with-groups

**描述**: Get Watchlist With Groups

- **API ID**: `watchlist_get_api_watchlist_with_groups`
- **标签**: watchlist

#### POST /api/watchlist/add

**描述**: Add To Watchlist

- **API ID**: `watchlist_post_api_watchlist_add`
- **标签**: watchlist
- **参数**: 1 个

#### POST /api/watchlist/groups

**描述**: Create Group

- **API ID**: `watchlist_post_api_watchlist_groups`
- **标签**: watchlist
- **参数**: 1 个

#### PUT /api/watchlist/groups/{group_id}

**描述**: Update Group

- **API ID**: `watchlist_put_api_watchlist_groups_group_id`
- **标签**: watchlist
- **参数**: 2 个

#### PUT /api/watchlist/move

**描述**: Move Stock To Group

- **API ID**: `watchlist_put_api_watchlist_move`
- **标签**: watchlist
- **参数**: 1 个

#### PUT /api/watchlist/notes/{symbol}

**描述**: Update Watchlist Notes

- **API ID**: `watchlist_put_api_watchlist_notes_symbol`
- **标签**: watchlist
- **参数**: 2 个

---

## wencai

### P0 - 核心业务API

#### GET /api/market/wencai/health

**描述**: 健康检查

- **API ID**: `wencai_get_api_market_wencai_health`
- **标签**: wencai

#### GET /api/market/wencai/history/{query_name}

**描述**: 获取查询历史

- **API ID**: `wencai_get_api_market_wencai_history_query_name`
- **标签**: wencai
- **参数**: 2 个

#### GET /api/market/wencai/queries

**描述**: 获取所有查询列表

- **API ID**: `wencai_get_api_market_wencai_queries`
- **标签**: wencai

#### GET /api/market/wencai/queries/{query_name}

**描述**: 获取指定查询信息

- **API ID**: `wencai_get_api_market_wencai_queries_query_name`
- **标签**: wencai
- **参数**: 1 个

#### GET /api/market/wencai/results/{query_name}

**描述**: 获取查询结果

- **API ID**: `wencai_get_api_market_wencai_results_query_name`
- **标签**: wencai
- **参数**: 3 个

#### POST /api/market/wencai/custom-query

**描述**: 执行自定义查询

- **API ID**: `wencai_post_api_market_wencai_custom_query`
- **标签**: wencai
- **参数**: 1 个

#### POST /api/market/wencai/query

**描述**: 执行问财查询

- **API ID**: `wencai_post_api_market_wencai_query`
- **标签**: wencai
- **参数**: 1 个

#### POST /api/market/wencai/refresh/{query_name}

**描述**: 刷新查询数据

- **API ID**: `wencai_post_api_market_wencai_refresh_query_name`
- **标签**: wencai
- **参数**: 2 个

---

## 策略管理-Week1

### P2 - 辅助功能API

#### DELETE /api/v1/strategy/strategies/{strategy_id}

**描述**: Delete Strategy

- **API ID**: `策略管理_Week1_delete_api_v1_strategy_strategies_strategy_id`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### GET /api/v1/strategy/backtest/results

**描述**: List Backtest Results

- **API ID**: `策略管理_Week1_get_api_v1_strategy_backtest_results`
- **标签**: 策略管理-Week1
- **参数**: 3 个

#### GET /api/v1/strategy/backtest/results/{backtest_id}

**描述**: Get Backtest Result

- **API ID**: `策略管理_Week1_get_api_v1_strategy_backtest_results_backtest_id`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### GET /api/v1/strategy/backtest/results/{backtest_id}/chart-data

**描述**: Get Backtest Chart Data

- **API ID**: `策略管理_Week1_get_api_v1_strategy_backtest_results_backtest_id_chart_data`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### GET /api/v1/strategy/models

**描述**: List Models

- **API ID**: `策略管理_Week1_get_api_v1_strategy_models`
- **标签**: 策略管理-Week1
- **参数**: 2 个

#### GET /api/v1/strategy/models/training/{task_id}/status

**描述**: Get Training Status

- **API ID**: `策略管理_Week1_get_api_v1_strategy_models_training_task_id_status`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### GET /api/v1/strategy/strategies

**描述**: List Strategies

- **API ID**: `策略管理_Week1_get_api_v1_strategy_strategies`
- **标签**: 策略管理-Week1
- **参数**: 3 个

#### GET /api/v1/strategy/strategies/{strategy_id}

**描述**: Get Strategy

- **API ID**: `策略管理_Week1_get_api_v1_strategy_strategies_strategy_id`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### POST /api/v1/strategy/backtest/run

**描述**: Run Backtest

- **API ID**: `策略管理_Week1_post_api_v1_strategy_backtest_run`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### POST /api/v1/strategy/models/train

**描述**: Train Model

- **API ID**: `策略管理_Week1_post_api_v1_strategy_models_train`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### POST /api/v1/strategy/strategies

**描述**: Create Strategy

- **API ID**: `策略管理_Week1_post_api_v1_strategy_strategies`
- **标签**: 策略管理-Week1
- **参数**: 1 个

#### PUT /api/v1/strategy/strategies/{strategy_id}

**描述**: Update Strategy

- **API ID**: `策略管理_Week1_put_api_v1_strategy_strategies_strategy_id`
- **标签**: 策略管理-Week1
- **参数**: 2 个

---

## 风险管理-Week1

### P2 - 辅助功能API

#### DELETE /api/v1/risk/alerts/{alert_id}

**描述**: Delete Risk Alert

- **API ID**: `风险管理_Week1_delete_api_v1_risk_alerts_alert_id`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### GET /api/v1/risk/alerts

**描述**: List Risk Alerts

- **API ID**: `风险管理_Week1_get_api_v1_risk_alerts`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### GET /api/v1/risk/dashboard

**描述**: Get Risk Dashboard

- **API ID**: `风险管理_Week1_get_api_v1_risk_dashboard`
- **标签**: 风险管理-Week1

#### GET /api/v1/risk/metrics/history

**描述**: Get Risk Metrics History

- **API ID**: `风险管理_Week1_get_api_v1_risk_metrics_history`
- **标签**: 风险管理-Week1
- **参数**: 4 个

#### POST /api/v1/risk/alerts

**描述**: Create Risk Alert

- **API ID**: `风险管理_Week1_post_api_v1_risk_alerts`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/alerts/generate

**描述**: Generate Risk Alerts

- **API ID**: `风险管理_Week1_post_api_v1_risk_alerts_generate`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/beta

**描述**: Calculate Beta

- **API ID**: `风险管理_Week1_post_api_v1_risk_beta`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/metrics/calculate

**描述**: Calculate Risk Metrics

- **API ID**: `风险管理_Week1_post_api_v1_risk_metrics_calculate`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/notifications/test

**描述**: Test Notification

- **API ID**: `风险管理_Week1_post_api_v1_risk_notifications_test`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/position/assess

**描述**: Assess Position Risk

- **API ID**: `风险管理_Week1_post_api_v1_risk_position_assess`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### POST /api/v1/risk/var-cvar

**描述**: Calculate Var Cvar

- **API ID**: `风险管理_Week1_post_api_v1_risk_var_cvar`
- **标签**: 风险管理-Week1
- **参数**: 1 个

#### PUT /api/v1/risk/alerts/{alert_id}

**描述**: Update Risk Alert

- **API ID**: `风险管理_Week1_put_api_v1_risk_alerts_alert_id`
- **标签**: 风险管理-Week1
- **参数**: 2 个

---
