# 代码清单扫描工具使用指南

> **参考指南说明**:
> 本文件用于说明 `src/` 目录下局部模块的使用方式、结构背景、调试方法、部署提示或技术参考，帮助理解具体实现。
> 其中的路径、步骤、指标和示例应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为共享规则或当前状态的唯一事实来源。


## 概述

代码清单扫描工具是 MyStocks 项目的代码质量监控模块，用于扫描和分析代码库中的：
- 代码行数统计（支持 .py, .vue, .ts, .tsx, .js, .jsx）
- Mock 数据使用检测
- 环境配置检查

## 快速开始

### 运行扫描

```bash
# 完整扫描（包含验证）
python -m src.monitoring.code_inventory.cli --scan-dirs src scripts web/backend/app

# 跳过验证快速扫描
python -m src.monitoring.code_inventory.cli --no-validation --scan-dirs src scripts web/backend/app

# 指定输出目录
python -m src.monitoring.code_inventory.cli --output-dir ./reports --scan-dirs src
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--scan-dirs` | 要扫描的目录（空格分隔） | src scripts web/backend/app |
| `--output-dir` | 报告输出目录 | reports |
| `--no-validation` | 跳过数据验证 | False |
| `--format` | 输出格式 (json/markdown) | markdown |

## 模块结构

```
src/monitoring/code_inventory/
├── cli.py           # 命令行入口
├── scanner.py       # 文件扫描器
├── line_counter.py  # 代码行数统计
├── mock_detector.py # Mock数据检测
├── env_checker.py   # 环境配置检查
├── reporter.py      # 报告生成器
├── models.py        # 数据模型
├── config.py       # 配置定义
└── storage.py      # 结果存储
```

## 输出说明

### 扫描结果

扫描完成后会生成：
- `summary.json` - 扫描摘要统计
- `inventory.json` - 详细文件清单
- `violations.json` - 违规项列表

### Markdown 报告

可在 `reports/` 目录下找到带时间戳的 Markdown 报告：
```
reports/code_inventory_report_YYYYMMDD.md
```

## 配置说明

### 阈值配置

在 `config.py` 中可调整以下阈值：

```python
# 代码行数阈值
LINE_THRESHOLD = 800

# Mock 使用严重性阈值
MOCK_SEVERITY_THRESHOLDS = {
    "error": 10,    # 超过10处使用视为error
    "warning": 5,   # 超过5处使用视为warning
}
```

### 扫描目录

默认扫描目录在 CLI 中定义，可通过 `--scan-dirs` 参数覆盖。

## 定期扫描

根据 `CLAUDE.md` 要求，**每月至少执行一次扫描**：

```bash
# 建议的执行频率
# 每月第一周执行完整扫描

python -m src.monitoring.code_inventory.cli --scan-dirs src scripts web
```

## 报告解读

### 摘要统计

- **总文件数**: 扫描的文件总数
- **总代码行数**: 所有文件的代码行数总和
- **超过阈值文件**: 代码行数超过配置阈值的文件数
- **使用Mock文件**: 检测到使用Mock数据的文件数

### 严重性级别

| 级别 | 说明 | 行动建议 |
|------|------|----------|
| error | 高风险，需立即处理 | 优先拆分或重构 |
| warning | 中风险，应关注 | 计划优化 |
| info | 低风险，仅供参考 | 可选处理 |

## 常见问题

### Q: 如何只扫描特定文件类型？
A: 当前版本扫描所有支持的文件类型。如需过滤，可在 `scanner.py` 中修改 `FILE_EXTENSIONS` 集合。

### Q: 报告在哪里查看？
A: Markdown 报告位于 `reports/code_inventory_report_*.md`

### Q: 如何忽略某些目录？
A: 在 `config.py` 的 `EXCLUDE_DIRS` 中添加目录名。

## 相关文档

- [代码清单扫描报告](../../reports/code_inventory_report_20260223.md)
- [CLAUDE.md](../../CLAUDE.md) - 定期扫描要求
