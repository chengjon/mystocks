#!/usr/bin/env python3
"""
Web API健康检查脚本

验证10个关键页面的数据接口可用性
"""

import sys
import requests
from typing import Dict, Tuple, Optional

BASE_URL = "http://localhost:8000"
TIMEOUT = 5  # 秒

# 测试凭据（从环境变量读取，默认为测试凭据）
import os
TEST_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "admin")
TEST_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "admin123")

# 10个关键API端点
API_ENDPOINTS = [
    {
        "name": "登录认证",
        "method": "POST",
        "url": "/api/auth/login",
        "data": {"username": TEST_USERNAME, "password": TEST_PASSWORD},
        "auth_required": False,
        "priority": "P1",
        "page": "登录页面",
    },
    {
        "name": "TDX实时行情",
        "method": "GET",
        "url": "/api/tdx/quote/600519",
        "data": None,
        "auth_required": True,
        "priority": "P1",
        "page": "TDX行情页面",
    },
    {
        "name": "TDX K线数据",
        "method": "GET",
        "url": "/api/tdx/kline?symbol=600519&period=1d&limit=10",
        "data": None,
        "auth_required": True,
        "priority": "P1",
        "page": "TDX K线页面",
    },
    {
        "name": "市场行情",
        "method": "GET",
        "url": "/api/market/quotes?symbols=600519,000001",
        "data": None,
        "auth_required": True,
        "priority": "P1",
        "page": "市场行情页面",
    },
    {
        "name": "股票列表",
        "method": "GET",
        "url": "/api/market/stocks?page=1&page_size=10",
        "data": None,
        "auth_required": True,
        "priority": "P2",
        "page": "股票列表页面",
    },
    {
        "name": "历史K线",
        "method": "GET",
        "url": "/api/data/kline/600519?start_date=2025-10-01&end_date=2025-10-15",
        "data": None,
        "auth_required": True,
        "priority": "P2",
        "page": "历史K线查询页面",
    },
    {
        "name": "财务数据",
        "method": "GET",
        "url": "/api/data/financial/600519?report_type=income",
        "data": None,
        "auth_required": True,
        "priority": "P2",
        "page": "财务数据查询页面",
    },
    {
        "name": "技术指标",
        "method": "POST",
        "url": "/api/indicators/calculate",
        "data": {"symbol": "600519", "indicators": ["MA"]},
        "auth_required": True,
        "priority": "P2",
        "page": "技术指标计算页面",
    },
    {
        "name": "数据源管理",
        "method": "GET",
        "url": "/api/system/datasources",
        "data": None,
        "auth_required": True,
        "priority": "P3",
        "page": "数据源管理页面",
    },
    {
        "name": "系统健康检查",
        "method": "GET",
        "url": "/api/system/health",
        "data": None,
        "auth_required": False,
        "priority": "P2",
        "page": "系统监控页面",
    },
]


def check_backend_running() -> bool:
    """检查Backend服务是否运行"""
    try:
        resp = requests.get(f"{BASE_URL}/api/docs", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def get_auth_token() -> Optional[str]:
    """获取认证Token"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except Exception as e:
        print(f"   警告: 无法获取Token - {str(e)}")
    return None


def test_api_endpoint(endpoint: Dict, token: Optional[str]) -> Tuple[bool, str, Optional[int]]:
    """
    测试单个API端点

    Returns:
        (成功, 错误消息, 状态码)
    """
    url = f"{BASE_URL}{endpoint['url']}"
    headers = {}

    # 添加认证头
    if endpoint["auth_required"] and token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # 发送请求
        if endpoint["method"] == "GET":
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif endpoint["method"] == "POST":
            headers["Content-Type"] = "application/json"
            resp = requests.post(url, json=endpoint["data"], headers=headers, timeout=TIMEOUT)
        else:
            return False, f"不支持的方法: {endpoint['method']}", None

        # 判断成功
        if resp.status_code == 200:
            return True, "成功", resp.status_code
        elif resp.status_code == 401:
            return False, "认证失败 (Token无效或过期)", resp.status_code
        elif resp.status_code == 404:
            return False, "端点不存在", resp.status_code
        elif resp.status_code == 500:
            return False, "服务器内部错误", resp.status_code
        elif resp.status_code == 503:
            return False, "服务不可用 (可能数据库连接失败)", resp.status_code
        else:
            return False, f"HTTP {resp.status_code}", resp.status_code

    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝 (Backend未启动?)", None
    except requests.exceptions.Timeout:
        return False, f"请求超时 (>{TIMEOUT}s)", None
    except Exception as e:
        return False, f"异常: {str(e)}", None


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("MyStocks Web API 健康检查")
    print("=" * 80)

    # Step 1: 检查Backend服务
    print("\n【Step 1】检查Backend服务状态...")
    backend_running = check_backend_running()

    if not backend_running:
        print("❌ Backend服务未运行")
        print("\n启动方法:")
        print("  cd web/backend")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\n或检查是否运行在其他端口:")
        print("  lsof -i :8000")
        print("  ps aux | grep uvicorn")
        return 1

    print(f"✅ Backend服务正在运行: {BASE_URL}")

    # Step 2: 获取认证Token
    print("\n【Step 2】获取认证Token...")
    token = get_auth_token()

    if token:
        print(f"✅ Token获取成功: {token[:20]}...")
    else:
        print("⚠️  Token获取失败 (将跳过需要认证的API)")

    # Step 3: 测试所有API
    print("\n【Step 3】测试10个关键API端点...")
    print("\n" + "-" * 80)

    results = {
        "P1": {"total": 0, "passed": 0, "failed": []},
        "P2": {"total": 0, "passed": 0, "failed": []},
        "P3": {"total": 0, "passed": 0, "failed": []},
    }

    for i, endpoint in enumerate(API_ENDPOINTS, 1):
        priority = endpoint["priority"]
        results[priority]["total"] += 1

        # 测试API
        success, message, status_code = test_api_endpoint(endpoint, token)

        # 显示结果
        icon = "✅" if success else "❌"
        status_str = f"({status_code})" if status_code else ""

        print(f"{i:2d}. {icon} [{priority}] {endpoint['name']:15s} {status_str:10s} {message}")
        print(f"    页面: {endpoint['page']}")
        print(f"    URL: {endpoint['method']} {endpoint['url']}")

        if success:
            results[priority]["passed"] += 1
        else:
            results[priority]["failed"].append(
                {
                    "name": endpoint["name"],
                    "page": endpoint["page"],
                    "url": endpoint["url"],
                    "error": message,
                }
            )

        print()

    # Step 4: 统计结果
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    total_all = sum(r["total"] for r in results.values())
    passed_all = sum(r["passed"] for r in results.values())
    pass_rate = passed_all / total_all * 100 if total_all > 0 else 0

    print(f"\n总计: {passed_all}/{total_all} 通过")
    print(f"通过率: {pass_rate:.1f}%\n")

    for priority in ["P1", "P2", "P3"]:
        r = results[priority]
        if r["total"] > 0:
            priority_rate = r["passed"] / r["total"] * 100
            icon = "✅" if r["passed"] == r["total"] else "⚠️" if r["passed"] > 0 else "❌"
            print(f"{icon} {priority}: {r['passed']}/{r['total']} 通过 ({priority_rate:.0f}%)")

    # Step 5: 失败项详情
    failed_all = [item for r in results.values() for item in r["failed"]]
    if failed_all:
        print("\n" + "=" * 80)
        print("失败项详情")
        print("=" * 80)

        for i, failed in enumerate(failed_all, 1):
            print(f"\n{i}. {failed['name']}")
            print(f"   页面: {failed['page']}")
            print(f"   URL: {failed['url']}")
            print(f"   错误: {failed['error']}")

    # Step 6: 修复建议
    if failed_all:
        print("\n" + "=" * 80)
        print("修复建议")
        print("=" * 80)

        # 按错误类型分组建议
        error_types = {}
        for failed in failed_all:
            error = failed["error"]
            if error not in error_types:
                error_types[error] = []
            error_types[error].append(failed["name"])

        for error, apis in error_types.items():
            print(f"\n【{error}】")
            print(f"   影响API: {', '.join(apis)}")

            if "连接被拒绝" in error:
                print("   修复: 启动Backend服务")
            elif "端点不存在" in error:
                print("   修复: 检查路由注册，确认API端点已实现")
            elif "认证失败" in error:
                print("   修复: 检查JWT配置，重新获取Token")
            elif "服务器内部错误" in error:
                print("   修复: 查看Backend日志，检查代码异常")
            elif "服务不可用" in error:
                print("   修复: 检查数据库连接 (运行 python utils/check_db_health.py)")

    print("\n" + "=" * 80)

    # 返回退出码
    # SC-010-NEW: 10个关键API中至少8个(≥80%)返回200
    return 0 if pass_rate >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
