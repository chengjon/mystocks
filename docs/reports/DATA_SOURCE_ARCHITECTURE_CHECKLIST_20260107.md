# 数据源集中管理架构检查清单

> **生成日期**: 2026-01-07
> **版本**: v2.0
> **用途**: 验证数据源管理架构的完整性和正确性

---

## 📊 架构概览

MyStocks 数据源管理 V2.0 采用**四层架构**实现集中式治理：

```
┌─────────────────────────────────────────────────────────────┐
│              接口层 (Interface Layer)                       │
│  FastAPI RESTful API  +  手动测试工具                       │
├─────────────────────────────────────────────────────────────┤
│              核心管理层 (Core Management)                    │
│  DataSourceManagerV2  (注册/路由/健康检查/监控)             │
├─────────────────────────────────────────────────────────────┤
│              适配器层 (Adapter Layer)                        │
│  7个数据源适配器 (akshare/tushare/tdx/baostock/...)        │
├─────────────────────────────────────────────────────────────┤
│              存储层 (Storage Layer)                          │
│  PostgreSQL注册表  +  YAML配置文件                         │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ 检查清单

### 1. 配置层 (Configuration Layer)

#### 1.1 YAML配置文件
- [ ] **文件位置**: `config/data_sources_registry.yaml`
- [ ] **版本**: v2.0
- [ ] **配置项**:
  - [ ] 版本号 (`version: "2.0"`)
  - [ ] 最后更新时间 (`last_updated`)
  - [ ] 数据源列表 (`data_sources`)
- [ ] **数据源配置**:
  - [ ] 基础信息 (source_name, source_type, endpoint_name)
  - [ ] 数据分类 (data_category, classification_level)
  - [ ] 目标数据库 (target_db, table_name)
  - [ ] 参数定义 (parameters - JSON Schema格式)
  - [ ] 测试参数 (test_parameters)
  - [ ] 数据源特定配置 (source_config)
  - [ ] 质量规则 (quality_rules)
- [ ] **已注册数据源数量**:
  - [ ] Mock数据源: 1个
  - [ ] AKShare: 2个 (日线K线、股票基本信息)
  - [ ] TuShare: 2个 (日线K线、财务数据)
  - [ ] 通达信: 1个 (实时行情)
  - [ ] 总计: 至少6个数据源

#### 1.2 PostgreSQL持久化
- [ ] **数据库**: PostgreSQL (`mystocks`)
- [ ] **表名**: `data_source_registry`
- [ ] **表结构**:
  - [ ] 基础信息字段 (id, source_name, source_type, endpoint_name)
  - [ ] 调用信息字段 (call_method, endpoint_url, parameters, response_format)
  - [ ] 分类与路由字段 (data_category, target_db, table_name)
  - [ ] 监控指标字段 (last_success_time, avg_response_time, success_rate)
  - [ ] 数据质量字段 (data_freshness, health_status)
- [ ] **索引**:
  - [ ] idx_dsr_category (data_category)
  - [ ] idx_dsr_status (status, health_status)
  - [ ] idx_dsr_quality_score (data_quality_score DESC, priority ASC)
- [ ] **触发器**: update_data_source_registry_updated_at
- [ ] **调用历史表**: `data_source_call_history`
  - [ ] 记录每次API调用
  - [ ] 存储响应时间和错误信息

---

### 2. 核心管理层 (Core Management Layer)

#### 2.1 DataSourceManagerV2 主类
- [ ] **文件位置**: `src/core/data_source_manager_v2.py`
- [ ] **架构**: 重构为8个子模块（最大176行）
- [ ] **向后兼容**: 通过 `__init__.py` 重新导出
- [ ] **子模块**:
  - [ ] `base.py` - 基类和初始化逻辑
  - [ ] `registry.py` - 数据源注册（从数据库和YAML加载）
  - [ ] `router.py` - 数据源路由（查找最佳endpoint）
  - [ ] `handler.py` - 数据调用处理（各种API handler）
  - [ ] `monitoring.py` - 监控记录（成功/失败记录、调用历史）
  - [ ] `health_check.py` - 健康检查（单个和批量endpoint检查）
  - [ ] `validation.py` - 数据验证
  - [ ] `cache.py` - LRUCache类

#### 2.2 核心功能模块
- [ ] **数据源注册** (`registry.py`)
  - [ ] 从YAML加载配置
  - [ ] 从PostgreSQL加载配置
  - [ ] 配置合并策略
  - [ ] 参数验证

- [ ] **智能路由** (`router.py`)
  - [ ] 基于数据分类查找endpoint
  - [ ] 按优先级排序
  - [ ] 按健康状态过滤
  - [ ] 负载均衡策略

- [ ] **健康检查** (`health.py`)
  - [ ] 单个endpoint检查
  - [ ] 批量endpoint检查
  - [ ] 健康状态更新
  - [ ] 自动告警

- [ ] **监控记录** (`monitoring.py`)
  - [ ] 成功调用记录
  - [ ] 失败调用记录
  - [ ] 响应时间统计
  - [ ] 调用历史查询

- [ ] **数据验证** (`validation.py`)
  - [ ] 参数验证
  - [ ] 响应数据验证
  - [ ] 质量规则检查
  - [ ] 数据类型检查

- [ ] **缓存管理** (`cache.py`)
  - [ ] LRU缓存实现
  - [ ] 缓存过期策略
  - [ ] 缓存命中率统计

---

### 3. 接口层 (Interface Layer)

#### 3.1 FastAPI管理接口
- [ ] **文件位置**: `web/backend/app/api/data_source_registry.py`
- [ ] **路由前缀**: `/api/v1/data-sources`
- [ ] **API端点**:
  - [ ] `GET /search` - 搜索数据源接口
  - [ ] `GET /category-stats` - 获取分类统计
  - [ ] `PUT /{endpoint_name}` - 更新数据源配置
  - [ ] `POST /test` - 手动测试数据源
  - [ ] `GET /health` - 健康检查
  - [ ] `GET /categories` - 获取所有分类
  - [ ] `GET /{endpoint_name}` - 获取单个数据源详情
- [ ] **Pydantic模型**:
  - [ ] DataSourceSearchResponse
  - [ ] CategoryStatsResponse
  - [ ] DataSourceUpdate
  - [ ] TestRequest
  - [ ] TestResponse
- [ ] **CORS配置**: 已配置允许前端访问

#### 3.2 手动测试工具
- [ ] **文件位置**: `scripts/tools/manual_data_source_tester.py`
- [ ] **运行模式**:
  - [ ] 交互式模式 (`--interactive`)
  - [ ] 命令行模式 (`--endpoint`, `--symbol`, `--start-date`, `--end-date`)
- [ ] **功能**:
  - [ ] 数据源接口测试
  - [ ] 数据质量分析
  - [ ] 完整性检查
  - [ ] 范围检查
  - [ ] 格式验证
  - [ ] 测试报告生成
- [ ] **输出**:
  - [ ] 接口配置信息
  - [ ] 测试参数
  - [ ] 响应时间
  - [ ] 数据量统计
  - [ ] 数据预览
  - [ ] 质量分析结果

---

### 4. 适配器层 (Adapter Layer)

#### 4.1 数据源适配器
- [ ] **位置**: `src/adapters/`
- [ ] **统一接口**: `IDataSource` (定义于 `src/interfaces/data_source.py`)
- [ ] **已实现适配器** (7个):
  - [ ] `AkshareDataSource` - AKShare中国市场数据
  - [ ] `BaostockDataSource` - Baostock历史数据
  - [ ] `FinancialDataSource` - 财务报表和基本面数据
  - [ ] `TdxDataSource` - 通达信直连数据源
  - [ ] `ByapiDataSource` - REST API数据源
  - [ ] `CustomerDataSource` - 实时行情数据源
  - [ ] `TushareDataSource` - Tushare专业数据源
- [ ] **适配器功能**:
  - [ ] 数据获取
  - [ ] 错误处理
  - [ ] 重试机制
  - [ ] 数据转换
  - [ ] 日志记录

#### 4.2 数据源管理器 (适配器层)
- [ ] **文件位置**: `src/adapters/data_source_manager.py`
- [ ] **功能**:
  - [ ] 适配器实例管理
  - [ ] 适配器选择逻辑
  - [ ] 统一调用接口
  - [ ] 结果合并

---

### 5. 数据分类体系

#### 5.1 五层数据分类
- [ ] **1层**: market_data (市场数据)
  - [ ] DAILY_KLINE (日线K线)
  - [ ] MINUTE_KLINE (分钟K线)
  - [ ] TICK_DATA (tick数据)
  - [ ] REALTIME_QUOTE (实时行情)
- [ ] **2层**: reference_data (参考数据)
  - [ ] SYMBOLS_INFO (股票基本信息)
  - [ ] FINANCIAL_DATA (财务数据)
  - [ ] CALENDAR_DATA (日历数据)
- [ ] **3层**: derived_data (衍生数据)
  - [ ] TECHNICAL_INDICATORS (技术指标)
  - [ ] FACTOR_DATA (因子数据)
- [ ] **4层**: transaction_data (交易数据)
  - [ ] ORDER_DATA (订单数据)
  - [ ] POSITION_DATA (持仓数据)
- [ ] **5层**: metadata (元数据)
  - [ ] CONFIGURATION (配置数据)
  - [ ] LOGGING (日志数据)

#### 5.2 数据源类型
- [ ] **api_library**: API库 (akshare, tushare)
- [ ] **database**: 数据库 (tdx)
- [ ] **crawler**: 爬虫
- [ ] **file**: 文件
- [ ] **mock**: 模拟数据

#### 5.3 调用方式
- [ ] **function_call**: 函数调用
- [ ] **http**: HTTP GET请求
- [ ] **post**: HTTP POST请求
- [ ] **tcp**: TCP连接

---

### 6. 监控与质量保证

#### 6.1 监控指标
- [ ] **性能指标**:
  - [ ] avg_response_time (平均响应时间)
  - [ ] success_rate (成功率)
  - [ ] total_calls (总调用次数)
  - [ ] failed_calls (失败调用次数)
- [ ] **质量指标**:
  - [ ] data_quality_score (数据质量评分 0-10)
  - [ ] health_status (健康状态: healthy/degraded/failed/unknown)
  - [ ] data_freshness (数据新鲜度)
  - [ ] consecutive_failures (连续失败次数)
- [ ] **额度管理**:
  - [ ] quota_used (已使用额度)
  - [ ] quota_limit (额度上限)

#### 6.2 质量验证规则
- [ ] **完整性检查**:
  - [ ] min_record_count (最小记录数)
  - [ ] required_columns (必需列)
  - [ ] required_fields (必需字段)
- [ ] **性能检查**:
  - [ ] max_response_time (最大响应时间)
- [ ] **类型检查**:
  - [ ] data_types (列数据类型定义)
- [ ] **格式验证**:
  - [ ] pattern (正则表达式验证)
  - [ ] format (日期格式等)

---

### 7. 集成与部署

#### 7.1 环境配置
- [ ] **数据库连接**:
  - [ ] POSTGRESQL_HOST
  - [ ] POSTGRESQL_PORT
  - [ ] POSTGRESQL_USER
  - [ ] POSTGRESQL_PASSWORD
  - [ ] POSTGRESQL_DATABASE
- [ ] **外部API密钥**:
  - [ ] TUSHARE_TOKEN (TuShare API)
- [ ] **监控配置**:
  - [ ] MONITOR_DB_URL (监控数据库连接)

#### 7.2 导入路径
- [ ] **核心管理器**:
  ```python
  from src.core.data_source_manager_v2 import DataSourceManagerV2
  from src.core.data_source import DataSourceManagerV2  # 推荐
  ```
- [ ] **API接口**:
  ```python
  from web.backend.app.api.data_source_registry import router
  ```
- [ ] **测试工具**:
  ```python
  from scripts.tools.manual_data_source_tester import DataSourceTester
  ```

#### 7.3 依赖项
- [ ] **核心依赖**:
  - [ ] fastapi >= 0.114.0
  - [ ] pydantic >= 2.0
  - [ ] psycopg2-binary (PostgreSQL驱动)
  - [ ] pyyaml (YAML解析)
  - [ ] pandas (数据处理)
- [ ] **数据源依赖**:
  - [ ] akshare (AKShare数据源)
  - [ ] tushare (TuShare数据源)
  - [ ] baostock (Baostock数据源)
  - [ ] pytdx (通达信数据源)

---

## 📋 架构验证结果

### ✅ 已验证组件

| 组件 | 状态 | 备注 |
|------|------|------|
| YAML配置文件 | ✅ | `config/data_sources_registry.yaml` 已存在 |
| PostgreSQL表结构 | ✅ | `data_source_registry` 和 `data_source_call_history` |
| 核心管理器 | ✅ | `DataSourceManagerV2` 已重构为8个子模块 |
| FastAPI接口 | ✅ | 7个RESTful API端点 |
| 手动测试工具 | ✅ | 支持交互式和命令行模式 |
| 数据源适配器 | ✅ | 7个适配器已实现 |
| 数据分类体系 | ✅ | 5层分类 + 34个数据类别 |

### 🔍 待验证项

| 项目 | 状态 | 验证方法 |
|------|------|----------|
| PostgreSQL数据同步 | ⏳ | 运行YAML到数据库的同步脚本 |
| 实际API调用测试 | ⏳ | 使用测试工具测试每个数据源 |
| 健康检查自动化 | ⏳ | 配置定时健康检查任务 |
| 监控仪表板 | ⏳ | 配置Grafana仪表板 |

---

## 📚 相关文档

- **架构设计**: `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md`
- **使用指南**: `docs/guides/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`
- **快速参考**: `docs/guides/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md`
- **验证报告**: `docs/reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md`
- **增强提案**: `docs/reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md`

---

## 🎯 下一步行动

1. **完成数据库同步**: 将YAML配置同步到PostgreSQL
2. **执行全面测试**: 测试所有已注册的数据源端点
3. **配置监控告警**: 设置健康检查和告警规则
4. **优化性能**: 根据监控数据优化路由策略
5. **完善文档**: 补充API文档和使用示例

---

**检查人**: Claude Code (Main CLI)
**检查日期**: 2026-01-07
**架构版本**: v2.0
**状态**: ✅ 架构完整，待部署验证
