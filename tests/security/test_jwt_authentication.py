#!/usr/bin/env python3
"""
JWT Authentication Test Script
测试JWT认证实现的功能性
"""

import asyncio
from datetime import datetime

import aiohttp

BASE_URL = "http://localhost:8020"


async def test_authentication():
    """测试JWT认证功能"""
    print("🔐 开始测试 JWT 认证实现...")

    async with aiohttp.ClientSession() as session:
        # 1. 测试公共端点 (无需认证)
        print("\n1️⃣ 测试公共端点...")

        # 测试基础健康检查 (应该可以访问)
        async with session.get(f"{BASE_URL}/health") as response:
            if response.status == 200:
                print("✅ 基础健康检查端点 - 公开访问正常")
                data = await response.json()
                print(f"   状态: {data.get('overall_status', 'unknown')}")
            else:
                print(f"❌ 基础健康检查失败: {response.status}")

        # 测试认证端点 (应该可以访问)
        async with session.post(
            f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"}
        ) as response:
            if response.status == 200:
                print("✅ 登录端点 - 公开访问正常")
                auth_data = await response.json()
                access_token = auth_data.get("access_token")
                print(f"   用户: {auth_data.get('user', {}).get('username')}")
            else:
                print(f"❌ 登录失败: {response.status}")
                return

        # 2. 测试需要认证的端点 (无token应该拒绝)
        print("\n2️⃣ 测试受保护端点 (无token)...")

        protected_endpoints = [
            "/cache/status",
            "/health/detailed",
            "/monitoring/summary",
            "/data/stocks/basic?limit=10",
        ]

        for endpoint in protected_endpoints:
            async with session.get(f"{BASE_URL}{endpoint}") as response:
                if response.status == 401:
                    print(f"✅ {endpoint} - 正确拒绝无认证访问")
                else:
                    print(f"❌ {endpoint} - 应该返回401但返回了{response.status}")

        # 3. 测试需要认证的端点 (有token应该允许)
        print("\n3️⃣ 测试受保护端点 (有token)...")

        headers = {"Authorization": f"Bearer {access_token}"}

        for endpoint in protected_endpoints:
            async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                if response.status in [200, 404]:  # 200=成功, 404=功能不存在但认证通过
                    print(f"✅ {endpoint} - 认证通过")
                else:
                    print(f"❌ {endpoint} - 认证失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误: {error_text[:100]}")

        # 4. 测试用户信息端点
        print("\n4️⃣ 测试用户信息端点...")

        async with session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                print(f"✅ 用户信息获取成功: {user_data.get('username')}")
            else:
                print(f"❌ 用户信息获取失败: {response.status}")

        # 5. 测试监控状态端点 (公开)
        print("\n5️⃣ 测试公开监控端点...")

        async with session.get(f"{BASE_URL}/api/monitoring/control/status") as response:
            if response.status == 200:
                print("✅ 监控状态端点 - 公开访问正常")
                status_data = await response.json()
                print(f"   监控中: {status_data.get('data', {}).get('is_monitoring', False)}")
            else:
                print(f"❌ 监控状态端点失败: {response.status}")

    print("\n🎉 JWT 认证测试完成!")


def main():
    """主函数"""
    print(f"🚀 开始 JWT 认证测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        asyncio.run(test_authentication())
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

    print("=" * 60)


if __name__ == "__main__":
    main()
