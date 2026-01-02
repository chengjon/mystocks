# CLI报到指引

**版本**: v2.1
**更新时间**: 2026-01-01
**适用范围**: Multi-CLI协作系统

---

## 📋 目录

1. [报到流程概述](#报到流程概述)
2. [快速开始](#快速开始)
3. [完整报到流程](#完整报到流程)
4. [相关脚本文件](#相关脚本文件)
5. [配置文件说明](#配置文件说明)
6. [使用示例](#使用示例)
7. [故障排查](#故障排查)

---

## 报到流程概述

**CLI报到机制**是Multi-CLI协作系统的核心功能，用于：
- ✅ 识别CLI身份（名称、类型、能力）
- ✅ 分配角色和任务
- ✅ 建立CLI-main与其他CLI的协作关系
- ✅ 持久化保存所有CLI的报到信息

### 核心原则

**异步通信** - 通过mailbox进行消息传递，避免阻塞
**JSON持久化** - 所有报到信息保存在`registrations.json`
**双向确认** - CLI发送报到 → main确认并分配角色

---

## 快速开始

### 一键初始化环境

```bash
# Step 1: 初始化完整的Multi-CLI环境
bash scripts/dev/init_multi_cli.sh

# Step 2: 启动各CLI的mailbox监听器（可选）
python scripts/dev/mailbox_watcher.py --cli=main &
python scripts/dev/mailbox_watcher.py --cli=web &
python scripts/dev/mailbox_watcher.py --cli=api &
```

### 最小化报到示例

```bash
# CLI-web向main报到
python scripts/dev/cli_registration.py --register --cli=web

# main确认web的报到
python scripts/dev/cli_registration.py --confirm --cli=web --role="前端开发" --tasks="task1,task2"
```

---

## 完整报到流程

### 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI报到完整流程                            │
└─────────────────────────────────────────────────────────────┘

步骤1: CLI-web发送报到请求
┌──────────────┐         报到消息         ┌──────────────┐
│   CLI-web    │ ──────────────────────> │   CLI-main   │
│ (前端开发)    │   (registration请求)    │   (协调器)     │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/cli_registration.py \
      |   --register --cli=web --type=worker \
      |   --capabilities="frontend,Vue,API-integration,UI-design"
      |
      V
✅ 报到信息保存到: CLIS/main/registrations.json
✅ 状态: pending
✅ 消息发送到: CLIS/main/mailbox/web_registration_*.md


步骤2: CLI-main确认报到并分配角色
┌──────────────┐      确认消息         ┌──────────────┐
│   CLI-main   │ ─────────────────────> │   CLI-web    │
│   (协调器)     │   (role确认)          │  (前端开发)    │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/cli_registration.py \
      |   --confirm --cli=web \
      |   --role="前端开发工程师" \
      |   --tasks="web-homepage,api-integration,ui-design"
      |
      V
✅ 报到信息更新: status → confirmed
✅ 角色分配: role = "前端开发工程师"
✅ 任务分配: assigned_tasks = ["web-homepage", "api-integration", "ui-design"]
✅ 确认消息发送到: CLIS/web/mailbox/main_confirmation_*.md


步骤3: CLI-web接收确认并开始工作
┌──────────────┐
│   CLI-web    │
│  (前端开发)    │
└──────────────┘
      |
      | 1. 查看确认消息: cat CLIS/web/mailbox/main_confirmation_*.md
      | 2. 查看分配的任务: cat CLIS/web/TASK.md
      | 3. 查看工作规范: cat CLIS/web/RULES.md
      | 4. 开始执行任务！
      |
      V
🎉 CLI-web已成功报到，main知道它是"前端开发工程师"
```

### 报到信息持久化

**位置**: `CLIS/main/registrations.json`

**示例内容**:
```json
{
  "web": {
    "name": "web",
    "type": "worker",
    "capabilities": ["frontend", "Vue", "API-integration", "UI-design"],
    "registration_time": "2026-01-01T19:02:37.994773",
    "status": "confirmed",
    "role": "前端开发工程师",
    "assigned_tasks": ["web-homepage", "api-integration", "ui-design"],
    "confirmation_time": "2026-01-01T19:04:18.370945"
  }
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | CLI名称 |
| `type` | string | CLI类型（main, worker, coordinator） |
| `capabilities` | array | CLI能力列表 |
| `registration_time` | string | 报到时间（ISO 8601） |
| `status` | string | 状态（pending, confirmed） |
| `role` | string | main分配的角色 |
| `assigned_tasks` | array | main分配的任务ID列表 |
| `confirmation_time` | string | 确认时间（ISO 8601） |

---

## 相关脚本文件

### 核心脚本

**1. CLI报到脚本** ([`scripts/dev/cli_registration.py`](../../scripts/dev/cli_registration.py))
- **功能**: 实现CLI报到和main确认机制
- **关键函数**:
  - `register_as_cli()` - CLI报到
  - `confirm_cli_registration()` - main确认
  - `auto_register` - 自动报到装饰器
- **使用**: 命令行工具或Python导入

**2. Mailbox监听器** ([`scripts/dev/mailbox_watcher.py`](../../scripts/dev/mailbox_watcher.py))
- **功能**: 事件驱动的mailbox消息监听
- **特性**:
  - 使用watchdog库实现秒级响应
  - 自动处理新消息并归档
  - 支持4种消息类型（ALERT, REQUEST, RESPONSE, NOTIFICATION）
- **使用**: 后台运行监听mailbox目录

**3. CLI协调器** ([`scripts/dev/cli_coordinator.py`](../../scripts/dev/cli_coordinator.py))
- **功能**: 基础CLI协调功能
- **关键方法**:
  - `scan_all_status()` - 扫描所有CLI状态
  - `get_cli_info()` - 获取CLI详细信息
  - `send_message()` - 发送消息到指定CLI
- **使用**: 命令行工具或Python导入

**4. 智能协调器** ([`scripts/dev/smart_coordinator.py`](../../scripts/dev/smart_coordinator.py))
- **功能**: 规则驱动的自动协调引擎
- **4个协调规则**:
  - `BlockageResolutionRule` - 阻塞自动解决
  - `IdleResourceRule` - 空闲资源分配
  - `ConflictPreventionRule` - 冲突自动预防
  - `HealthCheckRule` - 健康检查
- **使用**: 后台运行自动协调

**5. 自动状态更新** ([`scripts/dev/auto_status.py`](../../scripts/dev/auto_status.py))
- **功能**: 装饰器自动更新STATUS.md
- **特性**:
  - `@track_task` 装饰器自动跟踪任务状态
  - 自动处理异常和错误状态
  - 正则表达式更新STATUS.md字段
- **使用**: Python导入并使用装饰器

**6. 文件锁管理** ([`scripts/dev/simple_lock.py`](../../scripts/dev/simple_lock.py))
- **功能**: 简化的文件锁管理
- **特性**:
  - 使用fcntl+flock实现文件锁
  - 原子操作（os.O_EXCL）避免竞争条件
  - 进程崩溃自动释放锁
- **使用**: Python导入创建锁管理器

**7. 初始化脚本** ([`scripts/dev/init_multi_cli.sh`](../../scripts/dev/init_multi_cli.sh))
- **功能**: 一键初始化Multi-CLI环境
- **创建内容**:
  - 完整目录结构（8个CLI）
  - 模板文件（TASK.md, RULES.md, STATUS.md）
  - 配置文件（.cli_config）
  - 启动协调器后台进程
- **使用**: `bash scripts/dev/init_multi_cli.sh`

### 配置和模板文件

**CLI配置**: `CLIS/{cli_name}/.cli_config`
- CLI类型和mailbox配置
- 协调器配置参数

**任务模板**: `CLIS/templates/TASK.md.template`
- 任务清单格式
- 任务历史记录表

**规范模板**: `CLIS/templates/RULES.md.template`
- 核心职责定义
- 工作流程说明
- 沟通规范

**状态模板**: `CLIS/templates/STATUS.md.template`
- 当前状态（idle, active, blocked, error）
- 当前任务和进度
- 阻塞问题和Issue记录

---

## 配置文件说明

### .cli_config配置

**位置**: `CLIS/{cli_name}/.cli_config`

**示例**:
```ini
[cli]
name = web
type = worker

[mailbox]
watcher_enabled = true
scan_interval = 60

[coordination]
auto_coordinate = true
coordinate_interval = 300
```

**配置说明**:
- `name`: CLI名称
- `type`: CLI类型（main, worker, coordinator）
- `watcher_enabled`: 是否启用mailbox监听器
- `scan_interval`: mailbox扫描间隔（秒）
- `auto_coordinate`: 是否启用自动协调
- `coordinate_interval`: 协调器运行间隔（秒）

### STATUS.md格式

**位置**: `CLIS/{cli_name}/STATUS.md`

**格式**:
```markdown
# 当前状态

**CLI**: web
**Updated**: 2026-01-01 19:00:00

## Current State

**State**: 🟢 Idle
**Current Task**: 无
**Progress**: N/A

## Blocked On

无

## Issues

无
```

**状态标识**:
- 🟢 Idle - 空闲
- 🟡 Active - 工作中
- 🟠 Blocked - 被阻塞
- 🔴 Error - 错误

---

## 使用示例

### 示例1: 基础报到流程

**CLI-web报到**:
```bash
python scripts/dev/cli_registration.py \
  --register \
  --cli=web \
  --type=worker \
  --capabilities="frontend,Vue,API-integration"
```

**main确认**:
```bash
python scripts/dev/cli_registration.py \
  --confirm \
  --cli=web \
  --role="前端开发工程师" \
  --tasks="web-homepage,api-integration"
```

### 示例2: 使用Python API

```python
from scripts.dev.cli_registration import register_as_cli, confirm_cli_registration

# CLI-web报到
registration = register_as_cli(
    cli_name='web',
    cli_type='worker',
    capabilities=['frontend', 'Vue', 'API-integration', 'UI-design']
)
print(f"报到成功: {registration}")

# main确认
confirmed = confirm_cli_registration(
    cli_name='web',
    role='前端开发工程师',
    assigned_tasks=['web-homepage', 'api-integration', 'ui-design']
)
print(f"确认成功: {confirmed}")
```

### 示例3: 自动报到装饰器

```python
from scripts.dev.cli_registration import auto_register

@auto_register(
    cli_type='worker',
    capabilities=['database', 'PostgreSQL', 'TDengine', 'optimization']
)
def db_worker_main(cli_name='db'):
    """CLI-db主函数"""
    print(f"{cli_name} 已自动报到")
    # 执行db工作...

if __name__ == '__main__':
    db_worker_main(cli_name='db')
```

### 示例4: 查看CLI状态

```bash
# 扫描所有CLI状态
python scripts/dev/cli_coordinator.py --scan

# 查看特定CLI详细信息
python scripts/dev/cli_coordinator.py --info=web

# 查看报到信息
cat CLIS/main/registrations.json | jq .
```

### 示例5: 发送消息给CLI

```python
from scripts.dev.cli_coordinator import CLICoordinator

coordinator = CLICoordinator()

# 发送消息给web
message = """---
**From**: main
**To**: web
**Type**: REQUEST
**Priority**: HIGH
**Timestamp**: 2026-01-01 20:00:00

**Subject**: 新任务分配

请开始实现API集成功能。

**Expected Response**: 1小时内
"""

coordinator.send_message('web', message)
print("消息已发送到web的mailbox")
```

---

## 故障排查

### 问题1: 报到消息未发送

**症状**: 执行`--register`后没有显示"✅ 已向main发送报到请求"

**排查步骤**:
1. 检查main目录是否存在:
   ```bash
   ls -la CLIS/main/
   ```

2. 检查mailbox目录权限:
   ```bash
   ls -ld CLIS/main/mailbox/
   ```

3. 手动创建mailbox目录:
   ```bash
   mkdir -p CLIS/main/mailbox
   ```

### 问题2: main未收到报到消息

**症状**: registrations.json文件不存在或未更新

**排查步骤**:
1. 检查main的mailbox内容:
   ```bash
   ls -la CLIS/main/mailbox/
   cat CLIS/main/mailbox/web_registration_*.md
   ```

2. 检查文件权限:
   ```bash
   chmod 755 CLIS/main/mailbox
   ```

3. 手动查看报到消息文件:
   ```bash
   find CLIS/main/mailbox/ -name "*registration*" -exec cat {} \;
   ```

### 问题3: CLI未收到确认消息

**症状**: 执行`--confirm`后CLI的mailbox为空

**排查步骤**:
1. 检查CLI目录结构:
   ```bash
   ls -la CLIS/web/mailbox/
   ```

2. 手动创建mailbox目录:
   ```bash
   mkdir -p CLIS/web/mailbox
   ```

3. 重新发送确认:
   ```bash
   python scripts/dev/cli_registration.py --confirm --cli=web --role="test" --tasks="task1"
   ```

4. 验证消息文件:
   ```bash
   cat CLIS/web/mailbox/main_confirmation_*.md
   ```

### 问题4: registrations.json格式错误

**症状**: JSON解析失败

**排查步骤**:
1. 验证JSON格式:
   ```bash
   cat CLIS/main/registrations.json | jq .
   ```

2. 检查文件编码:
   ```bash
   file CLIS/main/registrations.json
   ```

3. 备份并重新初始化:
   ```bash
   cp CLIS/main/registrations.json CLIS/main/registrations.json.backup
   echo '{}' > CLIS/main/registrations.json
   ```

### 问题5: 协调器未运行

**症状**: 没有自动协调动作

**排查步骤**:
1. 检查协调器进程:
   ```bash
   cat CLIS/main/.coordinator_pid
   ps aux | grep $(cat CLIS/main/.coordinator_pid)
   ```

2. 查看协调器日志:
   ```bash
   tail -f CLIS/main/coordinator.log
   ```

3. 手动启动协调器:
   ```bash
   python scripts/dev/smart_coordinator.py --auto
   ```

4. 后台运行协调器:
   ```bash
   nohup python scripts/dev/smart_coordinator.py --auto >> CLIS/main/coordinator.log 2>&1 &
   echo $! > CLIS/main/.coordinator_pid
   ```

---

## 最佳实践

### 1. 使用mailbox监听器

**推荐**: 为每个CLI启动mailbox监听器，实现秒级响应

```bash
# 启动所有CLI的监听器
for cli in main web api db; do
  python scripts/dev/mailbox_watcher.py --cli=$cli &
done
```

### 2. 定期更新STATUS.md

**推荐**: 使用`@track_task`装饰器自动更新状态

```python
from scripts.dev.auto_status import track_task

@track_task('web')
def implement_api_integration():
    # 实现API集成
    pass

# STATUS.md会自动更新为idle
```

### 3. 使用智能协调器

**推荐**: 让main运行智能协调器，自动处理阻塞和资源分配

```bash
# 后台运行智能协调器
nohup python scripts/dev/smart_coordinator.py --auto >> CLIS/main/coordinator.log 2>&1 &
```

### 4. 定期备份registrations.json

**推荐**: 定期备份报到信息

```bash
# 添加到crontab
0 */6 * * * cp CLIS/main/registrations.json CLIS/main/registrations.json.$(date +\%Y\%m\%d_\%H\%M\%S).backup
```

---

## 相关文档

- **Multi-CLI V2实施方案**: [`MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md`](./MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md)
- **实施完成报告**: [`../reports/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md`](../reports/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md)
- **V2.1修复总结**: [`../reports/MULTI_CLI_V2_FIX_SUMMARY.md`](../reports/MULTI_CLI_V2_FIX_SUMMARY.md)
- **V1方法文档**: [`MULTI_CLI_COLLABORATION_METHOD.md`](./MULTI_CLI_COLLABORATION_METHOD.md)

---

## 常见问题 (FAQ)

**Q: CLI必须报到才能工作吗？**
A: 不是必须的，但强烈推荐。报到可以让main了解CLI的能力和状态，便于任务分配和协调。

**Q: 可以修改已分配的角色和任务吗？**
A: 可以。main可以随时重新执行`--confirm`命令更新CLI的角色和任务。

**Q: registrations.json丢失怎么办？**
A: 可以让所有CLI重新报到。建议定期备份此文件。

**Q: 多个CLI可以同时报到吗？**
A: 可以。系统支持并发报到，每个CLI的报到信息独立保存。

**Q: 如何删除一个CLI的报到信息？**
A: 编辑`CLIS/main/registrations.json`，删除对应的CLI条目。

---

**文档维护**: 本文档应随Multi-CLI系统的更新而维护
**最后更新**: 2026-01-01
**维护者**: Main CLI (Claude Code)
