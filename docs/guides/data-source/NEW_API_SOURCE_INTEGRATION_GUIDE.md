# 新增数据源/API 接口开发指引 (v2.3)

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文档旨在指导开发者如何在项目中集成新的数据源或 API。本项目采用 FastAPI 框架，全面切换至 ArtDeco 3.1 三数据库架构。

---

## 1. 核心架构约束 (Mandatory)

### 1.1 契约先行
所有新接口必须先更新 `web/backend/app/api/VERSION_MAPPING.py`。

### 1.2 响应标准化
返回体必须通过 `ResponseFormatMiddleware` 包装，严禁返回裸 JSON。

### 1.3 数据库路由
- 时序数据 (K线/Tick) -> **TDengine**
- 静态配置/元数据 -> **PostgreSQL**

### 1.4 Redis 集成要点 (Week 4+ Mandatory)
Redis 现已作为系统的“神经元”全面集成，不再是可选组件：
*   **L2 缓存**: 热点 API (如实时行情) 必须接入 `RedisCacheService`。
*   **Pub/Sub**: 跨系统信号 (如 Windows TDX 数据推送到 WSL2) 必须使用 `RedisPubSub`。
*   **分布式锁**: 针对定时同步任务，必须使用 `RedisLockService` 防止并发冲突。

---

## 2. 5步验证流程 (Verification)
每次提交前必须运行：
```bash
bash scripts/verify_data_source_integration.sh
```

## 3. YAML 注册表红线
- 必须使用 **偶数空格缩进**。
- `test_parameters` 必须包含真实的 symbol 用于健康检查。

---
**更新日志**:
- v2.3: Redis 升级为强制集成组件，补充跨系统桥接指南。
