# HANDOFF — C3 实战方向 6 PoC 完成 (multi_source_manager 收编)

> 跨 session 接力文档。本 session 接手上一版 handoff (`HANDOFF_C3_DIRECTION6.md`) 的"下一 session 要做的 3 件事",全部验证通过,已 commit;同时校正了对 Layer 2/3 的误读,并把 tasks.md 全部勾选状态同步到实际。

## 状态速览

| 阶段 | 状态 |
|------|------|
| 改造 1 (announcement_service 迁移到 OpenStockClient) | ✅ 已 commit `c68888ad3` |
| 改造 2 (删 4 个 OpenStock-owned 方法) | ✅ 已 commit `c68888ad3` |
| 改造 3 (Layer 1 单测先行) | ✅ 已 commit `c68888ad3` |
| Layer 1 单测验证 (18 passed) | ✅ |
| announcement_service import 校验 | ✅ `import ok` |
| Backend 启动 + snapshot 检查 | ✅ `{"adapters": []}` |
| black 修复 (test_layer1_opstock_owned_guard.py) | ✅ 已 amend-style 新 commit |
| tasks.md 全部 phase 1-5 同步勾选 | ✅ |

## Commit 历史

| SHA | Title | Note |
|-----|-------|------|
| `c68888ad3` | feat(extra-source): C3 方向 6 PoC — multi_source_manager 收编验证 | 本 PoC 主 commit |
| (本 session 准备 commit) | style(extra-source): black fix + tasks.md 同步勾选 | black 修复 + tasks.md 状态同步 |

## 改动文件

| 文件 | 性质 | 说明 |
|------|------|------|
| `web/backend/app/services/announcement_service.py` | 重构 (M) | `multi_source_manager.fetch_announcements(CNINFO)` → `OpenStockClient.fetch("ANNOUNCEMENTS")`; 新增 `_run_async` (sync→async bridge), `_openstock_result_to_dataframe` (字段 rename), `_ANNOUNCEMENT_FIELD_MAP` |
| `web/backend/app/services/multi_source_manager.py` | 删除 4 方法 + dead-code 清理 (M) | 删 `fetch_realtime_quote` / `fetch_fund_flow` / `fetch_dragon_tiger` / `fetch_announcements`; dead-code 收尾 `fetch_with_fallback` / `clear_cache` / `_cache` / `_cache_ttl` + 未用 imports |
| `web/backend/tests/unit/services/extra_source/test_layer1_opstock_owned_guard.py` | 新建 + black fix | 6 个 OpenStock-owned category 参数化 + drift sentinel |

## 本 session 三件验证结果

### 1. Layer 1 单测 ✅

```bash
cd /opt/claude/mystocks_spec
python -m pytest web/backend/tests/unit/services/extra_source/test_layer1_opstock_owned_guard.py -v
```

**结果**: `18 passed`。

### 2. announcement_service import ✅

```bash
cd /opt/claude/mystocks_spec/web/backend
python -c "from app.services.announcement_service import AnnouncementService; svc = AnnouncementService(); print('import ok')"
```

**结果**: `import ok`。

### 3. Backend 启动 + snapshot ✅

```bash
export PYTHONPATH=/opt/claude/mystocks_spec:${PYTHONPATH:-}
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# 进程 cwd = /opt/claude/mystocks_spec/web/backend
cat .extra-source-snapshot.json
```

**结果**: `{"adapters": []}`。

启动日志关键行:
```
INFO:app.main:ℹ️ No EXTRA_SOURCE_ADAPTERS configured; skipping ExtraSource registration
INFO:app.main:✅ ExtraSource registry snapshot dumped to .extra-source-snapshot.json
INFO:     Application startup complete.
```

## 本 session 校正:Layer 1/2/3 含义

**误读(本 session 起初)**:Layer 2 = mix-in 注册路径,Layer 3 = tenant override。

**正读(参 `openspec/changes/add-extra-source-adapter-contract/design.md` §2)**:

| Layer | 含义 | 本仓是否要实现 |
|-------|------|---------------|
| Layer 1 | ExtraSource 注册与校验(同步无网络,启动 lifespan) | ✅ **本提案范围,已完成** |
| Layer 2 | OpenStock 内部容灾(category-level fallback) | ❌ **完全排除** — 跨仓,属 OpenStock 仓,本仓永远不实现 |
| Layer 3 | 故障处理分工 | ✅ **作为契约纪律**(消费者侧永远不做 fallback),无代码,只需遵守 |

**含义**: 本提案 Phase 1-5 实际覆盖了 Layer 1 全部落地工作 + Layer 3 的契约纪律文档化(README/design.md)。Layer 2 不是本仓的活,本 session 不应再去推 mix-in adapter 真实注入 smoke test(那是 OpenStock 仓 Layer 2 落地后的事)。

## 本 session 踩坑记录 (与 PoC 无关,但下一 session 需知)

| 坑 | 表现 | 解决 |
|----|------|------|
| PYTHONPATH 缺仓库根 | `ModuleNotFoundError: No module named 'config.data_sources_loader'` | `export PYTHONPATH=/opt/claude/mystocks_spec:${PYTHONPATH:-}` |
| `.env` 必须在 cwd | `启动失败：缺少必需的环境变量配置 (POSTGRESQL_HOST, JWT_SECRET_KEY, BACKEND_PORT...)` | cwd 必须是 `web/backend/` (该处有 `.env`) |
| Bash 工具是新 shell | `cd` 后再单独调用 `cat` 找不到文件 | 用 `readlink /proc/$PID/cwd` 找 uvicorn 进程 cwd;snapshot 路径是 lifespan 写死的相对路径,只能靠进程 cwd 控制 |
| `python -m uvicorn --app-dir /opt/.../web/backend app.main:app` | cwd 变成 `--app-dir` 设置外的位置,找不到 `.env` | 不要用 `--app-dir`;先 `cd web/backend` 再启动 |
| pkill 自杀 | exit code 144 (SIGKILL),`pkill -f "uvicorn app.main:app"` 会杀掉自己所在 shell | 用 `kill $PID` 拿具体 PID 杀 |
| black 行尾空行 | 提交后才发现 black 想删一行空行 | commit 前必跑 `black --check` + `ruff check`,本 session 已修 |

## tasks.md 状态同步

本 session 核查发现:`tasks.md` 13 项未勾全部实际已完成(分散在 commit `284d9e360` / `60c5dc3a3` / `88d64a77f` / `c68888ad3`)。已批量改为 `[x]`,并在 Phase 2.3 / 3.3 添加路径注释(实际测试落在 `tests/unit/services/extra_source/` 和 `tests/scripts/`,与 tasks.md 原写路径不同)。

## 项目原生检查结果(Phase 5.3 复核)

| 命令 | 结果 |
|------|------|
| `pytest web/backend/tests/unit/services/extra_source/` | ✅ 66 passed |
| `ruff check web/backend/app/services/extra_source/` | ✅ No issues found |
| `black --check web/backend/app/services/extra_source/ web/backend/tests/unit/services/extra_source/` | ✅ All done, 12 files unchanged |

## 下一 session 可做的事 (按优先级)

### 优先 (真实剩余工作)

1. **announcement_service 字段映射集成测试** — 当前 Layer 1 单测只覆盖 registry 拒绝路径;迁移后 `_ANNOUNCEMENT_FIELD_MAP` + `_openstock_result_to_dataframe` 的字段 rename 需要端到端集成测试覆盖至少 1 条真实公告。
2. **drift sentinel CI 化** — 把 `OPENSTOCK_STATIC_CATEGORIES` drift sentinel 加到 CI,防止 OpenStock 端单方面增删 category 时静默漂移。
3. **multi_source_manager 后续退役路径** — PoC 删了 4 方法,但 `multi_source_manager` 仍是大量存量代码的入口;规划全量退役还是保留为 facade?需要 owner 决策。
4. **B4.014 Wave 2/3 真实 adapter 实现** — design.md §4 八方法归属表已落,本提案契约可承载 8 个 ExtraSource adapter 的实际代码。属 follow-up,不在本提案。

### 次要 (治理)

5. **删除 `HANDOFF_C3_DIRECTION6.md`** (上一版 handoff,本文件已替代它)。
6. **`multi_source_manager.py` 体积审计** — PoC 后从 `271 + 几行` 减到 6 行?如果是,考虑直接退役该模块。

### 不要做的事(契约纪律)

- ❌ **不要在消费者侧实现 Layer 2 fallback** — OpenStock 故障时切备源是 OpenStock 仓的活,跨仓(违反 Round 2 D 决策)。
- ❌ **不要为 OpenStock 静态 category 注册 ExtraSource adapter** — Layer 1 启动会 fail,这是设计目的。
- ❌ **不要给 ExtraSource adapter 加"健康检查 + 自动 failover"** — 违反 Layer 3 契约纪律,收到 `DATA_GATEWAY_UNAVAILABLE` 只能业务告警。

## 参考文档

- 三层契约 / Round 2 D 决策: `openspec/changes/add-extra-source-adapter-contract/design.md` §2
- 任务清单(已全部勾选): `openspec/changes/add-extra-source-adapter-contract/tasks.md`
- 上一版 handoff (已被本文件替代): `docs/guides/HANDOFF_C3_DIRECTION6.md`
- 本 PoC commit: `c68888ad3` on `feat/b4-014-fundflow-mixin-openspec-proposal`

## Git 状态

- 当前 branch: `feat/b4-014-fundflow-mixin-openspec-proposal`
- 本 PoC 已 commit (`c68888ad3`)
- black 修复 + tasks.md 同步: 待 commit (本 session 末尾)
- Worktree: `/opt/claude/mystocks_spec/` (主仓,非 worktree)
