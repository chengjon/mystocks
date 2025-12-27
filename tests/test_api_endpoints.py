#!/usr/bin/env python3
"""
测试API端点以获取真实状态
"""

import requests

# 后端基础URL
BASE_URL = "http://localhost:8000"


def test_api_endpoint(endpoint, method="GET", params=None, headers=None):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"

    print(f"\n测试 API: {url}")
    print(f"方法: {method}")

    try:
        response = requests.request(method, url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response.elapsed.total_seconds():.2f}s")

        if response.status_code == 200:
            print(
                "响应内容预览:",
                response.text[:200] + "..." if len(response.text) > 200 else response.text,
            )
        else:
            print(f"错误响应: {response.text}")

        return response
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None


def main():
    print("开始测试API端点...")

    # 测试健康检查
    test_api_endpoint("/health")

    # 测试API文档
    test_api_endpoint("/api/docs")

    # 测试需要认证的API（预期会返回401）
    test_api_endpoint("/api/data/stocks/basic", params={"limit": 5})

    # 测试其他API
    test_api_endpoint("/api/auth/login", method="POST", headers={"Content-Type": "application/json"})

    print("\nAPI测试完成")


if __name__ == "__main__":
    main()
