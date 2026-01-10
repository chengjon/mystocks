# 数据接口扫描工具使用指南

## 概述

数据接口扫描工具 (`scripts/tools/data_interface_scanner.py`) 用于扫描和分析 MyStocks 项目中所有已注册的数据接口，提供详细的明细表和统计信息。

## 功能特性

### 📊 核心功能
- **实时扫描**: 自动扫描 `config/data_sources_registry.yaml` 配置文件
- **明细表格**: 生成包含所有数据接口的详细表格
- **统计分析**: 按数据源类型、数据分类、目标数据库等维度统计
- **质量评估**: 显示数据质量评分和优先级分布
- **过滤功能**: 支持按数据源名称或类型过滤
- **多种输出**: 支持表格显示、JSON导出、CSV导出

### 📈 统计信息
- 数据源类型分布 (mock, api_library, database)
- 数据分类分布 (DAILY_KLINE, MINUTE_KLINE, FINANCIAL_DATA等)
- 目标数据库分布 (PostgreSQL, TDengine)
- 质量评分分布 (high/medium/low)
- 优先级分布 (high/medium/low)

## 使用方法

### 基本扫描
```bash
# 扫描所有数据接口，生成表格报告
python scripts/tools/data_interface_scanner.py
```

### 详细报告
```bash
# 生成包含详细信息和统计的完整报告
python scripts/tools/data_interface_scanner.py --detailed
```

### 按条件过滤
```bash
# 只显示 akshare 相关接口
python scripts/tools/data_interface_scanner.py --filter-source akshare

# 只显示 tushare 相关接口
python scripts/tools/data_interface_scanner.py --filter-source tushare
```

### 数据导出
```bash
# 导出为 JSON 格式
python scripts/tools/data_interface_scanner.py --output-format json --output-file interfaces.json

# 导出为 CSV 格式
python scripts/tools/data_interface_scanner.py --output-format csv --output-file interfaces.csv
```

## 输出示例

### 表格报告
```
====================================================================================================
📊 MyStocks 数据接口扫描报告
====================================================================================================
扫描时间: 2026-01-09 14:20:09
配置文件: /opt/claude/mystocks_spec/config/data_sources_registry.yaml
总接口数: 23

📈 统计概览:
  • 按数据源类型: {'mock': 1, 'api_library': 21, 'database': 1}
  • 按数据分类: {'DAILY_KLINE': 6, 'REALTIME_QUOTE': 1, ...}
  • 按目标数据库: {'postgresql': 22, 'tdengine': 1}
  • 质量评分分布: {'high': 10, 'medium': 13, 'low': 0}
  • 优先级分布: {'low': 1, 'high': 5, 'medium': 17}

📋 数据接口明细表:
+---------------------------+-------------+-------------+--------------------+------------+----------+----------+--------+
| 端点名称                  | 数据源      | 类型        | 数据分类           | 目标库     |   质量分 |   优先级 | 状态   |
+===========================+=============+=============+====================+============+==========+==========+========+
| mock_daily_kline          | system_mock | mock        | DAILY_KLINE        | postgresql |      9   |      999 | active |
+---------------------------+-------------+-------------+--------------------+------------+----------+----------+--------+
...
```

### 详细报告包含
- 接口基本信息（数据源、类型、分类）
- 存储位置（数据库和表名）
- 质量指标（评分、优先级、状态）
- 参数信息（总数、必需参数数）
- 测试状态和标签
- 详细描述

## 数据接口总览

### 按数据源统计
- **AKShare**: 2个接口 (股票日线、基本信息)
- **TuShare**: 2个接口 (股票日线、财务数据)
- **BaoStock**: 5个接口 (日K线、分钟K线、基本信息、财务指标、杜邦分析)
- **WebData**: 12个接口 (新浪、腾讯的各种数据)
- **TDX**: 1个接口 (实时行情)
- **Mock**: 1个接口 (测试数据)

### 数据分类分布
- **DAILY_KLINE**: 6个 (日线数据)
- **MINUTE_KLINE**: 4个 (分钟线数据)
- **FINANCIAL_DATA**: 3个 (财务数据)
- **SYMBOLS_INFO**: 3个 (股票基本信息)
- **ADJUSTMENT_DATA**: 2个 (复权数据)
- **REALTIME_***: 5个 (实时数据)

### 质量评估
- **高品质** (9.0+): 10个接口 (43%)
- **中等品质** (7.0-8.9): 13个接口 (57%)
- **低品质** (<7.0): 0个接口

## 技术实现

### 依赖要求
- Python 3.8+
- PyYAML (用于YAML解析)
- tabulate (用于表格显示，可选)

### 文件结构
```
scripts/tools/data_interface_scanner.py  # 主程序
config/data_sources_registry.yaml        # 数据源配置
data_interfaces.json                     # JSON导出结果
```

### 核心类
- `DataInterfaceScanner`: 主要扫描类
  - `load_config()`: 加载YAML配置
  - `scan_interfaces()`: 扫描和分析接口
  - `generate_table_report()`: 生成表格报告
  - `export_data()`: 导出数据

## 维护建议

### 更新频率
- **每日**: 运行基本扫描，监控接口状态
- **每周**: 生成详细报告，检查质量变化
- **每月**: 导出完整数据，归档分析

### 监控要点
1. 新增接口及时更新配置
2. 质量评分定期复核
3. 优先级根据使用情况调整
4. 测试参数保持有效性

### 扩展功能
- 支持更多输出格式 (HTML, PDF)
- 添加接口健康检查
- 集成到CI/CD流程
- 生成API文档

## 故障排除

### 常见问题
1. **配置文件不存在**: 检查 `config/data_sources_registry.yaml` 文件
2. **导入错误**: 确保项目根目录在Python路径中
3. **表格显示异常**: 安装 `tabulate` 库或使用 `--output-format json`

### 错误信息
- "错误: 配置文件不存在": 检查配置文件路径
- "错误: 加载配置文件失败": 检查YAML语法
- "警告: 未安装 tabulate 库": 使用简单文本输出

## 相关文档

- [数据源管理工具使用指南](./docs/guides/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md)
- [数据源配置文档](./config/data_sources_registry.yaml)
- [项目架构文档](./docs/architecture/ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md)