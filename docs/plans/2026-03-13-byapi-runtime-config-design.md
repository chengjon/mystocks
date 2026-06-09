# Byapi Runtime Config Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Goal

让 `ByapiAdapter` 在不把密钥写入仓库的前提下恢复可用，并与当前实际服务端口径对齐。

## Decision

- `ByapiAdapter` 默认 `base_url` 从 `http://api.biyingapi.com` 收敛到 `https://api.biyingapi.com`
- 运行时优先读取环境变量：
  - `BYAPI_KEY`
  - `BYAPI_LICENCE`
  - `BYAPI_LICENSE`
  - `BYAPI_TOKEN`
  - `BYAPI_BASE_URL`
- 显式传参优先级最高
- 不把任何有效 key 固化进源码、配置文件或测试文件

## Scope

- 修改 [src/adapters/byapi_adapter.py](../../src/adapters/byapi_adapter.py)
- 更新 Byapi 相关单测默认行为预期
- 用临时环境变量验证 Byapi 与 Tushare 实际恢复情况

## Non-Goals

- 不把密钥写入 `.env`
- 不修改 Tushare 适配器行为
- 不扩展 Byapi 接口功能面

## Verification

- Byapi:
  - 无环境变量时，默认 `base_url` 为 `https`
  - 有环境变量时，默认初始化读取环境变量
  - 临时注入有效 key 后，`get_stock_list()` 返回非空结果
- Tushare:
  - 临时注入有效 token 后，官方 `pro_api` 可返回 `stock_basic`
  - 项目 `TushareDataSource()` 可正常初始化
