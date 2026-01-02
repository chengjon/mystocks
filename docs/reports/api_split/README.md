# API数据清单 - 拆分文件说明

## 概述

原始的 `api_data_inventory.json` 文件太大（25689 tokens），已拆分成 143 个小文件，每个文件包含特定路径前缀的API端点。

## 文件结构

```
docs/reports/api_split/
├── API_SPLIT_INDEX.md          # 主索引文档（推荐从这里开始）
├── api_index.json              # JSON格式的索引文件
└── api_*.json                  # 143个按路径前缀拆分的文件
```

## 快速开始

### 方法1: 使用Markdown索引（推荐）

打开 `API_SPLIT_INDEX.md`，点击链接跳转到对应的JSON文件。

### 方法2: 使用命令行搜索

```bash
# 查找特定API
grep -r "/stocks/basic" docs/reports/api_split/

# 查看所有文件
ls -lh docs/reports/api_split/

# 查看索引
cat docs/reports/api_split/api_index.json
```

## 查找API的三种方式

### 1. 按路径前缀查找

如果你知道API路径的前缀（如 `/auth`, `/data`, `/dashboard`），直接打开对应的文件：

- `/auth` → `api_auth.json`
- `/data` → `api_data.json`
- `/stocks` → `api_stocks.json`

### 2. 按HTTP方法查找

使用 `jq` 或 `grep` 查找特定方法的API：

```bash
# 查找所有GET请求
grep -r '"method": "GET"' docs/reports/api_split/

# 查找所有POST请求
grep -r '"method": "POST"' docs/reports/api_split/
```

### 3. 按后端文件查找

查看 `API_SPLIT_INDEX.md` 中的"按API文件分组"部分，找到包含你需要的API的后端文件。

## 文件命名规则

拆分文件按API路径前缀命名：

| API路径前缀 | 文件名 |
|-------------|--------|
| `/auth` | `api_auth.json` |
| `/stocks/basic` | `api_stocks.json` (包含所有 `/stocks/*` 的API) |
| `/data` | `api_data.json` |
| `/dashboard` | `api_dashboard.json` |
| `/strategies` | `api_strategies.json` |

## 数据格式

每个拆分文件包含以下字段：

```json
{
  "generated_at": "2026-01-02T00:32:22.264253",
  "prefix": "/stocks",
  "total_endpoints": 10,
  "endpoints": [
    {
      "path": "/stocks/basic",
      "method": "GET",
      "file": "data.py",
      "function": "get_stocks_basic",
      "return_model": "dict",
      "data_fields": [],
      "db_dependencies": [],
      "source_type": "postgresql",
      "line_number": 33
    }
  ]
}
```

## 字段说明

- **path**: API路径
- **method**: HTTP方法（GET/POST/PUT/DELETE/PATCH）
- **file**: 后端文件名
- **function**: 函数名
- **return_model**: 返回数据类型
- **data_fields**: 返回的数据字段
- **db_dependencies**: 依赖的数据库表
- **source_type**: 数据源类型（postgresql/tdengine/mock）
- **line_number**: 代码行号

## 示例

### 查找认证相关API

```bash
# 打开认证API文件
cat docs/reports/api_split/api_auth.json

# 或搜索登录API
grep -A 5 '"/login"' docs/reports/api_split/api_auth.json
```

### 查找股票数据API

```bash
# 打开股票API文件
cat docs/reports/api_split/api_stocks.json

# 查找所有股票相关API
grep -r '"path": "/stocks' docs/reports/api_split/
```

### 统计API数量

```bash
# 统计每个文件的API数量
for f in docs/reports/api_split/api_*.json; do
  count=$(jq '.total_endpoints' "$f")
  echo "$(basename $f): $count"
done
```

## 重新拆分

如果需要重新拆分原始文件：

```bash
python scripts/split_api_inventory.py
```

## 原始文件

原始的大文件仍然保存在：
- `docs/reports/api_data_inventory.json`

## 注意事项

1. 所有拆分文件的生成时间与原始文件相同
2. 端点总数保持不变（356个）
3. 每个文件平均包含 2-3 个端点
4. 文件按路径前缀字母顺序排列

## 相关文档

- [API与Web前端数据使用分析报告](../API_WEB_DATA_USAGE_REPORT.md)
- [分析工具使用文档](../ANALYSIS_TOOL_README.md)
