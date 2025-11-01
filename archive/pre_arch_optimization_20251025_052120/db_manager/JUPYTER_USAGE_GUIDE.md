# Jupyter 环境使用指南

## 问题描述
在 Jupyter Notebook/IPython 环境中运行包含 argparse 的脚本时，会遇到参数解析冲突的问题：

```
ipykernel_launcher.py: error: unrecognized arguments: --f="..."
```

## 解决方案

### 方法1: 直接调用 API 函数（推荐）

```python
# 导入模块
from db_manager.init_db_monitor import init_monitoring_database

# 正常初始化（不删除已有表）
success = init_monitoring_database()

# 强制删除并重建表
success = init_monitoring_database(drop_existing=True)
```

### 方法2: 使用 exec 方式运行

```python
# 读取并执行脚本
exec(open('db_manager/init_db_monitor.py').read())
```

### 方法3: 使用 %run 魔法命令

```python
# 在 Jupyter 中使用 %run（无参数）
%run db_manager/init_db_monitor.py

# 注意：由于 argparse 冲突，不能直接传递参数
# %run db_manager/init_db_monitor.py --drop-existing  # 这会报错
```

## 最佳实践

### 在 Jupyter Notebook 中的完整示例

```python
# Cell 1: 导入和初始化
import os
import sys

# 确保在正确的工作目录
os.chdir('/path/to/your/project')

# 导入初始化函数
from db_manager.init_db_monitor import init_monitoring_database

# Cell 2: 执行初始化
print("🚀 开始初始化数据库监控系统...")

# 初始化监控数据库
success = init_monitoring_database(drop_existing=False)

if success:
    print("✅ 数据库监控系统初始化成功!")
else:
    print("❌ 初始化失败，请检查配置和网络连接")

# Cell 3: 验证结果
if success:
    print("🔍 验证创建的数据库结构...")
    print("数据库: db_monitor")
    print("表:")
    print("  • table_creation_log - 表创建日志表")
    print("  • column_definition_log - 列定义日志表") 
    print("  • table_operation_log - 表操作日志表")
    print("  • table_validation_log - 表结构验证日志表")
```

## 环境检测

脚本现在会自动检测运行环境：

- **Jupyter 环境**: 自动使用默认参数，避免 argparse 冲突
- **命令行环境**: 正常解析命令行参数

## 错误处理

如果仍然遇到问题，可以尝试：

1. **重启 Jupyter 内核**
2. **检查工作目录**
3. **验证环境变量文件路径**
4. **查看详细日志文件**: `logs/db_monitor_init_*.log`

## 日志文件

无论在何种环境下运行，都会生成详细的日志文件：

- 位置: `logs/db_monitor_init_YYYY-MM-DD.log`
- 编码: UTF-8
- 保留: 30天自动滚动
- 格式: 包含时间戳、函数名、行号等详细信息