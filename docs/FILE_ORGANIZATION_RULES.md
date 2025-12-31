# 项目目录文件整理规则

**文档版本**: v1.0
**最后更新**: 2025-12-30
**适用范围**: 所有项目（通用标准）

---

## 📋 目录规则

### 核心源码目录

#### `src/` - 主源代码目录
- **命名规则**:
  - 全小写，单词用下划线分隔
  - 不得使用驼峰命名（如 `myService` 应为 `my_service`）
  - Python包使用单数形式（`adapters/` 而非 `adapter/`）
  - 模块名使用名词复数（`models/`、`services/`、`utils/`）

- **子目录结构**:
  ```
  src/
  ├── adapters/          # 数据适配器
  ├── core/              # 核心业务逻辑
  ├── database/          # 数据库访问层
  ├── services/          # 业务服务
  ├── ml_strategy/        # 机器学习策略
  ├── monitoring/        # 监控服务
  ├── gpu/              # GPU相关功能
  ├── web/              # Web服务
  ├── interfaces/        # 接口定义
  ├── storage/           # 数据存储
  └── utils/            # 工具函数
  ```

- **文件命名规则**:
  - Python文件: `snake_case.py`
  - 配置文件: `config.yaml`、`config.json`、`settings.py`
  - 测试文件: `test_<module>.py`、`conftest_<module>.py`
  - 工厂/单例: `<module>_factory.py`
  - 管理器: `<module>_manager.py`

#### `config/` - 配置文件目录
- **命名规则**:
  - 全小写，单词用连字符或下划线
  - 不使用驼峰命名

- **子目录结构**:
  ```
  config/
  ├── adapters/         # 各适配器配置
  ├── databases/        # 数据库配置
  ├── monitoring/       # 监控配置
  ├── ml/              # 机器学习配置
  ├── alerts/          # 告警配置
  ├── cache/           # 缓存配置
  └── api/             # API配置
  ```

- **文件命名规则**:
  - YAML配置: `<component>_config.yaml`
  - JSON配置: `<component>_config.json`
  - 环境配置: `.env`（开发/测试/生产环境使用 `.env.<env>`）
  - 表配置: `table_config.yaml`
  - 策略配置: `strategy_config.yaml`

#### `tests/` - 测试目录
- **命名规则**:
  - 全小写

- **子目录结构**:
  ```
  tests/
  ├── unit/             # 单元测试
  ├── integration/      # 集成测试
  ├── e2e/              # 端到端测试
  ├── performance/      # 性能测试
  ├── acceptance/       # 验收测试
  ├── fixtures/         # 测试数据
  ├── mocks/            # Mock对象
  └── reports/          # 测试报告
  ```

- **文件命名规则**:
  - 单元测试: `test_<module>.py`（匹配 `src/<module>/`）
  - 集成测试: `test_<feature>_integration.py`
  - E2E测试: `test_<feature>_e2e.py` 或 `test_<page>.spec.ts`（前端）
  - 性能测试: `test_<component>_performance.py`
  - 验收测试: `test_user_acceptance.py`
  - Mock数据: `<entity>_fixture.py` 或 `mock_<data>.json`
  - 测试配置: `conftest.py`、`pytest.ini`

#### `scripts/` - 脚本目录
- **命名规则**:
  - 全小写，动词开头

- **子目录结构**:
  ```
  scripts/
  ├── dev/              # 开发工具脚本
  ├── maintenance/      # 维护脚本
  ├── deployment/       # 部署脚本
  ├── testing/          # 测试相关脚本
  ├── migration/        # 数据迁移脚本
  ├── cleanup/          # 清理脚本
  └── utils/            # 通用工具脚本
  ```

- **文件命名规则**:
  - 开发工具: `<action>_tool.py`
  - 维护脚本: `<action>_maintenance.sh`
  - 部署脚本: `deploy_<env>.sh`
  - 测试脚本: `run_<test_type>.sh`
  - 迁移脚本: `migrate_<to>_<from>.py`
  - 清理脚本: `cleanup_<target>.sh`
  - 工具脚本: `process_<data>.py`

#### `docs/` - 文档目录
- **命名规则**:
  - 全小写，单词用连字符

- **子目录结构**:
  ```
  docs/
  ├── 01-项目总览与核心规范/
  ├── 02-架构与设计文档/
  ├── 03-API与功能文档/
  ├── 04-测试与质量保障文档/
  ├── 05-部署与运维监控文档/
  ├── 06-项目管理与报告/
  ├── 归档文档/             # 已废弃/归档的文档
  ├── guides/             # 用户指南
  └── reports/           # 报告文档
  ```

- **文件命名规则**:
  - 核心文档: `README.md`、`CLAUDE.md`、`CHANGELOG.md`
  - 设计文档: `<feature>_design.md`
  - API文档: `api_<feature>.md`、`openapi_<version>.yaml`
  - 指南文档: `guides/<feature>.md`
  - 报告文档: `<report_type>_report_<date>.md`
  - 归档文档: `ARCHIVED_<year>.md`

#### `web/` - Web前端目录
- **命名规则**:
  - 全小写

- **子目录结构**:
  ```
  web/
  ├── frontend/         # 前端代码
  │   ├── src/
  │   │   ├── components/   # 组件
  │   │   ├── api/          # API调用
  │   │   ├── pages/        # 页面
  │   │   ├── utils/        # 工具
  │   │   ├── stores/       # 状态管理
  │   │   └── types/        # 类型定义
  │   ├── public/            # 静态资源
  │   └── tests/            # 测试
  └── backend/          # 后端代码
      ├── src/
      ├── api/          # API路由
      ├── services/      # 业务服务
      ├── models/        # 数据模型
      └── utils/         # 工具
  ```

- **文件命名规则**:
  - 前端组件: PascalCase（`UserProfile.ts`、`MarketChart.vue`）
  - API文件: PascalCase（`MarketApi.ts`、`IndicatorApi.ts`）
  - 工具文件: camelCase（`chartRenderer.ts`）
  - 页面组件: PascalCase（`Dashboard.vue`、`MarketView.vue`）
  - 后端路由: `__init__.py`、`<feature>_routes.py`
  - 后端服务: `<feature>_service.py`
  - 后端模型: PascalCase（`StockData.py`、`User.py`）

#### `data/` - 数据目录
- **命名规则**:
  - 全小写

- **子目录结构**:
  ```
  data/
  ├── cache/            # 缓存数据
  ├── models/            # 模型文件
  ├── backups/           # 备份数据
  ├── recovery/          # 恢复数据
  ├── exports/           # 导出数据
  ├── imports/           # 导入数据
  └── temp/             # 临时数据
  ```

- **文件命名规则**:
  - 缓存文件: `<data_type>.cache`、`cache_<index>.db`
  - 模型文件: `<model_name>.pkl`、`<model_name>.h5`
  - 备份文件: `<data>_<timestamp>_backup.<ext>`
  - 配置文件: `mystocks_config.json`、`alerts.json`
  - 导出文件: `<data>_<date>.csv`、`<data>_<date>.json`
  - 临时文件: `temp_<purpose>.<ext>`（临时文件必须清理）

---

## 📁 临时文件与缓存规则

### 临时文件命名
- **规则**: 必须使用 `temp_` 前缀
- **示例**:
  - ✅ `temp_data_export.json`
  - ✅ `temp_test_results.csv`
  - ❌ `temp_export.json`（缺少前缀）
  - ❌ `test_temp.json`（前缀不正确）

### 缓存文件命名
- **规则**: 必须使用 `.cache` 或 `.db` 后缀
- **示例**:
  - ✅ `redis_cache.db`
  - ✅ `model_cache.pkl`
  - ❌ `cache.db`（缺少描述）
  - ❌ `model.pkl`（缺少类型标识）

### 日志文件规则
- **规则**: 必须使用 `.log` 后缀，日志文件需有轮转机制
- **示例**:
  - ✅ `app.log`
  - ✅ `api_server.log`
  - ✅ `app.2025-12-30.log`（带日期）
  - ❌ `server.log`（缺少应用名）
  - ❌ `log.txt`（后缀错误）

### 备份文件规则
- **规则**: 必须使用 `_backup.<timestamp>` 后缀
- **示例**:
  - ✅ `table_config.yaml.backup_20251230`
  - ✅ `database_backup_20251230.sql`
  - ❌ `table_config.bak`（缺少时间戳）
  - ❌ `backup.sql`（缺少时间戳和内容标识）

### 报告文件规则
- **规则**: 必须使用 `_report_<date>` 后缀
- **示例**:
  - ✅ `performance_report_20251230.md`
  - ✅ `test_coverage_report.md`
  - ❌ `report.json`（缺少类型）
  - ❌ `summary.md`（缺乏时间戳）

---

## 🔧 文件清理与归档规则

### 需要清理的文件类型

#### 1. 临时文件（高优先级）
**清理规则**:
- **条件**: 创建时间 > 7天
- **操作**: 直接删除

**常见临时文件**:
- `temp_*.json`
- `temp_*.csv`
- `temp_*.sql`
- `temp_*.log`
- `.tmp` 文件
- `*.tmp` 文件

#### 2. 备份文件（中优先级）
**清理规则**:
- **条件**: 超过30天或已确认无需保留
- **操作**: 归档到 `data/backups/` 后删除

**常见备份文件**:
- `*_backup_*.sql`
- `*_backup_*.yaml`
- `*_backup_*.json`

#### 3. 日志文件（中优先级）
**清理规则**:
- **条件**: 超过14天
- **操作**: 压缩后归档

**日志轮转策略**:
- 当前日志: `<app>.log`
- 轮转日志: `<app>.<date>.log.gz`
- 归档目录: `logs/archive/`

#### 4. 报告文件（中优先级）
**清理规则**:
- **条件**: 超过90天
- **操作**: 移动到 `docs/reports/`

**常见报告文件**:
- 一次性测试报告
- 覆盖率报告
- 性能测试报告
- 技术债务分析报告

#### 5. 已归档的文档（低优先级）
**清理规则**:
- **条件**: 已完成并归档超过180天
- **操作**: 保留在 `docs/归档文档/`

---

## 📦 文件归档规范

### 归档目录结构
```
docs/归档文档/
├── 2024/
│   ├── Q1/
│   ├── Q2/
│   ├── Q3/
│   └── Q4/
├── 2025/
│   ├── Q1/
│   ├── Q2/
│   ├── Q3/
│   └── Q4/
├── obsolete/          # 已废弃的文档
└── templates/          # 文档模板
```

### 归档文件命名
- **格式**: `<year>/Q<quarter>/<document_type>_<name>_<version>.md`
- **示例**: `2025/Q1/phase5_completion_report_v1.0.md`

---

## ⚠️ 禁止的文件/目录

### 禁止的命名模式
- 驼峰命名目录（如 `MyModule/`）
- 空格或特殊字符（空格、`@`、`#`、`$`等）
- 混合语言命名（中英文混合）
- 过长的文件名（> 100字符）

### 禁止的文件后缀
- `.bak`（应使用 `_backup`）
- `.old`（应使用 `_backup`）
- `.tmp`（应使用 `temp_`）
- `~` 结尾的文件

### 禁止在根目录的文件
- 配置文件（应放入 `config/`）
- 日志文件（应放入 `logs/`）
- 临时文件（应放入 `data/temp/`）
- 数据文件（应放入 `data/`）

---

## 🎯 文件权限与所有权

### 文件权限规则
- **源代码文件**: `644`（可读写）
- **配置文件**: `600`（仅所有者可写）
- **脚本文件**: `755`（可执行）
- **日志文件**: `644`（可读写）

### 目录权限规则
- **源代码目录**: `755`（可进入）
- **配置目录**: `755`（可进入）
- **测试目录**: `755`（可进入）
- **日志目录**: `755`（可进入）

---

## 🔄 文件移动与重命名流程

### 移动文件到正确位置
1. **步骤1**: 创建目标目录结构
2. **步骤2**: 移动文件
3. **步骤3**: 验证文件可访问
4. **步骤4**: 更新导入路径
5. **步骤5**: 测试代码运行
6. **步骤6**: 删除旧位置文件

### 批量重命名规则
```bash
# 临时文件
find . -name "temp_*" -type f -mtime +7d -delete

# 日志文件
find logs/ -name "*.log" -mtime +14d -exec gzip {} \;

# 清理编译产物
find . -name "*.pyc" -type f -delete
find . -name "__pycache__" -type d -exec rm -rf {} \;
```

---

## 📊 文件大小与复杂度管理

### 文件大小限制
- **单个文件**: < 100MB
- **源文件**: < 10MB
- **配置文件**: < 1MB
- **测试文件**: < 5MB

### 目录大小限制
- **总大小**: < 10GB（源代码）
- **单目录**: < 2GB

### 代码行数限制
- **单个Python文件**: < 1000行
- **单个配置文件**: < 200行
- **单个测试文件**: < 300行

---

## ✅ 验收标准

### 文件整理完成标准
- [ ] 所有临时文件已清理
- [ ] 所有备份文件已归档
- [ ] 所有日志文件已轮转
- [ ] 目录结构符合规范
- [ ] 文件命名符合规则
- [ ] 文件权限正确设置
- [ ] 无冗余文件存在
- [ ] 导入路径已更新

### 代码质量检查
- [ ] 无循环导入
- [ ] 无硬编码路径
- [ ] 使用相对导入
- [ ] 配置文件统一管理
- [ ] 测试文件规范命名
- [ ] 文档与代码同步

---

## 📝 变更管理

### 文件整理记录
每次执行文件整理时，应记录：
1. 整理日期和时间
2. 整理的文件列表
3. 移动的文件数量
4. 删除的文件大小
5. 遇到的问题和解决方案
6. 影响范围和风险评估

### 回滚计划
如果整理后出现问题，提供：
1. 回滚脚本
2. 数据备份位置
3. 回滚步骤
4. 验证回滚成功

---

**文档维护者**: Main CLI
**审核状态**: ✅ 已审核
**下次审核**: 2026-01-30
