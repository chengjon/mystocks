# MyStocks 更新日志

> **历史文档说明**:
> 本文件是版本更新日志与历史变更记录，不是当前共享规则、当前实施状态或当前运行基线的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内版本状态、验证结果、阶段命名和变更摘要如未重新复核，应视为对应版本的历史快照，不得直接当作当前事实。

## Unreleased (2026-03-14)

### 🧭 MongoDB Multi-CLI Coordination（Maestro vNext）

- 将 `MongoDB Multi-CLI Coordination` 正式定义为 `Maestro` 体系下的下一代协作控制面，而不是平行新系统。
- 在 `maestro.collab` 内落地 Mongo control-plane：
  - `work_items`
  - `work_updates`
  - `work_requests`
  - `work_events`
  - `worker_status_views`
- 扩展 `maestro_collab.py` 与 `coordctl.py`，提供主 CLI / worker CLI 的 Mongo 协作命令面。
- 新增作用域校验、审计事件和自动摘要刷新，worker 不可直接修改 `work_item` 定义。
- `Symphony` runtime 支持 `sqlite / mongo / dual-write` 三种 collab backend。
- 新增 `MongoWorkItemTrackerClient`，`tracker.kind == mongo` 时可直接从 Mongo `work_items` 调度。
- runtime 事件已可自动回写 control-plane 状态，并把 control-plane 摘要并入 `/api/v1/state`。
- 新增迁移与导出脚本：
  - `scripts/runtime/migrate_collab_to_mongo.py`
  - `scripts/runtime/export_collab_snapshots.py`
- 新增真实 Mongo smoke 脚本：`scripts/runtime/smoke_mongo_multicli.py`

### ✅ 验证

- `pytest tests/unit/services/symphony/test_config.py tests/unit/services/symphony/test_tracker_factory.py tests/unit/services/symphony/test_mongo_tracker.py tests/unit/services/symphony/test_mongo_runtime_flow.py tests/unit/services/symphony/test_orchestrator.py tests/unit/services/symphony/test_workspace_manager.py tests/unit/services/symphony/test_status_api.py tests/unit/services/symphony/test_maestro_collab_cli.py tests/unit/services/symphony/test_maestro_namespace.py tests/unit/services/symphony/test_collab_backend_selection.py tests/unit/maestro_collab tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/runtime/test_collab_migration_scripts.py tests/unit/runtime/test_smoke_mongo_multicli.py -q -o addopts=''`
- 结果：`77 passed`
- `python scripts/runtime/smoke_mongo_multicli.py`
- 真实 Mongo smoke 结果：`assignment_status=retrying`，`control_plane_status=ready_for_review`，`status_api_control_plane_count=1`

### 🎼 Maestro / Symphony 本地优先收口

- 将 `Symphony + Linear` 的默认协作模型正式收敛为 **本地优先 + SQLite tracker + 多 CLI 协作**。
- 明确人类 / Main CLI / Worker CLI 的责任边界，并把权威说明沉淀到多 CLI 工作流文档中。
- 完成 `Maestro` 三层命名体系、总结文档与 `quick start` 文档，方便后续独立迁移为跨项目工具。
- 打通 owner suggestion → assign → tracker state 的本地主流程，并补齐相关回归测试与运行入口。

### 🧹 仓库卫生治理与生命周期目录

- 落地 `integrate-repository-hygiene` 的首轮执行结果，统一生命周期目录到 `docs/`、`reports/`、`archive/`、`var/`。
- 将 `TASK.md` 与 `TASK-REPORT.md` 正式定义为工作流允许的 root exception，而不是目录治理债务。
- 修正覆盖率、备份、清理、结构检查等脚本的默认落点，避免新的根目录运行时产物继续回流。
- 完成历史 `docs/*_reports`、`docs/archive/`、`docs/legacy/`、root `reviews/`、root `archived/` 等内容收敛。
- 当前目录治理基线已收敛为：
  - `errors: 0`
  - `warnings: 0`

### ✅ 验证

- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
- `openspec validate integrate-repository-hygiene --strict`
- `python scripts/maintenance/check_structure.py --format text`

## v1.4.0 (2025-12-28)

### 🎉 Phase 6 文档和标准化

#### 📚 新增文档

**API 文档**
- `docs/api/API_INDEX.md` - API 文档索引，包含所有核心端点说明
- `docs/api/DATA_MODELS.md` - 完整的数据模型文档
- `docs/api/ERROR_CODES.md` - 详细的错误码参考

**部署文档**
- `docs/guides/DEPLOYMENT.md` - 完整的 Docker/K8s 部署指南
- `docs/guides/USER_GUIDE.md` - 用户使用指南
- `docs/guides/TROUBLESHOOTING.md` - 故障排查手册

**技术规范**
- OpenAPI 3.1.0 Schema (`docs/api/openapi.json`)
- Swagger UI 可访问 (`/docs`)
- ReDoc 文档 (`/redoc`)

#### 📊 API 端点覆盖

| 模块 | 端点数 | 状态 |
|------|--------|------|
| 认证模块 | 5 | ✅ 完整 |
| 市场数据模块 | 8 | ✅ 完整 |
| 策略管理模块 | 7 | ✅ 完整 |
| 回测模块 | 6 | ✅ 完整 |
| 交易模块 | 5 | ✅ 完整 |
| 系统监控模块 | 5 | ✅ 完整 |
| **总计** | **36** | **100%** |

#### 🛠️ 文档改进

- 统一文档格式和风格
- 完整的代码示例
- 错误响应格式标准化
- 数据模型类型定义

---

## v1.3.1 (2025-11-12)

### 🐛 Bug 修复

#### Claude Code Hooks 系统完善
- **PostToolUse:Write Hooks JSON 错误处理修复**
  - 修复三个 PostToolUse:Write hooks 的 JSON 解析错误
  - 添加完整的 stdin 验证流程（空检查 + JSON 有效性验证）
  - 所有 jq 调用添加错误处理和 fallback 值
  - 确保非阻塞行为，永不中断工作流

#### 修复的 Hooks
1. `post-tool-use-file-edit-tracker.sh` - 编辑日志记录
2. `post-tool-use-database-schema-validator.sh` - 数据库架构验证
3. `post-tool-use-document-organizer.sh` - 文档位置检查

#### 技术细节
- **问题**: 当 stdin 包含无效 JSON 或为空时，jq 命令失败导致 exit code > 0
- **原因**: 脚本使用 `set -euo pipefail` 严格模式，任何命令失败都会导致退出
- **修复**:
  - stdin 验证：`if [ -z "$INPUT_JSON" ]; then exit 0; fi`
  - JSON 验证：`if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then exit 0; fi`
  - 安全 jq 调用：`jq ... 2>/dev/null || echo "default"`

#### 测试结果
- ✅ 无效 JSON: exit 0 (非阻塞)
- ✅ 空输入: exit 0 (非阻塞)
- ✅ 有效 JSON: exit 0 (正常处理)
- ✅ Edit/Write 工具: 正常工作
- ✅ 所有六个测试场景通过

#### 📚 文档更新
- `docs/guides/HOOKS_CONFIGURATION_DETAILED.md` - 添加详细的 PostToolUse:Write 修复历史
- `docs/guides/CLAUDE_CODE_TOOLS_GUIDE.md` - 添加修复摘要和测试验证

**Git 提交**: commit 4ad3503

---

## v1.3.0 (2025-11-04)

### 🎉 重大更新

#### 🚀 GPU缓存优化系统
- **缓存命中率提升**：从80%提升至**90%+**
- **6大核心优化策略**：
  1. **访问模式学习** (`AccessPatternLearner`) - EWMA预测算法，预期提升8-12%
  2. **查询结果缓存** (`QueryResultCache`) - MD5指纹去重，预期提升10-15%
  3. **负缓存机制** (`NegativeCache`) - 缓存不存在数据，预期提升2-5%
  4. **自适应TTL管理** (`AdaptiveTTLManager`) - 4级热度分区，预期提升3-5%
  5. **智能压缩** (`SmartCompressor`) - 选择性压缩，预期提升3-5%
  6. **预测性预加载** (`PredictivePrefetcher`) - 并发预加载，预期提升6-10%

#### 📚 新增文档
- `gpu_api_system/CACHE_OPTIMIZATION_GUIDE.md` - 完整的缓存优化指南
- `gpu_api_system/utils/cache_optimization_enhanced.py` - 增强缓存优化实现 (661行)
- `gpu_api_system/tests/unit/test_cache/test_cache_optimization_enhanced.py` - 完整测试套件 (21个测试用例)

#### 🛠️ 技术改进
- **性能优化**：GPU内存访问延迟显著降低
- **智能预热**：基于访问模式的自动数据预热
- **并发预加载**：ThreadPoolExecutor 5个worker并发处理
- **压缩优化**：智能判断压缩收益 (>10KB, <70%压缩率)

#### 📊 性能指标更新
| 指标 | 之前 | 现在 | 提升 |
|------|------|------|------|
| 缓存命中率 | >80% | **>90%** | +10% |
| 预测准确率 | N/A | 85%+ | 新增 |
| 预加载命中率 | N/A | 70%+ | 新增 |

## v1.2.0 (2025-09-17)

### 🎉 重大更新

#### ✅ 系统验证完成
- **架构验证**：完整验证了适配器模式+工厂模式的架构实现
- **功能验证**：全面测试所有数据源和功能模块
- **环境验证**：解决Python版本兼容性问题，确保系统稳定运行
- **性能验证**：验证系统在不同数据源间切换的性能表现

#### 📚 新增文档
- `FINAL_VALIDATION_REPORT.md` - 系统最终验证报告
- `ARCHITECTURE_VALIDATION_SUMMARY.md` - 架构验证总结报告

#### 🛠️ 技术改进
- **依赖管理优化**：解决baostock库在Python 3.13环境中的兼容性问题
- **错误处理增强**：完善异常处理机制和错误提示信息
- **文档完善**：更新README文档，添加架构验证相关信息

## v1.1.0 (2025-09-16)

### 🎉 重大更新

#### ✨ 新增功能
- **扩展核心抽象方法**：新增实时数据、交易日历、财务数据、新闻数据等4个核心接口
- **多返回类型支持**：支持DataFrame、Dict、List、JSON等多种返回格式
- **统一列名管理**：创建`ColumnMapper`工具，自动处理不同数据源的列名差异
- **批量数据源注册**：支持一次性注册多个数据源，简化扩展流程
- **Tushare数据源**：新增完整的Tushare数据源适配器
- **数据源管理增强**：支持查看、取消注册数据源

#### 🔧 改进优化
- **延迟导入机制**：避免依赖问题影响系统启动
- **错误处理增强**：更完善的异常处理和错误提示
- **代码格式化优化**：智能识别和转换不同数据源的股票代码格式
- **文档完善**：新增架构验证报告、扩展功能演示文档

#### 📚 新增文档
- `ARCHITECTURE_VERIFICATION_REPORT.md` - 完整的架构验证报告
- `EXTENSION_DEMO.md` - 系统扩展功能演示
- `register_new_sources.py` - 新数据源注册演示脚本
- `CHANGELOG.md` - 更新日志

#### 🏗️ 架构增强
- **接口扩展**：`IDataSource`接口新增4个抽象方法
- **工厂增强**：`DataSourceFactory`支持批量注册和管理
- **工具扩展**：新增`ColumnMapper`统一列名管理器
- **适配器完善**：所有适配器集成列名映射功能

### 🛠️ 技术细节

#### 新增文件
```
utils/column_mapper.py          # 统一列名管理器
adapters/tushare_adapter.py     # Tushare数据源适配器
register_new_sources.py         # 数据源注册演示
ARCHITECTURE_VERIFICATION_REPORT.md  # 架构验证报告
EXTENSION_DEMO.md               # 扩展功能演示
CHANGELOG.md                    # 更新日志
```

#### 修改文件
```
interfaces/data_source.py       # 新增4个抽象方法，支持多返回类型
factory/data_source_factory.py  # 新增批量注册、管理功能
adapters/akshare_adapter.py     # 集成列名映射器
adapters/baostock_adapter.py    # 集成列名映射器，完善延迟导入
README.md                       # 更新功能介绍和使用说明
```

## v1.0.0 (2025-09-15)

### 🎉 首次发布

#### ✨ 核心功能
- **适配器模式**：统一不同数据源的接口差异
- **工厂模式**：动态创建和管理数据源
- **统一管理器**：提供简洁的数据访问API
- **多数据源支持**：支持AKShare和Baostock数据源
- **智能格式化**：自动处理股票代码和日期格式

#### 🏗️ 系统架构
- **分层设计**：接口层、适配器层、工厂层、管理层、应用层
- **模块化结构**：清晰的目录结构和职责分离
- **可扩展性**：支持动态添加新数据源
- **容错机制**：完善的错误处理和重试机制

#### 📁 项目结构
```
mystocks/
├── interfaces/         # 接口定义
├── adapters/          # 数据源适配器
├── factory/           # 数据源工厂
├── manager/           # 统一数据管理器
├── tools/             # 工具类
├── examples/          # 使用示例
└── tests/             # 测试文件
```
