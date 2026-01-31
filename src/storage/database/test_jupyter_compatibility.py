#!/usr/bin/env python3
# pylint: disable=import-error,no-name-in-module
# -*- coding: utf-8 -*-
"""
测试 Jupyter 环境兼容性
"""

import os
import sys

# 添加路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from init_db_monitor import init_monitoring_database


def test_jupyter_api():
    """测试 Jupyter API 调用"""
    print("🧪 测试 Jupyter 环境下的数据库初始化...")

    try:
        # 测试正常初始化
        success = init_monitoring_database(drop_existing=False)

        if success:
            print("✅ Jupyter API 测试成功!")
            return True
        else:
            print("❌ Jupyter API 测试失败!")
            return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 模拟 Jupyter 环境
    print("🔬 模拟 Jupyter 环境测试")
    print("=" * 50)

    success = test_jupyter_api()

    print("=" * 50)
    if success:
        print("🎉 所有测试通过!")
    else:
        print("💥 测试失败!")
