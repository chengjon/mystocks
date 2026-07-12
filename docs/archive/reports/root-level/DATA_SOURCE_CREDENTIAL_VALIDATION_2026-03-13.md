# 数据源凭据验证补充记录

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> 日期: 2026-03-13
> 说明: 本记录基于用户提供的临时 Byapi / Tushare 凭据做运行时验证，不表示这些凭据已经写入项目环境文件。

## 结论

- Byapi 可恢复
  - 根因不是服务整体不可用，而是项目默认使用旧 license + `http`
  - 修复后 `ByapiAdapter` 默认走 `https`
  - `ByapiAdapter` 现在优先读取 `BYAPI_KEY` / `BYAPI_BASE_URL`
  - 使用用户提供的一组有效 Byapi key 做临时环境变量验证时，`get_stock_list()` 返回 `5191` rows

- Tushare 可恢复
  - 根因不是 token 无效，而是项目运行环境没有设置 `TUSHARE_TOKEN`
  - 使用用户提供的一组有效 Tushare token 做临时环境变量验证时：
    - 官方 `tushare.pro_api()` 可返回 `stock_basic`
    - 项目 `TushareDataSource()` 初始化成功，`available == True`

## 运行时入口选择

- 已选定持久化入口: Docker Compose / container env
- 当前资产落点: `config/docker/docker-compose.prod.yml`
- 真实凭据仍应通过本地 `--env-file` 或部署平台 secrets 注入

## 当前状态重新定义

- Byapi:
  - 从 `FAIL` 调整为 `凭据可用，等待环境持久化`

- Tushare:
  - 从 `FAIL` 调整为 `凭据可用，等待环境持久化`

## 仍需完成

1. 在实际部署使用的本地 `--env-file` 或 secrets 管理中填入主用 Byapi key 和 Tushare token
2. 避免把明文密钥提交进 Git
3. 选定最终生效的 Byapi key 和 Tushare token，只保留一套主用凭据
