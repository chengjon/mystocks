## 1. Data Source Management Module

### 1.1 Core Infrastructure
- [ ] 1.1.1 创建 `src/core/datasource/` 目录结构
- [ ] 1.1.2 实现 `DataSourceConfig` Pydantic 模型（定义数据源配置）
- [ ] 1.1.3 实现 `DataSourceRegistry` 核心类（注册/注销/查询）
- [ ] 1.1.4 实现 `DataSourceHealthMonitor` 健康监控器
- [ ] 1.1.5 编写单元测试（覆盖率 ≥ 80%）

### 1.2 Health Metrics Integration
- [ ] 1.2.1 创建 Prometheus 指标（datasource_requests_total, datasource_latency_seconds）
- [ ] 1.2.2 实现异步健康检查逻辑
- [ ] 1.2.3 配置健康检查调度任务（每 30 秒执行）
- [ ] 1.2.4 编写集成测试

### 1.3 Load Balancing & Failover
- [ ] 1.3.1 实现 `MultiSourceLoadBalancer` 负载均衡器
- [ ] 1.3.2 实现基于权重的故障转移逻辑
- [ ] 1.3.3 配置降级策略（主数据源故障自动切换）
- [ ] 1.3.4 编写负载均衡测试

### 1.4 Configuration Migration
- [ ] 1.4.1 导出现有 7 个数据源适配器的配置
- [ ] 1.4.2 创建注册中心初始化脚本
- [ ] 1.4.3 验证兼容性（确保现有功能正常）
- [ ] 1.4.4 编写迁移文档

## 2. Data Governance Module

### 2.1 Data Quality Framework
- [ ] 2.1.1 创建 `src/data_governance/quality.py`
- [ ] 2.1.2 实现 `QualityDimension` 枚举和 `QualityScore` 数据类
- [ ] 2.1.3 实现 `DataQualityChecker.completeness_check()`
- [ ] 2.1.4 实现 `DataQualityChecker.timeliness_check()`
- [ ] 2.1.5 实现 `DataQualityChecker.accuracy_check()`（简化版）
- [ ] 2.1.6 实现 `DataQualityChecker.consistency_check()`（简化版）
- [ ] 2.1.7 编写质量检查测试

### 2.2 Data Lineage Tracking
- [ ] 2.2.1 创建 `src/data_governance/lineage.py`
- [ ] 2.2.2 实现 `LineageNode` 和 `LineageEdge` 数据类
- [ ] 2.2.3 实现 `LineageTracker` 追踪器
- [ ] 2.2.4 实现 PostgreSQL 存储层
- [ ] 2.2.5 创建血缘数据库表（`data_lineage_nodes`, `data_lineage_edges`）
- [ ] 2.2.6 编写血缘追踪测试

### 2.3 Data Asset Registry
- [ ] 2.3.1 创建 `src/data_governance/asset.py`
- [ ] 2.3.2 实现 `DataAssetRegistry` 资产注册中心
- [ ] 2.3.3 实现资产自动发现（扫描数据库表）
- [ ] 2.3.4 实现资产元信息更新逻辑
- [ ] 2.3.5 创建资产数据库表（`data_assets`）
- [ ] 2.3.6 编写资产注册测试

### 2.4 Governance API
- [ ] 2.4.1 创建 `src/api/governance/` 目录
- [ ] 2.4.2 实现 `/api/governance/quality` 端点（查询质量分数）
- [ ] 2.4.3 实现 `/api/governance/lineage` 端点（查询血缘）
- [ ] 2.4.4 实现 `/api/governance/assets` 端点（查询资产列表）
- [ ] 2.4.5 遵循统一响应格式规范
- [ ] 2.4.6 编写 API 测试

## 3. Data Source API

### 3.1 Configuration API
- [ ] 3.1.1 创建 `src/api/datasource/` 目录
- [ ] 3.1.2 实现 `GET /api/datasources` 列出所有数据源
- [ ] 3.1.3 实现 `GET /api/datasources/{id}` 获取单个数据源详情
- [ ] 3.1.4 实现 `POST /api/datasources` 注册新数据源
- [ ] 3.1.5 实现 `PUT /api/datasources/{id}` 更新数据源配置
- [ ] 3.1.6 实现 `DELETE /api/datasources/{id}` 注销数据源
- [ ] 3.1.7 编写 API 测试

### 3.2 Health API
- [ ] 3.2.1 实现 `GET /api/datasources/{id}/health` 查询健康状态
- [ ] 3.2.2 实现 `GET /api/datasources/{id}/metrics` 查询性能指标
- [ ] 3.2.3 实现 `POST /api/datasources/{id}/check` 触发手动健康检查
- [ ] 3.2.4 编写 API 测试

## 4. Grafana Visualization

### 4.1 Data Source Dashboard
- [ ] 4.1.1 创建 `grafana/dashboards/data-source-overview.json`
- [ ] 4.1.2 添加数据源状态表格（使用 Table 面板）
- [ ] 4.1.3 添加 QPS 趋势图（使用 Graph 面板）
- [ ] 4.1.4 添加延迟分布图（使用 Histogram 面板）
- [ ] 4.1.5 添加错误率告警面板（使用 Gauge 面板）
- [ ] 4.1.6 配置 Prometheus Data Source

### 4.2 Data Quality Dashboard
- [ ] 4.2.1 创建 `grafana/dashboards/data-quality.json`
- [ ] 4.2.2 添加质量评分仪表盘（使用 Gauge 面板）
- [ ] 4.2.3 添加各维度分数趋势图（使用 Graph 面板）
- [ ] 4.2.4 添加异常检测告警面板（使用 Alert List 面板）
- [ ] 4.2.5 添加数据集质量对比表（使用 Table 面板）

### 4.3 Data Lineage Dashboard
- [ ] 4.3.1 创建 `grafana/dashboards/data-lineage.json`
- [ ] 4.3.2 添加拓扑图（使用 Node Graph 面板）
- [ ] 4.3.3 添加节点详情面板（使用 JSON 面板）
- [ ] 4.3.4 添加时间范围筛选器
- [ ] 4.3.5 配置 PostgreSQL Data Source（用于查询血缘数据）

### 4.4 Data Asset Dashboard
- [ ] 4.4.1 创建 `grafana/dashboards/data-assets.json`
- [ ] 4.4.2 添加资产目录列表（使用 Table 面板）
- [ ] 4.4.3 添加访问频次排名（使用 Bar Gauge 面板）
- [ ] 4.4.4 添加存储使用量（使用 Pie Chart 面板）
- [ ] 4.4.5 添加资产增长趋势图（使用 Graph 面板）

### 4.5 Alert Configuration
- [ ] 4.5.1 配置数据源故障告警规则
- [ ] 4.5.2 配置数据质量异常告警规则
- [ ] 4.5.3 配置延迟阈值告警规则
- [ ] 4.5.4 测试告警通知（Webhook/Email）

## 5. Integration & Testing

### 5.1 Adapter Integration
- [ ] 5.1.1 修改现有数据源适配器，从注册中心获取配置
- [ ] 5.1.2 为现有适配器添加 health_check 方法
- [ ] 5.1.3 为现有适配器添加血缘追踪装饰器
- [ ] 5.1.4 验证现有功能正常

### 5.2 End-to-End Testing
- [ ] 5.2.1 编写数据源管理 E2E 测试
- [ ] 5.2.2 编写数据治理 E2E 测试
- [ ] 5.2.3 编写 Grafana 面板测试（验证数据展示正确）
- [ ] 5.2.4 验证 Prometheus 指标正确暴露

### 5.3 Documentation
- [ ] 5.3.1 编写 API 文档（OpenAPI）
- [ ] 5.3.2 编写 Grafana Dashboard 使用指南
- [ ] 5.3.3 编写运维手册（配置、监控、告警）
- [ ] 5.3.4 更新 README（新增功能说明）

## 6. Deployment & Validation

### 6.1 Configuration
- [ ] 6.1.1 创建配置模板 `config/datasource.yaml.example`
- [ ] 6.1.2 创建配置模板 `config/governance.yaml.example`
- [ ] 6.1.3 更新环境变量说明

### 6.2 Validation
- [ ] 6.2.1 运行 lint（black, mypy）
- [ ] 6.2.2 运行单元测试（pytest, 覆盖率 ≥ 80%）
- [ ] 6.2.3 运行集成测试
- [ ] 6.2.4 验证 Grafana 面板正常显示
- [ ] 6.2.5 验证告警规则生效

## Summary

- Total tasks: 72
- Estimated effort: 6 weeks
- Dependencies: Grafana, Prometheus, PostgreSQL（现有组件）
- Breaking changes: None（向后兼容）
