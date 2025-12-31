"""
OpenAPI 配置模块
OpenAPI Configuration Module

为FastAPI应用提供增强的OpenAPI/Swagger文档配置:
- API元数据和版本信息
- 标签分组和描述
- 通用响应示例
- 安全方案定义

Author: Claude Code
Date: 2025-11-06
"""

from typing import Dict, Any

# ==================== API 元数据 ====================

API_METADATA = {
    "title": "MyStocks Web API",
    "description": """
# MyStocks 量化交易数据管理系统 Web API

MyStocks是一个专业的量化交易数据管理系统，提供全面的股票市场数据获取、分析和管理功能。

## 主要功能模块

### 📊 市场数据 (Market Data)
- 实时行情数据获取
- 历史K线数据查询
- 资金流向分析
- ETF数据分析
- 筹码分布数据

### 💾 缓存管理 (Cache Management)
- TDengine时序数据库缓存
- 缓存统计和监控
- 缓存淘汰策略
- 缓存预热功能

### 📈 技术指标 (Technical Indicators)
- 常用技术指标计算
- 自定义指标支持
- 实时指标推送

### 🤖 机器学习 (Machine Learning)
- 股票预测模型
- 特征工程
- 模型训练和评估

### 📋 策略管理 (Strategy Management)
- 策略创建和配置
- 回测系统
- 风险管理

### 🔔 实时推送 (Real-time Push)
- WebSocket实时数据推送
- SSE (Server-Sent Events) 流式推送
- 告警通知

### 🔐 认证授权 (Authentication)
- JWT Token认证
- CSRF保护
- 权限管理

## 架构特点

- **双数据库架构**: TDengine (时序数据) + PostgreSQL (关系数据)
- **统一响应格式**: 所有API遵循标准化响应结构
- **完整监控体系**: 性能监控、数据质量监控、告警系统
- **配置驱动**: YAML配置驱动的表管理和自动化

## 技术栈

- **后端框架**: FastAPI 0.104+ (Python 3.9+)
- **数据库**: TDengine 3.x, PostgreSQL 15+
- **缓存**: TDengine 时序缓存
- **异步**: asyncio, httpx
- **数据验证**: Pydantic v2
- **日志**: structlog

## 联系方式

- 项目文档: `/api/docs` (Swagger UI)
- 备用文档: `/api/redoc` (ReDoc)
- 健康检查: `/health`

---

**Version**: 2.0.0
**Last Updated**: 2025-11-06
**Environment**: Production
""",
    "version": "2.0.0",
    "terms_of_service": "https://mystocks.com/terms",
    "contact": {
        "name": "MyStocks API Support",
        "url": "https://mystocks.com/support",
        "email": "api@mystocks.com",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# ==================== API 标签分组 ====================

OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": """
**认证授权模块**

提供用户认证、JWT Token管理、CSRF保护等安全功能。

**主要功能**:
- 用户登录/登出
- JWT Token生成和验证
- CSRF Token管理
- 权限验证
""",
    },
    {
        "name": "market",
        "description": """
**市场数据模块 (V1)**

提供A股市场实时行情、历史数据、资金流向等核心市场数据。

**数据源**: AKShare, Baostock
**更新频率**: 实时 / 日级
**主要功能**:
- 实时行情查询
- 历史K线数据
- 资金流向分析
- 行业板块数据
- ETF数据
- 筹码分布
""",
    },
    {
        "name": "market-v2",
        "description": """
**市场数据模块 (V2 - 东方财富直接API)**

使用东方财富网直接API，提供更快速、更准确的市场数据。

**数据源**: 东方财富网 API
**优势**: 速度快、数据准确、更新及时
**主要功能**:
- 增强的实时行情
- 更详细的资金流向
- 龙虎榜数据
- 大单追踪
""",
    },
    {
        "name": "cache",
        "description": """
**缓存管理模块 (Task 2.2)**

基于TDengine时序数据库的智能缓存系统，提供高性能数据缓存和管理。

**存储引擎**: TDengine 3.x
**压缩比**: 20:1
**主要功能**:
- 缓存读写操作
- 缓存统计和监控
- 智能缓存淘汰 (LRU + TTL)
- 缓存预热
- 热点数据追踪
- 健康检查
""",
    },
    {
        "name": "indicators",
        "description": """
**技术指标计算模块 (P2 API)**

提供50+种技术指标的计算和批量处理功能。

**指标分类**:
- 趋势指标: SMA, EMA, MACD
- 动量指标: RSI, KDJ, CCI
- 波动指标: BOLL, ATR
- 成交量指标: OBV, VOL

**主要功能**:
- 单个/批量指标计算
- 指标配置管理 (CRUD)
- 缓存统计和清理
- 智能缓存机制 (TTL: 1小时)

**性能特性**:
- 速率限制: 60次/分钟
- 批量并发: 最多3个
- 缓存优化: 自动缓存常用计算

**计算引擎**: pandas_ta, talib
**认证**: 部分接口需要认证
""",
    },
    {
        "name": "machine-learning",
        "description": """
**机器学习模块**

提供股票预测模型训练、评估和预测功能。

**支持的模型**:
- 随机森林 (RandomForest)
- LSTM神经网络
- XGBoost
- LightGBM

**主要功能**:
- 特征工程
- 模型训练
- 模型评估
- 预测推理
- 模型版本管理
""",
    },
    {
        "name": "strategy",
        "description": """
**策略系统模块 (InStock集成)**

提供股票筛选策略、策略回测、收益分析等功能。

**策略类型**:
- 趋势策略
- 均值回归策略
- 突破策略
- 量价策略

**主要功能**:
- 策略配置
- 策略执行
- 结果分析
- 收益评估
""",
    },
    {
        "name": "strategy-management",
        "description": """
**策略管理模块 (Week 1 Architecture-Compliant)**

使用MyStocksUnifiedManager的企业级策略管理系统。

**架构特点**:
- 统一数据访问层
- 完整的监控集成
- 事务性操作
- 审计日志

**主要功能**:
- 策略CRUD操作
- 策略版本管理
- 策略参数配置
- 策略状态追踪
""",
    },
    {
        "name": "risk-management",
        "description": """
**风险管理模块 (Week 1 Architecture-Compliant)**

提供投资组合风险分析、告警规则配置等风险管理功能。

**风险指标**:
- VaR (Value at Risk)
- 最大回撤
- 夏普比率
- 波动率
- Beta系数

**主要功能**:
- 风险计算
- 告警规则管理
- 风险监控
- 风险报告
""",
    },
    {
        "name": "monitoring",
        "description": """
**实时监控模块**

提供系统和数据的实时监控、告警功能。

**监控维度**:
- 系统性能
- 数据质量
- API调用
- 缓存性能
- 数据库性能

**告警渠道**:
- 邮件通知
- Webhook
- 日志记录
""",
    },
    {
        "name": "sse",
        "description": """
**SSE实时推送模块 (Week 2)**

Server-Sent Events流式推送，提供实时数据更新。

**推送类型**:
- 训练进度推送
- 回测进度推送
- 告警推送
- 仪表盘数据推送

**特点**:
- 单向推送
- 自动重连
- 事件流格式
- 低延迟
""",
    },
    {
        "name": "data",
        "description": """
**数据管理模块**

提供数据导入、导出、同步等数据管理功能。

**主要功能**:
- 数据导入
- 数据导出
- 数据同步
- 数据清洗
- 数据校验
""",
    },
    {
        "name": "system",
        "description": """
**系统管理模块 (P2 API)**

提供系统级管理、监控和配置功能。

**子模块**:
- 健康检查: 系统状态、数据库状态、适配器状态
- 监控管理: 告警规则、实时监控、龙虎榜
- 日志管理: 日志查询、统计分析、摘要报告
- 架构信息: 系统架构、数据源配置

**主要功能**:
- 双数据库架构监控 (TDengine + PostgreSQL)
- LGTM Stack集成 (Loki, Grafana, Tempo, Prometheus)
- 实时告警规则管理
- 系统日志查询和分析
- 数据库连接测试

**监控指标**:
- 40+ Prometheus指标
- 实时性能数据
- 数据质量评分
- 缓存命中率

**认证**: 分级访问
""",
    },
    {
        "name": "tdx",
        "description": """
**通达信数据模块**

通达信数据源集成，提供Level-2行情数据。

**数据类型**:
- 分时数据
- 分笔成交
- 逐笔委托
- Level-2行情
""",
    },
    {
        "name": "metrics",
        "description": """
**Prometheus指标模块**

导出Prometheus格式的监控指标。

**指标类型**:
- Counter (计数器)
- Gauge (仪表)
- Histogram (直方图)
- Summary (摘要)
""",
    },
    {
        "name": "tasks",
        "description": """
**任务管理模块**

提供异步任务的创建、查询、取消等管理功能。

**任务类型**:
- 数据采集任务
- 计算任务
- 回测任务
- 训练任务
""",
    },
    {
        "name": "wencai",
        "description": """
**问财筛选模块**

同花顺问财条件选股集成。

**主要功能**:
- 自然语言选股
- 条件筛选
- 结果解析
""",
    },
    {
        "name": "stock-search",
        "description": """
**股票搜索模块 (OpenStock集成)**

提供快速的股票代码、名称搜索功能。

**搜索方式**:
- 代码搜索
- 名称搜索
- 拼音搜索
- 模糊搜索
""",
    },
    {
        "name": "watchlist",
        "description": """
**自选股管理模块 (OpenStock集成)**

用户自选股列表的创建、管理功能。

**主要功能**:
- 自选股分组
- 添加/删除股票
- 自选股排序
- 自选股导入/导出
""",
    },
    {
        "name": "tradingview",
        "description": """
**TradingView集成模块 (OpenStock集成)**

TradingView图表组件集成。

**主要功能**:
- K线图表
- 技术指标叠加
- 自定义周期
- 图表样式配置
""",
    },
    {
        "name": "notification",
        "description": """
**通知模块 (OpenStock集成)**

提供邮件、短信等多渠道通知功能。

**通知渠道**:
- 邮件通知
- 短信通知
- 站内消息
- Webhook
""",
    },
    {
        "name": "technical-analysis",
        "description": """
**技术分析模块**

增强的技术分析功能。

**分析类型**:
- 形态识别
- 趋势分析
- 支撑阻力
- 量价分析
""",
    },
    {
        "name": "multi-source",
        "description": """
**多数据源模块**

整合多个数据源，提供统一的数据访问接口。

**数据源**:
- AKShare
- Baostock
- 东方财富
- 通达信
- Tushare
""",
    },
    {
        "name": "announcement",
        "description": """
**公告监控模块 (P2 API)**

提供上市公司公告的抓取、解析和监控功能。

**公告类型**:
- 定期报告: 季报、半年报、年报
- 临时公告: 重大事项、停复牌
- 股东变动: 增减持、质押解押

**主要功能**:
- 公告数据抓取和存储
- 智能重要性分级 (0-5级)
- 监控规则管理 (CRUD)
- 触发记录追踪
- AI分析集成 (待实现)

**监控特性**:
- 关键词匹配
- 重要性过滤
- 股票黑白名单
- 多渠道通知

**认证**: 部分接口需要认证
""",
    },
    {
        "name": "backtest",
        "description": """
**回测策略模块 (P1 API)**

提供策略管理、模型训练和回测执行功能。

**核心功能**:
- 策略CRUD操作: 创建、查询、更新、删除策略
- 模型训练: 启动训练、查询状态、获取模型列表
- 回测执行: 运行回测、获取结果、图表数据
- 实时推送: WebSocket回测进度推送

**主要特性**:
- 完整的策略生命周期管理
- 异步模型训练支持
- 详细的回测结果分析
- 实时进度推送

**认证**: 大部分接口需要认证
**速率限制**: 60/分钟
""",
    },
    {
        "name": "user",
        "description": """
**用户认证模块 (P1 API)**

提供用户认证、授权和会话管理功能。

**核心功能**:
- 用户登录/登出
- JWT Token管理 (访问令牌、刷新令牌)
- 用户信息查询
- CSRF保护

**安全特性**:
- JWT Token认证
- CSRF Token保护
- 用户权限管理
- 会话管理

**认证**: 需要认证（部分除外）
**速率限制**: 20/分钟 (登录接口)
""",
    },
    {
        "name": "trade",
        "description": """
**交易执行模块 (P1 API)**

提供交易执行、持仓管理和统计分析功能。

**核心功能**:
- 交易执行: 买入、卖出股票
- 持仓管理: 查询持仓、持仓详情
- 交易记录: 历史交易查询
- 统计分析: 交易统计、绩效分析
- 投资组合: 组合概览、资产分布

**主要特性**:
- 完整的交易流程支持
- 实时持仓更新
- 详细的交易统计
- 投资组合分析

**认证**: 需要认证
**速率限制**: 30/分钟 (交易接口)
""",
    },
    {
        "name": "technical",
        "description": """
**技术分析模块 (P1 API)**

提供技术指标计算和形态识别功能。

**核心功能**:
- 趋势指标: SMA, EMA, MACD等
- 动量指标: RSI, KDJ, CCI等
- 波动指标: BOLL, ATR等
- 成交量指标: OBV, VOL等
- 技术形态: 识别K线形态
- 交易信号: 买卖信号生成

**主要特性**:
- 支持50+种技术指标
- 批量指标计算
- 自动形态识别
- 智能信号生成

**认证**: 部分接口需要认证
**速率限制**: 60/分钟
""",
    },
    {
        "name": "dashboard",
        "description": """
**仪表盘模块 (P1 API)**

提供数据聚合和可视化仪表盘功能。

**核心功能**:
- 数据汇总: 多维度数据聚合
- 市场概览: 整体市场情况
- 自定义仪表盘: 个性化配置

**主要特性**:
- 实时数据更新
- 多维度展示
- 响应式布局

**认证**: 需要认证
**速率限制**: 30/分钟
""",
    },
    {
        "name": "data",
        "description": """
**数据服务模块 (P1 API)**

提供基础数据查询和检索功能。

**核心功能**:
- 股票基本信息: 代码、名称、行业
- 行业概念: 行业分类、概念板块
- 市场数据: K线、日线、分时
- 财务数据: 财报、财务指标
- 热门追踪: 热门行业、概念
- 搜索功能: 股票搜索、模糊查询

**主要特性**:
- 完整的基础数据覆盖
- 快速搜索和检索
- 实时数据更新

**认证**: 部分接口需要认证
**速率限制**: 60/分钟
""",
    },
    {
        "name": "sse",
        "description": """
**SSE推送模块 (P1 API)**

提供Server-Sent Events实时数据推送功能。

**核心功能**:
- 训练进度推送: 模型训练进度
- 回测进度推送: 回测执行进度
- 告警推送: 实时告警通知
- 仪表盘推送: 实时数据更新

**主要特性**:
- 单向实时推送
- 自动重连机制
- 事件流格式
- 低延迟传输

**认证**: 需要认证
**速率限制**: N/A (流式推送)
""",
    },
    {
        "name": "tasks",
        "description": """
**任务管理模块 (P1 API)**

提供异步任务管理和执行功能。

**核心功能**:
- 任务注册: 创建和管理任务
- 任务控制: 启动、停止任务
- 执行记录: 查询执行历史
- 统计分析: 任务统计信息
- 审计日志: 操作日志记录
- 导入导出: 批量任务管理

**主要特性**:
- 完整的任务生命周期管理
- 异步执行支持
- 详细的执行记录
- 审计和监控

**认证**: 需要认证
**速率限制**: 30/分钟
""",
    },
    {
        "name": "market",
        "description": """
**市场数据模块 (P1 API)**

提供全面的市场数据获取和实时行情查询功能。

**核心功能**:
- 资金流向: 个股、行业、概念资金流向数据
- ETF数据: ETF列表、查询、刷新
- 龙虎榜: 龙虎榜数据查询和刷新
- 竞价抢筹: 竞价抢筹数据
- 实时行情: 股票实时报价
- K线数据: 日线、周线、月线K线
- 热力图: 市场热力图数据
- 分红配送: 股票分红配送数据
- 大宗交易: 大宗交易数据

**主要特性**:
- Market v1/v2双版本支持
- 实时数据刷新机制
- 批量数据刷新
- 缓存优化
- 东方财富数据源集成

**认证**: 部分接口需要认证
**速率限制**: 60/分钟
""",
    },
]

# ==================== 安全方案 ====================

SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Token认证。在请求头中添加: `Authorization: Bearer <token>`",
    },
    "CSRFToken": {
        "type": "apiKey",
        "in": "header",
        "name": "X-CSRF-Token",
        "description": "CSRF Token保护。所有修改操作(POST/PUT/PATCH/DELETE)需要在请求头中添加: `X-CSRF-Token: <token>`",
    },
}

# ==================== 通用响应示例 ====================

COMMON_RESPONSES = {
    200: {
        "description": "请求成功",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "操作成功",
                    "data": {"result": "示例数据"},
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    400: {
        "description": "请求参数错误",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "参数验证失败",
                    "error_code": "INVALID_PARAMETER",
                    "details": {"field": "symbol", "reason": "格式不正确"},
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    401: {
        "description": "未授权 - 需要登录",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "未授权访问",
                    "error_code": "UNAUTHORIZED",
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    403: {
        "description": "禁止访问 - CSRF Token无效或权限不足",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "权限不足或CSRF验证失败",
                    "error_code": "FORBIDDEN",
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    404: {
        "description": "资源不存在",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "请求的资源不存在",
                    "error_code": "RESOURCE_NOT_FOUND",
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    422: {
        "description": "数据验证失败",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "数据验证失败",
                    "error_code": "VALIDATION_ERROR",
                    "details": [
                        {
                            "loc": ["body", "symbol"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ],
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
    500: {
        "description": "服务器内部错误",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "服务器内部错误，请稍后重试",
                    "error_code": "INTERNAL_ERROR",
                    "timestamp": "2025-11-06T12:34:56.789Z",
                }
            }
        },
    },
}


def get_openapi_config() -> Dict[str, Any]:
    """
    获取OpenAPI配置

    Returns:
        OpenAPI配置字典，用于FastAPI app初始化
    """
    return {
        **API_METADATA,
        "openapi_tags": OPENAPI_TAGS,
        "swagger_ui_parameters": {
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "monokai",
            # 使用国内可访问的 CDN 镜像（解决 cdn.jsdelivr.net 被墙问题）
            "swagger_js_url": "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.0/swagger-ui-bundle.js",
            "swagger_css_url": "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.0/swagger-ui.css",
        },
        "swagger_ui_oauth2_redirect_url": "/api/docs/oauth2-redirect",
    }


def get_openapi_schema_extra() -> Dict[str, Any]:
    """
    获取OpenAPI Schema扩展配置

    Returns:
        OpenAPI Schema扩展配置（servers, security等）
    """
    return {
        "servers": [
            {"url": "http://localhost:8000", "description": "本地开发环境"},
            {"url": "http://127.0.0.1:8000", "description": "本地开发环境 (127.0.0.1)"},
            {
                "url": "https://api.mystocks.com",
                "description": "生产环境 (需要HTTPS)",
            },
        ],
        "components": {
            "securitySchemes": SECURITY_SCHEMES,
            "responses": COMMON_RESPONSES,
        },
        "security": [
            {"BearerAuth": []},  # 默认需要JWT Token
            {"CSRFToken": []},  # 修改操作需要CSRF Token
        ],
    }
