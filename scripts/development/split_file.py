#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件拆分脚本

根据《代码文件长度优化规范》拆分大文件为模块化结构。

使用方法:
    python split_file.py --source /path/to/source_file.py --target_dir /path/to/target_dir
    python split_file.py --source /path/to/source_file.py --target_dir /path/to/target_dir --split_config /path/to/config.json

作者: MyStocks开发团队
日期: 2025-11-25
"""

import os
import sys
import argparse
import json


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
    except IOError:
        return False


def find_modules(source_code):
    """从源代码中查找模块（类、函数、常量等）"""
    import re

    # 定义匹配模式
    class_pattern = r'^class\s+([A-Za-z_]\w*)\s*\('
    function_pattern = r'^def\s+([A-Za-z_]\w*)\s*\('
    constant_pattern = r'^([A-Za-z_]\w*)\s*='

    # 查找所有模块
    modules = []
    lines = source_code.split('\n')

    current_module = None
    module_content = []

    for i, line in enumerate(lines, 1):
        # 检查类定义
        class_match = re.match(class_pattern, line)
        if class_match:
            # 保存之前的模块
            if current_module:
                modules.append({
                    'name': current_module['name'],
                    'type': current_module['type'],
                    'content': '\n'.join(module_content)
                })

            # 开始新模块
            current_module = {
                'name': class_match.group(1),
                'type': 'class',
                'line_number': i
            }
            module_content = [line]
            continue

        # 检查函数定义
        function_match = re.match(function_pattern, line)
        if function_match and not current_module:
            # 保存之前的模块
            if current_module:
                modules.append({
                    'name': current_module['name'],
                    'type': current_module['type'],
                    'content': '\n'.join(module_content)
                })

            # 开始新模块
            current_module = {
                'name': function_match.group(1),
                'type': 'function',
                'line_number': i
            }
            module_content = [line]
            continue

        # 如果有当前模块，添加当前行
        if current_module:
            module_content.append(line)

    # 保存最后一个模块
    if current_module:
        modules.append({
            'name': current_module['name'],
            'type': current_module['type'],
            'content': '\n'.join(module_content)
        })

    return modules


def create_split_plan(source_file, split_config):
    """创建拆分计划"""
    # 读取拆分配置
    if split_config and os.path.exists(split_config):
        with open(split_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # 默认拆分配置
        config = {
            'modules': [
                {'name': 'kline_charts', 'description': 'K线图表相关功能'},
                {'name': 'realtime_charts', 'description': '实时图表功能'},
                {'name': 'alert_panel', 'description': '告警面板功能'},
                {'name': 'control_panel', 'description': '控制面板功能'},
                {'name': 'floating_actions', 'description': '浮动操作按钮功能'},
                {'name': 'utility', 'description': '通用工具函数'}
            ]
        }

    # 读取源代码
    source_code = read_file(source_file)
    if not source_code:
        print(f"无法读取源文件: {source_file}")
        return None

    # 查找所有模块
    modules = find_modules(source_code)

    # 创建拆分计划
    split_plan = {
        'source_file': source_file,
        'modules': modules,
        'config': config
    }

    return split_plan


def create_documentation(source_file, split_plan, target_dir):
    """创建拆分说明文档"""
    doc_content = f"""# 模块化拆分说明

## 源文件
{source_file}

## 拆分方案
"""

    for module in split_plan['config']['modules']:
        doc_content += f"""### {module['name']}
{model['description']}

文件路径: `{os.path.join(target_dir, 'components', f"{module['name']}.py")}`

"""

    doc_content += """## 使用说明

拆分后的代码保持向后兼容性，可以通过以下方式使用：

```python
# 直接导入主文件（推荐）
from web.frontend.nicegui_monitoring_dashboard_kline import EnhancedKlineMonitoringDashboard

# 或者按组件导入（高级用法）
from web.frontend.components.kline_charts import KlineChartsComponent
from web.frontend.components.control_panel import ControlPanelComponent
```

## 注意事项

- 拆分后的模块应保持功能的独立性和完整性
- 注意避免循环导入，特别是通过__init__.py统一暴露接口
- 为每个模块添加适当的文档说明其功能和用法
"""

    return doc_content


def split_file(source_file, target_dir, split_config=None, keep_main=True):
    """拆分文件"""
    # 创建拆分计划
    split_plan = create_split_plan(source_file, split_config)
    if not split_plan:
        return False

    # 读取源代码
    source_code = read_file(source_file)
    if not source_code:
        print(f"无法读取源文件: {source_file}")
        return False

    # 查找所有模块
    modules = split_plan['modules']

    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)

    # 创建组件目录
    components_dir = os.path.join(target_dir, 'components')
    os.makedirs(components_dir, exist_ok=True)

    # 创建每个组件文件
    component_files = []
    for module in modules:
        component_file = os.path.join(components_dir, f"{module['name']}.py")
        if write_file(component_file, module['content']):
            component_files.append(component_file)
            print(f"创建文件: {component_file}")
        else:
            print(f"创建文件失败: {component_file}")

    # 创建主入口文件
    if keep_main:
        main_file = os.path.join(target_dir, os.path.basename(source_file))
        main_content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{source_file.split('/')[-1]} - 模块化拆分版

该文件是模块化拆分后的主入口文件，保留了原有的功能，并导入了拆分后的组件模块。

原始文件: {source_file}

作者: MyStocks开发团队
日期: 2025-11-25
\"\"\"

# 导入拆分后的组件模块
from .components.alerts import *
from .components.charts import *
from .components.controls import *
from .components.header import *
from .components.metrics import *
from .components.system_health import *

# 导入核心类和函数
from .core import EnhancedNiceGUIMonitoringDashboard

# 为向后兼容性保留原有导入
from src.monitoring.ai_alert_manager import AIAlertManager
from src.monitoring.ai_realtime_monitor import AIRealtimeMonitor

# 应用启动函数
def create_and_run_monitoring_app():
    \"\"\"创建并运行监控应用\"\"\"
    from src.monitoring.ai_alert_manager import get_ai_alert_manager
    from src.monitoring.ai_realtime_monitor import get_ai_realtime_monitor

    # 创建告警管理器和监控器
    alert_manager = get_ai_alert_manager()
    monitor = get_ai_realtime_monitor(alert_manager)

    # 创建监控面板
    dashboard = EnhancedNiceGUIMonitoringDashboard(alert_manager, monitor)

    # 创建路由
    @ui.page('/')
    def index():
        dashboard.create_monitoring_page()

    # 启动NiceGUI
    ui.run(
        title='MyStocks 监控仪表板',
        host='0.0.0.0',
        port=8080,
        reload=False
    )

if __name__ == "__main__":
    create_and_run_monitoring_app()
"""

        write_file(main_file, main_content)
        print(f"创建主入口文件: {main_file}")

    # 创建拆分说明文档
    doc_content = create_documentation(source_file, split_plan, target_dir)
    doc_file = os.path.join(target_dir, 'MODULE_SPLIT_GUIDE.md')
    write_file(doc_file, doc_content)
    print(f"创建说明文档: {doc_file}")

    return True


def main():
    parser = argparse.ArgumentParser(description='拆分大文件为模块化结构')
    parser.add_argument('--source', type=str, required=True,
                        help='源文件路径')
    parser.add_argument('--target_dir', type=str, required=True,
                        help='目标目录')
    parser.add_argument('--split_config', type=str, default=None,
                        help='拆分配置文件')

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"源文件不存在: {args.source}")
        return 1

    if not os.path.exists(args.target_dir):
        os.makedirs(args.target_dir, exist_ok=True)

    # 拆分文件
    success = split_file(args.source, args.target_dir, args.split_config)

    if success:
        print(f"文件拆分成功: {args.source} -> {args.target_dir}")
        return 0
    else:
        print(f"文件拆分失败: {args.source} -> {args.target_dir}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
