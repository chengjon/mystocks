# CI/CD集成与告警通知指南

## 📚 概述

本文档介绍如何将API契约管理集成到CI/CD流水线，并配置自动化告警通知。

---

## 🔧 Pre-commit Hooks集成

### 安装Pre-commit Hooks

```bash
# 安装pre-commit (如果未安装)
pip install pre-commit

# 安装契约管理hooks
pre-commit install --config .pre-commit-hooks.yaml

# 手动运行所有hooks
pre-commit run --all-files --config .pre-commit-hooks.yaml
```

### Hook功能说明

| Hook | 功能 | 触发时机 |
|------|------|----------|
| validate-openapi-contracts | 验证OpenAPI契约语法 | 提交契约文件时 |
| black | 格式化Python代码 | 提交Python文件时 |
| ruff | Python Lint检查 | 提交Python文件时 |
| yamllint | YAML语法检查 | 提交YAML文件时 |
| detect-breaking-changes | 检测破坏性变更 | 提交契约文件时 |

### Hook工作流程

```
git commit
    ↓
1. 识别修改的文件
    ↓
2. 验证OpenAPI契约语法
    ↓
3. 检测破坏性变更
    ↓
4. 格式化代码
    ↓
5. 运行Lint检查
    ↓
✅ 通过 → 允许提交
❌ 失败 → 阻止提交
```

---

## 🚀 GitHub Actions集成

### 工作流文件

**位置**: `.github/workflows/api-contract-validation.yml`

### 触发条件

```yaml
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'docs/api/contracts/**'
      - 'web/backend/app/api/**/*.py'
  pull_request:
    branches: [ main, develop ]
```

### CI流水线阶段

#### 阶段1: 契约验证 (contract-validation)

```yaml
- 检出代码
- 设置Python环境
- 安装依赖
- 启动后端服务
- 验证所有OpenAPI契约文件
- 检查破坏性变更 (PR)
```

**验证命令**:
```bash
# 使用openapi-spec-validator
python -m openapi_spec_validator docs/api/contracts/*.yaml

# 使用prance (深度验证)
prance validate-file docs/api/contracts/market-api.yaml
```

---

#### 阶段2: 契约发布 (contract-publish)

```yaml
- 仅在main分支触发
- 生成版本号 (基于日期和commit)
- 创建契约版本
- 激活新版本
- 生成变更日志
```

**版本号格式**: `YYYY.MM.DD-{commit_sha}`

**发布命令**:
```bash
api-contract-sync create market-api $VERSION \
  -s openapi.yaml \
  -a "GitHub Actions" \
  -d "自动发布"
```

---

#### 阶段3: 差异检测 (diff-check)

```yaml
- 仅在PR触发
- 对比base分支和head分支
- 生成差异报告
- 发布PR评论
```

**差异检测**:
```bash
python scripts/ci/compare_contracts.py \
  --base origin/main \
  --head HEAD \
  --output diff-report.json
```

**PR评论示例**:
```markdown
# API契约差异报告

**PR**: #123
**作者**: developer
**分支**: feature/new-api

## 破坏性变更检测

- [critical] 删除API端点: /api/market/symbols
- [high] 新增必填字段: StockSymbol.code

## 非破坏性变更

- [info] 新增API端点: /api/market/realtime
- [info] 新增可选字段: StockSymbol.industry
```

---

#### 阶段4: 通知 (notify)

```yaml
- 发送成功/失败通知
- 集成Slack/企业微信/邮件
```

---

## 🔔 告警通知配置

### 通知方式

#### 1. Slack Webhook

**配置文件**: `scripts/notifications/slack.py`

```python
import os
import requests
import json

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def send_slack_notification(
    status: str,
    message: str,
    breaking_changes_count: int = 0
):
    """发送Slack通知"""

    color = {
        "success": "#36a64f",
        "failure": "#dc3545",
        "warning": "#ffc107"
    }.get(status, "#007bff")

    attachment = {
        "color": color,
        "title": "API契约CI/CD通知",
        "text": message,
        "fields": [
            {
                "title": "状态",
                "value": status.upper(),
                "short": True
            },
            {
                "title": "破坏性变更",
                "value": str(breaking_changes_count),
                "short": True
            }
        ]
    }

    requests.post(SLACK_WEBHOOK_URL, json={"attachments": [attachment]})
```

**环境变量**:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

#### 2. 企业微信机器人

**配置文件**: `scripts/notifications/wecom.py`

```python
import os
import requests

WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL")

def send_wecom_notification(message: str):
    """发送企业微信通知"""

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }

    requests.post(WECOM_WEBHOOK_URL, json=data)
```

**消息格式**:
```markdown
# API契约CI/CD通知

**状态**: ✅ 成功
**破坏性变更**: 2
**分支**: main
**Commit**: abc123def

[查看详情](https://github.com/.../actions/runs/123)
```

---

#### 3. 邮件通知

**配置文件**: `scripts/notifications/email.py`

```python
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

def send_email_notification(
    to_addresses: list,
    subject: str,
    body: str
):
    """发送邮件通知"""

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(to_addresses)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
```

---

### 通知触发条件

| 场景 | 通知级别 | 发送渠道 |
|------|---------|---------|
| 契约验证通过 | Info | Slack |
| 契约验证失败 | Error | Slack + 邮件 |
| 检测到破坏性变更 | Warning | Slack + 企业微信 |
| 发布新版本 | Info | Slack |
| CI/CD流水线失败 | Critical | Slack + 邮件 + 企业微信 |

---

## 📋 告警模板

### 模板1: 契约验证成功

```
✅ API契约验证通过

仓库: myorg/mystocks
分支: main
Commit: abc123def
作者: developer

验证的契约文件:
- market-api.yaml
- trade-api.yaml
- technical-api.yaml

查看详情: https://github.com/.../actions/runs/123
```

---

### 模板2: 破坏性变更警告

```
⚠️  检测到API破坏性变更

PR: #123
分支: feature/new-api
作者: developer

破坏性变更 (2个):
1. [critical] 删除API端点: /api/market/symbols
2. [high] 新增必填字段: StockSymbol.code

⚠️  请确认这些变更是预期的，并获得技术负责人批准

查看详情: https://github.com/.../pull/123
```

---

### 模板3: 契约验证失败

```
❌ API契约验证失败

仓库: myorg/mystocks
分支: feature/new-api
Commit: def456abc
作者: developer

错误信息:
- openapi.yaml: 缺少必需字段: info.title
- market-api.yaml: 引用的Schema不存在: StockSymbol

请修复后重新提交

查看日志: https://github.com/.../actions/runs/124
```

---

## 🔧 本地测试

### 测试Pre-commit Hooks

```bash
# 模拟提交 (不实际提交)
git commit --no-verify -m "test: 测试hooks"

# 手动运行所有hooks
pre-commit run --all-files --config .pre-commit-hooks.yaml

# 跳过某个hook (不推荐)
SKIP=detect-breaking-changes git commit -m "message"
```

---

### 测试CI流水线

```bash
# 使用act本地运行GitHub Actions (需要安装act)
act push --workflow .github/workflows/api-contract-validation.yml

# 或使用nebius/action-tunnel (在线测试)
# Push到测试分支，观察实际运行结果
```

---

## 🎯 最佳实践

### 1. 分支保护规则

**GitHub设置**: Settings → Branches → Add Rule

```yaml
分支保护规则 (main):
  ✅ Require pull request before merging
    - Require approvals: 1
  ✅ Require status checks to pass
    - contract-validation
    - contract-publish
  ✅ Require branches to be up to date
  ✅ Block force pushes
```

---

### 2. 提交规范

**推荐的提交消息格式**:
```bash
# 契约相关提交
feat(contracts): 新增market-api契约 v1.1.0
fix(contracts): 修正StockSymbol Schema定义
docs(contracts): 更新API契约文档

# 代码提交
feat(api): 实现实时行情接口
refactor(api): 重构错误处理逻辑
test(api): 添加契约验证测试
```

---

### 3. 版本发布流程

```bash
# 1. 创建release分支
git checkout -b release/api-v1.2.0

# 2. 更新契约文件
vim docs/api/contracts/market-api.yaml

# 3. 本地验证
pre-commit run --all-files --config .pre-commit-hooks.yaml

# 4. 提交并推送
git add .
git commit -m "chore(contracts): 发布market-api v1.2.0"
git push origin release/api-v1.2.0

# 5. 创建PR到main
gh pr create --title "Release: API契约 v1.2.0" --body "变更内容..."

# 6. 合并后自动触发CI/CD发布
```

---

### 4. 回滚策略

**如果新版本有问题**:
```bash
# 1. 激活上一个稳定版本
api-contract-sync activate <old_version_id>

# 2. 或回滚代码
git revert <commit_hash>
git push origin main

# 3. 通知团队
echo "❌ API契约已回滚到 v1.1.0" | send_notification
```

---

## 📊 监控指标

### 关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 契约验证通过率 | 验证成功的比例 | >95% |
| 破坏性变更率 | 破坏性变更的PR比例 | <10% |
| 平均修复时间 | 验证失败后修复的平均时间 | <2小时 |
| 自动发布成功率 | CI/CD自动发布的成功率 | >90% |

### Grafana Dashboard

TODO: 创建监控仪表盘
- 契约验证趋势
- 破坏性变更统计
- 发布频率分析

---

## 🔗 相关文档

- [CLI工具使用指南](./CLI_TOOL_GUIDE.md)
- [API契约管理平台文档](./CONTRACT_MANAGEMENT_API.md)
- [OpenAPI 3.0规范](https://swagger.io/specification/)

---

## 📞 支持

### 问题反馈

- GitHub Issues: [项目地址]
- 邮件: support@example.com

### 紧急联系

- 技术负责人: tech-lead@example.com
- DevOps团队: devops@example.com

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-29
**维护者**: MyStocks DevOps Team
