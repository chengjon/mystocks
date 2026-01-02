# Multi-CLI 配置系统使用指南

**版本**: v2.1
**更新时间**: 2026-01-01
**核心文件**: [`CLIS/config.yaml`](../../CLIS/config.yaml)

---

## 📋 目录

1. [系统概述](#系统概述)
2. [配置文件说明](#配置文件说明)
3. [快速开始](#快速开始)
4. [三种任务分配模式](#三种任务分配模式)
5. [跨项目配置](#跨项目配置)
6. [配置CLI定义](#配置cli定义)
7. [交互式任务分配](#交互式任务分配)
8. [常见问题](#常见问题)

---

## 系统概述

### 🎯 解决的问题

**问题1**: CLI分配任务时是否要征求用户意见？
- ✅ **解决方案**: 提供3种任务分配模式（自动/交互/手动）

**问题2**: 要建立几个CLI助手？
- ✅ **解决方案**: 通过配置文件定义，不硬编码

**问题3**: 换项目后CLI功能不同怎么办？
- ✅ **解决方案**: 配置文件驱动，不同项目不同配置

**问题4**: 能否通过配置文件规定CLI名称和任务范围？
- ✅ **解决方案**: 完整的CLI定义和任务范围配置

### 核心特性

**配置驱动** - 所有CLI通过YAML配置文件定义
**灵活适配** - 支持跨项目配置
**智能分配** - 基于技能和任务范围自动匹配
**交互确认** - 可选的交互式任务分配确认
**模板创建** - 从模板快速创建新CLI

---

## 配置文件说明

### 配置文件位置

```
CLIS/
├── config.yaml          # ⭐ 主配置文件（定义所有CLI）
├── README.md            # 快速参考
└── ... (各CLI目录)
```

### 配置文件结构

```yaml
multi_cli:
  version: "2.1"              # 配置版本
  project_name: "项目名称"     # 项目标识
  task_assignment_mode: "auto" # 任务分配模式
  auto_coordinate: true       # 是否自动协调

cli_definitions:             # CLI定义
  main:                      # CLI名称
    enabled: true             # 是否启用
    type: coordinator         # 类型（coordinator/worker）
    role: "协调器"             # 角色
    capabilities: [...]        # 能力列表
    task_scope:               # 任务范围
      include: [...]          # 包含的任务
      exclude: [...]          # 排除的任务
    limits:                    # 工作限制
      max_concurrent_tasks: 3  # 最大并发任务数

assignment_rules:            # 分配规则
  - name: "skill_based_assignment"
    enabled: true
    priority: 1
```

---

## 快速开始

### 1. 查看当前配置

```bash
# 列出所有启用的CLI
python scripts/dev/cli_config_manager.py --list

# 查看特定CLI详情
python scripts/dev/cli_config_manager.py --info=web

# 测试任务匹配
python scripts/dev/cli_config_manager.py --match=task-1.1 --skills="frontend,Vue"
```

### 2. 修改任务分配模式

```bash
# 设置为自动模式（main自动分配，不询问）
python scripts/dev/cli_config_manager.py --set-mode=auto

# 设置为交互模式（main询问后再分配）⭐ 推荐
python scripts/dev/cli_config_manager.py --set-mode=interactive

# 设置为手动模式（main不自动分配，需手动指定）
python scripts/dev/cli_config_manager.py --set-mode=manual
```

### 3. 创建新的CLI

```bash
# 从worker模板创建CLI
python scripts/dev/cli_config_manager.py --create-cli=worker4 --template=worker

# 从coordinator模板创建CLI
python scripts/dev/cli_config_manager.py --create-cli=backup-main --template=coordinator

# 然后编辑 config.yaml 添加具体的能力和任务范围
```

---

## 三种任务分配模式

### 模式1: 自动模式 (auto)

**适用场景**: 高度信任自动化，不需要人工干预

```yaml
multi_cli:
  task_assignment_mode: "auto"
```

**行为**:
- main自动分配任务给匹配的CLI
- 无需确认，直接分配
- 适合成熟的、稳定的项目

**示例**:
```bash
# main发布任务后，自动分配给web
python scripts/dev/task_pool.py --publish --task=task-1.1 --title="..." --skills="frontend"
# → 自动分配给web，无需确认
```

---

### 模式2: 交互模式 (interactive) ⭐ 推荐

**适用场景**: 需要人工确认重要任务分配

```yaml
multi_cli:
  task_assignment_mode: "interactive"
```

**行为**:
- main建议分配的CLI
- **询问用户是否确认**
- 用户可以：
  - 确认建议的CLI (y)
  - 拒绝分配 (n)
  - 查看CLI详情 (v)
  - 选择其他CLI (e)

**示例**:
```bash
python scripts/dev/task_pool.py --publish --task=task-1.1 --title="..." --skills="frontend"
```

**输出**:
```
============================================================
📋 任务分配确认
============================================================
任务ID: task-1.1
任务标题: 实现Web前端主页
任务描述: 使用Vue 3实现响应式主页...
优先级: HIGH
需要技能: frontend, Vue, UI-design
建议分配给: web
============================================================
是否确认分配？(y/n/e=edit/v=view_cli):
```

**交互命令**:
- `y` / `yes` - 确认分配给建议的CLI
- `n` / `no` - 取消分配
- `v` - 查看建议的CLI详细信息
- `e` - 手动输入要分配的CLI名称

---

### 模式3: 手动模式 (manual)

**适用场景**: 完全人工控制任务分配

```yaml
multi_cli:
  task_assignment_mode: "manual"
```

**行为**:
- main不自动分配任务
- 任务保持在任务池
- 需要手动认领

**示例**:
```bash
# main发布任务
python scripts/dev/task_pool.py --publish --task=task-1.1 ...

# CLI主动认领（main不分配）
python scripts/dev/task_pool.py --claim --task=task-1.1 --cli=web
```

---

## 跨项目配置

### 项目1: MyStocks项目

**配置文件**: `CLIS/config.yaml`

```yaml
multi_cli:
  project_name: "mystocks_spec"
  task_assignment_mode: "interactive"

cli_definitions:
  web:
    enabled: true
    role: "frontend_developer"
    capabilities: [frontend, Vue, UI-design]
    task_scope:
      include: ["task-1.*"]
  api:
    enabled: true
    role: "backend_developer"
    capabilities: [backend, FastAPI, API-design]
    task_scope:
      include: ["task-2.*"]
```

### 项目2: 电商项目

**配置文件**: `CLIS/config.ecommerce.yaml`

```yaml
multi_cli:
  project_name: "ecommerce_platform"
  task_assignment_mode: "auto"  # 自动模式

cli_definitions:
  frontend:
    enabled: true
    role: "vue_developer"
    capabilities: [Vue, React, TypeScript]
    task_scope:
      include: ["frontend-*", "ui-*"]

  payment:
    enabled: true
    role: "payment_specialist"
    capabilities: [payment-gateway, Stripe, PayPal]
    task_scope:
      include: ["payment-*"]

  inventory:
    enabled: true
    role: "inventory_manager"
    capabilities: [database, Redis, optimization]
    task_scope:
      include: ["inventory-*"]
```

**使用不同配置**:
```bash
# 使用默认配置
python scripts/dev/cli_config_manager.py

# 使用电商项目配置
python scripts/dev/cli_config_manager.py --config=CLIS/config.ecommerce.yaml
```

---

## 配置CLI定义

### 基础配置

```yaml
cli_definitions:
  # 最小配置
  worker1:
    enabled: true          # 是否启用
    type: worker            # 类型（coordinator/worker）
    capabilities: []       # 能力列表
```

### 完整配置

```yaml
cli_definitions:
  web:
    enabled: true
    type: worker
    role: "frontend_developer"           # 角色名称
    description: "前端开发，负责Vue组件"   # 描述
    capabilities:                        # 能力列表
      - frontend
      - Vue
      - UI-design
      - CSS
      - API-integration

    # 任务范围（支持通配符）
    task_scope:
      include:              # 包含的任务
        - "task-1.*"        # task-1.开头的所有任务
        - "feature-web-*"   # feature-web-开头的所有任务
      exclude:              # 排除的任务
        - "task-1.*.test"  # 排除所有测试任务

    # 工作限制
    limits:
      max_concurrent_tasks: 3     # 最大并发任务数
      max_hours_per_task: 16      # 单个任务最大工时
```

### 启用/禁用CLI

```yaml
cli_definitions:
  web:
    enabled: true    # ✅ 启用

  worker1:
    enabled: false   # ❌ 禁用（默认不启动）

  worker2:
    enabled: false   # ❌ 禁用
```

**查看所有CLI（包括禁用的）**:
```bash
python scripts/dev/cli_config_manager.py --list --show-disabled
```

---

## 交互式任务分配

### 配置交互式规则

```yaml
interactive_config:
  # 高优先级任务是否需要确认
  confirm_on_high_priority: true

  # 超时任务是否需要确认
  confirm_on_long_tasks: true
  long_task_threshold: 16      # 小时

  # 跨技能任务是否需要确认
  confirm_on_cross_skill: true

  # 默认等待时间（秒）
  default_timeout: 60
```

### 交互式分配示例

**场景1: 高优先级任务**

```bash
# 发布高优先级任务
python scripts/dev/task_pool.py \
  --publish \
  --task=critical-1 \
  --title="修复登录Bug" \
  --priority=HIGH \
  --skills="authentication,security"
```

**交互提示**:
```
============================================================
📋 任务分配确认
============================================================
任务ID: critical-1
任务标题: 修复登录Bug
优先级: HIGH 🔴
需要技能: authentication, security
建议分配给: api
============================================================
⚠️  高优先级任务，建议确认后再分配
是否确认分配？(y/n/e=edit/v=view_cli):
```

**场景2: 跨技能任务**

```bash
# 发布需要多种技能的任务
python scripts/dev/task_pool.py \
  --publish \
  --task=fullstack-1 \
  --title="全栈功能实现" \
  --skills="frontend,backend,database"
```

**交互提示**:
```
⚠️  跨技能任务（需要frontend, backend, database）
建议分配给: api
技能匹配度: 1/3（仅backend匹配）
是否确认分配？(y/n/e=edit/v=view_cli):
```

**场景3: 查看CLI详情后再决定**

```
是否确认分配？(y/n/e=edit/v=view_cli): v

============================================================
CLI详细信息: api
============================================================
类型: worker
角色: backend_developer
描述: 后端开发，负责API和业务逻辑
能力: backend, FastAPI, authentication, API-design, database
任务范围:
  包含: ['task-2.*', 'feature-api-*']
  排除: []
工作限制:
  最大并发任务: 2
  最大任务工时: 12小时
============================================================

是否确认分配？(y/n/e=edit/v=view_cli):
```

---

## 常见问题

### Q1: 如何决定使用几种分配模式？

**推荐策略**:
- **项目初期/团队新成员** → `interactive`（交互模式，便于学习和指导）
- **成熟项目/稳定团队** → `auto`（自动模式，高效）
- **关键任务/生产环境** → `manual`（手动模式，完全控制）

### Q2: 要创建多少个CLI？

**推荐配置**:
- **小型项目**（2-3人）: main + 2-3个worker
- **中型项目**（4-6人）: main + 4-6个worker
- **大型项目**（7+人）: main + 多个专用CLI + 通用worker池

**原则**: 按功能领域划分，而不是按人数

### Q3: 不同项目的CLI配置差异大怎么办？

**解决方案**:
1. **为每个项目创建独立配置文件**
   ```bash
   CLIS/
   ├── config.yaml          # 默认配置
   ├── config.ecommerce.yaml # 电商项目配置
   └── config.blog.yaml      # 博客项目配置
   ```

2. **使用模板配置**
   ```bash
   # 创建基础模板
   cp CLIS/config.yaml CLIS/templates/config.template.yaml

   # 新项目从模板创建
   cp CLIS/templates/config.template.yaml CLIS/config.blog.yaml
   # 然后修改项目特定的配置
   ```

3. **版本控制配置文件**
   ```bash
   # 每个项目的配置都纳入git
   git add CLIS/config.*.yaml
   git commit -m "Add project-specific CLI configs"
   ```

### Q4: 任务范围通配符如何使用？

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

### Q5: 如何动态调整CLI数量？

**无需修改代码，只需修改配置**:

```bash
# 步骤1: 编辑配置文件
vim CLIS/config.yaml

# 步骤2: 启用新的CLI
worker4:
  enabled: true  # 从 false 改为 true

# 步骤3: 重新加载配置（如果config_manager在运行）
# 配置会在下次操作时自动加载

# 步骤4: 验证配置
python scripts/dev/cli_config_manager.py --list
```

### Q6: 交互模式下如何快速批量分配？

**批量分配脚本**:
```bash
# 创建批量分配脚本
cat > batch_assign.sh <<'EOF'
#!/bin/bash
# 批量分配任务（跳过交互确认）

tasks=(
  "task-1.1:web"
  "task-1.2:web"
  "task-2.1:api"
  "task-3.1:db"
)

for task_cli in "${tasks[@]}"; do
  task_id=$(echo $task_cli | cut -d: -f1)
  cli=$(echo $task_cli | cut -d: -f2)

  python scripts/dev/task_pool.py --claim --task=$task_id --cli=$cli
done
EOF

chmod +x batch_assign.sh
./batch_assign.sh
```

---

## 配置管理器命令参考

### 完整命令列表

```bash
# 查看所有CLI
python scripts/dev/cli_config_manager.py --list

# 查看包括禁用的CLI
python scripts/dev/cli_config_manager.py --list --show-disabled

# 查看特定CLI详情
python scripts/dev/cli_config_manager.py --info=web

# 测试任务匹配
python scripts/dev/cli_config_manager.py --match=task-1.1 --skills="frontend,Vue"

# 设置任务分配模式
python scripts/dev/cli_config_manager.py --set-mode=interactive

# 创建新CLI
python scripts/dev/cli_config_manager.py --create-cli=worker4 --template=worker

# 使用自定义配置文件
python scripts/dev/cli_config_manager.py --config=CLIS/config.ecommerce.yaml --list
```

---

## 最佳实践

### 1. 配置文件组织

**推荐结构**:
```
CLIS/
├── config.yaml                 # 当前项目配置
├── config.example.yaml         # 示例配置
├── templates/                  # 配置模板
│   ├── minimal.yaml            # 最小配置模板
│   ├── small_project.yaml      # 小项目模板
│   └── large_project.yaml      # 大项目模板
└── README.md                   # 说明文档
```

### 2. 版本控制

**应该提交**:
- ✅ `config.yaml` （生产配置）
- ✅ `config.example.yaml` （示例配置）
- ✅ `templates/*.yaml` （配置模板）

**不应该提交**:
- ❌ `config.local.yaml` （本地覆盖配置）
- ❌ `config.*.dev.yaml` （开发配置）

### 3. 配置分层

**全局配置** (`config.yaml`):
```yaml
multi_cli:
  task_assignment_mode: "interactive"
```

**项目覆盖** (`config.project.yaml`):
```yaml
multi_cli:
  task_assignment_mode: "auto"  # 覆盖全局配置
```

**本地开发** (`config.local.yaml`):
```yaml
cli_definitions:
  worker_debug:
    enabled: true  # 仅本地开发使用
```

### 4. 配置验证

```bash
# 验证配置文件语法
python -c "import yaml; yaml.safe_load(open('CLIS/config.yaml'))"

# 验证CLI配置
python scripts/dev/cli_config_manager.py --list

# 测试任务匹配
python scripts/dev/cli_config_manager.py --match=test-task --skills="test"
```

---

## 相关文档

- **[Multi-CLI快速参考](../../CLIS/README.md)** - CLI工作快速参考
- **[任务池使用指南](../../docs/multi-cli/TASK_POOL_USAGE_GUIDE.md)** - 任务池完整文档
- **[V2实施方案](../../docs/multi-cli/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md)** - 系统架构设计

---

## 示例配置库

### 示例1: 小型全栈项目

```yaml
multi_cli:
  project_name: "small_fullstack"
  task_assignment_mode: "interactive"

cli_definitions:
  main:
    enabled: true
    type: coordinator

  fullstack:
    enabled: true
    type: worker
    role: "fullstack_developer"
    capabilities: [frontend, backend, database]
    task_scope:
      include: ["*"]
```

### 示例2: 大型微服务项目

```yaml
multi_cli:
  project_name: "large_microservices"
  task_assignment_mode: "auto"

cli_definitions:
  main:
    enabled: true
    type: coordinator

  frontend_team:
    enabled: true
    type: worker
    role: "frontend_developer"
    capabilities: [Vue, React, TypeScript]
    task_scope:
      include: ["frontend-*", "ui-*"]

  backend_team:
    enabled: true
    type: worker
    role: "backend_developer"
    capabilities: [FastAPI, gRPC, Kafka]
    task_scope:
      include: ["backend-*", "api-*"]

  database_team:
    enabled: true
    type: worker
    role: "database_admin"
    capabilities: [PostgreSQL, Redis, optimization]
    task_scope:
      include: ["database-*", "migration-*"]

  devops_team:
    enabled: true
    type: worker
    role: "devops_engineer"
    capabilities: [Docker, Kubernetes, CI/CD]
    task_scope:
      include: ["devops-*", "deployment-*"]
```

---

**配置系统维护**: 配置文件应该随项目演进定期更新
**最后更新**: 2026-01-01
**维护者**: Main CLI (Claude Code)
