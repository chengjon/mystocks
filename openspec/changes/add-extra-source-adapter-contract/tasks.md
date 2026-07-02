# Tasks — ExtraSourceAdapter Contract

> 实施清单。每项任务完成后将 `- [ ]` 改为 `- [x]`。
> 本提案 Layer 1 独立可落地,不依赖 OpenStock 跨仓改动。

## Phase 1 — 接口与契约(可独立合并)

- [ ] **1.1** 创建模块目录 `web/backend/app/services/extra_source/`
  - [ ] `__init__.py` 导出公开符号(`ExtraSourceMeta`, `ExtraSourceResult`, `ExtraSourceAdapter`, `register_extra_source`, `ExtraSourceCategoryConflictError`)
  - [ ] `contract.py` 定义 `ExtraSourceMeta` / `ExtraSourceResult` / `ExtraSourceAdapter` / `ExtraSourceCategoryConflictError`
  - [ ] `registry.py` 定义 `OPENSTOCK_STATIC_CATEGORIES: frozenset[str]`(70 项,来源 `DATA_CAPABILITY_SCOPE.md` 2026-07-02 快照)+ `register_extra_source()` + 内部 `_registered: dict[str, ExtraSourceAdapter]`
- [ ] **1.2** 同步 OpenStock 静态 70 category 到 `OPENSTOCK_STATIC_CATEGORIES`
  - 来源:`/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md` 2026-07-02 snapshot
  - 模块顶部注释写明来源 + 快照日期 + 同步责任人
- [ ] **1.3** 单元测试 `tests/unit/services/extra_source/test_registry.py`
  - [ ] 常规 ExtraSource(category 不重叠,`expires_on=None`)注册成功
  - [ ] TEMP_OVERRIDE(category 不重叠,`expires_on="2026-09-30"`)注册成功(静态注册期不做日期校验)
  - [ ] 重叠 category 触发 `ExtraSourceCategoryConflictError`
  - [ ] 同名 name 重复注册触发 `ExtraSourceNameConflictError`
- [ ] **1.4** 单元测试 `tests/unit/services/extra_source/test_contract.py`
  - [ ] `ExtraSourceMeta` frozen dataclass 不可变
  - [ ] `ExtraSourceResult` 仅含 `data` + `provider_used`(单源,无 fallback 字段)
  - [ ] Protocol `ExtraSourceAdapter` 实现类通过 isinstance 检查(若用 `runtime_checkable`)

## Phase 2 — 路由层与启动集成

- [ ] **2.1** 修改 `web/backend/app/services/data_source_factory/data_source_mode.py`
  - [ ] `HybridDataSource` 注入 `extra_source_registry` 引用
  - [ ] fallback 链扩展:Real(OpenStock) → ExtraSource(registry 内 category 命中)→ Mock(test) / UNSUPPORTED_CATEGORY(prod)
  - [ ] adapter `fetch()` 抛异常 → 捕获并包装为 `DATA_GATEWAY_UNAVAILABLE`,带 `adapter` / `cause` 上下文;不重试,不切 OpenStock
- [ ] **2.2** FastAPI lifespan 注入 ExtraSource 注册步骤
  - [ ] `web/backend/app/main.py` lifespan 启动阶段遍历配置中的 ExtraSource adapter 实例
  - [ ] 调用 `register_extra_source(adapter)`,校验失败则启动 fail
  - [ ] 关闭阶段清理 `_registered` dict(测试隔离用)
- [ ] **2.3** 集成测试 `tests/integration/services/extra_source/test_lifespan_registration.py`
  - [ ] 启动时正常注册一个 stub ExtraSource
  - [ ] 启动时重叠 category 触发启动 fail
  - [ ] 业务路由调用 ExtraSource 命中 category 时返回数据

## Phase 3 — TEMP_OVERRIDE 治理

- [ ] **3.1** CI 流水线新增步骤 `scripts/dev/check_temp_override_expiration.py`
  - [ ] 数据来源:lifespan 启动完成后,`registry.py` 调用 `dump_registered_snapshot(path=".extra-source-snapshot.json")` 输出当前注册表(含每个 adapter 的 `name` / `category` / `expires_on`);CI 脚本读该 JSON
  - [ ] 提取 `expires_on`,与当前日期比对
  - [ ] 过期 → exit 1;提前 7 天 → stderr warn
- [ ] **3.2** CI 集成(GitHub Actions / 类似 CI 配置)
  - 在 lint/test job 后追加 `temp-override-expiration` step
  - 失败阻断合并
- [ ] **3.3** 单元测试 `tests/unit/scripts/test_check_temp_override_expiration.py`
  - [ ] 无 ExtraSource → exit 0
  - [ ] 常规 ExtraSource → exit 0
  - [ ] TEMP_OVERRIDE 未过期 → exit 0
  - [ ] TEMP_OVERRIDE 过期 → exit 1
  - [ ] TEMP_OVERRIDE 提前 7 天 → exit 0 + stderr 包含 warning

## Phase 4 — Wave 2/3 归属附录落地(可与 Phase 1-3 并行)

- [ ] **4.1** B4.014 Wave 2/3 双仓 issue 开立
  - [ ] mystocks_spec 仓 issue:标 `cross-repo-dependency` + `temp-override-backlog`,记录 8 方法归属
  - [ ] OpenStock 仓 issue:`MARKET_BIG_DEAL` category 注册需求(Wave 2/3 中需进 OpenStock 的部分)
  - [ ] 两个 issue 正文互相链接
  - [ ] **完成标志**:两个 issue URL 填入下方(提案合并后 48h 内完成)
    - mystocks_spec issue URL: `<填入>`
    - OpenStock issue URL: `<填入>`
- [ ] **4.2** design.md 附录表格已落,本 phase 仅做 issue tracking,无代码改动

## Phase 5 — 文档与验证

- [ ] **5.1** 更新 `web/backend/app/services/extra_source/README.md`
  - [ ] 何时该用 ExtraSource(对应 design.md §4 判定规则)
  - [ ] 何时该用 TEMP_OVERRIDE
  - [ ] 不该用 ExtraSource 的反例(违反 Layer 2 / Round 2 D 决策)
- [ ] **5.2** 运行 `openspec validate add-extra-source-adapter-contract --strict`
  - 修复所有 validation 错误,直到通过
- [ ] **5.3** 运行项目原生检查(全部通过)
  - [ ] `pytest tests/unit/services/extra_source/ tests/integration/services/extra_source/`
  - [ ] `ruff check web/backend/app/services/extra_source/`
  - [ ] `black --check web/backend/app/services/extra_source/`

## Non-Blocking Follow-ups(不在本提案范围)

- C1 客户端构造点收口(独立提案)
- C2 两 factory 收口(独立提案)
- C7 typed schema(观察期 ≥ 1 月后开独立提案)
- B4.014 Wave 2/3 实际代码落地(使用本提案契约实现 8 个 ExtraSource adapter)
- Layer 2 OpenStock 内部 fallback 框架(跨仓,待 OpenStock 仓自行开提案)
