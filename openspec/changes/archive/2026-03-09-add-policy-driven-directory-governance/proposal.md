# Change Proposal: add-policy-driven-directory-governance

## Why

当前目录治理工具以“阈值统计 + 后缀搬运”为主，适合一次性清理，不适合长期治理。随着 MyStocks 演化为包含 Python、Web、OpenSpec、AI 工具链和大量治理资产的仓库，现有 `scripts/maintenance/check-structure.sh` 已无法准确区分：

- 新引入的结构违规
- 仓库中已有但暂未收敛的历史技术债
- 应被忽略的工具链与运行时目录

这导致“检查通过”与“治理收敛”之间存在断层，也让根目录与文档/报告/归档的长期收敛缺少自动化护栏。

## What Changes

本变更新增一个**策略清单驱动**的目录治理检查器，并保持现有命令入口兼容：

- 新增机器可读的目录治理策略文件
- 新增 Python 版检查引擎，按策略评估根目录和关键收敛规则
- 保留 `scripts/maintenance/check-structure.sh` 作为兼容入口
- 将“新违规”和“历史债务”分开报告
- 支持按变更路径增量评估，用于 pre-commit、`.githooks` 和 CI
- 支持文本与 JSON 输出，便于人工查看和 CI 集成

## Scope

### In Scope

- 目录治理策略 YAML
- 目录治理检查引擎
- `check-structure.sh` 兼容包装
- 覆盖核心行为的单元测试
- OpenSpec 规格与设计文档

### Out of Scope

- 直接迁移全仓目录
- 自动搬运文件
- 修改 `organize-files.sh` 的整理逻辑
- 大规模清理历史目录债务

## Expected Impact

- 为后续目录收敛提供长期、可执行、可演进的检查基线
- 将“新增违规阻断”和“历史债务提示”分层处理
- 为后续 CI / pre-commit / 定时巡检提供统一接口

## Risks and Mitigations

- **风险：规则过严导致当前仓库无法使用**
  - **缓解**：引入 tolerated legacy 条目，将历史债务降级为 warning
- **风险：扫描成本过高**
  - **缓解**：跳过 dot-directories、`node_modules`、`__pycache__` 等已知噪音目录
- **风险：破坏现有调用方式**
  - **缓解**：保留 `check-structure.sh` 命令入口与常用参数
