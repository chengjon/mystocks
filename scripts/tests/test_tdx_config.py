#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDX配置系统测试脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.adapters.tdx.config import get_tdx_config, get_tdx_server_list, get_tdx_path


def test_config():
    """测试配置系统"""
    print("\n" + "=" * 70)
    print("TDX配置系统测试")
    print("=" * 70)

    try:
        # 获取配置实例
        config = get_tdx_config()
        print(f"\n✅ 配置文件路径: {config.config_file}")
        print(f"   文件存在: {os.path.exists(config.config_file)}")

        # 获取服务器列表
        servers = get_tdx_server_list()
        print(f"\n✅ 服务器列表 (共{len(servers)}个):")
        for i, (host, port) in enumerate(servers, 1):
            print(f"   {i}. {host}:{port}")

        # 获取通达信路径
        tdx_path = get_tdx_path()
        print(f"\n✅ 通达信路径: {tdx_path}")
        print(f"   环境变量 TDX_DATA_PATH: {os.getenv('TDX_DATA_PATH', '未设置')}")

        # 获取性能配置
        perf = config.get_performance_config()
        print(f"\n✅ 性能配置:")
        print(f"   连接超时: {perf['connect_timeout']}秒")
        print(f"   API超时: {perf['api_timeout']}秒")
        print(f"   重试次数: {perf['retry_count']}")

        print("\n" + "=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_config()
    sys.exit(0 if success else 1)
