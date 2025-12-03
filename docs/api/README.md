# MyStocks API 文档中心

## 📚 文档导航

### 🚀 快速开始
- **[Apifox 快速开始](APIFOX_QUICK_START.md)** - 5分钟上手 Apifox
- **[API 使用指南](API_GUIDE.md)** - 完整的 API 使用教程
- **[API 使用示例和最佳实践](API_EXAMPLES.md)** - 详细的代码示例、常见场景和客户端SDK 🆕
- **[Swagger UI 指南](SWAGGER_UI_GUIDE.md)** - 本地 Swagger UI 使用

### 📋 导入指南
- **[Apifox 导入指南](APIFOX_IMPORT_GUIDE.md)** - 完整的导入操作手册
- **[导入成功报告](APIFOX_IMPORT_SUCCESS.md)** - 最近一次导入结果

### 🔧 API 开发指南
- **[API 开发标准指南](API_DEVELOPMENT_GUIDELINES.md)** - REST API开发标准和最佳实践 🆕
- **[API 开发检查清单](API_DEVELOPMENT_CHECKLIST.md)** - 开发过程中的质量检查清单 🆕
- **[API 快速开始模板](API_QUICK_START_TEMPLATE.md)** - 5分钟创建新API端点的模板 🆕
- **[API 端点文档](API_ENDPOINT_DOCUMENTATION.md)** - 完整的280+个API端点参考

### 🧪 API 合规性测试
- **[API 合规性测试框架](API_COMPLIANCE_TESTING_FRAMEWORK.md)** - 完整的自动化测试框架 (1,200+ LOC) 🆕
- **[API 合规性报告](API_COMPLIANCE_REPORT.md)** - 详细的合规性分析和改进建议 🆕
- **[API 合规性改进建议](API_COMPLIANCE_IMPROVEMENTS.md)** - 具体的代码改进示例和最佳实践 🆕
- **[API 合规性测试完成报告](API_COMPLIANCE_TEST_COMPLETION_REPORT.md)** - 测试框架部署和验证结果 🆕
- **[合规性测试快速开始](README_COMPLIANCE_TESTING.md)** - 5分钟设置自动化测试环境 🆕

### 📖 API 参考
- **[OpenAPI 规范 (JSON)](openapi.json)** - OpenAPI 3.1.0 格式
- **[OpenAPI 规范 (YAML)](openapi.yaml)** - YAML 格式
- **[API 前端映射](API_FRONTEND_MAPPING.md)** - 前端组件与API的对应关系

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

### Apifox 项目
**项目地址**: https://app.apifox.com/project/7376246

**导入状态**:
- ✅ 218 个 API 端点
- ✅ 96 个数据模型
- ✅ 25 个接口目录
- ✅ 0 个错误

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

- **总端点数**: 218
- **数据模型**: 96
- **认证方式**: JWT Bearer Token + CSRF
- **API 版本**: 2.0.0
- **OpenAPI 版本**: 3.1.0

---

## 🔧 工具和脚本

### 导入工具

**Python 脚本**: `scripts/runtime/import_to_apifox.py`

```bash
# 运行导入脚本
python scripts/runtime/import_to_apifox.py
```

**功能**:
- ✅ 自动导入 OpenAPI 文档到 Apifox
- ✅ 智能合并（保留现有数据）
- ✅ 详细的导入统计
- ✅ 错误检测和报告

### 同步脚本

当 API 有更新时，使用同步脚本：

```bash
# 方法1: 从运行中的服务导出
curl http://localhost:8000/openapi.json > docs/api/openapi.json

# 方法2: 重新导入到 Apifox
python scripts/runtime/import_to_apifox.py
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

**使用 Apifox**:
1. 在 Apifox 中选择 API
2. 填写参数
3. 点击发送

### 批量测试

**在 Apifox 中**:
1. 创建测试套件
2. 添加测试用例
3. 运行测试

### 生成客户端代码

**在 Apifox 中**:
1. 选择 API
2. 点击 "代码生成"
3. 选择语言（Python/JavaScript/Java/Go...）
4. 复制代码

### 导出文档

**在 Apifox 中**:
1. 点击右上角 "⋯"
2. 选择 "导出"
3. 选择格式（Markdown/HTML/PDF）

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

在 Apifox 中配置环境变量：

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

前端开发时使用 Apifox Mock 服务，无需等待后端完成。

### 4. API 文档同步

API 变更后及时更新 Apifox 文档：
```bash
python scripts/runtime/import_to_apifox.py
```

### 5. 持续集成

在 CI/CD 中集成 API 测试：
```bash
apifox run --project-id 7376246 --test-suite "核心功能测试"
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
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Apifox 项目**: https://app.apifox.com/project/7376246

### Apifox 资源
- **官方文档**: https://apifox.com/help/
- **视频教程**: https://apifox.com/help/video/
- **社区论坛**: https://community.apifox.com/

### MyStocks 项目
- **GitHub**: [项目仓库]
- **技术栈**: FastAPI + TDengine + PostgreSQL
- **架构文档**: `../../CLAUDE.md`

---

## 🎉 下一步

1. ✅ **访问 Apifox 项目**: https://app.apifox.com/project/7376246
2. ✅ **阅读快速开始**: [APIFOX_QUICK_START.md](APIFOX_QUICK_START.md)
3. ✅ **测试核心 API**: 从健康检查开始
4. ✅ **配置认证**: 设置自动登录脚本
5. ✅ **创建测试套件**: 自动化测试
6. ✅ **使用 Mock 服务**: 加速前端开发

---

**最后更新**: 2025-11-12
**文档版本**: 2.1.0
**API 端点**: 231 (+13 Alert History/Analytics endpoints)
**数据模型**: 96
**完成任务**: Task 13 (Monitoring) ✅ | Task 15 (Alert Escalation) ✅

_开始您的 API 探索之旅！_ 🚀
