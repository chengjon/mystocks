# Tasks — ExtraSourceAdapter Contract

> 实施清单。每项任务完成后将 `- [ ]` 改为 `- [x]`。
> 本提案 Layer 1 独立可落地,不依赖 OpenStock 跨仓改动。

## Phase 1 — 接口与契约(可独立合并)

- [x] **1.1** 创建模块目录 `web/backend/app/services/extra_source/`
  - [x] `__init__.py` 导出公开符号(`ExtraSourceMeta`, `ExtraSourceResult`, `ExtraSourceAdapter`, `register_extra_source`, `ExtraSourceCategoryConflictError`)
  - [x] `contract.py` 定义 `ExtraSourceMeta` / `ExtraSourceResult` / `ExtraSourceAdapter` / `ExtraSourceCategoryConflictError`
  - [x] `registry.py` 定义 `OPENSTOCK_STATIC_CATEGORIES: frozenset[str]`(70 项,来源 `DATA_CAPABILITY_SCOPE.md` 2026-07-02 快照)+ `register_extra_source()` + 内部 `_registered: dict[str, ExtraSourceAdapter]`
- [x] **1.2** 同步 OpenStock 静态 70 category 到 `OPENSTOCK_STATIC_CATEGORIES`
  - 来源:`/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md` 2026-07-02 snapshot
  - 模块顶部注释写明来源 + 快照日期 + 同步责任人
- [x] **1.3** 单元测试 `tests/unit/services/extra_source/test_registry.py`
  - [x] 常规 ExtraSource(category 不重叠,`expires_on=None`)注册成功
  - [x] TEMP_OVERRIDE(category 不重叠,`expires_on="2026-09-30"`)注册成功(静态注册期不做日期校验)
  - [x] 重叠 category 触发 `ExtraSourceCategoryConflictError`
  - [x] 同名 name 重复注册触发 `ExtraSourceNameConflictError`
- [x] **1.4** 单元测试 `tests/unit/services/extra_source/test_contract.py`
  - [x] `ExtraSourceMeta` frozen dataclass 不可变
  - [x] `ExtraSourceResult` 仅含 `data` + `provider_used`(单源,无 fallback 字段)
  - [x] Protocol `ExtraSourceAdapter` 实现类通过 isinstance 检查(若用 `runtime_checkable`)

## Phase 2 — 路由层与启动集成

- [x] **2.1** 新增 `web/backend/app/services/extra_source/router.py`
  - [x] 不动 `data_source_factory/data_source_mode.py`:`HybridDataSource` 是 endpoint-driven,与 category 路由抽象错位
  - [x] `ExtraSourceRouter.fetch(category, params)`:
    * `category ∈ OPENSTOCK_STATIC_CATEGORIES` → 抛 `UnsupportedCategoryError`(编程错误)
    * `category` 在 registry 中 → 调 `adapter.fetch(params)`
    * 其他 → 抛 `UnsupportedCategoryError`(handler 映射为 `UNSUPPORTED_CATEGORY` 信封)
  - [x] adapter `fetch()` 抛异常 → 捕获并包装为 `ExtraSourceFetchError`,带 `adapter` / `cause` 上下文;不重试,不切 OpenStock(handler 映射为 `DATA_GATEWAY_UNAVAILABLE`)
- [x] **2.2** FastAPI lifespan 注入 ExtraSource 注册步骤
  - [x] `web/backend/app/main.py` lifespan 启动阶段遍历配置中的 ExtraSource adapter 实例
  - [x] 调用 `register_extra_source(adapter)`,校验失败则启动 fail
  - [x] 关闭阶段调用 `clear_registered()`(测试隔离用)
  - [x] 启动注册完成后调用 `dump_registered_snapshot(".extra-source-snapshot.json")`(Phase 3 CI 读)
- [x] **2.3** 集成测试 `tests/unit/services/extra_source/test_lifespan_loading.py`
  > 注:项目无 `tests/integration/` 目录,Phase 2.3 测试落在 `tests/unit/services/extra_source/`,实际为 lifespan + adapter loading 的集成式 unit test
  - [x] 启动时正常注册一个 stub ExtraSource
  - [x] 启动时重叠 category 触发启动 fail
  - [x] 启动后 `ExtraSourceRouter.fetch(category)` 命中 stub adapter 返回数据
  - [x] `ExtraSourceRouter.fetch(static_category)` 抛 `UnsupportedCategoryError`
  - [x] `ExtraSourceRouter.fetch(unknown_category)` 抛 `UnsupportedCategoryError`

## Phase 3 — TEMP_OVERRIDE 治理

- [x] **3.1** CI 流水线新增步骤 `scripts/dev/check_temp_override_expiration.py`
  - [x] 数据来源:lifespan 启动完成后,`registry.py` 调用 `dump_registered_snapshot(path=".extra-source-snapshot.json")` 输出当前注册表(含每个 adapter 的 `name` / `category` / `expires_on`);CI 脚本读该 JSON
  - [x] 提取 `expires_on`,与当前日期比对
  - [x] 过期 → exit 1;提前 7 天 → stderr warn
- [x] **3.2** CI 集成(GitHub Actions / 类似 CI 配置)
  - `.github/workflows/temp-override-expiration.yml`(独立 workflow,仅 ExtraSource 相关路径变更时触发)
  - 失败阻断合并
- [x] **3.3** 单元测试 `tests/scripts/test_check_temp_override_expiration.py`
  > 注:测试落在 `tests/scripts/` 而非 tasks.md 原写的 `tests/unit/scripts/`(项目历史命名)
  - [x] 无 ExtraSource → exit 0
  - [x] 常规 ExtraSource → exit 0
  - [x] TEMP_OVERRIDE 未过期 → exit 0
  - [x] TEMP_OVERRIDE 过期 → exit 1
  - [x] TEMP_OVERRIDE 提前 7 天 → exit 0 + stderr 包含 warning

## Phase 4 — Wave 2/3 归属附录落地(可与 Phase 1-3 并行)

- [x] **4.1** B4.014 Wave 2/3 双仓 issue 开立
  - [x] mystocks_spec 仓 issue:标 `cross-repo-dependency` + `temp-override-backlog`,记录 8 方法归属
  - [x] OpenStock 仓 issue:`MARKET_BIG_DEAL` category 注册需求(Wave 2/3 中需进 OpenStock 的部分)
  - [x] 两个 issue 正文互相链接
  - [x] **完成标志**:两个 issue URL 填入下方(提案合并后 48h 内完成)
    - mystocks_spec issue URL: `https://github.com/chengjon/mystocks/issues/491`
    - OpenStock issue URL: `http://192.168.123.104:3001/john/openstock/issues/11`
- [x] **4.2** design.md 附录表格已落,本 phase 仅做 issue tracking,无代码改动

## Phase 5 — 文档与验证

- [x] **5.1** 更新 `web/backend/app/services/extra_source/README.md`
  - [x] 何时该用 ExtraSource(对应 design.md §4 判定规则)
  - [x] 何时该用 TEMP_OVERRIDE
  - [x] 不该用 ExtraSource 的反例(违反 Layer 2 / Round 2 D 决策)
- [x] **5.2** 运行 `openspec validate add-extra-source-adapter-contract --strict`
  - 修复所有 validation 错误,直到通过
- [x] **5.3** 运行项目原生检查(全部通过)
  - [x] `pytest web/backend/tests/unit/services/extra_source/`(66 passed)
  - [x] `ruff check web/backend/app/services/extra_source/`(No issues found)
  - [x] `black --check web/backend/app/services/extra_source/ web/backend/tests/unit/services/extra_source/`(All done, 12 files unchanged)

## Non-Blocking Follow-ups(不在本提案范围)

- C1 客户端构造点收口(独立提案)
- C2 两 factory 收口(独立提案)
- C7 typed schema(观察期 ≥ 1 月后开独立提案)
- B4.014 Wave 2/3 实际代码落地(使用本提案契约实现 8 个 ExtraSource adapter)
- Layer 2 OpenStock 内部 fallback 框架(跨仓,待 OpenStock 仓自行开提案)
