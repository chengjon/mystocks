#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拆分nicegui_monitoring_dashboard_kline.py文件 - 修复版

根据《代码文件长度优化规范》拆分大文件为模块化结构。

使用方法:
    python split_kline_dashboard_fixed.py

作者: MyStocks开发团队
日期: 2025-11-25
版本: 修复版
"""

import os
import sys
import shutil
from datetime import datetime

# 添加源码路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 源文件路径
SOURCE_FILE = "/opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard_kline.py"
TARGET_DIR = "/opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard"
COMPONENTS_DIR = os.path.join(TARGET_DIR, "components")


def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (IOError, UnicodeDecodeError):
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except (IOError, UnicodeDecodeError):
            return None


def write_file(file_path, content):
    """写入文件内容"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"写入文件失败: {file_path}, 错误: {e}")
        return False


def extract_class_methods(code, class_name):
    """提取特定类的所有方法"""
    import re

    # 查找类定义
    class_pattern = rf"^class\s+{class_name}\s*\("
    class_start = None

    for i, line in enumerate(code.split('\n')):
        if re.match(class_pattern, line):
            class_start = i
            break

    if class_start is None:
        # 尝试使用更宽松的匹配模式
        class_pattern = rf"^class\s+{class_name}\s*[:\(]"
        for i, line in enumerate(code.split('\n')):
            if re.match(class_pattern, line):
                class_start = i
                break

        if class_start is None:
            print(f"警告: 未找到类 {class_name} 的定义")
            return None

    # 查找类结束位置
    # 使用缩进级别判断类结束位置
    lines = code.split('\n')
    class_content = []
    class_indent = None
    class_end = None

    for i in range(class_start, len(lines)):
        line = lines[i]

        # 如果是第一个非空行，记录缩进级别
        if class_indent is None and line.strip():
            class_indent = len(line) - len(line.lstrip())

        # 跳过类定义行
        if i == class_start:
            class_content.append(line)
            continue

        # 如果遇到缩进级别小于等于类缩进级别的非空行，则认为类结束
        if line.strip() and (len(line) - len(line.lstrip())) <= class_indent:
            class_end = i
            break

        class_content.append(line)

    if class_end is None:
        class_content = lines[class_start:]

    # 确保返回正确的类内容
    return '\n'.join(class_content)


def extract_functions_by_pattern(code, pattern):
    """提取符合特定模式的函数"""
    import re

    # 将模式转换为正则表达式模式
    # 例如 "kline|Kline|KLINE" 转换为 "kline.*|Kline.*|KLINE.*"
    regex_pattern = "|".join([f"{p}.*" for p in pattern.split("|")])

    lines = code.split('\n')
    functions = []
    current_function = []
    in_function = False
    function_indent = None
    function_start = None

    for i, line in enumerate(lines):
        # 检查是否是函数定义行 - 使用更宽松的匹配模式
        function_match = re.match(rf"^\s*def\s+(?:{regex_pattern})\s*\(", line)

        if function_match:
            # 保存之前的函数
            if in_function and current_function:
                function_name_match = re.search(r'def\s+([A-Za-z_]\w*)', current_function[0])
                if function_name_match:
                    functions.append({
                        'name': function_name_match.group(1),
                        'content': '\n'.join(current_function),
                        'line_number': function_start
                    })

            # 开始新函数
            in_function = True
            function_start = i
            function_indent = len(line) - len(line.lstrip())
            current_function = [line]
            continue

        # 如果在函数内部，添加当前行
        if in_function:
            # 如果遇到缩进级别小于等于函数缩进级别的非空行，则认为函数结束
            if line.strip() and (len(line) - len(line.lstrip())) <= function_indent:
                in_function = False
                # 保存函数
                if current_function:
                    function_name_match = re.search(r'def\s+([A-Za-z_]\w*)', current_function[0])
                    if function_name_match:
                        functions.append({
                            'name': function_name_match.group(1),
                            'content': '\n'.join(current_function),
                            'line_number': function_start
                        })
                current_function = []
                # 不添加当前行，继续处理下一行
            else:
                current_function.append(line)

    # 保存最后一个函数
    if in_function and current_function:
        function_name_match = re.search(r'def\s+([A-Za-z_]\w*)', current_function[0])
        if function_name_match:
            functions.append({
                'name': function_name_match.group(1),
                'content': '\n'.join(current_function),
                'line_number': function_start
            })

    # 输出匹配到的函数数量
    print(f"匹配模式 '{pattern}' 找到 {len(functions)} 个函数")

    return functions


def split_file():
    """拆分文件"""
    # 读取源代码
    source_code = read_file(SOURCE_FILE)
    if not source_code:
        print(f"错误: 无法读取源文件: {SOURCE_FILE}")
        return False

    # 创建目标目录
    os.makedirs(TARGET_DIR, exist_ok=True)
    os.makedirs(COMPONENTS_DIR, exist_ok=True)

    print(f"开始拆分文件: {SOURCE_FILE}")

    # 提取核心类和功能
    print("提取类: EnhancedKlineMonitoringDashboard")
    enhanced_kline_dashboard_class = extract_class_methods(source_code, "EnhancedKlineMonitoringDashboard")

    if not enhanced_kline_dashboard_class:
        print("错误: 无法提取核心类")
        return False

    print(f"类提取成功，长度: {len(enhanced_kline_dashboard_class)} 字符")

    # 提取各种功能的函数
    print("提取函数...")
    kline_functions = extract_functions_by_pattern(source_code, "kline|Kline|KLINE")
    chart_functions = extract_functions_by_pattern(source_code, "chart|Chart|Chart")
    alert_functions = extract_functions_by_pattern(source_code, "alert|Alert|Alert")
    control_functions = extract_functions_by_pattern(source_code, "control|Control|Control")
    action_functions = extract_functions_by_pattern(source_code, "action|Action|Action")
    utility_functions = extract_functions_by_pattern(source_code, "util|Helper|_.*")

    # 创建组件文件
    components = {}

    # K线图表组件
    kline_content = """# K线图表相关功能

\"\"\"
K线图表相关功能
\"\"\"

"""
    for func in kline_functions:
        kline_content += f"\n\n{func['content']}\n"

    components['kline_charts'] = kline_content

    # 实时图表组件
    chart_content = """# 实时图表功能

\"\"\"
实时图表功能
\"\"\"

"""
    for func in chart_functions:
        chart_content += f"\n\n{func['content']}\n"

    components['realtime_charts'] = chart_content

    # 告警面板组件
    alert_content = """# 告警面板功能

\"\"\"
告警面板功能
\"\"\"

"""
    for func in alert_functions:
        alert_content += f"\n\n{func['content']}\n"

    components['alert_panel'] = alert_content

    # 控制面板组件
    control_content = """# 控制面板功能

\"\"\"
控制面板功能
\"\"\"

"""
    for func in control_functions:
        control_content += f"\n\n{func['content']}\n"

    components['control_panel'] = control_content

    # 浮动操作按钮组件
    action_content = """# 浮动操作按钮功能

\"\"\"
浮动操作按钮功能
\"\"\"

"""
    for func in action_functions:
        action_content += f"\n\n{func['content']}\n"

    components['floating_actions'] = action_content

    # 通用工具函数
    utility_content = """# 通用工具函数

\"\"\"
通用工具函数
\"\"\"

"""
    for func in utility_functions:
        utility_content += f"\n\n{func['content']}\n"

    components['utility'] = utility_content

    # 写入组件文件
    print("创建组件文件...")
    for component_name, component_content in components.items():
        component_file = os.path.join(COMPONENTS_DIR, f"{component_name}.py")
        if component_content.strip() != components[component_name].strip():  # 检查是否有内容
            if write_file(component_file, component_content):
                print(f"  创建组件文件: {component_file} (大小: {len(component_content)} 字符)")
            else:
                print(f"  创建组件文件失败: {component_file}")
        else:
            print(f"  组件文件 {component_name} 无内容，跳过")

    # 创建核心类和主入口文件
    print("创建核心文件...")
    core_content = f"""# 核心类和功能

\"\"\"
{os.path.basename(SOURCE_FILE)} - 模块化拆分版
原始文件: {SOURCE_FILE}
拆分时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
\"\"\"

{enhanced_kline_dashboard_class}

# 注意：此文件是从原始文件模块化拆分而来，保持向后兼容性
# 原始功能仍可通过导入此文件和原始类名使用
"""

    core_file = os.path.join(TARGET_DIR, "core.py")
    if write_file(core_file, core_content):
        print(f"创建核心文件: {core_file} (大小: {len(core_content)} 字符)")
    else:
        print(f"创建核心文件失败: {core_file}")

    # 提取导入部分
    import_section = []
    lines = source_code.split('\n')
    for i, line in enumerate(lines):
        if i < 20:  # 检查前20行的导入部分
            if line.startswith('import ') or line.startswith('from '):
                import_section.append(line)

    # 添加导入部分
    if import_section:
        main_imports = '\n'.join(import_section) + '\n\n'
    else:
        main_imports = ''

    # 创建主入口文件
    print("创建主入口文件...")
    main_content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{os.path.basename(SOURCE_FILE)} - 模块化拆分版
原始文件: {SOURCE_FILE}
拆分时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是模块化拆分后的主入口文件，保留了原有的功能，并导入了拆分后的组件模块。
\"\"\"

{main_imports}

# 为向后兼容性保留原有导入
from src.monitoring.ai_alert_manager import AIAlertManager
from src.monitoring.ai_realtime_monitor import AIRealtimeMonitor

# 导入核心类和组件
from .core import EnhancedKlineMonitoringDashboard
from .components import *

# 应用启动函数
def create_and_run_monitoring_app():
    \"\"\"创建并运行监控应用\"\"\"
    from src.monitoring.ai_alert_manager import get_ai_alert_manager
    from src.monitoring.ai_realtime_monitor import get_ai_realtime_monitor

    # 创建告警管理器和监控器
    alert_manager = get_ai_alert_manager()
    monitor = get_ai_realtime_monitor(alert_manager)

    # 创建监控面板
    dashboard = EnhancedKlineMonitoringDashboard(alert_manager, monitor)

    # 创建路由
    @ui.page('/')
    def index():
        dashboard.create_monitoring_page()

    # 启动NiceGUI
    ui.run(
        title='MyStocks K线监控仪表板',
        host='0.0.0.0',
        port=8080,
        reload=False
    )

if __name__ == "__main__":
    create_and_run_monitoring_app()
"""

    main_file = os.path.join(TARGET_DIR, os.path.basename(SOURCE_FILE))
    if write_file(main_file, main_content):
        print(f"创建主入口文件: {main_file} (大小: {len(main_content)} 字符)")
    else:
        print(f"创建主入口文件失败: {main_file}")

    # 创建组件索引文件
    components_index = """# 组件索引文件

\"\"\"
组件索引文件，导入所有组件模块，便于外部调用。
\"\"\"

from .kline_charts import *
from .realtime_charts import *
from .alert_panel import *
from .control_panel import *
from .floating_actions import *
from .utility import *
"""

    components_index_file = os.path.join(COMPONENTS_DIR, "__init__.py")
    if write_file(components_index_file, components_index):
        print(f"创建组件索引文件: {components_index_file}")
    else:
        print(f"创建组件索引文件失败: {components_index_file}")

    # 创建拆分说明文档
    print("创建说明文档...")
    doc_content = f"""# 模块化拆分说明

## 源文件
```
{SOURCE_FILE}
```

## 拆分方案

该文件已按照《代码文件长度优化规范》拆分为以下模块：

### 主入口文件
- `nicegui_monitoring_dashboard_kline.py`: 主入口文件，包含原有导入和启动函数

### 核心文件
- `core.py`: 核心类和功能实现

### 组件文件
- `components/kline_charts.py`: K线图表相关功能 ({len(kline_functions)} 个函数)
- `components/realtime_charts.py`: 实时图表功能 ({len(chart_functions)} 个函数)
- `components/alert_panel.py`: 告警面板功能 ({len(alert_functions)} 个函数)
- `components/control_panel.py`: 控制面板功能 ({len(control_functions)} 个函数)
- `components/floating_actions.py`: 浮动操作按钮功能 ({len(action_functions)} 个函数)
- `components/utility.py`: 通用工具函数 ({len(utility_functions)} 个函数)

### 组件索引
- `components/__init__.py`: 组件索引文件，导入所有组件模块

## 使用说明

拆分后的代码保持向后兼容性，可以通过以下方式使用：

```python
# 直接导入主文件（推荐）
from web.frontend.nicegui_monitoring_dashboard import create_and_run_monitoring_app

# 或者按组件导入（高级用法）
from web.frontend.nicegui_monitoring_dashboard.components.kline_charts import *
from web.frontend.nicegui_monitoring_dashboard.core import EnhancedKlineMonitoringDashboard
```

## 注意事项

- 拆分后的模块应保持功能的独立性和完整性
- 注意避免循环导入，特别是通过__init__.py统一暴露接口
- 为每个模块添加适当的文档说明其功能和用法
"""

    doc_file = os.path.join(TARGET_DIR, 'MODULE_SPLIT_GUIDE.md')
    if write_file(doc_file, doc_content):
        print(f"创建说明文档: {doc_file} (大小: {len(doc_content)} 字符)")
    else:
        print(f"创建说明文档失败: {doc_file}")

    # 备份原始文件
    backup_file = SOURCE_FILE + '.bak.' + datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2(SOURCE_FILE, backup_file)
    print(f"原始文件已备份至: {backup_file}")

    print("\n✅ 拆分完成!")
    return True


if __name__ == '__main__':
    split_file()
