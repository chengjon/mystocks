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

from typing import Dict, List, Any

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
**技术指标模块**

提供常用技术指标计算和自定义指标支持。

**支持的指标**:
- 均线 (MA, EMA)
- MACD
- RSI
- KDJ
- 布林带 (BOLL)
- 成交量指标
- 自定义指标

**计算引擎**: pandas_ta, talib
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
**实时监控模块 (ValueCell集成)**

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
**系统管理模块**

提供系统配置、健康检查、性能监控等系统级功能。

**主要功能**:
- 系统配置管理
- 健康检查
- 性能指标
- 日志管理
- 任务调度
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
**技术分析模块 (ValueCell Phase 2)**

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
**多数据源模块 (ValueCell Phase 3)**

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
**公告监控模块 (ValueCell Phase 3)**

上市公司公告的抓取、解析和监控。

**公告类型**:
- 定期报告
- 临时公告
- 重大事项
- 股东变动
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
