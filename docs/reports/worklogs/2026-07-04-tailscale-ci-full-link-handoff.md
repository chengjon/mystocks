# Handoff: Tailscale CI Full-Link Validation + Router-Defined Bug Cleanup

> **跨 session 工作线交接文档**
> **日期**: 2026-07-04
> **分支**: `feat/b4-014-fundflow-mixin-openspec-proposal`
> **PR**: [#492 — ci: Tailscale tunnel + CI full-link validation](https://github.com/chengjon/mystocks/pull/492)
> **作者**: Claude (Opus 4.7)
> **审核状态**: 待 user 确认

---

## 0. 一句话总结

打通 GitHub Actions runner → Tailscale 隧道 → NAS TDengine/TimescaleDB → OpenAPI 契约验证全链路,过程中暴露并修复了 2 个真正缺 `router = APIRouter(...)` 定义的 module-level bug(signal_history_response、data_quality)。初版 handoff 误判的"剩余 4 个"实际通过 `from ._xxx_responses import router` 间接导入,无需修复。

---

## 1. 完成的任务

### 1.1 核心成就:CI 全链路打通

```
Setup Tailscale (tailscale/github-action@v4)
  → tailscale up → connected to tailnet as tag:ci
Configure env → 100.74.218.112:6041/5438 (NAS via tailscale tunnel)
Validate OpenAPI generation → ✓ paths generated, spec saved
Validate API Contracts job → ✓ success
Generate TypeScript Types → ✓ success (run #28695148377)
```

**关键验证 run**:
- ✅ #28695148377(workflow_dispatch)— Validate API Contracts + Generate TypeScript Types 双 success
- ✅ #28696249836(workflow_dispatch)— sklearn 修复后 Validate API Contracts success
- ⚠️ #28701069984、#28702471062(push)— 暴露系统性 router bug,持续修复中

### 1.2 已完成修复(共 9 项,跨 5 个 session)

| # | 修复 | 文件/位置 | 性质 | commit |
|---|------|----------|------|--------|
| 1 | GitHub Secrets(8 个) | `chengjon/mystocks` repo settings | 用户操作 | — |
| 2 | workflow 加 `workflow_dispatch` 触发器 | `.github/workflows/api-contract-validation.yml` | paths 过滤的空 commit 不触发 | `051ce121a` |
| 3 | action 仓库从 `tailscale/tailscale@v3` 改为 `tailscale/github-action@v4` | 同上 | client 仓库 vs GitHub Action | `72b00f5bd` |
| 4 | 去掉 args 中重复的 `--accept-routes` | 同上 | action 内部已加 flag | `50d82f353` |
| 5 | args `--hostname=X` 改用 `hostname:` input | 同上 | 避免与内部 flag 冲突 | `f2a60a8e4` |
| 6 | Tailnet ACL 加 `tag:ci → tag:nas:6041,5438` 规则 + `tagOwners` | login.tailscale.com/admin/acls | ACL 默认 deny,tag:ci 节点零规则 | (UI 手改) |
| 7 | requirements 加 `loguru>=0.7.0` | `web/backend/requirements.txt` | local 跑通≠依赖正确 | `9ccd42612` |
| 8 | requirements 加 `scikit-learn>=1.5.0` | 同上 | 同款模式 | `703219acf` |
| 9 | `signal_history_response.py` 加 `router = APIRouter(...)` | `web/backend/app/api/signal_monitoring/signal_history_response.py` | 仓库系统性 module-level router 缺失 bug | `251640af5` |
| 10 | `data_quality.py` 加 router 定义 | `web/backend/app/api/data_quality.py` | 同款 bug | `033fb861a` |

### 1.3 文档产出

- `/opt/claude/mynas/docs/tailscale-tun-deploy-record.md` v1.0 → v2.0(CI 全链路打通,新增 §5.11-5.15 五个坑点)
- `/opt/claude/mynas/docs/tailscale-ci-handoff.md` v2.0(NAS → mystocks 仓库更正)

---

## 2. 在 FUNCTION_TREE.md 中的位置

### 2.1 应归功能域:`{#domain-08}` 系统管理与配置

**当前盲点**:`docs/FUNCTION_TREE.md` L451-L456 的 domain-08 领域入口表**完全没有**以下条目:

| 缺失入口 | 应补条目 |
|---------|---------|
| CI/CD 入口 | `.github/workflows/api-contract-validation.yml`(契约验证 + 类型生成主 workflow) |
| 部署隧道入口 | Tailscale ACL + `nas-config/compose-files/tailscale/`(在 mynas 仓库) |
| 跨域 DB 访问入口 | CI runner → Tailscale → NAS TDengine:6041/TimescaleDB:5438 |

### 2.2 关联节点

- `{#domain-08-node-04}` 前端类型扩展与治理 — CI 的 `Generate TypeScript Types` job 是这条链路的下游消费者;当前 ✅ 状态的运行时证据依赖本条线打通的 CI 链路
- `{#domain-09-node-01}` 数据库架构 — CI 现在直连生产 NAS DB(待办:只读用户)

### 2.3 主线对齐

当前 Active mainline 是 `B4.013 Runtime Mainline Bring-Up`(FUNCTION_TREE L47)。本条线**不属于 B4.013 P0 主线**,属于"工程基础设施 / CI 可见性"支线——但它是**契约治理证据链**的必要前提:CI 跑不通则 `Validate OpenAPI generation` 永久 timeout,(domain-08-node-04)的 ✅ 实际上**缺乏运行时证据**。

---

## 3. 下一步工作计划

### P0 — 阻塞 PR #492 合并

#### P0-1 router-undefined bug 状态(已澄清,无需进一步修复)

**v2.0 修正(2026-07-05)**: 初版 handoff 的"剩余 4 个 broken 文件"判断**有误**。

经实际 importlib 验证,以下 4 个文件**实际能正常导入,router 属性存在**:

```
web/backend/app/api/monitoring_watchlists.py
web/backend/app/api/data_source_config.py
web/backend/app/api/strategy_management/_strategy_crud_router.py
web/backend/app/api/strategy_management/_model_backtest_router.py
```

**真实模式**: 这 4 个文件通过 `from ._xxx_responses import router` **间接导入** router(router 定义在 `_xxx_responses.py` helper 文件中,如 `_monitoring_watchlists_responses.py:61`)。这与之前修复的 `signal_history_response.py` / `data_quality.py` **不同**——后两个文件确实在 HEAD 中缺定义、且 working tree 也是真 broken。

**结论**: 已修的 2 个文件(signal_history_response、data_quality)是真 bug,已正确修复。声称的"剩余 4 个"是误判,无需修复。**P0-1 关闭**。

**经验教训**: 用 `grep -c "^router = APIRouter"` 判断 broken 时,正则 `^from` 不匹配缩进的 `from` import,导致漏看间接导入模式。未来类似判断必须用 `importlib.import_module(mod); hasattr(m, 'router')` 实测。

#### P0-2 验证 `Detect Breaking Changes` job

修完 4 个 router bug 后,CI 全链路应当稳定运行。然后:
- 当前 PR #492 push 触发的 run event 是 `push`,detect-breaking-changes 的 `if: github.event_name == 'pull_request'` 不满足
- 需要重新触发 PR sync event(关闭再开 PR #492,或推一个 paths 内的小改动)
- success 即契约治理链路最后一环的运行时证据

### P1 — 安全/治理收口

#### P1-1 CI 专用只读 DB 用户(强烈建议)

当前 CI 用 `root`/`postgres` 直连生产,风险高。

```sql
-- NAS TDengine
CREATE USER ci_tdengine_reader PASS '...' READONLY;

-- NAS Postgres
CREATE ROLE ci_pg_reader WITH LOGIN PASSWORD '...' READONLY;
GRANT USAGE ON SCHEMA public TO ci_pg_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ci_pg_reader;
```

更新 4 个 secrets:`CI_TDENGINE_USER`、`CI_TDENGINE_PASSWORD`、`CI_POSTGRESQL_USER`、`CI_POSTGRESQL_PASSWORD`。

#### P1-2 FUNCTION_TREE.md domain-08 补 CI/部署入口(任务 #9)

在 `docs/FUNCTION_TREE.md` L451-L456 领域入口表加入:

```markdown
| CI/CD 入口 | [.github/workflows/api-contract-validation.yml](../../.github/workflows/api-contract-validation.yml)
              (契约验证 + 类型生成主 workflow) | CI 跑通是契约治理证据链前提 |
| 部署隧道入口 | Tailscale ACL + nas-config/compose-files/tailscale/(在 mynas 仓库) | CI runner → NAS 跨域通道 |
| 跨域 DB 访问入口 | CI runner → Tailscale → NAS TDengine:6041 / TimescaleDB:5438 | CI 直接读生产 DB(待改只读) |
```

### P2 — 端到端验证补全

- **Windows tailscale 客户端升级** — 笔记本无法 tailnet 直连 NAS 端口(`mynas/docs/tailscale-tun-deploy-record.md` §5.2),CI runner 已替代验证,但开发者本地验证路径仍断
- **DSM 重启自愈实测** — rc.d + 任务计划双保险已配,但未实机重启验证

### P3 — 文档同步

- **Tailscale ACL 配置进 mynas 仓库版本控制** — 当前 ACL 是 admin UI 手改,应导出 HuJSON 提交到 `nas-config/`
- **本 handoff 文档归档** — 完成后归档到 `docs/reports/worklogs/claude-auto/`

---

## 4. 关键参考链接

| 资料 | 位置 |
|------|------|
| NAS tailscale 部署实录 v2.0(含 15 个坑点) | `/opt/claude/mynas/docs/tailscale-tun-deploy-record.md` |
| NAS → mystocks 仓库 handoff v2.0 | `/opt/claude/mynas/docs/tailscale-ci-handoff.md` |
| NAS 运维 KB | `/opt/claude/mynas/nas-config/KNOWLEDGE-BASE.md` |
| mystocks workflow | `.github/workflows/api-contract-validation.yml` |
| PR #492 | https://github.com/chengjon/mystocks/pull/492 |
| GitHub Secrets(mystocks) | https://github.com/chengjon/mystocks/settings/secrets/actions |
| Tailscale ACL 配置 | https://login.tailscale.com/admin/acls |
| Tailscale 节点管理 | https://login.tailscale.com/admin/machines |

---

## 5. 关键参数速查

```
NAS tailscale IP:        100.74.218.112
NAS LAN IP:              192.168.123.104
NAS SSH:                 192.168.123.104:223 (john/c790414J)
Tailnet:                 tail7019b.ts.net
Tailscale DERP:          lax (Los Angeles, ~155ms)
TDengine port (NAS):     6041 (REST) / 6030 (native)
TimescaleDB port (NAS):  5438 (容器内 5432,外部映射 5438)
TDengine password:       c790414J
TimescaleDB password:    c790414J

TAILSCALE_AUTH_KEY 类型: Reusable + Ephemeral + Preauthorized, tag:ci
Tailnet ACL 关键规则:    tag:ci → tag:nas:6041,5438 (tcp accept)
ACL 编辑页面:            https://login.tailscale.com/admin/acls

GitHub repos:
  workflow push target:  chengjon/mystocks
  当前 PR:               #492
  工作分支:              feat/b4-014-fundflow-mixin-openspec-proposal
```

---

## 6. 教训沉淀(写入项目知识库候选)

1. **本地能跑 ≠ CI 能跑** — loguru、sklearn、router 定义三次同款坑;**强烈建议**做"全 venv 依赖审计 + module-level smoke import"专项
2. **working tree 长期掩盖 HEAD broken 状态** — 多个 router 定义 bug 在 working tree 已修但未 commit,CI 全新 checkout 暴露。建议定期 `git stash && python -c "import ..."` 验证 HEAD 真相
3. **Tailscale ACL 默认 deny,timeout(非 refused)是设计行为** — ACL 不放行 tag:ci 时静默 drop,表现为 timeout 而非 connection refused
4. **GitHub Action `args` 与 action 内部 flag 易冲突** — 能用 input 就别用 args
5. **任何带 `paths` 过滤的 workflow 都应加 `workflow_dispatch`** — 方便事后重跑,空 commit 不触发 paths 过滤

---

*文档版本: v1.0 | 生成日期: 2026-07-04 | 作者: Claude (Opus 4.7)*
*审核状态: 待 user 确认*
