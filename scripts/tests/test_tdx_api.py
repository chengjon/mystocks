"""
测试TDX API接口
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web/backend"))

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_health_check():
    """测试健康检查接口(不需要认证)"""
    print("\n=== 测试 TDX 健康检查 ===")
    response = client.get("/api/tdx/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def get_auth_token():
    """获取认证令牌"""
    print("\n=== 获取认证令牌 ===")
    response = client.post(
        "/api/auth/login", data={"username": "admin", "password": "admin123"}
    )
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"Login failed: {response.json()}")
        return None


def test_stock_quote(token):
    """测试股票实时行情接口"""
    print("\n=== 测试股票实时行情 (600519 贵州茅台) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/tdx/quote/600519", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票名称: {data.get('name')}")
        print(f"最新价: {data.get('price')}")
        print(f"涨跌幅: {data.get('change_pct')}%")
        print(f"成交量: {data.get('volume')}")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.json()}")


def test_index_quote(token):
    """测试指数实时行情接口"""
    print("\n=== 测试指数实时行情 (000001 上证指数) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/tdx/index/quote/000001", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"指数名称: {data.get('name')}")
        print(f"当前点位: {data.get('price')}")
        print(f"涨跌幅: {data.get('change_pct')}%")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.json()}")


def test_stock_kline(token):
    """测试股票K线接口"""
    print("\n=== 测试股票K线 (600519, 5分钟) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/tdx/kline?symbol=600519&period=5m&start_date=2025-10-14&end_date=2025-10-15",
        headers=headers,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票代码: {data.get('code')}")
        print(f"周期: {data.get('period')}")
        print(f"数据条数: {data.get('count')}")
        if data.get("data"):
            print(f"最新一条: {data['data'][-1]}")
    else:
        print(f"Error: {response.json()}")


def test_invalid_requests(token):
    """测试无效请求"""
    print("\n=== 测试无效请求 ===")
    headers = {"Authorization": f"Bearer {token}"}

    # 无效股票代码
    print("\n1. 无效股票代码 (99999):")
    response = client.get("/api/tdx/quote/99999", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # 无效周期
    print("\n2. 无效K线周期 (2m):")
    response = client.get("/api/tdx/kline?symbol=600519&period=2m", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # 未认证请求
    print("\n3. 未认证请求:")
    response = client.get("/api/tdx/quote/600519")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("=" * 60)
    print("TDX API 接口测试")
    print("=" * 60)

    try:
        # 1. 测试健康检查
        test_health_check()

        # 2. 获取认证令牌
        token = get_auth_token()
        if not token:
            print("\n❌ 无法获取认证令牌,停止测试")
            sys.exit(1)

        # 3. 测试股票实时行情
        test_stock_quote(token)

        # 4. 测试指数实时行情
        test_index_quote(token)

        # 5. 测试股票K线
        test_stock_kline(token)

        # 6. 测试无效请求
        test_invalid_requests(token)

        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
