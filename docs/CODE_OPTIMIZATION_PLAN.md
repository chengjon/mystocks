# MyStocks代码优化方案

## 项目现状分析

根据对项目代码库的分析，我们发现了以下情况：

- **文件数量**: 整个项目包含**1862个Python文件**
- **最大文件**: `temp/freqtrade/tests/exchange/test_exchange.py` 达**6357行**，远超合理范围
- **目录结构**: 存在大量临时目录（temp）、归档目录（archive）和未使用的目录（unused_modules）
- **需要处理的文件**: 除了已拆分的`nicegui_monitoring_dashboard_kline.py`（1463行），还有其他一些需要处理的大文件

## 1. Python文件精简方案

### 1.1 目录清理（优先执行）

1. **清理临时和归档文件**:
   - 删除或移动`temp`、`archive`、`unused_modules`目录中的内容
   - 删除`.mypy_cache`、`.pytest_cache`等自动生成的缓存目录
   - 清理`.archive`目录下的废弃代码

2. **示例命令**:
   ```bash
   # 备份归档目录到外部存储
   mv /opt/claude/mystocks_spec/.archive /external-storage/mystocks-archive-$(date +%Y%m%d)
   # 清理临时目录
   rm -rf /opt/claude/mystocks_spec/temp
   # 清理缓存目录
   find /opt/claude/mystocks_spec -type d -name "__pycache__" -exec rm -rf {} +
   find /opt/claude/mystocks_spec -type d -name ".pytest_cache" -exec rm -rf {} +
   ```

### 1.2 大文件拆分（接下来执行）

根据项目中的大文件情况，建议优先拆分以下文件：

1. **temp/freqtrade/tests/exchange/test_exchange.py (6357行)**
   - 建议拆分为:
     - test_exchange_core.py (核心测试)
     - test_exchange_pairs.py (货币对测试)
     - test_exchange_orders.py (订单测试)
     - test_exchange_api.py (API测试)

2. **temp/freqtrade/tests/freqtradebot/test_freqtradebot.py (5916行)**
   - 建议拆分为:
     - test_freqtradebot_core.py (核心机器人测试)
     - test_freqtradebot_strategies.py (策略测试)
     - test_freqtradebot_rpc.py (RPC测试)

3. **temp/freqtrade/freqtrade/exchange/exchange.py (3953行)**
   - 建议拆分为:
     - exchange_core.py (交易所核心类)
     - exchange_api.py (交易所API接口)
     - exchange_pairs.py (交易对处理)
     - exchange_websocket.py (WebSocket连接)

4. **web/frontend/nicegui_monitoring_dashboard_kline.py (已拆分)**
   - 已成功拆分为模块化结构，如之前报告所述

### 1.3 小文件合并（然后执行）

需要合并的示例文件包括：
- 如果存在多个小型的工具函数文件（如多个data_utils.py, str_utils.py等）
- 测试文件中的重复代码段

### 1.4 模块归一化

1. **合并功能重叠的模块**:
   - data_fetch 和 data_collect 应合并为 data_collection
   - 相同名称但不同位置的模块需要统一

2. **优化目录结构**:
   - 减少目录层级过深的问题
   - 扁平化过深的目录结构

## 2. CI/CD流程添加文件大小/数量检查方案

### 2.1 编写检查脚本

1. **check_file_lines.py**:
   ```python
   #!/usr/bin/env python3
   import os
   import sys
   import re
   
   # 配置文件大小阈值
   MAX_FILE_LINES = 2000
   MIN_FILE_LINES = 50
   
   def check_files(directory):
       """检查目录中的Python文件行数"""
       large_files = []
       small_files = []
       
       for root, _, files in os.walk(directory):
           # 忽略特定目录
           if any(ignore_dir in root for ignore_dir in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
               continue
           
           for file in files:
               if file.endswith('.py'):
                   file_path = os.path.join(root, file)
                   try:
                       with open(file_path, 'r', encoding='utf-8') as f:
                           lines = sum(1 for _ in f)
                           
                       if lines > MAX_FILE_LINES:
                           large_files.append(f"{file_path}: {lines} lines")
                       elif lines < MIN_FILE_LINES:
                           small_files.append(f"{file_path}: {lines} lines")
                   except Exception as e:
                       print(f"Error reading {file_path}: {e}")
       
       return large_files, small_files
   
   if __name__ == "__main__":
       directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
       large_files, small_files = check_files(directory)
       
       if large_files:
           print("❌ 以下文件超过行数限制:")
           for file in large_files:
               print(f"  {file}")
           sys.exit(1)
       
       if small_files:
           print("⚠️ 以下文件少于最小行数限制:")
           for file in small_files:
               print(f"  {file}")
           # 小文件不影响检查结果，只给出警告
       
       print("✅ 所有文件行数检查通过")
   ```

2. **check_file_count.py**:
   ```python
   #!/usr/bin/env python3
   import os
   import sys
   import json
   from datetime import datetime
   
   # 配置文件数量阈值
   MAX_NEW_FILES = 10
   
   # 记录每次提交的文件数量基线
   BASELINE_FILE = "file_count_baseline.json"
   
   def count_python_files(directory):
       """统计目录中的Python文件数量"""
       count = 0
       for root, _, files in os.walk(directory):
           # 忽略特定目录
           if any(ignore_dir in root for ignore_dir in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.mypy_cache']):
               continue
           
           for file in files:
               if file.endswith('.py'):
                   count += 1
       return count
   
   def update_baseline(count):
       """更新基线文件"""
       baseline = {}
       if os.path.exists(BASELINE_FILE):
           with open(BASELINE_FILE, 'r') as f:
               baseline = json.load(f)
       
       baseline['last_count'] = count
       baseline['last_update'] = str(datetime.now())
       
       with open(BASELINE_FILE, 'w') as f:
           json.dump(baseline, f)
   
   def get_baseline():
       """获取基线数量"""
       if not os.path.exists(BASELINE_FILE):
           return None
       
       with open(BASELINE_FILE, 'r') as f:
           baseline = json.load(f)
           return baseline.get('last_count')
   
   if __name__ == "__main__":
       directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
       current_count = count_python_files(directory)
       baseline_count = get_baseline()
       
       if baseline_count is None:
           print(f"📝 首次运行，保存当前文件数量为基线: {current_count}")
           update_baseline(current_count)
           sys.exit(0)
       
       new_files = current_count - baseline_count
       if new_files > MAX_NEW_FILES:
           print(f"❌ 新增文件数量({new_files})超过限制({MAX_NEW_FILES})")
           print(f"当前文件总数: {current_count}")
           print(f"基线文件总数: {baseline_count}")
           sys.exit(1)
       
       if new_files > 0:
           print(f"ℹ️ 本次提交新增 {new_files} 个Python文件")
           print(f"当前文件总数: {current_count}")
           print(f"基线文件总数: {baseline_count}")
           update_baseline(current_count)
       else:
           print(f"✅ Python文件数量检查通过: {current_count}")
   
   ```

### 2.2 CI/CD流水线集成

1. **GitLab CI/CD示例配置**:
   ```yaml
   # .gitlab-ci.yml
   stages:
     - lint
     - test
     - build
     - deploy
   
   # 文件检查阶段
   file_check:
     stage: lint
     script:
       - echo "检查文件大小和数量..."
       - python scripts/check_file_lines.py .
       - python scripts/check_file_count.py .
     only:
       - merge_requests
       - master
     except:
       - triggers
   ```

2. **GitHub Actions示例配置**:
   ```yaml
   # .github/workflows/code-quality.yml
   name: Code Quality Checks
   
   on: [push, pull_request]
   
   jobs:
     file-check:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Run file checks
           run: |
             python scripts/check_file_lines.py .
             python scripts/check_file_count.py .
   ```

### 2.3 告警与通知

1. **自定义通知脚本**:
   ```python
   # notify_check_failures.py
   def notify_check_failures(check_type, failures):
       # 发送到企业微信/钉钉/邮件等通知
       # 仅在检查失败时触发
       pass
   ```

## 3. 开发规范建议

### 3.1 文件创建规范

1. **最小必要原则**:
   - 新增文件前先检查现有模块是否可容纳该功能
   - 禁止为单一函数创建独立文件

2. **命名与目录规范**:
   - 文件名采用"功能描述+类型"（如data_validator.py）
   - 目录层级不超过4层

### 3.2 文件大小限制要求

1. **硬性阈值**:
   - 单个.py文件行数≤2000
   - 单个文件行数＜50时需说明独立存在的合理性

2. **拆分/合并触发条件**:
   - 当文件行数接近1800行时需主动拆分
   - 同一模块下小文件超过3个且功能关联需合并

### 3.3 代码审查要求

在Code Review中应检查：
- 新增文件是否必要
- 修改后的文件行数是否超标
- 是否删除了无用代码/文件

### 3.4 定期维护要求

1. **月度文件审计**:
   - 每月最后一周进行文件数量和超大文件清单清理

2. **新人培训**:
   - 将文件规范纳入新人培训内容

## 4. 实施计划

1. **第一阶段（立即执行）**:
   - 清理临时和归档文件
   - 拆分最大的几个测试文件

2. **第二阶段（1周内）**:
   - 实施CI/CD检查脚本
   - 开始小文件合并工作

3. **第三阶段（2周内）**:
   - 完成所有大文件拆分
   - 建立定期审查机制

4. **第四阶段（1个月内）**:
   - 完成模块归一化
   - 评估优化效果并调整规范

## 5. 预期效果

1. **短期效果**:
   - 文件数量减少约20-30%
   - 平均文件行数降低约30%
   - 提高代码可读性和维护性

2. **长期效果**:
   - 建立持续的文件质量检查机制
   - 规范团队开发流程
   - 提高开发效率和代码质量

---

此方案综合考虑了当前项目实际情况和您的建议，通过分阶段实施，可以在不影响当前开发进度的情况下，显著提高代码质量。