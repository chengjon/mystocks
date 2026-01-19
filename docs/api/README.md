# MyStocks API 文档中心

**📅 最新更新**: 2026-01-19 API文档重新评估和修正
- ✅ **基于实际代码审计**: 571个API端点，54个API文件，反映真实项目状态
- ✅ **核心文档优先级调整**: 突出API契约管理、集成指南、端点分析三个核心文档
- ✅ **降低实验性功能权重**: APIFOX等尝试性功能移至次要位置
- ✅ **架构重新评估**: 完整FastAPI后端系统，多种数据源集成，无实质性APIFOX依赖

---

## 🎯 核心文档优先级

### 🔥 一级核心文档（必须阅读）

#### 1. **API契约管理架构** 📋
**位置**: `docs/api/API_CONTRACT_ARCHITECTURE_ANALYSIS.md`
**重要性**: ⭐⭐⭐⭐⭐ 最高优先级
**内容**: API契约生态系统、同步机制、版本管理、企业级应用

#### 2. **API集成指南** 🔌
**位置**: `docs/guides/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
**重要性**: ⭐⭐⭐⭐⭐ 最高优先级
**内容**: 数据源集成、适配器模式、强制性开发要求、BUG案例分析

#### 3. **API端点统计分析** 📊
**位置**: `docs/api/API_ENDPOINTS_STATISTICS_REPORT.md`
**重要性**: ⭐⭐⭐⭐⭐ 最高优先级
**内容**: 571个端点分析、功能分类、HTTP方法分布、性能统计

---

## 📚 文档导航

### 🚀 快速开始

#### 系统架构概览
MyStocks采用**双数据库架构** + **多数据源集成**的完整量化交易系统：

```
前端 (Vue 3) ←→ 后端 (FastAPI 571个API) ←→ 数据源 (7个适配器)
                           ↓
数据库: TDengine (时序) + PostgreSQL (结构化) + Redis (缓存)
```

#### 核心架构特性

**🎯 双数据库分工**:
- **TDengine**: 高频时序数据（Tick/分钟K线，20:1压缩比，极致写入性能）
- **PostgreSQL**: 结构化数据（股票信息、交易记录、技术指标、元数据）
- **Redis**: 缓存层（热点数据、会话管理）

**🔧 适配器模式**: 7个核心数据源适配器统一接口，支持动态切换和故障转移

**📊 智能路由**: 根据数据分类自动选择最优存储引擎

**🔐 企业级安全**: JWT认证、CSRF保护、API合规性验证

#### 启动完整系统
```bash
# 一键启动所有服务
./run_platform.sh

# 或手动启动
# 1. 数据库: docker run -d tdengine/tdengine:3.0.4.0
# 2. 后端: cd web/backend && uvicorn app.main:app --port 8000
# 3. 前端: cd web/frontend && npm run dev --port 3000
```

**访问地址**:
- 🌐 前端界面: http://localhost:3000
- 🔧 API文档: http://localhost:8000/docs
- 📊 健康检查: http://localhost:8000/health
- **[Swagger UI 指南](SWAGGER_UI_GUIDE.md)** - 本地 Swagger UI 使用

### 🔗 API-Web 对齐集成 🆕
- **[API集成优化计划](guides/integration/api_integration_optimization_plan.md)** - 4阶段优化实施方案（2025-12-25）
- **[API集成实施状态](guides/integration/api_integration_implementation_status.md)** - Phase 1-2 实施进度报告（50%完成）
- **[API验收标准](testing/compliance/api_acceptance_standards.md)** - 完整的4层验收体系（E2E/UX/运维）🆕
- **[Phase 2 完成报告](reports/milestones/PHASE2_COMPLETION_REPORT.md)** - 策略管理模块完整实施报告
- **[前后端API对齐方案](../guides/API对齐方案.md)** - 完整的对齐策略和方法论
- **[前后端API对齐核心流程](../guides/API对齐核心流程.md)** - 数据对接与控件对齐核心流程



### 🔧 API 开发指南
- **[API 开发标准指南](guides/development/api_development_guidelines.md)** - REST API开发标准和最佳实践 🆕
- **[API 开发检查清单](guides/development/api_development_checklist.md)** - 开发过程中的质量检查清单 🆕
- **[API 快速开始模板](guides/development/api_quick_start_template.md)** - 5分钟创建新API端点的模板 🆕
- **[API 端点统计](reports/analysis/api_endpoints_statistics_report.md)** - 完整的571个API端点分析

### 🧪 API 合规性测试
- **[API 合规性测试框架](testing/compliance/api_compliance_testing_framework.md)** - 完整的自动化测试框架 (1,200+ LOC) 🆕
- **[API 合规性报告](testing/compliance/api_compliance_report.md)** - 详细的合规性分析和改进建议 🆕
- **[API 合规性改进建议](testing/compliance/api_compliance_improvements.md)** - 具体的代码改进示例和最佳实践 🆕
- **[API 合规性测试完成报告](reports/milestones/api_compliance_test_completion_report.md)** - 测试框架部署和验证结果 🆕
- **[Phase 4 完成报告](reports/milestones/phase4_completion_report.md)** - API企业级安全优化完成报告 🆕

#### 🔧 合规性测试快速开始
```bash
# 一键设置合规性测试环境
./setup_compliance_testing.sh

# 运行所有合规性测试
./run_compliance_tests.sh

# 生成合规性报告
./generate_compliance_report.sh
```
**测试内容**: API合规性、静态代码分析、文档验证、性能安全测试

### 📖 API 参考
- **[OpenAPI 规范 (JSON)](openapi.json)** - OpenAPI 3.1.0 格式
- **[OpenAPI 规范 (YAML)](openapi.yaml)** - YAML 格式
- **[API 前端映射](guides/integration/api_frontend_mapping.md)** - 前端组件与API的对应关系

### 🗂️ 任务完成总结

#### 任务 14: 性能优化 (Task 14 - Performance Optimization) ✅ COMPLETE

##### 任务 14.1: Locust 压测脚本 ✅
- **[压测快速参考](LOAD_TEST_QUICK_REFERENCE.md)** - 4种压测场景和常用命令
  - 基准测试 (100用户, 5分钟)
  - 正常负载 (500用户, 10分钟)
  - 高峰负载 (1000用户, 10分钟)
  - 压力测试 (2000用户, 15分钟)
- **[压测完整指南](LOAD_TESTING_GUIDE.md)** - 1,766 LOC 压测框架
  - 5种用户角色建模
  - 24小时流量模型
  - 性能指标和优化建议

##### 任务 14.2: WebSocket 性能优化 ✅
- **[WebSocket 优化指南](WEBSOCKET_OPTIMIZATION_GUIDE.md)** - 完整的WebSocket性能优化系统
  - 连接池管理 (Min/Max 连接数, 自动清理)
  - 消息批处理 (10:1 压缩比, < 50ms 延迟)
  - 内存优化 (4级压力监控, 自动GC)
  - 性能管理集成 (统一API, 综合监控)
  - **代码行数**: 1,475 LOC 优化框架
  - **性能提升**: 2倍并发, 2倍吞吐量, 50% 内存占用

##### 任务 14.3: 数据库性能优化 ✅
- **[数据库优化指南](DATABASE_OPTIMIZATION_GUIDE.md)** - 完整的数据库性能优化系统
  - 连接池优化 (20-100连接, 95%复用率)
  - 查询批处理 (1000行/批, 2倍吞吐量)
  - 性能监控 (慢查询检测, 自动告警)
  - 性能管理集成 (统一API, 综合监控)
  - **代码行数**: 1,650 LOC 优化框架
  - **性能提升**: 95%连接复用, 2倍批处理, 50%查询延迟

#### 任务 14 完成总结 ✅ COMPLETE
- **[Task 14 完成总结](TASK_14_COMPLETION_SUMMARY.md)** - 性能优化三阶段完整报告
  - 压测脚本 + WebSocket优化 + 数据库优化
  - 4,891 LOC 性能优化代码
  - 2,500+ LOC 详细文档
  - 2-4倍 性能提升
  - 95%+ 系统可靠性

#### 任务 15: 告警升级机制 (Task 15 - Alert Escalation Mechanism) ✅ COMPLETE
- **[任务15完成总结](TASK_15_COMPLETION_SUMMARY.md)** - 多级告警升级和管理系统的完整报告
  - 4个核心模块完整实现
  - 13+ REST API 分析端点
  - 1,100+ 行生产代码，2,300+ 行文档
  - 企业级告警路由、聚合和通知系统

- **[15.1 多级告警规则设计](TASK_15_ALERT_ESCALATION_DESIGN.md)** - 三层告警体系与升级逻辑
  - L1 Critical (严重)、L2 Warning (警告)、L3 Info (信息) 告警分类
  - 自动升级规则和时间阈值
  - 40+ 告警完整映射表
  - 根因分析提示和路由矩阵

- **[15.2 告警聚合和抑制](TASK_15_ALERT_AGGREGATION_SUPPRESSION.md)** - 告警聚合引擎
  - 时间窗口聚合 (0s/30s/60s)
  - 基于标签的分组和关联分组
  - 父子抑制规则 (根因抑制症状)
  - AlertManager 完整配置示例

- **[15.3 告警通知系统](TASK_15_ALERT_NOTIFICATION_SYSTEM.md)** - 多渠道通知实现
  - Email (SMTP)、Slack、SMS (Twilio)、Webhooks、PagerDuty
  - 异步并发投递和指数退避重试
  - SQLite 通知历史数据库
  - 完整的集成示例和测试工具

- **[15.4 告警历史和统计](TASK_15_ALERT_HISTORY_ANALYTICS.md)** - 告警分析数据库层
  - 完整的告警生命周期追踪
  - 13+ REST API 分析端点
  - 服务健康评分 (0-100)
  - 告警相关性检测和趋势分析

#### 任务 13: 监控和告警系统 (Task 13 - Monitoring & Alerting)
- **[任务13完成总结](TASK_13_COMPLETION_SUMMARY.md)** - 监控与告警系统实现的完成报告
  - 40+ 自定义监控指标定义
  - Prometheus Exporter 完整实现
  - Grafana 仪表板（18 个面板）
  - 40+ 告警规则配置

#### 任务 12: 契约测试框架 (Task 12 - Contract Testing)
- **[任务12完成总结](TASK_12_COMPLETION_SUMMARY.md)** - 契约测试框架实现的完成报告
  - 5个核心模块实现
  - 29个单元测试（100%通过）
  - GitHub Actions CI/CD集成
  - 完整的API参考和框架指南

#### 任务 11: 数据库索引优化 (Task 11 - Database Optimization)
- **[任务11完成总结](TASK_11_COMPLETION_SUMMARY.md)** - 数据库索引优化任务的完成报告
  - 数据库索引优化策略和性能基准: [DATABASE_INDEX_OPTIMIZATION_REPORT.md](DATABASE_INDEX_OPTIMIZATION_REPORT.md)
  - 实现索引导航: [IMPLEMENTATION_INDEX.md](IMPLEMENTATION_INDEX.md)

### 🧪 契约测试框架
- **[契约测试 API 参考](CONTRACT_TESTING_API.md)** - 完整的 API 文档和 SDK 使用指南
- **[契约测试框架指南](../guides/CONTRACT_TESTING_GUIDE.md)** - 框架使用教程和最佳实践

### 📊 监控与告警 (Task 13)
- **[监控指标定义](MONITORING_METRICS_DEFINITION.md)** - 40+ 自定义监控指标的完整规范
  - 业务指标 (市场数据、用户行为、交易)
  - 技术指标 (API、WebSocket、缓存、数据库)
  - 告警指标 (系统健康、依赖可用性)
- **[告警规则配置指南](ALERTING_CONFIGURATION_GUIDE.md)** - 告警规则、通知渠道和响应流程
  - 40+ 告警规则跨 9 个类别
  - Slack/PagerDuty/Email 多渠道通知
  - 告警路由和抑制规则
  - 响应工作流和 SLA

### 🔌 Prometheus & Grafana 集成
- **Prometheus 配置**: `config/prometheus.yml` - 15 个采集任务配置
- **Grafana 仪表板**: `grafana_dashboard.json` - 18 个监控面板
- **AlertManager 配置**: `config/alertmanager.yml` - 多渠道告警路由
- **告警规则**: `config/alerts/mystocks-alerts.yml` - 40+ 告警规则

---

## 🌐 在线访问



### 本地 Swagger UI
**Swagger UI**: http://localhost:8000/api/docs
**ReDoc**: http://localhost:8000/api/redoc
**OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📊 API 概览

### 主要功能模块

1. **系统管理** - 健康检查、系统信息、Socket.IO状态
2. **认证授权** - JWT Token 认证、CSRF 保护
3. **市场数据** - 实时行情、K线、资金流向、筹码分布
4. **市场数据 V2** - 批量行情、板块分析、市场概览
5. **市场数据 V3** - 行业资金流向（申万、证监会分类）
6. **股票搜索** - 智能搜索、股票详情
7. **自选股管理** - 添加、删除、查询自选股
8. **问财接口** - 自然语言查询
9. **缓存管理** - 统计、清理、预热
10. **策略管理** - 策略创建、回测、绩效
11. **指标数据** - 系统指标、市场指标
12. **通知管理** - 推送通知、告警
13. **通达信接口** - TDX 数据源
14. **任务管理** - 异步任务执行
15. **监控管理** - 性能监控、健康检查

### API 统计

- **总端点数**: 571（基于实际代码审计）
- **数据模型**: 96
- **API 文件**: 54个
- **认证方式**: JWT Bearer Token + CSRF
- **API 版本**: 2.0.0
- **OpenAPI 版本**: 3.1.0

---

## 🔧 工具和脚本

### 文档导出工具

**从运行中的服务导出**:

```bash
# 导出 OpenAPI 规范
curl http://localhost:8000/openapi.json > openapi.json
curl http://localhost:8000/openapi.yaml > openapi.yaml

# 查看 Swagger UI
open http://localhost:8000/docs

# 查看 ReDoc
open http://localhost:8000/redoc
```

### 同步脚本

当 API 有更新时，从运行中的服务重新导出：

```bash
# 导出最新规范
curl http://localhost:8000/openapi.json > docs/api/openapi.json
curl http://localhost:8000/openapi.yaml > docs/api/openapi.yaml
```

---

## 🎯 常用操作

### 测试单个 API

**使用 curl**:
```bash
# 健康检查
curl http://localhost:8000/health

# 获取实时行情（需要认证）
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/market/realtime/000001
```

**使用 Swagger UI**:
1. 访问 http://localhost:8000/docs
2. 选择 API 端点
3. 填写参数并执行

### 批量测试

**使用测试脚本**:
1. 运行合规性测试: `./run_compliance_tests.sh`
2. 查看测试报告: `docs/api/testing/compliance/`
3. 运行端到端测试: `npm run test:e2e`

### 生成客户端代码

**使用 OpenAPI 生成器**:
```bash
# 生成 Python 客户端
openapi-generator generate -i openapi.json -g python -o client/python

# 生成 TypeScript 客户端
openapi-generator generate -i openapi.json -g typescript -o client/typescript
```

### 导出文档

**导出文档**:
```bash
# Markdown 格式
curl http://localhost:8000/openapi.json | jq . > api_spec.json

# HTML 文档
redoc-cli bundle openapi.json --output docs/api/index.html
```

---

## 🔐 认证流程

### 步骤1: 获取 CSRF Token

```http
GET /api/auth/csrf-token
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "abc123..."
  }
}
```

### 步骤2: 登录获取 JWT Token

```http
POST /api/auth/login
Content-Type: application/json
X-CSRF-Token: abc123...

{
  "username": "admin",
  "password": "your_password"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 步骤3: 使用 Token 调用 API

```http
GET /api/market/realtime/000001
Authorization: Bearer eyJhbGc...
```

---

## 📝 开发建议

### 1. 使用环境变量

配置环境变量：

```json
{
  "base_url": "http://localhost:8000",
  "auth_token": "{{auto_generated}}",
  "csrf_token": "{{auto_generated}}"
}
```

### 2. 自动化认证

在环境的 **前置脚本** 中添加自动登录逻辑。

### 3. Mock 数据开发

前端开发时可以使用本地 Mock 服务或测试数据，无需等待后端完成。

### 4. API 文档同步

API 变更后重新导出文档：
```bash
curl http://localhost:8000/openapi.json > docs/api/openapi.json
```

### 5. 持续集成

在 CI/CD 中集成 API 测试：
```bash
# 运行合规性测试
./run_compliance_tests.sh

# 运行端到端测试
npm run test:e2e
```

---

## 🐛 故障排查

### 问题1: 401 未授权

**原因**: 未提供有效的 JWT Token

**解决方案**:
1. 先调用 `/api/auth/login` 获取 token
2. 在请求头中添加 `Authorization: Bearer {token}`

### 问题2: 403 CSRF 验证失败

**原因**: 未提供 CSRF Token 或 Token 无效

**解决方案**:
1. 调用 `/api/auth/csrf-token` 获取新 token
2. 在请求头中添加 `X-CSRF-Token: {csrf_token}`

### 问题3: 404 Not Found

**原因**: API 路径错误或服务未启动

**解决方案**:
1. 检查 API 路径是否正确
2. 确认后端服务正在运行: `curl http://localhost:8000/health`

### 问题4: 500 服务器错误

**原因**: 服务器内部错误

**解决方案**:
1. 检查服务器日志
2. 验证请求参数格式
3. 检查数据库连接

---

## 📞 获取帮助

### 文档资源
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### MyStocks 项目
- **GitHub**: [项目仓库]
- **技术栈**: FastAPI + TDengine + PostgreSQL
- **架构文档**: `../../CLAUDE.md`

---

## 🎉 下一步

1. ✅ **访问 Swagger UI**: http://localhost:8000/docs
2. ✅ **查看 API 规范**: http://localhost:8000/openapi.json
3. ✅ **测试核心 API**: 从健康检查开始
4. ✅ **配置认证**: 设置自动登录脚本
5. ✅ **创建测试套件**: 自动化测试
6. ✅ **使用 Mock 服务**: 加速前端开发

---

**最后更新**: 2026-01-19 12:00 UTC
**文档版本**: 2.4.0
**API 端点**: 571（基于实际代码审计修正）
**数据模型**: 96
**API 文件**: 54个
**API合规性**: 97% (企业级标准)
**核心修正**: 去除实验性功能权重，突出真实架构

_开始您的 API 探索之旅！_ 🚀
