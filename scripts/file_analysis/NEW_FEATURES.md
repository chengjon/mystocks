# 文件分析系统 - 新功能说明

## 概述

本次更新为文件分析系统添加了三个重要功能：
1. **修复引用分析Bug** - 修复了Path对象与字符串连接的错误
2. **添加CSS和JSON文件支持** - 扩展了文件类型覆盖范围
3. **实现增量扫描功能** - 提高了扫描效率

---

## 功能 1: 修复引用分析Bug

### 问题描述
在`reference_analyzer.py`中，存在一个类型错误：
```python
# 错误代码
target_path = root_dir / module.replace('.', '/') + '.py'
```

错误信息：
```
unsupported operand type(s) for +: 'PosixPath' and 'str'
```

### 修复方案
将Path对象的连接方式从使用`+`运算符改为使用`with_suffix()`方法和正确的字符串拼接：

```python
# 修复后的代码
target_path = root_dir / (module.replace('.', '/') + '.py')
# 或者
target_path = target_path.with_suffix(ext)
```

### 修复位置
- 文件：`scripts/file_analysis/reference_analyzer.py`
- 方法：
  - `_resolve_python_reference()`
  - `_resolve_ts_js_reference()`

### 验证方法
运行测试脚本验证引用分析是否正常工作：
```bash
python3 scripts/file_analysis/query_tool.py --references --limit 10
```

---

## 功能 2: 添加CSS和JSON文件支持

### 新增分析器

#### CSS分析器 (`css_analyzer.py`)
分析CSS文件，提取以下信息：
- 选择器列表
- CSS属性
- 媒体查询
- 关键帧动画
- URL引用
- @import规则
- 复杂度评分

支持的特性检测：
- Flexbox布局
- CSS Grid布局
- 动画和过渡
- CSS变量
- 响应式设计

#### JSON分析器 (`json_analyzer.py`)
分析JSON文件，提取以下信息：
- 所有键（递归）
- 嵌套深度
- 数组数量
- 对象数量
- 文件类型判断（配置文件或数据文件）
- 文件引用（在字符串值中）

### 数据库更新
为`analysis_runs`表添加了两个新列：
- `css_files INTEGER` - CSS文件数量
- `json_files INTEGER` - JSON文件数量

迁移脚本：`migration_add_css_json.sql`

### 文件分类
CSS和JSON文件被归类到'config'分类：
```python
category_map = {
    'css': 'config',
    'json': 'config'
}
```

### 使用示例
```bash
# 查询CSS文件
python3 scripts/file_analysis/query_tool.py --type css --limit 10

# 查询JSON文件
python3 scripts/file_analysis/query_tool.py --type json --limit 10
```

---

## 功能 3: 增量扫描功能

### 功能描述
增量扫描功能允许只扫描在上次扫描之后修改过的文件，大幅提高扫描效率。

### 使用方法

#### 1. 自动增量扫描（基于上次扫描时间）
```bash
# 自动从数据库获取上次扫描时间
python3 scripts/file_analysis/main.py --incremental
```

#### 2. 指定起始时间的增量扫描
```bash
# 从指定时间开始扫描
python3 scripts/file_analysis/main.py --incremental --since "2026-01-01 00:00:00"
```

#### 3. 全量扫描
```bash
# 扫描所有文件（默认行为）
python3 scripts/file_analysis/main.py
```

### 工作原理

1. **自动模式**：
   - 从数据库查询最后一次成功完成扫描的时间
   - 只扫描修改时间晚于该时间的文件
   - 如果没有历史记录，自动降级为全量扫描

2. **指定时间模式**：
   - 使用用户提供的起始时间
   - 只扫描修改时间晚于该时间的文件

3. **文件过滤**：
   - 检查每个文件的修改时间戳
   - 只处理修改时间晚于基准时间的文件
   - 排除无法获取修改时间的文件

### 性能优势
- **全量扫描**：扫描所有文件（可能数千个）
- **增量扫描**：只扫描修改过的文件（通常只有几十个）

典型场景：
- 日常开发：只扫描当天修改的文件
- CI/CD：只扫描提交的文件
- 定期维护：只扫描最近一周的文件

### 实现细节

#### 新增方法
```python
def scan_files_incremental(self, last_scan_time: datetime) -> List[str]:
    """增量扫描文件（只扫描修改过的文件）"""
    # 扫描所有文件
    # 检查每个文件的修改时间
    # 只返回修改时间晚于last_scan_time的文件
```

#### 修改的方法
- `run(incremental=False, since=None)` - 主运行方法
- `main()` - 命令行参数解析

---

## 测试

### 运行完整测试
```bash
cd /opt/claude/mystocks_spec
./scripts/file_analysis/test_new_features.sh
```

### 测试脚本功能
测试脚本`test_new_features.sh`包含以下步骤：
1. 运行数据库迁移
2. 测试全量扫描（包含CSS和JSON）
3. 查询统计信息
4. 测试自动增量扫描
5. 测试指定时间增量扫描
6. 查询CSS和JSON文件
7. 验证引用分析

### 手动测试

#### 测试引用分析修复
```bash
# 运行全量扫描
python3 scripts/file_analysis/main.py

# 查询引用关系（应该无错误）
python3 scripts/file_analysis/query_tool.py --references
```

#### 测试CSS和JSON支持
```bash
# 运行扫描
python3 scripts/file_analysis/main.py

# 查询CSS文件
python3 scripts/file_analysis/query_tool.py --type css

# 查询JSON文件
python3 scripts/file_analysis/query_tool.py --type json

# 查看统计
python3 scripts/file_analysis/query_tool.py --stats
```

#### 测试增量扫描
```bash
# 第一次全量扫描
python3 scripts/file_analysis/main.py

# 修改一个文件
echo "print('test')" >> test.py

# 增量扫描（应该只扫描修改的文件）
python3 scripts/file_analysis/main.py --incremental

# 指定时间增量扫描
python3 scripts/file_analysis/main.py --incremental --since "2026-01-01 00:00:00"
```

---

## 配置

### 环境变量
```bash
export POSTGRES_HOST=192.168.123.104
export POSTGRES_PORT=5438
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export ANALYSIS_DB=file_analysis_db
```

### 数据库初始化
```bash
# 初始化数据库
python3 scripts/file_analysis/init_database.py

# 运行迁移（添加CSS和JSON列）
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $ANALYSIS_DB \
  -f scripts/file_analysis/migration_add_css_json.sql
```

---

## 命令行参数

### main.py参数
```bash
usage: main.py [-h] [--incremental] [--since SINCE] [project_root]

文件分析系统

positional arguments:
  project_root          项目根目录路径 (默认: /opt/claude/mystocks_spec)

optional arguments:
  -h, --help           显示帮助信息
  --incremental        启用增量扫描（只扫描修改过的文件）
  --since SINCE        增量扫描的起始时间（格式：YYYY-MM-DD HH:MM:SS）
```

### query_tool.py参数
```bash
usage: query_tool.py [-h] [--name NAME] [--path PATH] [--type TYPE]
                     [--category CATEGORY] [--stats] [--references]
                     [--latest] [--most-referenced] [--limit LIMIT]
                     [--output {json,text}]

文件查询工具

optional arguments:
  -h, --help           显示帮助信息
  --name NAME          按文件名查询
  --path PATH          按文件路径查询
  --type TYPE          按文件类型查询 (python, typescript, javascript, vue, html, css, json)
  --category CATEGORY  按分类查询
  --stats              显示统计信息
  --references         显示引用关系
  --latest             显示最近分析的文件
  --most-referenced    显示被引用最多的文件
  --limit LIMIT        限制结果数量
  --output {json,text} 输出格式
```

---

## 输出示例

### 统计信息输出
```
=====================================
文件统计信息
=====================================

分析运行记录:
  运行ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  开始时间: 2026-01-19 10:30:00
  结束时间: 2026-01-19 10:35:00
  状态: completed
  总文件数: 150

文件类型统计:
  Python文件: 80
  TypeScript文件: 30
  JavaScript文件: 20
  Vue文件: 10
  HTML文件: 5
  CSS文件: 3
  JSON文件: 2

引用关系统计:
  总引用数: 250
  有效引用: 245
  无效引用: 5
```

### 增量扫描输出
```
======================================
文件分析系统开始运行
模式: 增量扫描
======================================
开始连接数据库
数据库连接成功
创建分析运行记录: d4e5f6a7-b8c9-0123-4567-89abcdef0123
使用上次扫描时间: 2026-01-19 10:30:00
开始增量扫描项目文件: /opt/claude/mystocks_spec
只扫描修改时间晚于 2026-01-19 10:30:00 的文件
增量扫描完成，共找到 15 个修改过的文件
开始分析 15 个文件
进度: 15/15
文件分析完成，成功分析 15 个文件
```

---

## 故障排查

### 问题1: 数据库连接失败
**错误**: `Connection refused`

**解决方案**:
```bash
export POSTGRES_HOST=192.168.123.104
export POSTGRES_PORT=5438
```

### 问题2: 增量扫描没有找到文件
**原因**: 所有文件的修改时间都早于基准时间

**解决方案**:
```bash
# 使用更早的时间
python3 scripts/file_analysis/main.py --incremental --since "2025-01-01 00:00:00"

# 或者执行全量扫描
python3 scripts/file_analysis/main.py
```

### 问题3: CSS或JSON文件没有被统计
**原因**: 数据库表缺少新列

**解决方案**:
```bash
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $ANALYSIS_DB \
  -f scripts/file_analysis/migration_add_css_json.sql
```

### 问题4: 引用分析仍然报错
**原因**: 缓存或旧代码

**解决方案**:
```bash
# 清理Python缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 重新运行扫描
python3 scripts/file_analysis/main.py
```

---

## 总结

本次更新为文件分析系统带来了以下改进：

1. **稳定性提升**: 修复了引用分析的Path连接错误
2. **覆盖范围扩大**: 支持CSS和JSON文件分析
3. **性能优化**: 实现增量扫描，大幅提高扫描效率

所有功能都已经过测试，可以直接使用。如有问题，请参考故障排查部分或查看日志文件`file_analysis.log`。

---

**更新时间**: 2026-01-19
**版本**: v1.1.0
**作者**: iFlow CLI