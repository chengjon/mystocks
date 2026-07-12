# MyStocks CI/CD 体系

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    MyStocks CI/CD 体系                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  开发阶段               提交阶段               部署阶段       │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ pre-commit│───→│ GitHub Actions│───→│  PM2 生产部署    │   │
│  │ 本地检查   │    │ 远程CI管道    │    │  (WSL)           │   │
│  └──────────┘    └──────────────┘    └──────────────────┘   │
│       │                │                      │             │
│       ▼                ▼                      ▼             │
│  • ruff lint     • 类型检查(Pyright)     • 重启后端服务     │
│  • black format  • P0质量门禁            • 重启前端服务     │
│  • 本地冒烟      • 冒烟测试(23用例)       • 健康检查         │
│  • 单元测试      • E2E测试               • 回滚机制         │
│                   • 安全扫描                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 三层 Pipeline

### Layer 1: 本地开发 (pre-commit)

触发: `git commit`
运行地: WSL 本地
耗时: < 30s
文件: `.pre-commit-config.yaml`

```
步骤:
  1. ruff lint (Python)
  2. black format check
  3. 单元测试 (pytest)
  4. 冒烟测试 (smoke_test.py) ← 新增
```

### Layer 2: CI 远程 (GitHub Actions)

触发: `push` / `PR` → main/develop
运行地: GitHub 托管 runner
文件: `.github/workflows/`

```
主干管道 (ci-cd.yml):
  1. scope-detect       → 检测变更范围
  2. lint               → ruff + black
  3. type-check         → pyright + mypy
  4. test               → pytest (单元/集成)
  5. smoke-test         → smoke_test.py (23用例)  ← 新增
  6. security-scan      → bandit
  7. build              → 构建前端
  8. report             → 测试报告

质量门禁 (p0-quality-gate.yml):
  - lint 失败 → 阻止PR合并
  - type-check 失败 → 阻止PR合并
  - smoke-test 失败 → 阻止PR合并  ← 新增

部署 (deploy.yml):
  - develop → staging (自动)
  - main → production (手动审批)
```

### Layer 3: 本地 Runner (自托管)

用于 WSL 环境，替代 GitHub Actions 在本地运行完整管道。

```bash
# 运行完整管道
python3 tests/ci/run_pipeline.py

# 快速冒烟
python3 smoke_test.py

# 单步测试
pytest tests/ -x -v
```

## 测试管道

```
smoke_test.py (23个用例, 6秒)
├── 2 服务进程检查
│   ├── Backend online (PM2)
│   └── Frontend online (PM2)
├── 1 登录验证
│   └── Auth login (JWT)
├── 15 后端API
│   ├── Dashboard概览
│   ├── 实时行情
│   ├── K线
│   ├── 龙虎榜
│   ├── 板块动向
│   ├── 概念动向
│   ├── 资金流向
│   ├── 自选组合
│   ├── 股票列表
│   ├── 策略列表
│   ├── 交易信号
│   ├── 头寸
│   ├── 健康检查
│   ├── 股票详情
│   └── 技术指标
├── 5 前端页面
│   ├── 首页
│   ├── Dashboard
│   ├── 实时行情
│   ├── 股票列表
│   └── 股票详情
└── 报告输出
```

## 文档索引

| 文档 | 用途 |
|------|------|
| `docs/operations/ci-cd/INDEX.md` | CI/CD 文档总索引 |
| `docs/operations/ci-cd/LOCAL_CI_INTEGRATION.md` | 本地开发CI集成 |
| `.github/workflows/ci-cd.yml` | 主干CI管道 |
| `.github/workflows/p0-quality-gate.yml` | P0质量门禁 |
| `.github/workflows/deploy.yml` | 部署管道 |
| `smoke_test.py` | 冒烟测试脚本 (23用例) |
| `tests/ci/run_pipeline.py` | 本地CI管道运行器 |
| `tests/ci/test_continuous_integration.py` | CI系统测试 |

## 运行方式

```bash
# 本地冒烟测试 (推荐)
cd /opt/claude/mystocks_spec
python3 smoke_test.py

# 本地完整CI管道
python3 tests/ci/run_pipeline.py

# pytest 单元测试
pytest tests/ -x -v -m "not slow"

# pre-commit 本地检查
pre-commit run --all-files
```

## 当前状态 (2026-07-12)

- ✅ 冒烟测试: 23/23 通过
- ✅ 后端API: 15/15 200
- ✅ 前端页面: 5/5 200
- ❌ 本地 runner: 未安装 (actions-runner)
- ❌ smoke_test.py: 尚未纳入 GitHub Actions workflow
- ❌ .pre-commit-config.yaml: 未包含冒烟测试