#!/usr/bin/env python3
"""
交互式数据库测试菜单兼容入口。

该模块为拆分后的 `test_database_menu.py` 保留稳定导入路径，
供旧测试和工具通过 `run_database_test_menu` 启动 CLI。
"""

from __future__ import annotations


def run_database_test_menu(tool_cls) -> None:
    """运行最小交互式数据库测试菜单。"""
    tool = tool_cls()
    tool.run_all_tests()
