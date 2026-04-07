# Mock Data Validator Hook 调整总结报告

> **历史总结说明**:
> 本文件是某次阶段性交付、修复验收、部署确认或专题推进的历史总结快照，用于追溯当时的实施结论。
> 其中的完成度、通过状态和结论不应直接视为当前事实；引用前应结合 `architecture/STANDARDS.md`、当前实现与最新验证结果重新确认。


**日期**: 2026-03-01
**范围**: `.claude/hooks/post-tool-use-mock-data-validator.sh` 及相关说明文档
**目标**: 扩大 mock 数据检测覆盖范围，同时降低误报噪音并支持阈值可配置

---

## 1. 背景与问题

你反馈 `post-tool-use-mock-data-validator.sh` “平时感觉不到它在工作”。

排查后确认主要原因：
- 旧规则覆盖面不足（部分语言/场景易跳过）。
- 输出可感知性不足（提示不稳定）。
- 建议规则过宽时会引入大量噪音。

---

## 2. 本次改造内容

### 2.1 覆盖范围扩容
- 支持 `PostToolUse` 下 `Edit|Write` 两类输入。
- 分析内容优先级：
  1) `tool_input.new_string`（Edit）
  2) `tool_input.content`（Write）
  3) 文件落盘内容（回退）
- 生效范围扩大到常见可写文本代码文件（Python/TS/JS/Vue/JSON/YAML 等）。

### 2.2 输出机制标准化
- 统一改为 `hookSpecificOutput.additionalContext` JSON 输出。
- 保持非阻塞：`exit 0`。

### 2.3 规则调优（降噪）
- 规则5（数据源工厂建议）改为：**仅在已有违规命中时再提示**。
- 规则5关键词收窄，去除高噪音词，保留更贴近行情读取语义的关键词。
- 文档类扩展名排除，避免在纯文档里产生无意义检测。

### 2.4 阈值参数化（新）
新增环境变量（含默认值和非法值兜底）：
- `MOCK_VALIDATOR_PRICE_MIN`（默认 `3`）
- `MOCK_VALIDATOR_STOCK_CODE_MIN`（默认 `5`）

判定逻辑改为动态阈值，并在告警文案中带出阈值，便于定位：
- 价格字段：`PRICE_COUNT >= PRICE_MIN`
- 股票代码：`STOCK_CODE_COUNT >= STOCK_CODE_MIN`

---

## 3. 验证结果

### 3.1 语法与基本行为
- `bash -n .claude/hooks/post-tool-use-mock-data-validator.sh`：通过。
- 默认阈值下样例可触发告警。
- 自定义高阈值（`10/10`）下同样样例不触发：符合预期。

### 3.2 全仓回放统计（调优前）
- 总扫描：2222
- 总命中：625
- 命中率：28.13%
- 分区：
  - `src`: 929 扫描 / 256 命中（27.56%）
  - `web/frontend/src`: 808 扫描 / 203 命中（25.25%）
  - `web/backend/app`: 485 扫描 / 166 命中（34.23%）

### 3.3 全仓回放统计（调优后）
- 分区：
  - `src`: 907 扫描 / 50 命中（5.51%）
  - `web/frontend/src`: 797 扫描 / 63 命中（7.90%）
  - `web/backend/app`: 484 扫描 / 28 命中（5.79%）

结论：命中率显著下降，噪音明显减少，检测更聚焦于真实可疑硬编码场景。

---

## 4. 变更文件清单

1. `.claude/hooks/post-tool-use-mock-data-validator.sh`
   - 扩容、标准化输出、规则调优、阈值参数化。

2. `.claude/hooks/README.md`
   - 新增阈值调参说明（`Mock Data Validator Threshold Tuning`）。

---

## 5. 使用说明（运维/本地调参）

提高阈值（减少告警）：

```bash
export MOCK_VALIDATOR_PRICE_MIN=6
export MOCK_VALIDATOR_STOCK_CODE_MIN=8
```

降低阈值（更严格）：

```bash
export MOCK_VALIDATOR_PRICE_MIN=2
export MOCK_VALIDATOR_STOCK_CODE_MIN=3
```

> 建议在团队内统一一套默认阈值，并在 CI/本地环境保持一致，避免“本地命中/CI不命中”分歧。

---

## 6. 当前结论

本次目标已完成：
- ✅ mock 数据检测覆盖范围已扩大到常见可写文本代码文件场景。
- ✅ 输出可感知性提升（稳定 JSON additionalContext）。
- ✅ 误报噪音显著下降。
- ✅ 阈值可配置，后续可按模块/阶段动态调优。
