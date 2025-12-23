#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟不同工作目录下运行的测试
"""

import os
import sys

# 切换到不同的工作目录来测试路径检测
test_dirs = [
    r"D:\MyData\GITHUB",  # 项目根目录
    r"D:\MyData\GITHUB\mystocks",  # mystocks目录
    r"D:\MyData\GITHUB\mystocks\db_manager",  # db_manager目录
    r"D:\MyData",  # 上级目录
]


def test_from_directory(test_dir):
    """从指定目录测试初始化"""
    print(f"\n{'=' * 60}")
    print(f"🧪 测试目录: {test_dir}")
    print(f"{'=' * 60}")

    try:
        # 切换工作目录
        original_dir = os.getcwd()
        os.chdir(test_dir)
        print(f"📂 当前工作目录: {os.getcwd()}")

        # 导入并测试初始化函数
        sys.path.insert(0, r"D:\MyData\GITHUB\mystocks\db_manager")
        from init_db_monitor import init_monitoring_database

        # 执行初始化
        success = init_monitoring_database(drop_existing=False)

        if success:
            print("✅ 测试成功!")
            return True
        else:
            print("❌ 测试失败!")
            return False

    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)


def main():
    """主测试函数"""
    print("🔬 多工作目录环境变量文件检测测试")
    print("测试智能路径检测功能是否能在不同工作目录下正确找到 .env 文件")

    success_count = 0
    total_count = len(test_dirs)

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            success = test_from_directory(test_dir)
            if success:
                success_count += 1
        else:
            print(f"⚠️ 测试目录不存在，跳过: {test_dir}")
            total_count -= 1

    print(f"\n{'=' * 60}")
    print(f"🎯 测试结果汇总: {success_count}/{total_count} 成功")
    print(f"{'=' * 60}")

    if success_count == total_count:
        print("🎉 所有测试通过! 智能路径检测功能正常工作")
    else:
        print(f"⚠️ 有 {total_count - success_count} 个测试失败")

    return success_count == total_count


if __name__ == "__main__":
    main()
