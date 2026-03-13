# Byapi Runtime Config Design

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

- 修改 [src/adapters/byapi_adapter.py](/opt/claude/mystocks_spec/src/adapters/byapi_adapter.py)
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
