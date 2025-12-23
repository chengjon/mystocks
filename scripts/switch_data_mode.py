#!/usr/bin/env python3
"""
MyStocks 数据模式切换工具

用途：在Mock数据和Real数据之间切换
作者：Claude Code
创建日期：2025-12-16
版本：1.0.0

使用方法：
    python scripts/switch_data_mode.py --mode mock    # 切换到Mock模式
    python scripts/switch_data_mode.py --mode real    # 切换到Real模式
    python scripts/switch_data_mode.py --status      # 查看当前模式
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv, set_key


def load_env_file():
    """加载环境变量文件"""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print(f"❌ .env 文件不存在: {env_path}")
        return False

    load_dotenv(env_path)
    return True


def get_current_mode():
    """获取当前数据模式"""
    if not load_env_file():
        return None

    use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    real_available = os.getenv("REAL_DATA_AVAILABLE", "false").lower() == "true"

    timeseries_source = os.getenv("TIMESERIES_DATA_SOURCE", "unknown")
    relational_source = os.getenv("RELATIONAL_DATA_SOURCE", "unknown")
    business_source = os.getenv("BUSINESS_DATA_SOURCE", "unknown")

    return {
        "use_mock": use_mock,
        "real_available": real_available,
        "timeseries_source": timeseries_source,
        "relational_source": relational_source,
        "business_source": business_source,
        "mode": "mock" if use_mock else "real",
    }


def switch_to_mock():
    """切换到Mock模式"""
    print("🔄 切换到 Mock 模式...")

    env_path = PROJECT_ROOT / ".env"

    # 更新环境变量
    set_key(env_path, "USE_MOCK_DATA", "true")
    set_key(env_path, "TIMESERIES_DATA_SOURCE", "mock")
    set_key(env_path, "RELATIONAL_DATA_SOURCE", "mock")
    set_key(env_path, "BUSINESS_DATA_SOURCE", "mock")

    print("✅ Mock 模式配置已更新")
    return True


def switch_to_real():
    """切换到Real模式"""
    print("🔄 切换到 Real 模式...")

    env_path = PROJECT_ROOT / ".env"

    # 更新环境变量
    set_key(env_path, "USE_MOCK_DATA", "false")
    set_key(env_path, "REAL_DATA_AVAILABLE", "true")
    set_key(env_path, "TIMESERIES_DATA_SOURCE", "tdengine")
    set_key(env_path, "RELATIONAL_DATA_SOURCE", "postgresql")
    set_key(env_path, "BUSINESS_DATA_SOURCE", "composite")

    print("✅ Real 模式配置已更新")
    return True


def restart_backend():
    """重启后端服务"""
    print("🔄 重启后端服务...")

    try:
        # 停止现有服务
        subprocess.run(
            ["pkill", "-f", "python.*start_server"], capture_output=True, check=False
        )

        # 等待一下
        import time

        time.sleep(2)

        # 启动新服务
        backend_dir = PROJECT_ROOT / "web" / "backend"
        subprocess.Popen(
            ["python", "start_server.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        print("✅ 后端服务重启完成")
        return True

    except Exception as e:
        print(f"❌ 重启后端服务失败: {e}")
        return False


def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点...")

    import requests
    import time

    # 等待服务启动
    print("   等待后端服务启动...")
    time.sleep(8)

    test_cases = [
        ("健康检查", "http://localhost:8000/health"),
        ("API状态", "http://localhost:8000/api/status"),
        ("概念分析", "http://localhost:8000/api/analysis/concept/list?limit=3"),
    ]

    results = []

    for name, url in test_cases:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: 正常")
                results.append((name, True, response.status_code))
            else:
                print(f"   ⚠️  {name}: HTTP {response.status_code}")
                results.append((name, False, response.status_code))
        except Exception as e:
            print(f"   ❌ {name}: {str(e)}")
            results.append((name, False, None))

    return results


def test_data_sources():
    """测试数据源工厂"""
    print("🔧 测试数据源工厂...")

    try:
        from src.data_sources.factory import DataSourceFactory

        factory = DataSourceFactory()
        config = factory.get_current_config()
        registered = factory.list_registered_sources()

        print(f"   当前配置: {config}")
        print(f"   已注册源: {registered}")

        # 测试Mock数据源
        try:
            mock_ts = factory.get_timeseries_source()
            print(f"   ✅ Mock时序数据源: {type(mock_ts).__name__}")

            # 测试获取数据
            data = mock_ts.get_realtime_quotes(["600000"])
            print(f"   ✅ Mock数据获取: {len(data)} 条")
        except Exception as e:
            print(f"   ❌ Mock数据源测试失败: {e}")

        return True

    except Exception as e:
        print(f"   ❌ 数据源工厂测试失败: {e}")
        return False


def show_status():
    """显示当前状态"""
    mode_info = get_current_mode()

    if not mode_info:
        print("❌ 无法获取当前模式信息")
        return

    print("📊 当前数据模式状态:")
    print(f"   模式: {mode_info['mode'].upper()}")
    print(f"   USE_MOCK_DATA: {mode_info['use_mock']}")
    print(f"   REAL_DATA_AVAILABLE: {mode_info['real_available']}")
    print(f"   时序数据源: {mode_info['timeseries_source']}")
    print(f"   关系数据源: {mode_info['relational_source']}")
    print(f"   业务数据源: {mode_info['business_source']}")

    # 显示服务状态
    print("\n🖥️  服务状态:")
    try:
        import requests

        # 后端服务
        backend_response = requests.get("http://localhost:8000/health", timeout=3)
        backend_status = (
            "✅ 运行中" if backend_response.status_code == 200 else "⚠️  异常"
        )
        print(f"   后端服务 (8000): {backend_status}")

        # 前端服务
        frontend_response = requests.get("http://localhost:3000", timeout=3)
        frontend_status = (
            "✅ 运行中" if frontend_response.status_code == 200 else "⚠️  异常"
        )
        print(f"   前端服务 (3000): {frontend_status}")

    except Exception as e:
        print(f"   服务状态检查失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MyStocks 数据模式切换工具")
    parser.add_argument(
        "--mode", choices=["mock", "real", "status"], help="切换模式: mock/real/status"
    )
    parser.add_argument("--no-restart", action="store_true", help="不重启后端服务")
    parser.add_argument("--test", action="store_true", help="切换后运行测试")

    args = parser.parse_args()

    if args.mode == "status":
        show_status()
        return

    elif args.mode == "mock":
        if switch_to_mock():
            if not args.no_restart:
                restart_backend()
                if args.test:
                    print("\n" + "=" * 50)
                    test_data_sources()
                    test_api_endpoints()
        show_status()

    elif args.mode == "real":
        if switch_to_real():
            if not args.no_restart:
                restart_backend()
                if args.test:
                    print("\n" + "=" * 50)
                    test_data_sources()
                    test_api_endpoints()
        show_status()


if __name__ == "__main__":
    main()
