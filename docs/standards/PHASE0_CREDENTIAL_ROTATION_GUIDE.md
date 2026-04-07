# PHASE0 凭据轮换指南（模板）

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


> 目的：当密钥/密码/Token 发生泄露或疑似泄露时，以最短时间完成止血、轮换、验证与复盘。  
> 适用范围：数据库凭据、第三方 API Key、JWT Secret、SMTP 凭据、云平台访问密钥、CI/CD Secret。  
> 等级：P0（阻断级）。

## 1. 触发条件

满足任一条件即启动 PHASE0：
- 代码仓库（当前或历史）出现明文敏感信息；
- 日志、告警、工单、聊天记录暴露凭据；
- 第三方平台通知密钥泄露或异常调用；
- 发现未授权访问与凭据相关联。

## 2. 响应 SLA

- `T+0 ~ T+15min`：事件确认与冻结变更。
- `T+15 ~ T+60min`：撤销旧凭据、发放新凭据。
- `T+60 ~ T+120min`：业务验证与恢复发布。
- `T+24h`：完成复盘与整改项登记。

## 3. 角色与职责

- 事件指挥（IC）：统一调度、对外同步状态。
- 应用负责人（Dev）：代码修复、配置切换、回归验证。
- 平台/运维（Ops）：Secret 更新、发布流水线控制。
- 安全负责人（Sec）：泄露范围评估、审计与复盘把关。

## 4. 标准处置流程

### 4.1 立即止血

1. 冻结发布与高风险变更（主干保护、流水线暂停）。
2. 标记事件级别为 `P0`，建立事件记录单。
3. 锁定影响资产清单（系统、环境、仓库、第三方服务）。

### 4.2 失效旧凭据

1. 在凭据源头立即撤销旧值（数据库/云平台/API 控制台）。
2. 若支持，启用强制登出或会话失效（Token/JWT）。
3. 记录撤销时间、操作者、影响范围。

### 4.3 生成与分发新凭据

1. 按最小权限重新生成新凭据。
2. 通过 Secret 管理系统注入（禁止明文传递）。
3. 分环境更新（dev/test/staging/prod），避免混用。

### 4.4 清理代码与历史

1. 修复当前分支：删除明文，改为环境变量或 Secret 读取。
2. 必要时清理 git 历史（`git filter-repo`）。
3. 强制推送后通知全员执行本地仓库重置。

示例（按需）：

```bash
# replacements.txt 示例格式:
# regex:<旧敏感值>==><REDACTED>

git filter-repo --replace-text replacements.txt
git push --force --all
git push --force --tags
```

### 4.5 验证恢复

1. 核验关键业务链路（登录、核心 API、数据库连接、异步任务）。
2. 运行泄露扫描工具确认“当前与历史无新增泄露”。
3. 完成灰度/全量恢复。

## 5. Vault/Secret 管理接入基线

- 应用代码仅读取环境变量，不存储默认明文凭据。
- Secret 注入由部署系统完成（K8s Secret、CI Secret、Vault Agent）。
- 禁止将 `role_id/secret_id` 等二级凭据写入仓库。

示例（启动注入）：

```bash
export POSTGRESQL_PASSWORD="$(vault kv get -field=password secret/prod/postgresql)"
export TDENGINE_PASSWORD="$(vault kv get -field=password secret/prod/tdengine)"
```

## 6. 工具链与门禁

建议最小组合：
- 提交前：`detect-secrets`
- CI 阶段：`gitleaks` + `bandit`
- 周期巡检：`trufflehog`

示例：

```bash
detect-secrets scan > .secrets.baseline
gitleaks detect --source . --verbose
trufflehog filesystem .
bandit -r src/
```

## 7. 对外沟通模板（简版）

### 7.1 内部通告
- 事件编号：
- 发现时间：
- 影响系统：
- 已完成动作：
- 当前风险状态：
- 下一次同步时间：

### 7.2 外部说明（如需）
- 影响窗口：
- 风险评估：
- 已实施控制：
- 用户侧建议动作：
- 联系方式：

## 8. 复盘模板

- 根因分类：流程缺失 / 门禁缺失 / 人为误操作 / 工具误报漏报
- 首次泄露点：
- 检测延迟（分钟）：
- 处置总时长（分钟）：
- 是否触发二次风险：
- 永久性改进项（含负责人与截止日期）：

## 9. 项目落地检查清单

- [ ] 所有敏感项已迁移到 Secret 管理
- [ ] 所有旧凭据已撤销并确认无残留
- [ ] CI 已启用泄露扫描阻断规则
- [ ] 应急联系人与责任分工已固化
- [ ] 已完成至少一次桌面演练（Tabletop Exercise）

## 10. 文档定位与关联

本指南定位为**应急处置流程补充**，不替代项目既有开发与部署规范：

- 硬编码分级与长期治理：`docs/standards/security/HARDCODING_GOVERNANCE_TIERING_GUIDE.md`
- 本地变量注入与启动校验：`docs/standards/LOCAL_ENV_SETUP.md`

推荐落地顺序：

1. 先按分级指南识别与下发整改优先级  
2. 出现泄露事件时按本 PHASE0 指南执行轮换  
3. 轮换完成后回写治理台账与 CI 门禁
