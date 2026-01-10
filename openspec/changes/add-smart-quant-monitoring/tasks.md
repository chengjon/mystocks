# 智能量化监控与决策系统 - 实施任务清单

**变更ID**: `add-smart-quant-monitoring`
**创建日期**: 2026-01-07
**预计周期**: 9-10周
**状态**: 待审核

---

## Phase 1: 基础设施连接 (1周)

**目标**: 建立数据库表、异步访问层、事件总线扩展

### 1.1 数据库表创建 (2天)

**任务**:
- [ ] 创建 `monitoring_watchlists` 表
- [ ] 创建 `monitoring_watchlist_stocks` 表（含入库上下文字段）
- [ ] 创建 `monitoring_health_scores` 表（含高级风险指标）
- [ ] 创建索引（user_id, watchlist_id, stock_code, score_date）
- [ ] 添加外键约束和级联删除规则

**验证标准**:
- SQL脚本可重复执行（CREATE IF NOT EXISTS）
- 所有索引创建成功
- 外键约束生效（级联删除测试通过）

**输出文件**:
- `scripts/migrations/001_monitoring_tables.sql`

**依赖**: 无

---

### 1.2 异步数据库访问层 (2天)

**任务**:
- [ ] 创建 `src/monitoring/infrastructure/postgresql_async.py`
- [ ] 实现 `MonitoringPostgreSQLAccess` 类
- [ ] 实现连接池管理（min_size=5, max_size=20）
- [ ] 实现 `batch_save_health_scores()` 方法
- [ ] 实现 `get_watchlist_with_stocks()` 方法
- [ ] 实现 `get_health_score_history()` 方法
- [ ] 添加连接健康检查逻辑

**验证标准**:
- 单元测试：连接池初始化成功
- 单元测试：批量写入100条数据 <1秒
- 单元测试：连接池自动释放

**输出文件**:
- `src/monitoring/infrastructure/postgresql_async.py`
- `tests/unit/test_postgresql_async.py`

**依赖**: 任务1.1（数据库表创建）

---

### 1.3 事件总线扩展 (2天)

**任务**:
- [ ] 扩展 `MonitoringEvent` 类型（支持 `metric_update`）
- [ ] 修改 `MonitoringEventWorker._flush_events_async()`
- [ ] 添加 `metric_update` 事件处理逻辑
- [ ] 集成 `postgres_async.batch_save_health_scores()`
- [ ] 添加事件处理失败重试机制

**验证标准**:
- 单元测试：发布 `metric_update` 事件
- 集成测试：Worker正确消费并批量写入数据库
- 验证：事件丢失时进入降级缓存

**输出文件**:
- 修改 `src/monitoring/async_monitoring.py`
- `tests/integration/test_metric_update_events.py`

**依赖**: 任务1.2（异步数据库访问层）

---

### 1.4 FastAPI集成 (1天)

**任务**:
- [ ] 在 `app/main.py` 添加 startup/shutdown 事件
- [ ] 初始化 `postgres_async` 连接池
- [ ] 添加健康检查端点（验证异步连接）
- [ ] 配置环境变量（POSTGRESQL_*, REDIS_*）

**验证标准**:
- 启动后端服务无错误
- 健康检查端点返回 200 OK
- 连接池状态正常

**输出文件**:
- 修改 `web/backend/app/main.py`
- 修改 `web/backend/app/core/config.py`

**依赖**: 任务1.2（异步数据库访问层）

---

## Phase 2: 核心计算引擎 (4-5周)

**目标**: 实现市场体制识别、CPU/GPU计算引擎、高级风险指标

### 2.1 市场体制识别器 (1周)

**任务**:
- [ ] 创建 `src/monitoring/domain/market_regime.py`
- [ ] 实现 `MarketRegimeIdentifier` 类
- [ ] 实现 `_calculate_ma_slope()` 方法（MA斜率计算）
- [ ] 实现 `_calculate_market_breadth()` 方法（涨跌家数比）
- [ ] 实现 `_calculate_regime_volatility()` 方法（ATR波动率）
- [ ] 实现综合评分逻辑（权重0.4/0.3/0.3）
- [ ] 定义动态权重矩阵 `DYNAMIC_WEIGHTS`

**验证标准**:
- 单元测试：2020年牛市识别准确率 >70%
- 单元测试：2022年熊市识别准确率 >70%
- 单元测试：震荡市识别准确率 >60%

**输出文件**:
- `src/monitoring/domain/market_regime.py`
- `tests/unit/test_market_regime_identifier.py`
- 回测验证报告（2020-2025历史数据）

**依赖**: 任务1.1（数据库表创建）

---

### 2.2 CPU向量化计算引擎 (1周)

**任务**:
- [ ] 创建 `src/monitoring/domain/calculator_cpu.py`
- [ ] 实现 `VectorizedHealthCalculator` 类
- [ ] 实现向量化五维评分计算（避免循环）
- [ ] 实现趋势评分（MA斜率、价格位置）
- [ ] 实现技术评分（MACD、RSI、KDJ）
- [ ] 实现动量评分（ROC、动量因子）
- [ ] 实现波动率评分（ATR、历史波动率）
- [ ] 实现风险评分（最大回撤、下行风险）

**验证标准**:
- 性能测试：100只股票 <5秒
- 性能测试：500只股票 <20秒
- 验证：结果一致性（多次计算结果相同）

**输出文件**:
- `src/monitoring/domain/calculator_cpu.py`
- `tests/unit/test_vectorized_calculator.py`
- 性能测试报告

**依赖**: 任务2.1（市场体制识别器）

---

### 2.3 GPU桥接和集成 (1.5周)

**任务**:
- [ ] 创建 `src/monitoring/domain/calculator_gpu.py`
- [ ] 实现 `GPUHealthCalculator` 类
- [ ] 复用 `src/gpu/core/hardware_abstraction/resource_manager.py`
- [ ] 实现 GPU 健康检查逻辑
- [ ] 实现显存监控（<4GB 降级CPU）
- [ ] 实现 CuPy 向量化计算逻辑
- [ ] 集成 RAPIDS cuDF（加速 DataFrame 操作）
- [ ] 添加 GPU 故障降级逻辑

**验证标准**:
- 性能测试：1000只股票 <2秒
- 性能测试：对比CPU加速比 >50x
- 验证：GPU vs CPU 结果误差 <0.01
- 验证：显存不足时自动降级CPU

**输出文件**:
- `src/monitoring/domain/calculator_gpu.py`
- `tests/unit/test_gpu_calculator.py`
- GPU集成测试报告

**依赖**: 任务2.2（CPU计算引擎）

---

### 2.4 高级风险指标计算器 (1周)

**任务**:
- [ ] 扩展计算引擎（CPU/GPU均支持）
- [ ] 实现 Sortino 比率计算（下行风险调整收益）
- [ ] 实现 Calmar 比率计算（最大回撤调整收益）
- [ ] 实现最大回撤持续期计算
- [ ] 实现下行标准差计算（Downside Deviation）
- [ ] 添加指标到 JSONB radar_scores 存储

**验证标准**:
- 单元测试：Sortino 比率计算正确性（与Excel对比）
- 单元测试：Calmar 比率计算正确性
- 单元测试：回撤持续期计算正确性
- 验证：所有指标在 CPU/GPU 模式下结果一致

**输出文件**:
- 修改 `src/monitoring/domain/calculator_cpu.py`
- 修改 `src/monitoring/domain/calculator_gpu.py`
- `tests/unit/test_advanced_risk_metrics.py`

**依赖**: 任务2.2（CPU计算引擎）、任务2.3（GPU桥接）

---

### 2.5 计算引擎工厂和切换逻辑 (0.5周)

**任务**:
- [ ] 创建 `src/monitoring/domain/calculator_factory.py`
- [ ] 实现 `HealthCalculatorFactory.get_calculator()`
- [ ] 实现智能切换逻辑（数据规模 + GPU健康状态）
- [ ] 配置阈值（>3000行用GPU，显存>4GB）
- [ ] 添加切换决策日志

**验证标准**:
- 单元测试：小规模数据（<100只股票）选择CPU
- 单元测试：大规模数据（>3000行）选择GPU
- 单元测试：GPU不可用时降级CPU
- 验证：切换逻辑符合预期

**输出文件**:
- `src/monitoring/domain/calculator_factory.py`
- `tests/unit/test_calculator_factory.py`

**依赖**: 任务2.2、2.3、2.4（所有计算引擎完成）

---

### 2.6 测试和验证 (0.5周)

**任务**:
- [ ] 端到端测试：完整计算流程
- [ ] 性能测试：不同数据规模的响应时间
- [ ] 压力测试：并发计算稳定性
- [ ] 回测验证：历史数据健康度评分
- [ ] 修复发现的问题

**验证标准**:
- E2E测试：10个场景通过率100%
- 性能测试：P95延迟 <500ms
- 压力测试：100并发无错误
- 回测验证：2020-2025年数据无异常

**输出文件**:
- `tests/integration/test_health_calculation_e2e.py`
- 测试报告

**依赖**: 任务2.5（计算引擎工厂）

---

## Phase 3: 业务 API 开发 (2周)

**目标**: 实现清单管理、智能分析、数据迁移 API

### 3.1 清单管理 API (0.5周)

**任务**:
- [ ] 创建 `web/backend/app/api/monitoring_watchlists.py`
- [ ] 实现 `POST /watchlists` (创建清单)
- [ ] 实现 `GET /watchlists/{id}` (获取清单)
- [ ] 实现 `GET /watchlists` (列出所有清单)
- [ ] 实现 `PUT /watchlists/{id}` (更新清单)
- [ ] 实现 `DELETE /watchlists/{id}` (删除清单)

**验证标准**:
- API测试：CRUD操作正常
- 验证：删除清单时级联删除成员
- 验证：响应格式符合统一规范

**输出文件**:
- `web/backend/app/api/monitoring_watchlists.py`
- `tests/api/test_watchlist_api.py`

**依赖**: 任务1.4（FastAPI集成）

---

### 3.2 清单成员管理 API (0.5周)

**任务**:
- [ ] 实现 `POST /watchlists/{id}/stocks` (添加股票)
- [ ] 实现 `DELETE /watchlists/{id}/stocks/{code}` (移除股票)
- [ ] 支持入库上下文参数（entry_price, entry_reason, stop_loss, target）
- [ ] 实现批量添加接口
- [ ] 添加参数验证（Pydantic models）

**验证标准**:
- API测试：添加/移除股票正常
- 验证：入库上下文字段正确保存
- 验证：重复添加返回400错误

**输出文件**:
- `web/backend/app/api/monitoring_watchlists.py` (扩展)
- `web/backend/app/models/monitoring.py` (Pydantic models)

**依赖**: 任务3.1（清单管理 API）

---

### 3.3 智能分析 API (1周)

**任务**:
- [ ] 创建 `web/backend/app/api/monitoring_analysis.py`
- [ ] 实现 `POST /analysis/calculate` (计算健康度)
- [ ] 实现调用计算引擎工厂
- [ ] 实现异步事件发布（metric_update）
- [ ] 实现 `GET /analysis/results/{code}` (历史曲线)
- [ ] 实现 `GET /analysis/portfolio/{id}` (组合分析)

**验证标准**:
- API测试：计算接口返回结果 <500ms (P95)
- 验证：异步事件成功发布到Redis
- 验证：Worker成功写入数据库
- 验证：历史曲线查询正确

**输出文件**:
- `web/backend/app/api/monitoring_analysis.py`
- `tests/api/test_analysis_api.py`
- `tests/integration/test_analysis_workflow.py`

**依赖**: 任务2.6（计算引擎测试通过）

---

### 3.4 数据迁移脚本 (0.5周)

**任务**:
- [ ] 创建 `scripts/migrations/migrate_watchlist_to_monitoring.py`
- [ ] 实现读取SQLite数据逻辑
- [ ] 实现数据验证（完整性检查）
- [ ] 实现批量写入PostgreSQL
- [ ] 实现迁移结果验证
- [ ] 创建管理API `POST /admin/migrate-watchlists`

**验证标准**:
- 测试迁移：测试数据迁移成功
- 验证：所有记录正确迁移
- 验证：迁移后数据完整性
- 回滚测试：迁移失败可回滚

**输出文件**:
- `scripts/migrations/migrate_watchlist_to_monitoring.py`
- `scripts/migrations/verify_migration.py`
- `web/backend/app/api/admin.py` (管理接口)

**依赖**: 任务3.2（清单成员管理 API）

---

### 3.5 API文档和测试 (0.5周)

**任务**:
- [ ] 完善 API 文档（OpenAPI 3.0）
- [ ] 添加请求/响应示例
- [ ] 编写API集成测试
- [ ] 测试错误处理和边界情况
- [ ] 性能测试（并发请求）

**验证标准**:
- 文档完整性：所有端点有文档
- 测试覆盖率：API测试覆盖率 >80%
- 性能测试：100并发无错误

**输出文件**:
- API 文档（Swagger UI 自动生成）
- `tests/api/` (完整测试套件)

**依赖**: 任务3.3、3.4（所有API完成）

---

## Phase 4: 前端可视化 (2周)

**目标**: 实现清单管理页面、健康度雷达图、风控看板

### 4.1 清单管理页面 (0.5周)

**任务**:
- [ ] 创建 `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- [ ] 实现清单列表展示
- [ ] 实现创建/编辑/删除清单
- [ ] 实现添加/移除股票
- [ ] 实现入库上下文表单（entry_price, entry_reason, stop_loss, target）

**验证标准**:
- 功能测试：CRUD操作正常
- 验证：表单验证正确
- 验证：错误提示友好

**输出文件**:
- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/components/monitoring/WatchlistForm.vue`

**依赖**: 任务3.2（清单成员管理 API）

---

### 4.2 健康度雷达图组件 (0.5周)

**任务**:
- [ ] 创建 `web/frontend/src/components/monitoring/HealthRadarChart.vue`
- [ ] 集成 ECharts 雷达图
- [ ] 实现五维雷达图展示（趋势、技术、动量、波动、风险）
- [ ] 实现历史数据对比（多日雷达图叠加）
- [ ] 实现交互功能（悬停显示详情）

**验证标准**:
- 功能测试：雷达图正确渲染
- 验证：数据更新时图表自动刷新
- 验证：多股票对比功能正常

**输出文件**:
- `web/frontend/src/components/monitoring/HealthRadarChart.vue`
- `web/frontend/src/api/monitoring.js`

**依赖**: 任务3.3（智能分析 API）

---

### 4.3 组合分析页面 (0.5周)

**任务**:
- [ ] 创建 `web/frontend/src/views/monitoring/PortfolioAnalysis.vue`
- [ ] 实现组合整体健康度展示
- [ ] 实现个股详情列表
- [ ] 实现再平衡建议（REBALANCE/HOLD）
- [ ] 实现风险预警（触发止损/止盈股票高亮）

**验证标准**:
- 功能测试：组合分析数据正确
- 验证：再平衡建议逻辑正确
- 验证：风险预警及时触发

**输出文件**:
- `web/frontend/src/views/monitoring/PortfolioAnalysis.vue`
- `web/frontend/src/components/monitoring/StockHealthCard.vue`

**依赖**: 任务3.3（智能分析 API）

---

### 4.4 风控看板页面 (0.5周)

**任务**:
- [ ] 创建 `web/frontend/src/views/monitoring/RiskDashboard.vue`
- [ ] 实现止损/止盈预警列表
- [ ] 实现高级风险指标展示（Sortino、Calmar、最大回撤）
- [ ] 实现回撤持续期可视化
- [ ] 实现导出报告功能

**验证标准**:
- 功能测试：风控看板数据正确
- 验证：预警触发准确
- 验证：报告导出正常

**输出文件**:
- `web/frontend/src/views/monitoring/RiskDashboard.vue`
- `web/frontend/src/components/monitoring/RiskMetricsCard.vue`

**依赖**: 任务3.3（智能分析 API）

---

## 数据迁移任务

### 数据备份和验证

**任务**:
- [ ] 备份现有 watchlist.db 数据库
- [ ] 验证备份数据完整性
- [ ] 创建回滚计划
- [ ] 执行迁移脚本
- [ ] 验证迁移结果

**验证标准**:
- 备份成功：可恢复
- 迁移成功：所有记录正确迁移
- 验证通过：数据完整性检查通过

**输出文件**:
- 备份文件：`backups/watchlist_db_YYYYMMDD.sqlite`
- 迁移报告

**执行时机**: Phase 3 完成后

---

## 测试和验证任务

### 单元测试

**目标**: 测试覆盖率 >80%

**任务**:
- [ ] 市场体制识别器测试
- [ ] CPU/GPU 计算引擎测试
- [ ] 计算引擎工厂测试
- [ ] 异步数据库访问层测试
- [ ] 高级风险指标测试

**验证标准**:
- 测试覆盖率 >80%
- 所有核心路径有测试

---

### 集成测试

**任务**:
- [ ] API端到端测试
- [ ] 事件总线集成测试
- [ ] 计算引擎集成测试
- [ ] 数据迁移集成测试

**验证标准**:
- 所有集成测试通过
- 无回归问题

---

### 性能测试

**任务**:
- [ ] API响应时间测试（P95 <500ms）
- [ ] 并发压力测试（100并发）
- [ ] 数据库查询性能测试
- [ ] GPU加速效果验证

**验证标准**:
- 性能指标达标
- 无内存泄漏
- 无性能退化

---

## 部署和上线任务

### 预生产环境验证

**任务**:
- [ ] 部署到预生产环境
- [ ] 执行数据迁移
- [ ] 验证所有功能
- [ ] 性能测试
- [ ] 用户验收测试

**验证标准**:
- 所有功能正常
- 性能达标
- 用户满意

---

### 生产环境上线

**任务**:
- [ ] 制定上线计划
- [ ] 执行数据库迁移
- [ ] 部署后端服务
- [ ] 部署前端资源
- [ ] 监控告警配置
- [ ] 上线后验证

**验证标准**:
- 上线成功无故障
- 监控正常
- 用户可用

---

## 风险和依赖

### 关键路径风险

| 阶段 | 风险 | 应对措施 |
|------|------|----------|
| Phase 2 | GPU集成复杂度高 | 预留1.5周缓冲，充分测试 |
| Phase 3 | API性能不达标 | 优化查询、添加缓存 |
| Phase 4 | 前端组件开发延期 | 优先核心功能，次要功能后续迭代 |

### 外部依赖

- ✅ PostgreSQL 数据库（已有）
- ✅ Redis 缓存（已有）
- ✅ TDengine（已有）
- ⚠️ GPU 环境（可选，非必需）

---

## 进度跟踪

### 里程碑

- **M1**: Phase 1 完成 - 数据库和基础设施就绪
- **M2**: Phase 2 完成 - 核心计算引擎可用
- **M3**: Phase 3 完成 - API全部上线
- **M4**: Phase 4 完成 - 前端可视化完成
- **M5**: 数据迁移完成 - 历史数据可用
- **M6**: 生产上线 - 系统正式交付

### 每周评审

- 每周一：进度回顾
- 每周五：下周计划
- 每个阶段结束：里程碑评审

---

## 总计

**预计总周期**: 9-10周

**工作量分解**:
- Phase 1: 1周（基础设施）
- Phase 2: 4-5周（核心引擎）← 调整
- Phase 3: 2周（业务API）
- Phase 4: 2周（前端可视化）
- 测试验证：贯穿各阶段
- 数据迁移：Phase 3 期间执行

**关键成功因素**:
1. 充分复用现有资产（60%复用率）
2. GPU集成预留充足时间
3. 持续测试和验证
4. 用户及时反馈

---

**文档版本**: v1.0
**最后更新**: 2026-01-07
**状态**: 待审核
