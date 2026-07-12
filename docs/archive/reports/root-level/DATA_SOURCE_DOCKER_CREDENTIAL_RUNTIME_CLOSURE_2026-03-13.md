# 数据源 Docker 凭据接通补充报告

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


> 日期: 2026-03-13
> 作用: 覆盖 2026-03-12 最终检查报告中关于 Byapi / Tushare 的旧状态描述

## 当前结论

- `ByapiAdapter` 已收敛到运行时读取 `BYAPI_KEY` / `BYAPI_BASE_URL`
- `TushareDataSource` 已修复只读文件系统问题，初始化不再依赖 `ts.set_token()` 落盘
- Docker 生产 compose 已暴露：
  - `BYAPI_KEY`
  - `BYAPI_BASE_URL`
  - `TUSHARE_TOKEN`
- `config/docker/scripts/start-all.sh` 和 `config/docker-infra/scripts/start-all.sh` 已自动加载根目录 `.env.data-sources.local`
- 根目录本地凭据文件已创建：`.env.data-sources.local`
  - Git 状态为 ignored
  - 当前权限为 `600`

## 实测结果

- 基于 `.env.data-sources.local` 的联合探针：
  - `ByapiAdapter().get_stock_list()` -> `5191` rows
  - `TushareDataSource().available` -> `True`

## 定向验证

- 聚焦回归：`43 passed`
- 范围覆盖：
  - Byapi runtime config
  - Tushare read-only runtime fix
  - Docker credential assets
  - Docker start scripts local env loading

## 现在应视为已完成的事项

- Byapi 凭据接入
- Tushare 凭据接入
- Docker 入口的数据源凭据持久化

## 保留约束

- 明文密钥仍未写入任何版本化文件
- 真实凭据仅存在于 `.env.data-sources.local`
- 若后续更换凭据，只需更新 `.env.data-sources.local`
