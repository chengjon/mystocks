#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版拆分脚本 - 直接基于代码内容拆分
"""

import os
import re

# 添加源码路径
SOURCE_FILE = "/opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard_kline.py"
TARGET_DIR = "/opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard/components"
KLINE_FILE = os.path.join(TARGET_DIR, "kline_charts.py")
CHART_FILE = os.path.join(TARGET_DIR, "realtime_charts.py")
ALERT_FILE = os.path.join(TARGET_DIR, "alert_panel.py")
CONTROL_FILE = os.path.join(TARGET_DIR, "control_panel.py")
ACTION_FILE = os.path.join(TARGET_DIR, "floating_actions.py")
UTILITY_FILE = os.path.join(TARGET_DIR, "utility.py")


def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None


def write_file(file_path, content):
    """写入文件内容"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False


def split_simple():
    """直接拆分脚本"""
    # 读取原始文件
    print(f"读取文件: {SOURCE_FILE}")
    source_code = read_file(SOURCE_FILE)
    if not source_code:
        print(f"错误: 无法读取文件 {SOURCE_FILE}")
        return

    # 创建目录
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 提取所有函数
    def extract_functions(code):
        lines = code.split('\n')
        functions = []
        current_function = []
        in_function = False
        function_indent = None
        function_start = None
        function_name = None

        for i, line in enumerate(lines):
            # 检查是否是函数定义行
            function_match = re.match(r'^\s*def\s+([A-Za-z_]\w*)\s*\(', line)

            if function_match:
                # 保存之前的函数
                if in_function and current_function and function_name:
                    functions.append({
                        'name': function_name,
                        'content': '\n'.join(current_function)
                    })

                # 开始新函数
                in_function = True
                function_start = i
                function_indent = len(line) - len(line.lstrip())
                function_name = function_match.group(1)
                current_function = [line]
                continue

            # 如果在函数内部，添加当前行
            if in_function:
                # 如果遇到缩进级别小于等于函数缩进级别的非空行，则认为函数结束
                if line.strip() and (len(line) - len(line.lstrip())) <= function_indent:
                    in_function = False
                    # 保存函数
                    if current_function and function_name:
                        functions.append({
                            'name': function_name,
                            'content': '\n'.join(current_function)
                        })
                    current_function = []
                    # 不添加当前行，继续处理下一行
                else:
                    current_function.append(line)

        # 保存最后一个函数
        if in_function and current_function and function_name:
            functions.append({
                'name': function_name,
                'content': '\n'.join(current_function)
            })

        return functions

    # 提取函数
    functions = extract_functions(source_code)
    print(f"提取到 {len(functions)} 个函数")

    # 分类函数
    kline_functions = []
    chart_functions = []
    alert_functions = []
    control_functions = []
    action_functions = []
    utility_functions = []

    for func in functions:
        name = func['name'].lower()
        if 'kline' in name or 'chart' in name:
            kline_functions.append(func)
        elif 'alert' in name or 'notification' in name:
            alert_functions.append(func)
        elif 'control' in name or 'toggle' in name or 'change' in name:
            control_functions.append(func)
        elif 'action' in name or 'click' in name:
            action_functions.append(func)
        elif func['name'].startswith('_') or 'create' in name or 'format' in name or 'setup' in name:
            utility_functions.append(func)
        else:
            utility_functions.append(func)  # 默认为工具函数

    print(f"K线相关函数: {len(kline_functions)}")
    print(f"告警相关函数: {len(alert_functions)}")
    print(f"控制相关函数: {len(control_functions)}")
    print(f"操作相关函数: {len(action_functions)}")
    print(f"工具函数: {len(utility_functions)}")

    # 创建组件文件
    create_component_file(KLINE_FILE, "K线图表相关功能", kline_functions)
    create_component_file(CHART_FILE, "实时图表功能", chart_functions)
    create_component_file(ALERT_FILE, "告警面板功能", alert_functions)
    create_component_file(CONTROL_FILE, "控制面板功能", control_functions)
    create_component_file(ACTION_FILE, "浮动操作按钮功能", action_functions)
    create_component_file(UTILITY_FILE, "通用工具函数", utility_functions)

    # 创建__init__.py
    init_content = """# 组件索引文件

from .kline_charts import *
from .realtime_charts import *
from .alert_panel import *
from .control_panel import *
from .floating_actions import *
from .utility import *
"""
    init_file = os.path.join(TARGET_DIR, "__init__.py")
    write_file(init_file, init_content)
    print(f"创建文件: {init_file}")

    print("\n✅ 拆分完成!")


def create_component_file(file_path, title, functions):
    """创建组件文件"""
    content = f"""# {title}

"""
    content += f"""
{title}
"""

    for func in functions:
        content += f"\n\n{func['content']}\n"

    # 检查内容长度
    if len(functions) > 0:
        if write_file(file_path, content):
            print(f"创建文件: {file_path} (包含 {len(functions)} 个函数)")
        else:
            print(f"创建文件失败: {file_path}")
    else:
        print(f"跳过空文件: {file_path}")


if __name__ == '__main__':
    split_simple()
