# OpenStock 同步策略决策文档

> 状态：**待审核**
> 日期：2026-07-03
> 作者：Claude（AI 协作）
> 审核：用户（JohnC）
> 关联：`openspec/changes/add-extra-source-adapter-contract/` (C3 方向 6 PoC 收尾)

---

## 1. 背景

### 1.1 触发场景

`web/backend/app/services/extra_source/registry.py:30-105` 的 `OPENSTOCK_STATIC_CATEGORIES` 是 OpenStock 70 category 的**硬编码 frozenset 快照**（来源 `DATA_CAPABILITY_SCOPE.md` 2026-07-02）。

当前问题：
- 测试 `test_layer1_opstock_owned_guard.py` 仅守 6 项 PoC 涉及 category 子集（ANNOUNCEMENTS/DRAGON_TIGER/FUND_FLOW/REALTIME_QUOTES/KLINES/BLOCK_TRADE）
- **不能**检测 OpenStock 端单方面增删 category 时本仓漏同步
- design.md §2 已写明"未来 OpenStock 落地 `/sources/categories` endpoint 后改动态加载"，但 endpoint 尚未存在

### 1.2 跨仓拓扑

```
┌─────────────────────┐    ┌─────────────────────┐
│   mystocks_spec     │    │   quantix-rust      │
│   (Python/FastAPI)  │    │   (Rust)            │
│   GitHub: chengjon/ │    │   GitHub: chengjon/ │
│   mystocks          │    │   quantix-rust      │
└──────────┬──────────┘    └──────────┬──────────┘
           │                          │
           │   都消费                 │   已有 archived
           │   OpenStock 数据接口     │   openstock-data-consumption
           │                          │   OpenSpec 提案
           ▼                          ▼
       ┌─────────────────────────────────┐
       │   openstock                     │
       │   Gitea (NAS):                  │
       │   192.168.123.104:3001/john/    │
       │   openstock.git                 │
       │                                 │
       │   工作副本: /opt/claude/openstock│
       │   HEAD: f99c332 on main         │
       └─────────────────────────────────┘
```

### 1.3 关键事实（已核实）

| 项 | 状态 |
|----|------|
| openstock 是独立 git 仓 | ✅ origin = Gitea HTTP，HEAD `f99c332` on `main` |
| openstock 自身有 submodule | ❌ 无（`.gitmodules` 不存在） |
| mystocks_spec 已用 submodule | ❌ 无（全仓 0 submodule） |
| quantix-rust 已用 submodule | ❌ 无（全仓 0 submodule） |
| quantix-rust 与 openstock 关系 | 已 archived `2026-06-* openstock-data-consumption` 提案，确认在消费 |
| Gitea HTTP 可达性 | ✅ 200 |
| 三仓 git host 分布 | openstock → Gitea / quantix-rust → GitHub / mystocks → GitHub |

---

## 2. 候选方案

### 方案 A — 全量 git submodule（不推荐）

**做法**：openstock 作为 mystocks 和 quantix-rust 各自的 submodule。

**陷阱 1（决定性）— Host 不一致 + 网络拓扑**：
- mystocks 和 quantix-rust 都在 **GitHub**
- openstock 在 **Gitea NAS**（`192.168.123.104:3001`，仅局域网可达）
- GitHub 仓的 CI 拉 submodule 时**走公网**，公网无法访问内网 Gitea
- 后果：CI 失败，除非把 Gitea 暴露公网（安全风险）或把 openstock 镜像到 GitHub

**陷阱 2 — pointer 各自漂移**：
- mystocks 锁 openstock commit A，quantix-rust 锁 commit B
- 行为分裂时归因困难
- （这其实是 submodule 设计本质，非本方案独有）

**陷阱 3 — 源码级耦合过重**：
- 本仓真正需要的只是 `docs/DATA_CAPABILITY_SCOPE.md` 一个文件
- submodule 引入整个 openstock 仓（含 server 代码、测试 fixture、adapters 等）
- 文件体积、CI clone 时间、心智负担都不划算

**结论**：**否决**。Host 拓扑决定性否决。

---

### 方案 B — sparse-checkout submodule（仅 docs/）

**做法**：submodule + `git config submodule.openstock.sparseCheckout true` + 只 checkout `docs/`。

**优**：文件体积最小（只拉 docs/）。
**劣**：仍继承方案 A 的 Host 拓扑陷阱（GitHub CI 拉内网 Gitea），且 sparse-checkout 配置在团队多机器同步时易出错。

**结论**：**否决**。Host 拓扑未解决。

---

### 方案 C — CI 跨仓拉取 + 手动 drift check 脚本（推荐短期）

**做法**：
1. 写 `scripts/dev/check_openstock_categories_drift.py`
2. 脚本读环境变量 `OPENSTOCK_REPO_PATH`（默认 `/opt/claude/openstock`）
3. 对比 `docs/DATA_CAPABILITY_SCOPE.md` 与本仓 `OPENSTOCK_STATIC_CATEGORIES`
4. 三档输出：漏同步（上游有、本仓无）/ 残留（上游无、本仓有）/ 一致
5. exit 0 一致 / exit 1 漂移
6. **CI 化可选**：仅当本仓 CI runner 能访问 Gitea 时加 workflow；否则作为本地手动工具

**优**：
- 零源码耦合
- 不引入 submodule 心智负担
- 跨 host 不受影响（脚本只读本地路径）
- 可被 cron / pre-commit / 手动跑

**劣**：
- CI 化受 Gitea 局域网限制（GitHub Actions 跑不动）
- 需要本地存在 openstock 工作副本（已是当前事实）

**结论**：**推荐为短期方案（1-3 个月）**。

---

### 方案 D — 发布制 / 版本号锁定（推荐长期）

**做法**：
1. openstock 每次影响 category 清单的改动打 git tag（如 `data-scope-2026-07`）
2. openstock 同步发布一个**纯契约包**到 GitHub Packages / PyPI / 私有 registry，包内容：
   - `openstock_contracts/data_categories.json`（机器可读的 category 清单）
   - `openstock_contracts/__init__.py`（Python 绑定）
3. mystocks 通过 `requirements.txt` / `pyproject.toml` 锁版本
4. quantix-rust 通过 `Cargo.toml`（如果出 Rust binding）或直接读 JSON

**优**：
- 真正"互不影响"——版本号是显式契约
- 各消费者按自己节奏升级
- 跨 host 无障碍（包 registry 走公网）
- 与 design.md §2 "未来 `/sources/categories` endpoint" 兼容（endpoint 落地后，"包"换成"API call"即可）

**劣**：
- openstock 仓需要新增发布流程（CI 发包、版本号管理、changelog）
- 短期工程量大
- 需要 openstock owner（也是 JohnC）确认契约包的 schema

**结论**：**推荐为长期方案（3-6 个月落地）**，作为 OpenSpec 提案。

---

### 方案 E — 不做（保持现状）

**做法**：维持 hardcoded frozenset + 6 项 sentinel 测试，不做任何 drift 检测。

**风险**：
- OpenStock 端删 category（如某 category 改名） → 本仓 Layer 1 拒绝逻辑失效
- OpenStock 端加 category → 本仓 ExtraSource 仍可注册该 category 名（重名风险）

**结论**：**否决**。当前 sentinel 只守 6 项，剩余 64 项无防护。

---

## 3. 推荐路径

### 短期（本周）— 方案 C

| 步骤 | 工件 | 责任 |
|------|------|------|
| 1. 写 drift check 脚本 | `scripts/dev/check_openstock_categories_drift.py` | Claude/next session |
| 2. 写脚本单测 | `tests/scripts/test_check_openstock_categories_drift.py`（5 场景：一致/漏同步/残留/空清单/路径不存在） | 同上 |
| 3. 文档化运行方式 | `docs/guides/HANDOFF_C3_DIRECTION6_DONE.md` 增章节 | 同上 |
| 4. 频率 | 手动 + 月度 cron（不动 CI，因 Gitea 局域网） | 用户决定 |

### 中期（1-2 月）— 评估方案 D

| 决策点 | 输入 |
|--------|------|
| openstock 是否愿意发包？ | 与 openstock owner（JohnC）确认 |
| 包 schema？JSON / YAML / TOML | 设计提案 |
| 包 host？Gitea Packages / GitHub Packages / PyPI 私有 | 部署决策 |
| 是否一并覆盖 quantix-rust？ | 双仓契约一致性 |

落地形式：在 **openstock 仓**开 OpenSpec 提案 `add-data-scope-contract-package`（不是本仓）。

### 长期（3-6 月）— 等 OpenStock `/sources/categories` endpoint

design.md §2 已写明终极方案：OpenStock 启动期发布 `/sources/categories` 静态 endpoint，本仓 lifespan 启动期动态拉取，**完全取代 frozenset**。

落地形式：在 **openstock 仓**开提案 `add-categories-static-endpoint`，本仓 follow-up 改 lifespan 加载逻辑。

---

## 4. 不在本策略范围

- `multi_source_manager.py` 彻底退役（独立 commit/PR）
- `eastmoney_enhanced` / `cninfo_adapter` DI 消费链路审计
- `announcement_service._ANNOUNCEMENT_FIELD_MAP` 端到端集成测试
- Layer 2 OpenStock 内部容灾（跨仓，design.md §2 已排除）

---

## 5. 待审核问题（请用户决定）

| # | 问题 | 选项 | 推荐 |
|---|------|------|------|
| Q1 | 短期方案采纳？ | C / E / 其他 | **C** |
| Q2 | 是否在 openstock 仓开方案 D 提案？ | 是 / 否 / 先观察 | **先观察 1 个月** |
| Q3 | drift check 脚本运行频率？ | 手动 / 周 cron / 月 cron | **月 cron**（openstock category 清单变动低频） |
| Q4 | 本决策文档位置是否合适？ | `docs/standards/` 保留 / 迁 `openspec/changes/` | **保留**（跨提案的长期决策） |

---

## 6. 变更历史

| 日期 | 变更 | 作者 |
|------|------|------|
| 2026-07-03 | 初稿（基于本仓 C3 方向 6 PoC 收尾） | Claude |
