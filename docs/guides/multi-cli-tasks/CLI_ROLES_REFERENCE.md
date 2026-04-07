# CLI角色查看指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: v2.1
**更新时间**: 2026-01-01
**配置文件**: [`CLIS/config.yaml`](../../CLIS/config.yaml)
**相关工具**: [`scripts/dev/cli_config_manager.py`](../../scripts/dev/cli_config_manager.py)

---

## 📋 目录

1. [查看所有可用角色](#查看所有可用角色)
2. [当前预定义的角色](#当前预定义的角色)
3. [CLI如何报到注册](#cli如何报到注册)
4. [创建新的CLI角色](#创建新的cli角色)
5. [查看特定CLI详情](#查看特定cli详情)
6. [启用/禁用CLI](#启用禁用cli)
7. [角色配置参考](#角色配置参考)

---

## 查看所有可用角色

### 方法1: 查看配置文件

```bash
cat CLIS/config.yaml
```

**优点**: 完整查看所有配置细节
**缺点**: 需要手动解析YAML结构

### 方法2: 使用命令行工具 ⭐ 推荐

```bash
# 只显示启用的CLI
python scripts/dev/cli_config_manager.py --list

# 显示所有CLI（包括禁用的）
python scripts/dev/cli_config_manager.py --list --show-disabled
```

**优点**: 格式化输出，易于阅读
**缺点**: 需要运行Python脚本

---

## 当前预定义的角色

根据配置文件，系统预定义了 **7个CLI角色**：

### ✅ 已启用的角色 (4个)

| CLI名称 | 类型 | 角色 | 描述 | 能力 | 任务范围 |
|---------|------|------|------|------|----------|
| **main** | coordinator | N/A | 主协调器，负责任务分配和CLI协调 | coordination, monitoring, task_assignment, conflict_resolution | 所有协调任务 |
| **web** | worker | **frontend_developer** | 前端开发，负责Vue组件和UI实现 | frontend, Vue, UI-design, CSS, API-integration | `task-1.*`, `feature-web-*` |
| **api** | worker | **backend_developer** | 后端开发，负责API和业务逻辑 | backend, FastAPI, authentication, API-design, database | `task-2.*`, `feature-api-*` |
| **db** | worker | **database_admin** | 数据库管理，负责查询优化和数据维护 | database, PostgreSQL, TDengine, SQL, optimization | `task-3.*`, `optimization-*` |

### ❌ 默认禁用的角色 (3个)

| CLI名称 | 类型 | 角色 | 描述 | 能力 | 任务范围 |
|---------|------|------|------|------|----------|
| **it/worker1** | worker | **general_developer** | 通用开发助手 | python, testing, documentation | `task-*` |
| **it/worker2** | worker | **general_developer** | 通用开发助手 | python, testing, bugfix | `task-*` |
| **it/worker3** | worker | **general_developer** | 通用开发助手 | python, refactoring, optimization | `task-*` |

---

## CLI如何报到注册

### 报到流程

```
CLI启动 → 执行报到命令 → main收到请求 → main确认角色 → CLI收到确认消息
```

### 报到命令示例

**示例1: 注册为前端开发者 (web)**

```bash
python scripts/dev/cli_registration.py \
  --register \
  --cli=web \
  --type=worker \
  --capabilities="frontend,Vue,UI-design,CSS,API-integration"
```

**示例2: 注册为后端开发者 (api)**

```bash
python scripts/dev/cli_registration.py \
  --register \
  --cli=api \
  --type=worker \
  --capabilities="backend,FastAPI,authentication,API-design,database"
```

**示例3: 注册为数据库管理员 (db)**

```bash
python scripts/dev/cli_registration.py \
  --register \
  --cli=db \
  --type=worker \
  --capabilities="database,PostgreSQL,TDengine,SQL,optimization"
```

**示例4: 注册为主协调器 (main)**

```bash
python scripts/dev/cli_registration.py \
  --register \
  --cli=main \
  --type=coordinator \
  --capabilities="coordination,monitoring,task_assignment,conflict_resolution"
```

### main确认报到

```bash
# main确认CLI报到并分配角色
python scripts/dev/cli_registration.py \
  --confirm \
  --cli=web \
  --role="frontend_developer" \
  --tasks="task-1.1,task-1.2"
```

### 验证报到状态

```bash
# 方法1: 查看报到信息
cat CLIS/main/registrations.json | jq .

# 方法2: 查看CLI收到的确认消息
cat CLIS/web/mailbox/main_confirmation_*.md
```

---

## 创建新的CLI角色

### 方法1: 编辑配置文件 ⭐ 推荐

**步骤**:

1. **编辑配置文件**:
```bash
vim CLIS/config.yaml
```

2. **添加新的CLI定义**:
```yaml
cli_definitions:
  devops:
    enabled: true
    type: worker
    role: "devops_engineer"
    description: "DevOps工程师，负责部署和运维"

    capabilities:
      - Docker
      - Kubernetes
      - CI-CD
      - monitoring

    task_scope:
      include:
        - "deployment-*"
        - "devops-*"
        - "infrastructure-*"
      exclude:
        - "*-test"

    limits:
      max_concurrent_tasks: 2
      max_hours_per_task: 8
```

3. **验证配置**:
```bash
# 查看新添加的CLI
python scripts/dev/cli_config_manager.py --list --show-disabled
```

### 方法2: 使用命令行工具从模板创建

```bash
# 从worker模板创建新CLI
python scripts/dev/cli_config_manager.py --create-cli=devops --template=worker

# 从coordinator模板创建新CLI
python scripts/dev/cli_config_manager.py --create-cli=backup-main --template=coordinator
```

**然后编辑config.yaml添加具体的能力和任务范围**

---

## 查看特定CLI详情

### 命令格式

```bash
python scripts/dev/cli_config_manager.py --info=<CLI名称>
```

### 示例

**查看web CLI详情**:
```bash
python scripts/dev/cli_config_manager.py --info=web
```

**输出示例**:
```
============================================================
CLI详细信息: web
============================================================
类型: worker
角色: frontend_developer
描述: 前端开发，负责Vue组件和UI实现
能力: frontend, Vue, UI-design, CSS, API-integration
任务范围:
  包含: ['task-1.*', 'feature-web-*']
  排除: ['task-1.*.test']
工作限制:
  最大并发任务: 3
  最大任务工时: 16小时
============================================================
```

**查看api CLI详情**:
```bash
python scripts/dev/cli_config_manager.py --info=api
```

**查看db CLI详情**:
```bash
python scripts/dev/cli_config_manager.py --info=db
```

---

## 启用/禁用CLI

### 启用已禁用的CLI

**步骤**:

1. **编辑配置文件**:
```bash
vim CLIS/config.yaml
```

2. **修改enabled字段**:
```yaml
it/worker1:
  enabled: true  # 从false改为true
  type: worker
  role: "general_developer"
  ...
```

3. **验证**:
```bash
python scripts/dev/cli_config_manager.py --list --show-disabled
```

### 禁用已启用的CLI

```bash
# 编辑config.yaml
vim CLIS/config.yaml

# 将enabled: true改为enabled: false
web:
  enabled: false  # 从true改为false
  ...
```

---

## 角色配置参考

### CLI配置结构

```yaml
cli_definitions:
  <CLI名称>:
    enabled: true              # 是否启用 (true/false)
    type: worker               # 类型 (coordinator/worker)
    role: "角色名称"           # 角色标识

    description: "描述"       # CLI功能描述

    capabilities:              # 能力列表
      - skill1
      - skill2
      - skill3

    task_scope:                # 任务范围
      include:                 # 包含的任务（支持通配符）
        - "task-1.*"
        - "feature-*"
      exclude:                 # 排除的任务
        - "task-1.*.test"

    limits:                    # 工作限制
      max_concurrent_tasks: 3  # 最大并发任务数
      max_hours_per_task: 16   # 单个任务最大工时
```

### CLI类型说明

| 类型 | 用途 | 示例 | 特殊配置 |
|------|------|------|----------|
| **coordinator** | 协调器 | main | 需要`coordinator_config`配置 |
| **worker** | 工作CLI | web, api, db, worker* | 需要`task_scope`和`limits`配置 |

### 角色命名规范

**推荐命名**:
- **角色**: 使用下划线分隔的小写单词
  - ✅ `frontend_developer`
  - ✅ `backend_developer`
  - ✅ `database_admin`
  - ❌ `Frontend-Developer`

- **CLI名称**: 使用小写单词和连字符
  - ✅ `web`, `api`, `db`
  - ✅ `it/worker1`, `it/worker2`
  - ❌ `Web`, `API`, `Worker1`

### 能力标签规范

**前端能力**: `frontend`, `Vue`, `React`, `UI-design`, `CSS`, `TypeScript`
**后端能力**: `backend`, `FastAPI`, `authentication`, `API-design`, `microservices`
**数据库能力**: `database`, `PostgreSQL`, `TDengine`, `SQL`, `optimization`
**测试能力**: `testing`, `pytest`, `e2e`, `integration-test`
**DevOps能力**: `Docker`, `Kubernetes`, `CI-CD`, `monitoring`

### 任务范围通配符

**通配符规则**:
- `*` 匹配任意字符
- `task-1.*` 匹配 `task-1.1`, `task-1.2`, `task-1.a` 等
- `feature-*` 匹配所有以 `feature-` 开头的任务

**示例**:
```yaml
task_scope:
  include:
    - "task-1.*"        # task-1.1, task-1.2, ...
    - "feature-*"       # feature-web, feature-api, ...
    - "bugfix-*"        # bugfix-login, bugfix-ui, ...
  exclude:
    - "task-1.*.test"  # 排除所有test任务
    - "*-deprecated"   # 排除所有废弃任务
```

---

## 常见问题

### Q1: 如何知道有哪些可用的CLI角色？

```bash
# 查看所有启用的CLI
python scripts/dev/cli_config_manager.py --list

# 查看所有CLI（包括禁用的）
python scripts/dev/cli_config_manager.py --list --show-disabled
```

### Q2: CLI报到时role和capabilities有什么区别？

- **role**: CLI的角色名称（如 `frontend_developer`），用于标识CLI的身份
- **capabilities**: CLI的能力列表（如 `frontend,Vue,UI-design`），用于任务匹配

**建议**: capabilities应该与config.yaml中定义的能力保持一致

### Q3: 两个CLI可以有相同的role吗？

**可以**，但不推荐。每个CLI应该有独特的角色和职责。

**错误示例**:
```yaml
web:
  role: "developer"

api:
  role: "developer"  # ❌ 不推荐：角色重复
```

**正确示例**:
```yaml
web:
  role: "frontend_developer"  # ✅ 明确区分

api:
  role: "backend_developer"   # ✅ 明确区分
```

### Q4: 如何测试新创建的CLI角色？

```bash
# 步骤1: 创建CLI
python scripts/dev/cli_config_manager.py --create-cli=test-worker --template=worker

# 步骤2: 编辑config.yaml添加配置
vim CLIS/config.yaml

# 步骤3: 查看CLI详情
python scripts/dev/cli_config_manager.py --info=test-worker

# 步骤4: 测试任务匹配
python scripts/dev/cli_config_manager.py --match=test-task-1 --skills="python"

# 步骤5: 执行报到
python scripts/dev/cli_registration.py --register --cli=test-worker --type=worker --capabilities="python"
```

### Q5: 修改配置后需要重启系统吗？

**不需要**。配置文件会在下次操作时自动加载。

**但如果是**: 修改已启动CLI的配置（如enabled状态），建议重启该CLI以应用新配置。

---

## 相关文档

- **[配置系统完整指南](./CONFIG_SYSTEM_GUIDE.md)** - YAML配置文件详细说明
- **[CLI报到完整指南](./CLI_REGISTRATION_GUIDE.md)** - 报到流程、API文档、故障排查
- **[任务池使用指南](./TASK_POOL_USAGE_GUIDE.md)** - 任务发布、认领、更新
- **[Multi-CLI快速参考](../../CLIS/README.md)** - 命令速查表

---

## 命令速查

```bash
# 查看所有启用的CLI
python scripts/dev/cli_config_manager.py --list

# 查看所有CLI（包括禁用的）
python scripts/dev/cli_config_manager.py --list --show-disabled

# 查看特定CLI详情
python scripts/dev/cli_config_manager.py --info=<CLI名称>

# 测试任务匹配
python scripts/dev/cli_config_manager.py --match=<任务ID> --skills="<技能>"

# 创建新CLI
python scripts/dev/cli_config_manager.py --create-cli=<CLI名称> --template=<模板>

# CLI报到
python scripts/dev/cli_registration.py --register --cli=<CLI名称> --type=<类型> --capabilities="<能力>"

# main确认报到
python scripts/dev/cli_registration.py --confirm --cli=<CLI名称> --role="<角色>" --tasks="<任务列表>"
```

---

**文档维护**: 当config.yaml中添加或修改CLI定义时，请更新本文档
**最后更新**: 2026-01-01
**维护者**: Main CLI (Claude Code)
