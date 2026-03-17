import time

import requests


# 测试前端页面是否能正常加载
def test_frontend_pages():
    base_url = "http://localhost:3020"

    # 测试页面列表
    pages = [
        "/",  # 首页
        "/dashboard",  # 仪表板
        "/stocks",  # 股票列表
        "/technical-analysis",  # 技术分析
    ]

    print("测试前端页面访问...")
    for page in pages:
        try:
            response = requests.get(base_url + page)
            if response.status_code == 200:
                print(f"✅ {page} - 页面加载成功")
            else:
                print(f"❌ {page} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - 访问失败: {str(e)}")
        time.sleep(1)

    # 测试API接口
    print("\n测试API接口...")
    api_endpoints = [
        "/api/data/stocks/basic?limit=5",
        "/api/data/markets/overview",
    ]

    headers = {
        "Authorization": "Bearer <jwt-token>"
    }

    for endpoint in api_endpoints:
        try:
            response = requests.get(base_url + endpoint, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ {endpoint} - API调用成功，返回{len(data.get('data', []))}条记录")
                else:
                    print(f"❌ {endpoint} - API返回错误: {data}")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - API调用失败: {str(e)}")
        time.sleep(1)


if __name__ == "__main__":
    test_frontend_pages()
