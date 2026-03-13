# Change: Audit Data And DB Runtime

## Why
当前数据源、数据库、缓存与运行依赖存在历史沉积，缺少一轮统一盘点与清理口径。

## What Changes
- 盘点数据源和数据库运行现状
- 标识冗余项、兼容保留项和待判定项
- 做必要清理与优化修复

## Impact
- Affected specs: data access, storage, runtime config
- Affected code: `src/adapters/**`, `src/data_access/**`, `src/storage/**`, `config/**`
