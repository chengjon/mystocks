# 文件分析系统

一个强大的项目文件分析工具，支持Python、TypeScript、JavaScript、Vue、HTML、CSS和JSON文件的深度分析。

## 功能特性

### 核心功能
- ✅ **多语言支持**: Python、TypeScript、JavaScript、Vue、HTML、CSS、JSON
- ✅ **深度分析**: 提取函数、类、导入/导出、复杂度等信息
- ✅ **引用关系**: 自动分析文件间的引用和依赖关系
- ✅ **增量扫描**: 只扫描修改过的文件，提高效率
- ✅ **PostgreSQL存储**: 使用数据库存储分析结果，支持复杂查询
- ✅ **统计报告**: 生成详细的统计报告和分析报告

### 最新更新 (v1.1.0)
- 🐛 **Bug修复**: 修复引用分析中的Path连接错误
- 🎨 **CSS支持**: 新增CSS文件分析器
- 📄 **JSON支持**: 新增JSON文件分析器
- ⚡ **增量扫描**: 实现基于时间戳的增量扫描功能

详见 [NEW_FEATURES.md](NEW_FEATURES.md)

## 快速开始

### 1. 环境要求
- Python 3.8+
- PostgreSQL 12+
- 必要的Python包（见requirements.txt）

### 2. 安装依赖
```bash
cd /opt/claude/mystocks_spec/scripts/file_analysis
pip install -r requirements.txt
```

### 3. 配置数据库
```bash
export POSTGRES_HOST=192.168.123.104
export POSTGRES_PORT=5438
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export ANALYSIS_DB=file_analysis_db
```

### 4. 初始化数据库
```bash
python3 init_database.py
```

### 5. 运行分析
```bash
# 全量扫描
python3 main.py

# 增量扫描
python3 main.py --incremental

# 指定时间的增量扫描
python3 main.py --incremental --since "2026-01-01 00:00:00"
```

### 6. 查询结果
```bash
# 查看统计信息
python3 query_tool.py --stats

# 查询特定类型文件
python3 query_tool.py --type python --limit 10

# 查看引用关系
python3 query_tool.py --references --limit 20

# 查看最近分析的文件
python3 query_tool.py --latest --limit 10
```

## 项目结构

```
file_analysis/
├── main.py                      # 主程序
├── init_database.py             # 数据库初始化
├── query_tool.py                # 查询工具
├── python_analyzer.py           # Python分析器
├── typescript_analyzer.py       # TypeScript/JavaScript分析器
├── html_analyzer.py             # HTML/Vue分析器
├── css_analyzer.py              # CSS分析器 (新增)
├── json_analyzer.py             # JSON分析器 (新增)
├── reference_analyzer.py        # 引用关系分析器
├── schema.sql                   # 数据库表结构
├── migration_add_css_json.sql   # 数据库迁移脚本 (新增)
├── test_new_features.sh         # 新功能测试脚本 (新增)
├── NEW_FEATURES.md              # 新功能说明文档 (新增)
└── README.md                    # 本文档
```

## 数据库表结构

### 1. analysis_runs - 分析运行记录
存储每次扫描的运行信息，包括开始时间、结束时间、状态、文件统计等。

### 2. file_categories - 文件分类
定义文件的分类体系，如Python后端、TypeScript前端、配置文件等。

### 3. file_metadata - 文件元数据
存储每个文件的详细信息，包括：
- 文件基本信息（名称、路径、大小、行数）
- 代码结构（函数数、类数、导入/导出数）
- 复杂度和质量评分
- 引用统计（被引用次数、引用次数）
- 分类和功能描述

### 4. file_references - 文件引用关系
存储文件间的引用关系，包括：
- 源文件和目标文件
- 引用类型（import、require、export等）
- 引用位置和代码
- 引用有效性验证

## 使用指南

### 命令行参数

#### main.py - 文件分析
```bash
python3 main.py [project_root] [options]

参数:
  project_root          项目根目录路径 (默认: /opt/claude/mystocks_spec)

选项:
  --incremental         启用增量扫描
  --since SINCE         增量扫描的起始时间 (格式: YYYY-MM-DD HH:MM:SS)
```

#### query_tool.py - 查询工具
```bash
python3 query_tool.py [options]

选项:
  --name NAME          按文件名查询
  --path PATH          按文件路径查询
  --type TYPE          按文件类型查询
  --category CATEGORY  按分类查询
  --stats              显示统计信息
  --references         显示引用关系
  --latest             显示最近分析的文件
  --most-referenced    显示被引用最多的文件
  --limit LIMIT        限制结果数量
  --output FORMAT      输出格式 (json/text)
```

### 文件类型

支持以下文件类型：
- **Python** (.py) - Python源代码文件
- **TypeScript** (.ts, .tsx) - TypeScript源代码文件
- **JavaScript** (.js, .jsx, .mjs) - JavaScript源代码文件
- **Vue** (.vue) - Vue单文件组件
- **HTML** (.html, .htm) - HTML页面文件
- **CSS** (.css) - CSS样式文件
- **JSON** (.json) - JSON配置和数据文件

### 增量扫描

增量扫描只分析修改过的文件，大幅提高效率。

**自动增量扫描**：
```bash
python3 main.py --incremental
```
自动从数据库获取上次扫描时间。

**指定时间增量扫描**：
```bash
python3 main.py --incremental --since "2026-01-01 00:00:00"
```
从指定时间开始扫描。

**全量扫描**：
```bash
python3 main.py
```
扫描所有文件。

## 分析器详解

### Python分析器
- 使用AST解析Python代码
- 提取函数、类、导入/导出
- 计算复杂度评分
- 识别测试文件和入口文件

### TypeScript/JavaScript分析器
- 支持TypeScript和JavaScript语法
- 解析import/export语句
- 识别类和函数定义
- 支持JSX语法

### HTML/Vue分析器
- 解析HTML结构
- 提取组件信息
- 分析脚本和样式
- 支持Vue单文件组件

### CSS分析器 (新增)
- 提取选择器和属性
- 检测媒体查询和动画
- 识别URL引用
- 计算复杂度评分

### JSON分析器 (新增)
- 解析JSON结构
- 提取所有键
- 计算嵌套深度
- 识别配置文件和数据文件

### 引用关系分析器
- 解析import/require语句
- 解析相对和绝对路径
- 验证引用有效性
- 构建引用关系图

## 输出报告

### 统计报告
每次分析完成后，系统会生成统计报告，包括：
- 总文件数和各类文件数
- 总行数和函数/类数量
- 平均复杂度和质量评分
- 引用关系统计

### 分析报告
生成Markdown格式的详细分析报告，包含：
- 分析概览
- 统计信息
- 文件列表
- 引用关系
- 问题清单

## 测试

### 运行测试脚本
```bash
./test_new_features.sh
```

测试脚本会自动：
1. 运行数据库迁移
2. 测试全量扫描
3. 测试增量扫描
4. 验证所有新功能

### 手动测试
```bash
# 测试引用分析
python3 main.py
python3 query_tool.py --references

# 测试CSS和JSON支持
python3 main.py
python3 query_tool.py --type css
python3 query_tool.py --type json

# 测试增量扫描
python3 main.py --incremental
```

## 故障排查

### 数据库连接失败
```bash
export POSTGRES_HOST=192.168.123.104
export POSTGRES_PORT=5438
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

### 增量扫描没有找到文件
```bash
# 使用更早的时间
python3 main.py --incremental --since "2025-01-01 00:00:00"
```

### 数据库表缺少列
```bash
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $ANALYSIS_DB \
  -f migration_add_css_json.sql
```

## 性能优化

### 增量扫描
- 只扫描修改过的文件
- 大幅减少扫描时间
- 适合日常开发使用

### 数据库索引
- 为常用查询字段创建索引
- 提高查询性能
- 支持大规模项目

### 批量处理
- 批量插入数据
- 减少数据库往返
- 提高写入性能

## 最佳实践

### 日常使用
1. 使用增量扫描进行日常分析
2. 定期运行全量扫描以更新所有文件
3. 使用查询工具快速查找信息

### CI/CD集成
1. 在每次提交后运行增量扫描
2. 检测新增和修改的文件
3. 验证引用关系完整性

### 项目维护
1. 定期查看统计信息
2. 识别高复杂度文件
3. 优化引用关系

## 更新日志

### v1.1.0 (2026-01-19)
- 🐛 修复引用分析Bug
- 🎨 添加CSS文件支持
- 📄 添加JSON文件支持
- ⚡ 实现增量扫描功能
- 📝 完善文档和测试

### v1.0.0 (2026-01-18)
- 🎉 初始版本发布
- ✅ 支持Python、TypeScript、JavaScript、Vue、HTML
- ✅ 实现引用关系分析
- ✅ 支持PostgreSQL存储

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License

## 联系方式

如有问题，请查看 [NEW_FEATURES.md](NEW_FEATURES.md) 或查看日志文件 `file_analysis.log`。

---

**版本**: v1.1.0
**更新时间**: 2026-01-19
**作者**: iFlow CLI