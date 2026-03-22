# 目录与文件整理通用规则 (Directory and File Organization Rules)

**版本**: 1.0
**适用范围**: 通用软件项目
**最后更新**: 2026-03-22

---

## 一、核心理念 (Core Philosophy)

### 1.1 根目录极简主义 (Root Directory Minimalism)

**原则**: 项目根目录应保持最小化，仅保留核心入口文件。

**根目录允许清单**:

| 类别 | 允许的文件 |
|------|-----------|
| **项目入口** | `README.md`, `LICENSE`, `CHANGELOG.md` |
| **AI助手配置** | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `IFLOW.md` |
| **Python工具链** | `pyproject.toml`, `requirements.txt`, `pytest.ini`, `mypy.ini`, `conftest.py` |
| **Node/E2E工具链** | `package.json`, `package-lock.json`, `tsconfig.json`, `vitest.config.*`, `playwright.config.*` |
| **部署配置** | `docker-compose*.yml`, `Dockerfile`, `pm2.config.js` |
| **规范系统** | `.mcp.json`, `opencode.json` |

**禁止在根目录出现**:
- `*.log` - 运行时日志
- `*.csv` - 生成的数据文件
- `*.tmp`, `*.bak` - 临时/备份文件
- `.coverage`, `coverage.xml` - 覆盖率报告
- `node_modules/`, `__pycache__/` - 依赖/缓存目录

---

## 二、标准目录结构 (Standard Directory Structure)

### 2.1 九大顶层目录

```
Project_Root/
├── src/                    # 源代码 (核心业务逻辑)
├── tests/                  # 测试文件 (独立顶层)
├── scripts/                # 脚本工具
├── config/                 # 配置文件
├── docs/                   # 文档
├── architecture/           # 架构设计文档 (独立顶层)
├── reports/                # 生成报告
├── archive/                # 归档文件 (独立顶层)
└── data/                   # 数据文件 (独立顶层)
```

### 2.2 各目录详细规则

#### 1. `src/` - 源代码目录

**规则**: 所有核心业务代码必须放入此目录。

```
src/
├── core/           # 核心模块 (配置、日志、工具类)
├── adapters/       # 适配器层 (外部接口封装)
├── services/       # 业务服务层
├── data_access/    # 数据访问层
├── interfaces/     # 接口定义
├── storage/        # 存储层
├── monitoring/     # 监控模块
└── utils/          # 工具函数
```

**命名规则**:
- 模块名使用 `snake_case`
- 每个目录必须包含 `__init__.py`

#### 2. `tests/` - 测试目录 (独立顶层)

**规则**: 所有测试文件统一放在此目录，与源代码物理隔离。

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/            # 端到端测试
└── conftest.py     # pytest 配置
```

**文件命名**:
- 测试文件: `test_*.py` 或 `*_test.py`
- 测试类: `TestClassName`
- 测试方法: `test_method_name`

#### 3. `scripts/` - 脚本工具目录

**规则**: 按功能分类组织脚本。

```
scripts/
├── runtime/        # 运行脚本 (run_*, save_*, monitor_*, *_demo.py)
├── database/       # 数据库脚本 (check_*, verify_*, create_*, init_*, migrate_*)
├── dev/            # 开发工具 (validate_*, analyze_*, generate_*)
└── maintenance/    # 维护脚本
```

**脚本命名前缀规则**:

| 前缀 | 含义 | 目标目录 |
|------|------|----------|
| `run_*` | 运行/启动脚本 | `scripts/runtime/` |
| `save_*` | 数据保存脚本 | `scripts/runtime/` |
| `monitor_*` | 监控脚本 | `scripts/runtime/` |
| `*_demo.py` | 演示脚本 | `scripts/runtime/` |
| `check_*` | 检查脚本 | `scripts/database/` |
| `verify_*` | 验证脚本 | `scripts/database/` |
| `create_*` | 创建脚本 | `scripts/database/` |
| `init_*` | 初始化脚本 | `scripts/database/` |
| `migrate_*` | 迁移脚本 | `scripts/database/` |
| `validate_*` | 验证工具 | `scripts/dev/` |
| `analyze_*` | 分析工具 | `scripts/dev/` |
| `generate_*` | 生成工具 | `scripts/dev/` |

#### 4. `config/` - 配置文件目录

**规则**: 所有项目级配置文件统一存放。

```
config/
├── *.yaml          # YAML 配置
├── *.yml           # YAML 配置 (docker-compose 等)
├── *.ini           # INI 配置
├── *.toml          # TOML 配置
└── *.json          # JSON 配置
```

**例外**: 工具链配置 (如 `pytest.ini`, `mypy.ini`) 可保留在根目录。

#### 5. `docs/` - 文档目录

**规则**: 按文档类型分类组织。

```
docs/
├── INDEX.md            # 文档总索引 (必需)
├── guides/             # 用户/开发者指南
│   ├── QUICKSTART.md   # 快速开始
│   ├── TUTORIALS.md    # 教程
│   └── TROUBLESHOOTING.md  # 故障排查
├── api/                # API 文档
│   └── REFERENCE.md    # API 参考
├── standards/          # 标准与规范
│   └── CODING_STANDARDS.md
├── operations/         # 运维文档
│   ├── DEPLOYMENT.md   # 部署指南
│   └── MONITORING.md   # 监控配置
└── archive/            # 归档文档
    └── deprecated/     # 废弃文档
```

**文档命名规则**:

| 文档类型 | 关键词 | 目标目录 |
|----------|--------|----------|
| 用户指南 | `GUIDE`, `TUTORIAL`, `SETUP` | `docs/guides/` |
| API文档 | `API`, `REFERENCE`, `ENDPOINT` | `docs/api/` |
| 标准规范 | `STANDARD`, `POLICY`, `RULE` | `docs/standards/` |
| 报告文档 | `REPORT`, `ANALYSIS`, `REVIEW` | `docs/reports/` 或 `reports/` |
| 架构文档 | `ARCHITECTURE`, `DESIGN`, `ADR` | `architecture/` |
| 归档文档 | 废弃/历史 | `docs/archive/` 或 `archive/` |

#### 6. `architecture/` - 架构文档目录 (独立顶层)

**规则**: 系统架构设计文档独立存放。

```
architecture/
├── OVERVIEW.md         # 架构概述
├── COMPONENTS.md       # 组件设计
├── DATABASE.md         # 数据库设计
├── PATTERNS.md         # 设计模式
├── STANDARDS.md        # 架构红线
└── adr/                # 架构决策记录 (ADR)
    ├── 001-*.md
    └── 002-*.md
```

#### 7. `reports/` - 生成报告目录

**规则**: 脚本生成的报告文件统一存放。

```
reports/
├── analysis/           # 分析报告
├── coverage/           # 覆盖率报告
├── performance/        # 性能报告
├── security/           # 安全审计
└── YYYYMMDD_HHMMSS_*.json  # 带时间戳的报告
```

**命名约定**: 时间戳格式 `YYYYMMDD_HHMMSS`

#### 8. `archive/` - 归档目录 (独立顶层)

**规则**: 不再使用但需保留的文件。

```
archive/
├── deprecated/         # 废弃代码
├── legacy/             # 历史版本
├── migrations/         # 迁移记录
└── tools/              # 旧工具
```

**归档标记**: 归档文件顶部应添加废弃声明。

#### 9. `data/` - 数据目录 (独立顶层)

**规则**: 项目数据文件存放。

```
data/
├── datasets/           # 数据集
├── backups/            # 备份
├── exports/            # 导出数据
└── samples/            # 示例数据
```

**注意**: 大型数据文件应通过 `.gitignore` 排除。

---

## 三、文件放置决策树 (File Placement Decision Tree)

```
创建/移动文件?
│
├─ 在根目录允许清单中? (README/CLAUDE/LICENSE/pyproject.toml/...)
│  ├─ 是 → 放置在根目录
│  └─ 否 → 继续
│
├─ 是测试文件? (test_*.py, *_test.py)
│  └─ → tests/ (unit/, integration/, e2e/)
│
├─ 是脚本文件? (.py, .sh)
│  ├─ run_*, save_*, monitor_*, *_demo.py → scripts/runtime/
│  ├─ check_*, verify_*, create_*, init_*, migrate_* → scripts/database/
│  └─ 其他开发工具 → scripts/dev/
│
├─ 是文档文件? (.md, .rst)
│  ├─ 用户/开发者指南 → docs/guides/
│  ├─ API文档 → docs/api/
│  ├─ 标准/规范 → docs/standards/
│  ├─ 架构/设计 → architecture/
│  └─ 废弃/历史 → archive/ 或 docs/archive/
│
├─ 是配置文件? (.yaml, .yml, .ini, .toml, .json)
│  └─ → config/
│
├─ 是报告/分析? (.json, .txt 带时间戳)
│  └─ → reports/
│
├─ 是归档/废弃文件?
│  └─ → archive/
│
└─ 是数据文件?
   └─ → data/
```

---

## 四、自动化分类规则 (Automated Classification Rules)

### 4.1 基于文件名关键词的分类

| 关键词模式 | 目标目录 | 说明 |
|------------|----------|------|
| `API`, `ENDPOINT`, `REFERENCE` | `docs/api/` | API 相关文档 |
| `GUIDE`, `TUTORIAL`, `SETUP`, `INTEGRATION` | `docs/guides/` | 指南类文档 |
| `REPORT`, `SESSION`, `ANALYSIS`, `STATUS` | `reports/` | 报告类文件 |
| `ARCHITECTURE`, `DESIGN`, `ADR` | `architecture/` | 架构设计文档 |
| `TROUBLESHOOTING`, `NEXT_STEPS` | `docs/guides/` | 问题排查指南 |
| `TEST_VALIDATION`, `TEST_PLAN` | `tests/` | 测试文档 |
| `TASK_*`, `COMPLETION`, `VERIFICATION` | `reports/` | 任务报告 |

### 4.2 基于文件扩展名的分类

| 扩展名 | 默认目录 | 例外 |
|--------|----------|------|
| `.py` (test) | `tests/` | - |
| `.py` (script) | `scripts/` | `src/` 中的业务代码 |
| `.md` | `docs/` | 根目录允许的入口文档 |
| `.yaml`, `.yml` | `config/` | `.github/workflows/` |
| `.json` (config) | `config/` | `reports/` 中的报告 |
| `.json` (report) | `reports/` | - |
| `.log`, `.tmp` | 不应入库 | 通过 `.gitignore` 排除 |

---

## 五、Git 操作最佳实践 (Git Best Practices)

### 5.1 文件移动必须保留历史

```bash
# ✅ 正确: 使用 git mv 保留文件历史
git mv old_location/file.md new_location/file.md

# ❌ 错误: 使用 mv 会断开历史
mv old_location/file.md new_location/file.md
git add new-location/file.md
```

### 5.2 移动文件后必须更新引用

```bash
# 1. 搜索所有引用
grep -r "old-location/file" .

# 2. 更新文档链接
# 3. 更新导入路径
# 4. 提交时说明变更范围
git commit -m "refactor: move file.md to docs/guides/ per organization rules"
```

### 5.3 提交信息规范

```bash
# 文件整理类提交
git commit -m "refactor: organize files according to directory structure rules

- Move test_*.py to tests/unit/
- Move config files to config/
- Archive deprecated documentation to docs/archive/"
```

---

## 六、合规检查清单 (Compliance Checklist)

### 6.1 新文件创建前检查

- [ ] 确认文件用途 (测试/脚本/文档/配置/报告)
- [ ] 对照决策树确定正确目录
- [ ] 确认命名符合规范
- [ ] 直接在正确目录创建

### 6.2 文件整理后验证

- [ ] 根目录仅包含允许清单中的文件
- [ ] 所有脚本分类正确 (`scripts/{runtime,database,dev}/`)
- [ ] 所有文档分类正确 (`docs/{guides,api,standards}/`)
- [ ] 所有配置文件在 `config/`
- [ ] 所有报告在 `reports/`
- [ ] 移动后的脚本导入路径已更新
- [ ] 文档链接已更新
- [ ] `git status` 显示移动 (非删除+新增)
- [ ] 测试通过

---

## 七、常见错误与纠正 (Common Mistakes)

| 错误 | 正确做法 |
|------|----------|
| 在根目录创建测试文件 | 放入 `tests/` |
| 在根目录创建脚本 | 放入 `scripts/` 对应子目录 |
| 使用 `mv` 而非 `git mv` | 始终用 `git mv` 保留历史 |
| 移动后忘记更新引用 | 搜索并更新所有链接和导入 |
| 测试文件与源码混放 | 物理隔离到 `tests/` |
| 配置文件散落各处 | 集中到 `config/` |
| 归档文件无标记 | 添加废弃声明和时间戳 |

---

## 八、治理策略配置示例 (Governance Policy Example)

### 8.1 YAML 格式的治理策略

```yaml
version: 1

root:
  allowed_files:
    - README.md
    - LICENSE
    - CLAUDE.md
    - AGENTS.md
    - pyproject.toml
    - requirements.txt
    - package.json
  allowed_directories:
    - src
    - tests
    - scripts
    - config
    - docs
    - architecture
    - reports
    - archive
    - data
  forbidden_file_patterns:
    - pattern: "*.log"
      message: "日志文件不应入库"
      recommendation: "添加到 .gitignore"
    - pattern: "*.tmp"
      message: "临时文件不应入库"
      recommendation: "使用后删除"
    - pattern: ".coverage"
      message: "覆盖率文件不应入库"
      recommendation: "移至 reports/coverage/"

rules:
  - id: reports-convergence
    severity: warning
    match_any:
      - docs/**/*_reports/**
      - docs/**/completion_reports/**
    message: "报告文件应集中存放"
    recommendation: "移至 reports/"
```

---

## 九、索引维护 (Index Maintenance)

### 9.1 文档索引要求

每个主要目录应包含 `INDEX.md` 或 `README.md`:

```
docs/INDEX.md          # 文档总索引
docs/api/INDEX.md      # API 文档索引
architecture/INDEX.md  # 架构文档索引
scripts/README.md      # 脚本说明
```

### 9.2 新增文档时更新索引

- 新增 API 文档 → 更新 `docs/api/INDEX.md`
- 新增架构文档 → 更新 `architecture/INDEX.md`
- 新增标准文档 → 更新 `docs/standards/INDEX.md`

---

## 十、生命周期管理 (Lifecycle Management)

### 10.1 文件生命周期

```
创建 → 活跃使用 → 降级归档 → 最终删除
 │         │           │           │
 └─────────┴───────────┴───────────┴── 记录变更历史
```

### 10.2 归档时机

- 6个月未修改的文档 → 考虑归档
- 已废弃的功能代码 → 标记后归档
- 一次性分析报告 → 保留3个月后归档
- 版本迁移记录 → 永久保留

---

## 附录 A: 目录结构模板

```
Project_Root/
├── README.md
├── CLAUDE.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── package.json
│
├── src/
│   ├── __init__.py
│   ├── core/
│   ├── adapters/
│   ├── services/
│   └── utils/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/
│   ├── runtime/
│   ├── database/
│   ├── dev/
│   └── maintenance/
│
├── config/
│   ├── app.yaml
│   └── docker-compose.yml
│
├── docs/
│   ├── INDEX.md
│   ├── guides/
│   ├── api/
│   ├── standards/
│   └── archive/
│
├── architecture/
│   ├── OVERVIEW.md
│   └── adr/
│
├── reports/
│   ├── analysis/
│   └── coverage/
│
├── archive/
│   └── deprecated/
│
└── data/
    └── samples/
```

---

## 附录 B: 快速参考卡

| 文件类型 | 放置位置 | 示例 |
|----------|----------|------|
| 单元测试 | `tests/unit/` | `test_manager.py` |
| 集成测试 | `tests/integration/` | `test_database.py` |
| 运行脚本 | `scripts/runtime/` | `run_server.py` |
| 数据库脚本 | `scripts/database/` | `check_tables.py` |
| 开发工具 | `scripts/dev/` | `generate_types.py` |
| 用户指南 | `docs/guides/` | `QUICKSTART.md` |
| API文档 | `docs/api/` | `REFERENCE.md` |
| 架构文档 | `architecture/` | `SYSTEM_DESIGN.md` |
| 编码规范 | `docs/standards/` | `CODING_STANDARDS.md` |
| 分析报告 | `reports/` | `analysis_20260322.json` |
| 配置文件 | `config/` | `app_config.yaml` |
| 归档文件 | `archive/` | `old_migration.md` |

---

**参考来源**: 本文档整理自 MyStocks 项目的目录治理规范，包括:
- `openspec/specs/directory-governance/spec.md`
- `openspec/specs/file-organization/spec.md`
- `governance/mainline/policies/directory-structure.yaml`
- `.claude/hooks/FILE_ORGANIZATION_GUIDE.md`

**许可**: 本规则文档可自由复用于任何软件项目。
