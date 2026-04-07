# API数据清单 - 快速入门

> **参考指南说明**:
> 本文件用于提供某一局部主题的使用方法、操作步骤、背景说明或参考材料，帮助理解仓库中的具体实践。
> 其中的命令、路径、流程和示例应与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果一并核对，不应单独视为共享规则或当前状态的唯一事实来源。


## 🎯 一分钟快速开始

### 1. 查看统计信息
```bash
python scripts/api_query.py --summary
```

### 2. 查找特定API
```bash
# 按路径查找
python scripts/api_query.py --path /stocks

# 按方法查找
python scripts/api_query.py --method GET

# 按文件查找
python scripts/api_query.py --file data.py

# 按函数查找
python scripts/api_query.py --function login
```

### 3. 打开索引文档
在浏览器或编辑器中打开：`docs/reports/api_split/API_SPLIT_INDEX.md`

## 📚 文件导航

```
docs/reports/
├── api_data_inventory.json           # 原始大文件 (101KB)
└── api_split/                        # 拆分目录 (推荐使用)
    ├── API_SPLIT_INDEX.md            # 📖 主索引 (从这里开始)
    ├── api_index.json                # 索引文件
    ├── README.md                     # 详细说明
    ├── SPLIT_COMPLETION_REPORT.md    # 完成报告
    └── api_*.json                   # 143个拆分文件
```

## 🔍 三种查找方式

### 方式1: 使用查询工具（推荐）
```bash
python scripts/api_query.py --help
```

### 方式2: 使用Markdown索引
打开 `API_SPLIT_INDEX.md`，点击链接跳转

### 方式3: 直接搜索文件
```bash
grep -r "/login" docs/reports/api_split/
```

## 📊 快速统计

- **总API端点**: 356个
- **拆分文件**: 143个
- **GET请求**: 223个 (62.6%)
- **POST请求**: 115个 (32.3%)
- **数据源**: PostgreSQL (99.7%)

## 💡 常用查询

### 查找认证相关API
```bash
python scripts/api_query.py --path /auth
```

### 查找股票数据API
```bash
python scripts/api_query.py --path /stocks
```

### 查找所有GET请求
```bash
python scripts/api_query.py --method GET
```

### 查找特定文件的API
```bash
python scripts/api_query.py --file data.py
```

### 查看详细列表
```bash
python scripts/api_query.py --list
```

## 📖 更多信息

- [详细使用说明](docs/reports/api_split/README.md)
- [拆分完成报告](docs/reports/api_split/SPLIT_COMPLETION_REPORT.md)
- [API分析报告](docs/reports/API_WEB_DATA_USAGE_REPORT.md)
- [分析工具文档](docs/reports/ANALYSIS_TOOL_README.md)

## 🔧 工具脚本

### 重新拆分文件
```bash
python scripts/split_api_inventory.py
```

### 查询API
```bash
python scripts/api_query.py [选项]
```

### 运行完整分析
```bash
python scripts/analyze_api_data_usage.py
```

## ✅ 问题排查

### Q: 找不到API？
A: 尝试使用更通用的关键词，或查看所有列表：
```bash
python scripts/api_query.py --list
```

### Q: 文件太大无法读取？
A: 使用拆分文件，所有文件都在token限制内：
```bash
cat docs/reports/api_split/api_stocks.json
```

### Q: 想重新拆分？
A: 清理并重新运行：
```bash
rm -rf docs/reports/api_split
python scripts/split_api_inventory.py
```

---

**提示**: 从 `API_SPLIT_INDEX.md` 开始是最好的方式！
