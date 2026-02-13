# 目标结构规格说明

> 本文档定义 reorganize-project-directory-structure 变更完成后的项目根目录目标状态。

## 目标根目录结构

```
mystocks_spec/
├── .amazonq/              # [禁区] AWS Q 配置
├── .archive/              # [禁区] 归档存储（新增，合并原 archived/archive/）
├── .benchmarks/           # [禁区] 性能基准
├── .claude/               # [禁区] Claude 配置
├── .claude-trace/         # [禁区] Claude 追踪
├── .config/               # [禁区] 项目配置
├── .cursor/               # [禁区] Cursor 配置
├── .gemini/               # [禁区] Gemini 配置
├── .git/                  # [禁区] Git 仓库
├── .github/               # [禁区] GitHub 配置
├── .migration/            # [禁区] 迁移记录
├── .mypy_cache/           # [禁区] MyPy 缓存
├── .omc/                  # [禁区] OMC 配置
├── .opencode/             # [禁区] OpenCode 配置
├── .playwright-mcp/       # [禁区] Playwright MCP
├── .pytest_cache/         # [禁区] Pytest 缓存
├── .ruff_cache/           # [禁区] Ruff 缓存
├── .shared/               # [禁区] 共享配置
├── .specify/              # [禁区] Specify 配置
├── .taskmaster/           # [禁区] Taskmaster 配置
├── .vscode/               # [禁区] VS Code 配置
├── .worktrees/            # [禁区] Git worktrees
├── .zencoder/             # [禁区] Zencoder 配置
├── .zenflow/              # [禁区] Zenflow 配置
│
├── src/                   # 核心业务代码
│   ├── adapters/
│   ├── core/
│   ├── data_access/
│   ├── db_manager/
│   ├── interfaces/
│   ├── monitoring/
│   ├── storage/
│   └── utils/
│
├── config/                # 所有配置文件
│   ├── docker-compose.test.yml
│   ├── docker-compose.prod.yml
│   ├── pytest.ini
│   ├── mypy.ini
│   └── ...
│
├── scripts/               # 脚本工具
│   ├── dev/               # 开发脚本
│   ├── deploy/            # 部署脚本
│   ├── database/          # 数据库脚本
│   └── maintenance/       # 维护脚本
│
├── docs/                  # 文档
│   ├── guides/            # 指南
│   ├── architecture/      # 架构文档
│   ├── api/               # API 文档
│   ├── standards/         # 标准规范
│   ├── reports/           # 报告
│   ├── plans/             # 计划
│   ├── reviews/           # 审查
│   └── legacy/            # 历史文档
│
├── tests/                 # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── web/                   # Web 前后端（子模块自治）
│   ├── frontend/
│   ├── backend/
│   └── api/
│
├── architecture/          # 架构定义
│
├── data/                  # 数据文件
│
├── openspec/              # OpenSpec 变更管理
│   ├── changes/
│   ├── specs/
│   └── project.md
│
├── reports/               # 生成的分析报告
│
├── services/              # 微服务（子模块自治）
│
├── gpu_api_system/        # GPU API 系统（可选）
│
│── # === 根文件（仅保留以下） ===
├── README.md              # 项目说明
├── CLAUDE.md              # Claude 指令
├── IFLOW.md               # IFlow 指令
├── __init__.py            # 包初始化
├── core.py                # 兼容入口 → src.core
├── data_access.py         # 兼容入口 → src.data_access
├── monitoring.py          # 兼容入口 → src.monitoring
├── unified_manager.py     # 兼容入口 → src.interfaces
├── pyproject.toml         # Python 项目配置
├── package.json           # Monorepo 根级工具依赖
├── vitest.config.ts       # 根级测试配置
├── tsconfig.json          # TypeScript 配置
├── requirements.txt       # Python 依赖
│
│── # === 根级隐藏文件（禁区） ===
├── .env                   # 环境变量
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略规则
├── .gitattributes         # Git 属性
├── .mcp.json              # MCP 配置
├── .pre-commit-config.yaml # Pre-commit 配置
└── .pylintrc              # Pylint 配置
```

## 量化目标

| 指标 | 当前值 | 目标值 | 变化 |
|------|--------|--------|------|
| 非隐藏根目录数 | 83 | 13 | -84% |
| 根文件数 | 50 | ~13 | -74% |
| 磁盘占用（可回收） | ~240GB | 0 | -240GB |
| 目录最大嵌套深度 | >8 | ≤5 | 规范化 |

## 验收标准

1. `find . -maxdepth 1 -type d ! -name '.*' | wc -l` 输出 ≤ 14（含 `.`）
2. `find . -maxdepth 1 -type f ! -name '.*' | wc -l` 输出 ≤ 15
3. `python -c "from src.core import *"` 正常执行
4. `python -c "from src.data_access import *"` 正常执行
5. 4 个兼容入口文件（core.py 等）正常工作
6. `cd web/frontend && npm run build` 正常执行
7. `pytest --co -q` 能收集到所有测试
8. 所有 GitHub Actions workflow 正常运行
9. 所有 23 个 dot-directories 完整无损
10. `git status` 无意外的未跟踪文件

## 不在范围内

- web/ 内部结构调整（子模块自治）
- services/ 内部结构调整（子模块自治）
- src/ 内部模块重构（另开 change）
- 代码逻辑修改（仅移动文件和更新路径）
