## 0. Proposal And Governance

- [x] 0.1 Confirm affected specs: `data-source-runtime-service`, `data-sources`, `containerized-runtime-deployment`, `market-data`, `architecture-governance`.
  - Repo-truth（2026-06-09）：spec deltas 已创建于 `openspec/changes/extract-data-source-runtime-service/specs/`。
- [x] 0.2 Reconcile `optimize-data-source-v2` active status and classify remaining grey/production validation items as blockers or parallel follow-up.
  - Repo-truth（2026-06-09）：本 change 明确依赖并接续 `optimize-data-source-v2`，V2 剩余灰度/生产验收不由本地合成测试冒充完成。
- [x] 0.3 Run `openspec validate extract-data-source-runtime-service --strict`.
  - Repo-truth（2026-06-09）：strict validate 通过。
- [x] 0.4 Obtain user approval before implementation.
  - Repo-truth（2026-06-09）：用户已回复“同意，请继续”后才进入 Phase 1 代码变更。

## 1. In-Process Client Contract

- [x] 1.1 Add `DataSourceClient` interface and `LocalDataSourceClient` implementation backed by the current data-source runtime.
  - Repo-truth（2026-06-09）：新增 `src/core/data_source/client.py`，当前实现只建立 local seam，不迁移 provider 源码。
- [x] 1.2 Add `tests/unit/data_source/test_data_source_client_contract.py`.
  - Repo-truth（2026-06-09）：新增 contract test 文件。
- [x] 1.3 Verify successful responses include source, endpoint, route decision, request id, exchange/received time, staleness, cache state, quality flags, and latency metadata.
  - Repo-truth（2026-06-09）：`test_local_client_fetch_snapshot_returns_contract_metadata` 覆盖该 metadata contract。
- [x] 1.4 Verify typed errors for provider unavailable, timeout, rate limited, circuit open, registry missing, invalid request, and data quality failure.
  - Repo-truth（2026-06-09）：`test_data_source_client_contract.py` 覆盖 provider unavailable、timeout、rate limited、circuit open、registry missing、invalid request 与 data quality failed。
- [x] 1.5 Run V2 prerequisite matrix:
  - `pytest tests/unit/test_smart_router.py tests/unit/test_smart_router_integration.py tests/unit/test_metrics.py tests/unit/test_data_source_metrics_integration.py src/governance/tests/test_fetcher_bridge.py tests/integration/test_batch_processing.py tests/unit/adapters/test_runtime_data_source_regressions.py -q --no-cov`
  - Repo-truth（2026-06-09）：结果 `42 passed`。
- [x] 1.6 Run local contract test:
  - `pytest tests/unit/data_source/test_data_source_client_contract.py -q --no-cov`
  - Repo-truth（2026-06-09）：结果 `8 passed`。

## 2. OpenStock Remote Runtime Container

- [x] 2.0 Obtain explicit Phase 2 approval after reviewing this proposal, completed Phase 0/1 evidence, REST/WebSocket runtime scope, and rollback path.
  - Repo-truth（2026-06-09）：用户在 Phase 2 scope lock 后回复“请继续”，本轮仅执行 REST/WebSocket runtime 和 remote client，不执行 MCP。
- [x] 2.1 Design the `openstock` REST/OpenAPI boundary for health, sources, registry reload, route selection, fetch, and batch endpoints.
  - Repo-truth（2026-06-09）：`/opt/claude/openstock/openstock/app.py` 已提供 health、sources、registry reload、routing、fetch、batch 的最小 REST contract；已推送为 `openstock` 提交 `62e7cd7 feat: add openstock runtime tracer bullet`。
- [x] 2.2 Design the `openstock` WebSocket data-runtime boundary for the approved stream slice; do not implement MCP transports or tools.
  - Repo-truth（2026-06-09）：`/opt/claude/openstock/openstock/app.py` 已提供 `/ws/market` subscribe/snapshot 最小 contract；MCP 排除检查显示 runtime/tests 中无 MCP 实现痕迹。
- [x] 2.3 Add `openstock` runtime service boundary with health, sources, registry reload, route selection, fetch, and batch endpoints.
  - Repo-truth（2026-06-09）：`openstock` runtime tracer bullet 已覆盖 health、sources、registry reload、route selection、fetch、batch 与 `/ws/market` subscribe/snapshot。
- [x] 2.4 Add `RemoteDataSourceClient` using REST/OpenAPI for pull/control-plane operations.
  - Repo-truth（2026-06-09）：`src/core/data_source/client.py` 已新增 `RemoteDataSourceClient` 与 JSON transport。
- [x] 2.5 Add `DATA_SOURCE_CLIENT_MODE=local|remote` rollback switch.
  - Repo-truth（2026-06-09）：`create_data_source_client()` 支持 `DATA_SOURCE_CLIENT_MODE=local|remote`，remote base URL 默认 `OPENSTOCK_BASE_URL` 或 `http://localhost:8031`。
- [x] 2.6 Add `tests/integration/data_source/test_remote_data_source_client_contract.py`.
  - Repo-truth（2026-06-09）：remote client contract tests 已新增并通过。
- [x] 2.7 Add or update config facade parity tests:
  - `tests/api/file_tests/test_data_source_config_api.py`
  - `tests/api/file_tests/test_data_source_registry_api.py`
  - Repo-truth（2026-06-09）：现有 config/registry facade file-level contract tests 覆盖路由、响应模型、reload、registry 操作与配置更新；已与 remote client contract 一起验证通过。
- [x] 2.8 Add `scripts/run_data_source_runtime_smoke.sh`.
  - Repo-truth（2026-06-09）：smoke 脚本已新增；运行结果为 openstock runtime contract `4 passed`，MyStocks remote client contract `5 passed`。
- [x] 2.9 Run:
  - `pytest tests/integration/data_source/test_remote_data_source_client_contract.py tests/api/file_tests/test_data_source_config_api.py tests/api/file_tests/test_data_source_registry_api.py -q --no-cov`
  - `bash scripts/run_data_source_runtime_smoke.sh`
  - Repo-truth（2026-06-09）：combined remote/config facade command `30 passed, 14 warnings`；runtime smoke command openstock `4 passed`，MyStocks remote client `5 passed`。
- [x] 2.10 Verify Phase 2 contains no MCP tool implementation, standalone MCP transport, mounted MCP app, or MCP-over-SSE compatibility work.
  - Repo-truth（2026-06-09）：`openstock/openstock` 与 `openstock/tests` 中无 MCP 代码或测试实现；MCP 仍保留在 Phase 5。

## 2A. OpenStock Repository Bootstrap

- [x] 2A.1 Create or clone `/opt/claude/openstock`.
  - Repo-truth（2026-06-09）：`/opt/claude/openstock` 已初始化为 Git 仓库，当前分支为 `main`。
- [x] 2A.2 Connect the repository to `http://192.168.123.104:3001/john/openstock.git`.
  - Repo-truth（2026-06-09）：`origin` 已绑定到本地私库并推送 `main`。
- [x] 2A.3 Add an initial repository README that states `openstock` is the extracted MyStocks data-source runtime and that implementation requires approved OpenSpec scope.
  - Repo-truth（2026-06-09）：初始提交 `446ddd3 docs: bootstrap openstock runtime repo` 仅包含 `README.md`。
- [x] 2A.4 Do not copy source code from MyStocks into `openstock` until Phase 1 contract boundaries and approval are complete.
  - Repo-truth（2026-06-09）：未向 `/opt/claude/openstock` 拷贝 MyStocks 源码；Phase 2 仅新增独立 REST/WebSocket runtime tracer bullet、contract tests、Dockerfile 与 `pyproject.toml`，提交为 `62e7cd7`。

## 3. AkShare REST/Pull Pilot

- [x] 3.1 Select one AkShare REST/pull category for the first provider/category migration.
  - Repo-truth（2026-06-10）：首个 provider/category 选定为 AkShare A股实时行情/基础列表，MyStocks category 使用既有 `REALTIME_QUOTES`；openstock primary endpoint 为 `akshare.stock_zh_a_spot`。
- [x] 3.2 Ensure route decisions are explainable and include fallback candidates.
  - Repo-truth（2026-06-10）：`/routing/best` 返回 `reason=akshare_realtime_quotes_primary`，并暴露 `fallback_candidates=["akshare.stock_info_a_code_name", "legacy_mystocks_akshare", "local_cache"]`。
- [x] 3.3 Ensure timeout, cache, fallback, circuit breaker, and metrics behavior are observable.
  - Repo-truth（2026-06-10）：request payload 保留 `timeout_ms`；fetch response 暴露 `cache_state`、`quality_flags`、`circuit_state=closed`、`latency_ms`；真实 smoke 验证过 primary 成功路径，也验证过 primary 上游异常时可 fallback 到 `akshare.stock_info_a_code_name` 并通过 `quality_flags` 标注原因。
- [x] 3.4 Add `tests/integration/data_source/test_akshare_runtime_pilot.py`.
  - Repo-truth（2026-06-10）：MyStocks 侧新增 remote client AkShare runtime pilot tests；openstock 侧新增 `tests/test_akshare_runtime_pilot.py`。
- [x] 3.5 Run:
  - `pytest tests/integration/data_source/test_akshare_runtime_pilot.py -q --no-cov`
  - Repo-truth（2026-06-10）：`pytest tests/integration/data_source/test_akshare_runtime_pilot.py -q --no-cov -p no:cacheprovider` 通过 `3 passed`；升级后的 `bash scripts/run_data_source_runtime_smoke.sh` 通过 openstock `9 passed`、真实 AkShare smoke、MyStocks remote client `5 passed`、MyStocks AkShare pilot `3 passed`。

## 4. Realtime WebSocket Pilot

- [x] 4.1 Add data-source runtime `/ws/market` stream for the selected realtime pilot.
  - Repo-truth（2026-06-10）：`/opt/claude/openstock/openstock/app.py` 已将 `/ws/market` 升级为 AkShare realtime pilot stream，支持 subscribe ack、snapshot、quote.update、heartbeat、unsubscribe 与非法消息 error。
- [x] 4.2 Preserve the main backend ability to proxy/bridge to existing `/ws/events` consumers during migration.
  - Repo-truth（2026-06-10）：新增 `src/core/data_source/market_stream_bridge.py`，将 openstock stream message 映射为现有 `/ws/events` 语义通道：`events:market`、`events:market:{symbol}`、`events:system`；未改动既有 FastAPI WebSocket 路由。
- [x] 4.3 Define message types: `subscribe`, `unsubscribe`, `snapshot`, `quote.update`, `heartbeat`, `error`.
  - Repo-truth（2026-06-10）：openstock runtime contract 与 MyStocks bridge contract 均显式覆盖上述六类消息；control message 不广播到 `/ws/events` 消费者。
- [x] 4.4 Add `tests/integration/data_source/test_market_stream_contract.py`.
  - Repo-truth（2026-06-10）：MyStocks 新增 `tests/integration/data_source/test_market_stream_contract.py`；openstock 新增 `/opt/claude/openstock/tests/test_market_stream_contract.py` 并更新 runtime WebSocket contract。
- [x] 4.5 Run:
  - `pytest tests/integration/data_source/test_market_stream_contract.py -q --no-cov`
  - Repo-truth（2026-06-10）：TDD 红灯已确认：openstock 初始失败为连接提前关闭/非法类型未识别；MyStocks 初始失败为缺少 bridge 模块。绿色验证：openstock websocket/runtime contract `6 passed`，MyStocks market stream bridge contract `5 passed`。
  - Repo-truth（2026-06-10）：升级后的 `bash scripts/run_data_source_runtime_smoke.sh` 通过 openstock runtime/AkShare/market-stream `11 passed`、真实 AkShare smoke（`akshare.stock_zh_a_spot`）、MyStocks remote client `5 passed`、MyStocks AkShare pilot `3 passed`、MyStocks market stream bridge `5 passed`。
  - Repo-truth（2026-06-10）：V2 前置回归矩阵保持 `42 passed`；`openspec validate extract-data-source-runtime-service --strict` 通过。

## 5. MCP Diagnostics

- [x] 5.1 Add stdio diagnostics MCP for local low-frequency admin tools if needed.
  - Repo-truth（2026-06-10）：新增 `src/core/data_source/mcp_diagnostics.py`，`stdio` access mode 仅暴露 `get_data_source_health` 与 `explain_route_decision` 两个低频诊断工具，不暴露 fetch/batch/stream 热路径工具。
- [x] 5.2 Add standalone remote MCP only as a diagnostics entrypoint that calls `DataSourceClient` or REST.
  - Repo-truth（2026-06-10）：`standalone_remote` access mode 通过 `RemoteDataSourceClient`/REST `/routing/best` 解释 route decision；contract test 验证不会调用 `/data/fetch`、batch 或 stream。
- [x] 5.3 Add mounted MCP only if it reuses the same `DataSourceRuntime`.
  - Repo-truth（2026-06-10）：`mounted` access mode 要求传入既有 runtime client，并记录/返回同一 `runtime_identity`；未创建 provider 直连或第二套运行时。
- [x] 5.4 Add `tests/integration/data_source/test_mcp_access_modes.py`.
  - Repo-truth（2026-06-10）：新增 MCP access mode contract tests，覆盖 stdio、standalone remote、mounted 以及 `fetch_snapshot`、`fetch_batch`、`stream_market`、`subscribe_market` 热路径拒绝。
- [x] 5.5 Run:
  - `pytest tests/integration/data_source/test_mcp_access_modes.py -q --no-cov`
  - Repo-truth（2026-06-10）：TDD 红灯为缺少 `src.core.data_source.mcp_diagnostics`；实现后 `pytest tests/integration/data_source/test_mcp_access_modes.py -q --no-cov -p no:cacheprovider` 通过 `8 passed`。
  - Repo-truth（2026-06-10）：扩展后的 `bash scripts/run_data_source_runtime_smoke.sh` 通过 openstock runtime/AkShare/market-stream `11 passed`、真实 AkShare smoke（`akshare.stock_zh_a_spot`）、MyStocks remote client `5 passed`、AkShare pilot `3 passed`、market stream bridge `5 passed`、MCP access modes `8 passed`。
  - Repo-truth（2026-06-10）：data-source Phase 1-5 组合验证 `30 passed`；V2 前置回归矩阵保持 `42 passed`；`openspec validate extract-data-source-runtime-service --strict` 通过。

## 6. Old Path Closure

- [x] 6.1 Migrate `adapter_priority_config.yaml` semantics into registry/routing policy after remote mode is stable.
  - Repo-truth（2026-06-10）：新增 `src/core/data_source/closure_policy.py`，将 `config/adapter_priority_config.yaml` 解释为 runtime registry/routing 的 fallback seed policy；`REALTIME_QUOTES` 映射到 legacy `realtime_quote` 顺序 `tdx -> customer -> akshare`，未知 category 回退到 `default`。
- [x] 6.2 Demote YAML registry to seed/fallback only.
  - Repo-truth（2026-06-10）：closure policy 显式声明 `runtime_truth_source=openstock_runtime`、`yaml_registry_role=seed_or_fallback`，不再把 YAML registry 判定为运行时真相源。
- [x] 6.3 Keep old manager/config paths as thin compatibility wrappers until closure evidence is complete.
  - Repo-truth（2026-06-10）：Phase 6 未删除旧 manager/config 路径，policy 中 `retired_paths=()` 且 `compatibility_wrappers_retained=True`；旧路径保留为兼容/回滚边界。
- [x] 6.4 Add `tests/integration/data_source/test_data_source_public_api_parity.py`.
  - Repo-truth（2026-06-10）：新增 public API parity/closure tests，覆盖 legacy priority seed、openstock remote registry contract、YAML seed/fallback role 与旧路径未退役。
- [x] 6.5 Run:
  - `pytest tests/integration/data_source/test_data_source_public_api_parity.py -q --no-cov`
  - `openspec validate extract-data-source-runtime-service --strict`
  - Repo-truth（2026-06-10）：TDD 红灯为缺少 `src.core.data_source.closure_policy`；实现后 `pytest tests/integration/data_source/test_data_source_public_api_parity.py -q --no-cov -p no:cacheprovider` 通过 `3 passed`。
  - Repo-truth（2026-06-10）：data-source Phase 1-6 组合验证 `33 passed`；扩展后的 `bash scripts/run_data_source_runtime_smoke.sh` 通过 openstock `11 passed`、真实 AkShare smoke、MyStocks remote `5 passed`、AkShare pilot `3 passed`、market stream `5 passed`、MCP access modes `8 passed`、public parity `3 passed`；V2 前置回归矩阵保持 `42 passed`。
- [x] 6.6 Archive the change only after implementation tasks, parity evidence, runtime smoke, and rollback evidence are complete.
  - Repo-truth（2026-06-11）：`openspec archive extract-data-source-runtime-service --yes` 已将变更归档为 `openspec/changes/archive/2026-06-11-extract-data-source-runtime-service/`，并更新 `architecture-governance`、`containerized-runtime-deployment`、`data-source-runtime-service`、`data-sources` 与 `market-data` specs。
