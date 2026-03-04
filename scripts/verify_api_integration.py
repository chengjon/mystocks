#!/usr/bin/env python3
"""
API集成验证脚本

验证前后端API集成是否正常工作
"""

import requests
import os
from datetime import datetime
from typing import Dict, Any

# API配置
BACKEND_PORT = os.getenv("BACKEND_PORT", "").strip()
if not BACKEND_PORT:
    raise RuntimeError("Missing BACKEND_PORT in environment")
BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def test_api_endpoint(endpoint: str, method: str = "GET") -> Dict[str, Any]:
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"

    try:
        print_info(f"Testing {method} {endpoint}")

        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=10)
        else:
            response = requests.post(url, headers=HEADERS, timeout=10)

        # Parse response
        data = response.json()

        # Validate response format
        if 'success' in data and 'code' in data and 'message' in data:
            if data['success']:
                print_success(f"{endpoint} - Success (Code: {data['code']})")
                return {'status': 'success', 'data': data}
            else:
                print_warning(f"{endpoint} - Failed: {data['message']}")
                return {'status': 'failed', 'data': data}
        else:
            print_error(f"{endpoint} - Invalid response format")
            return {'status': 'error', 'data': data}

    except requests.exceptions.ConnectionError:
        print_error(f"{endpoint} - Connection failed")
        return {'status': 'error', 'error': 'Connection failed'}

    except requests.exceptions.Timeout:
        print_error(f"{endpoint} - Timeout")
        return {'status': 'error', 'error': 'Timeout'}

    except Exception as e:
        print_error(f"{endpoint} - {str(e)}")
        return {'status': 'error', 'error': str(e)}

def main():
    """主测试流程"""
    print("=" * 60)
    print("📊 MyStocks API集成验证")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端URL: {BASE_URL}")
    print("=" * 60)
    print()

    # 测试用例
    tests = [
        ("健康检查", "/api/health"),
        ("市场概览", "/api/market/overview"),
        ("资金流向", "/api/market/fund-flow?symbol=600519"),
        ("K线数据", "/api/market/kline?stock_code=000001"),
        ("龙虎榜", "/api/market/lhb?limit=5"),
        ("CSRF Token", "/api/csrf-token"),
    ]

    results = []

    for name, endpoint in tests:
        result = test_api_endpoint(endpoint)
        results.append((name, endpoint, result))
        print()

    # 汇总结果
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    success_count = sum(1 for _, _, r in results if r['status'] == 'success')
    total_count = len(results)

    for name, endpoint, result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {name}: {endpoint}")

    print()
    print(f"总计: {success_count}/{total_count} 通过")
    print("=" * 60)

    # 详细信息
    if success_count > 0:
        print()
        print("📄 详细响应示例:")
        print("-" * 60)

        # 显示市场概览详细信息
        for name, endpoint, result in results:
            if name == "市场概览" and result['status'] == 'success':
                data = result['data'].get('data', {})
                print("市场统计:")
                print(f"  总股票数: {data.get('market_stats', {}).get('total_stocks', 'N/A')}")
                print(f"  上涨股票: {data.get('market_stats', {}).get('rising_stocks', 'N/A')}")
                print(f"  下跌股票: {data.get('market_stats', {}).get('falling_stocks', 'N/A')}")

                top_etfs = data.get('top_etfs', [])
                if top_etfs:
                    print("\n  前3个ETF:")
                    for i, etf in enumerate(top_etfs[:3], 1):
                        print(f"    {i}. {etf.get('name')} ({etf.get('symbol')})")
                        print(f"       价格: {etf.get('latest_price')} | 涨跌幅: {etf.get('change_percent')}%")
                break

    print()
    print("=" * 60)

    if success_count == total_count:
        print_success("所有测试通过！API集成正常工作")
        return 0
    else:
        print_warning(f"{total_count - success_count} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())
