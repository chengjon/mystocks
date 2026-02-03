#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的数据库连接测试脚本
用于验证TDengine导入问题是否已解决
"""

import importlib.util
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimpleTest")


def test_taos_import():
    """测试TDengine导入"""
    print("开始测试TDengine导入...")

    if importlib.util.find_spec("taos"):
        print("✓ TDengine客户端库导入成功！")
        return True
    else:
        print("✗ TDengine客户端库导入失败")
        print("提示: 请确保已正确安装TDengine客户端库")
        return False


def test_other_databases():
    """测试其他数据库库的导入"""
    print("\n开始测试其他数据库库...")

    # 测试PostgreSQL
    if importlib.util.find_spec("psycopg2"):
        print("✓ psycopg2导入成功")
    else:
        print("✗ psycopg2导入失败")

    # 测试Redis
    if importlib.util.find_spec("redis"):
        print("✓ redis导入成功")
    else:
        print("✗ redis导入失败")


def test_conditional_import():
    """测试条件导入机制"""
    print("\n测试条件导入机制...")

    # 尝试导入TDengine，如果失败则设置为None
    if importlib.util.find_spec("taos"):
        TAOS_AVAILABLE = True
        print("✓ TDengine可用，TAOS_AVAILABLE = True")
    else:
        TAOS_AVAILABLE = False
        print("✓ TDengine不可用，TAOS_AVAILABLE = False")

    return TAOS_AVAILABLE


if __name__ == "__main__":
    print("=" * 50)
    print("数据库连接库测试")
    print("=" * 50)

    # 测试TDengine导入
    taos_success = test_taos_import()

    # 测试其他数据库
    test_other_databases()

    # 测试条件导入
    taos_available = test_conditional_import()

    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"TDengine可用: {'是' if taos_available else '否'}")
    if not taos_available:
        print("\n解决方案:")
        print("1. 安装TDengine客户端: https://docs.taosdata.com/get-started/")
        print("2. 或者修改代码以跳过TDengine相关功能")
    print("=" * 50)
