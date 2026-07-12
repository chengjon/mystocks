#!/usr/bin/env python3
"""MyStocks系统状态检查脚本
检查前端、后端和数据库服务的运行状态
"""

import os
import socket
import subprocess
from datetime import datetime

import requests


BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8020"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3020"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://localhost:{BACKEND_PORT}")
FRONTEND_URL = os.getenv("FRONTEND_URL", f"http://localhost:{FRONTEND_PORT}")


# 检查端口是否被占用
def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


# 检查服务状态
def check_service_status(name, port, url=None):
    """检查服务状态"""
    print(f"\n{'=' * 60}")
    print(f"检查 {name} 服务...")
    print(f"{'=' * 60}")

    # 检查端口
    port_status = is_port_in_use(port)
    print(f"端口 {port}: {'✅ 运行中' if port_status else '❌ 未运行'}")

    # 检查HTTP连接
    if url and port_status:
        try:
            response = requests.get(url, timeout=5)
            print(f"HTTP状态: {response.status_code}")
            print(f"响应时间: {response.elapsed.total_seconds():.2f}秒")

            # 尝试获取特定API响应
            if name == "后端服务 (API)":
                try:
                    cache_response = requests.get(
                        f"http://localhost:{port}/api/cache/status",
                        timeout=5,
                    )
                    if cache_response.status_code == 200:
                        cache_data = cache_response.json()
                        print("缓存状态: ✅ 正常工作")
                        print(
                            f"  - 总读取次数: {cache_data.get('data', {}).get('total_reads', 0)}",
                        )
                        print(
                            f"  - 总写入次数: {cache_data.get('data', {}).get('total_writes', 0)}",
                        )
                        print(
                            f"  - 命中率: {cache_data.get('data', {}).get('hit_rate_percent', '0.0%')}",
                        )
                except Exception as e:
                    print(f"缓存状态: ❌ 无法获取 ({e!s})")
        except Exception as e:
            print(f"HTTP连接错误: {e!s}")

    # 检查进程
    try:
        result = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if name.lower().replace(" ", "") in line.lower().replace(" ", ""):
                print("进程信息: 找到进程")
                break
        else:
            print("进程信息: 未找到进程")
    except Exception as e:
        print(f"进程检查错误: {e!s}")

    return port_status


# 检查日志目录
def check_logs_directory():
    """检查日志目录"""
    print(f"\n{'=' * 60}")
    print("检查日志目录...")
    print(f"{'=' * 60}")

    log_dirs = [
        "/opt/claude/mystocks_spec/var/log",
        "/opt/claude/mystocks_spec/var/log/tests",
    ]

    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            print(f"目录存在: {log_dir}")
            files = os.listdir(log_dir)
            print(f"  文件数量: {len(files)}")
            if files:
                latest_file = max(
                    [os.path.join(log_dir, f) for f in files],
                    key=os.path.getctime,
                )
                print(f"  最新文件: {latest_file}")
        else:
            print(f"目录不存在: {log_dir}")


# 检查环境变量
def check_environment_variables():
    """检查环境变量"""
    print(f"\n{'=' * 60}")
    print("检查环境变量...")
    print(f"{'=' * 60}")

    env_vars = ["USE_MOCK_DATA", "DATABASE_URL", "TDENGINE_URL", "PORT"]

    for var in env_vars:
        value = os.getenv(var, "未设置")
        # 隐藏敏感信息
        if var in ["DATABASE_URL", "TDENGINE_URL"] and value != "未设置":
            value = "[已设置]"
        print(f"{var}: {value}")


# 主函数
def main():
    """主函数"""
    print(f"\n{'=' * 60}")
    print("MyStocks 系统状态检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    # 检查前端和后端服务
    check_service_status("后端服务 (API)", BACKEND_PORT, f"{BACKEND_URL}/")
    check_service_status("前端服务 (Vue)", FRONTEND_PORT, f"{FRONTEND_URL}/")

    # 检查日志目录
    check_logs_directory()

    # 检查环境变量
    check_environment_variables()

    # 总结
    print(f"\n{'=' * 60}")
    print("总结")
    print(f"{'=' * 60}")

    backend_running = is_port_in_use(BACKEND_PORT)
    frontend_running = is_port_in_use(FRONTEND_PORT)

    if backend_running and frontend_running:
        print("✅ 前端和后端服务均正常运行")
        print("🔗 访问地址:")
        print(f"   - API文档: {BACKEND_URL}/api/docs")
        print(f"   - 前端界面: {FRONTEND_URL}")
        print(f"   - 系统监控: {BACKEND_URL}/api/cache/status")
    else:
        print("❌ 部分服务未正常运行")
        if not backend_running:
            print("   - 后端服务 (API) 未运行")
        if not frontend_running:
            print("   - 前端服务 (Vue) 未运行")

    print("\n💡 提示: 如需进一步检查，请访问API文档或前端界面")


if __name__ == "__main__":
    main()
