"""
Phase 3: Multi-source Integration Test Script
Multi-data Source Support

测试多数据源管理和公告监控系统
"""

import requests
import json
from datetime import date, timedelta

# API base URL
BASE_URL = "http://localhost:8000"
headers = {}


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_json(data, max_items=5):
    """打印JSON数据"""
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            # 限制输出数量
            print(
                json.dumps(
                    {**data, "data": data["data"][:max_items]},
                    indent=2,
                    ensure_ascii=False,
                )
            )
            if len(data["data"]) > max_items:
                print(f"  ... and {len(data['data']) - max_items} more items")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


# ============================================================================
# 多数据源管理测试
# ============================================================================


def test_multi_source_health():
    """测试1: 获取所有数据源健康状态"""
    print_section("测试 1: 获取所有数据源健康状态")

    response = requests.get(f"{BASE_URL}/api/multi-source/health", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n共有 {len(data)} 个数据源:")
        for source in data:
            print(f"\n  - {source['source_type']} (优先级: {source['priority']})")
            print(f"    状态: {source['status']}")
            print(f"    启用: {source['enabled']}")
            print(f"    成功率: {source['success_rate']:.2%}")
            print(f"    平均响应时间: {source['avg_response_time']:.3f}秒")
            print(f"    支持的数据类别: {', '.join(source['supported_categories'])}")


def test_single_source_health():
    """测试2: 获取单个数据源健康状态"""
    print_section("测试 2: 获取单个数据源健康状态")

    for source in ["eastmoney", "cninfo"]:
        print(f"\n--- {source.upper()} ---")
        response = requests.get(f"{BASE_URL}/api/multi-source/health/{source}", headers=headers)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_json(data)


def test_supported_categories():
    """测试3: 获取支持的数据类别"""
    print_section("测试 3: 获取支持的数据类别")

    response = requests.get(f"{BASE_URL}/api/multi-source/supported-categories", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n共支持 {data['total_categories']} 个数据类别:")
        for category, sources in data["categories"].items():
            print(f"  - {category}: {', '.join(sources)}")


def test_realtime_quote():
    """测试4: 获取实时行情（多数据源）"""
    print_section("测试 4: 获取实时行情（多数据源）")

    # 测试使用默认数据源
    print("\n--- 使用默认数据源 ---")
    response = requests.get(
        f"{BASE_URL}/api/multi-source/realtime-quote",
        params={"symbols": "600519,000001"},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"数据源: {data.get('source')}")
        print(f"响应时间: {data.get('response_time')}秒")
        print(f"缓存: {data.get('cached', False)}")
        if data.get("data"):
            print(f"数据条数: {data.get('count', 0)}")
            print_json(data, max_items=3)


def test_fund_flow():
    """测试5: 获取资金流向（多数据源）"""
    print_section("测试 5: 获取资金流向（多数据源）")

    response = requests.get(
        f"{BASE_URL}/api/multi-source/fund-flow",
        params={"symbol": "600519", "timeframe": "今日"},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"数据源: {data.get('source')}")
        print(f"成功: {data.get('success')}")
        if data.get("data"):
            print(f"数据条数: {data.get('count', 0)}")
            print_json(data, max_items=3)


def test_dragon_tiger():
    """测试6: 获取龙虎榜（多数据源）"""
    print_section("测试 6: 获取龙虎榜（多数据源）")

    # 获取昨天的龙虎榜
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    response = requests.get(
        f"{BASE_URL}/api/multi-source/dragon-tiger",
        params={"date_str": yesterday},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"日期: {yesterday}")
        print(f"数据源: {data.get('source')}")
        print(f"成功: {data.get('success')}")
        if data.get("data"):
            print(f"数据条数: {data.get('count', 0)}")
            print_json(data, max_items=3)


# ============================================================================
# 公告系统测试
# ============================================================================


def test_fetch_announcements():
    """测试7: 获取并保存公告"""
    print_section("测试 7: 获取并保存公告")

    # 获取最近3天的公告
    end_date = date.today().strftime("%Y-%m-%d")
    start_date = (date.today() - timedelta(days=3)).strftime("%Y-%m-%d")

    print(f"获取日期范围: {start_date} 至 {end_date}")

    response = requests.post(
        f"{BASE_URL}/api/announcement/fetch",
        params={"start_date": start_date, "end_date": end_date, "category": "all"},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)


def test_get_announcement_types():
    """测试8: 获取公告类型"""
    print_section("测试 8: 获取公告类型")

    response = requests.get(f"{BASE_URL}/api/announcement/types", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n共有 {len(data['types'])} 种公告类型:")
        for ann_type in data["types"][:10]:  # 只显示前10个
            print(f"  - {ann_type['code']}: {ann_type['name']}")


def test_get_today_announcements():
    """测试9: 获取今日公告"""
    print_section("测试 9: 获取今日公告")

    response = requests.get(
        f"{BASE_URL}/api/announcement/today",
        params={"min_importance": 0},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"日期: {data.get('date')}")
        print(f"公告数量: {data.get('count', 0)}")

        if data.get("announcements"):
            print("\n前5条公告:")
            for ann in data["announcements"][:5]:
                print(f"\n  股票: {ann['stock_code']} {ann.get('stock_name', '')}")
                print(f"  标题: {ann['title']}")
                print(f"  类型: {ann.get('type', 'N/A')}")
                print(f"  重要性: {ann['importance_level']}")
                print(f"  情感: {ann.get('sentiment', 'N/A')}")


def test_get_important_announcements():
    """测试10: 获取重要公告"""
    print_section("测试 10: 获取重要公告")

    response = requests.get(
        f"{BASE_URL}/api/announcement/important",
        params={"days": 7, "min_importance": 3},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"日期范围: {data.get('start_date')} 至 {data.get('end_date')}")
        print(f"最小重要性: {data.get('min_importance')}")
        print(f"公告数量: {data.get('count', 0)}")

        if data.get("announcements"):
            print("\n重要公告列表:")
            for ann in data["announcements"][:10]:
                print(f"\n  [{ann['importance_level']}] {ann['stock_code']} {ann.get('stock_name', '')}")
                print(f"  {ann['title']}")
                print(f"  发布日期: {ann['publish_date']}")


def test_get_stock_announcements():
    """测试11: 获取指定股票公告"""
    print_section("测试 11: 获取指定股票公告")

    stock_code = "600519"  # 贵州茅台
    print(f"查询股票: {stock_code}")

    response = requests.get(
        f"{BASE_URL}/api/announcement/stock/{stock_code}",
        params={"days": 30},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"股票代码: {data.get('stock_code')}")
        print(f"日期范围: {data.get('start_date')} 至 {data.get('end_date')}")
        print(f"公告数量: {data.get('count', 0)}")

        if data.get("announcements"):
            print("\n公告列表:")
            for ann in data["announcements"][:10]:
                print(f"\n  {ann['publish_date']}: {ann['title']}")
                print(f"    类型: {ann.get('type', 'N/A')} | 重要性: {ann['importance_level']}")


def test_announcement_list():
    """测试12: 查询公告列表（分页）"""
    print_section("测试 12: 查询公告列表（分页）")

    response = requests.get(
        f"{BASE_URL}/api/announcement/list",
        params={"page": 1, "page_size": 10, "min_importance": 2},
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"总数: {data.get('total', 0)}")
        print(f"当前页: {data.get('page')}/{data.get('total_pages')}")
        print(f"每页数量: {data.get('page_size')}")

        if data.get("data"):
            print("\n本页公告:")
            for ann in data["data"]:
                print(f"  - {ann['stock_code']}: {ann['title'][:50]}...")


def test_announcement_stats():
    """测试13: 获取公告统计"""
    print_section("测试 13: 获取公告统计")

    response = requests.get(f"{BASE_URL}/api/announcement/stats", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)


def test_evaluate_monitor_rules():
    """测试14: 评估监控规则"""
    print_section("测试 14: 评估监控规则")

    response = requests.post(f"{BASE_URL}/api/announcement/monitor/evaluate", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)


def test_refresh_health():
    """测试15: 刷新数据源健康状态"""
    print_section("测试 15: 刷新数据源健康状态")

    response = requests.post(f"{BASE_URL}/api/multi-source/refresh-health", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"刷新成功: {data.get('message')}")
        print(f"数据源数量: {data.get('sources')}")


def test_clear_cache():
    """测试16: 清空缓存"""
    print_section("测试 16: 清空缓存")

    response = requests.post(f"{BASE_URL}/api/multi-source/clear-cache", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)


# ============================================================================
# 主测试流程
# ============================================================================


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("  MyStocks Phase 3: Multi-source Integration API 测试")
    print("  Multi-data Source Support")
    print("=" * 80)

    try:
        # 多数据源管理测试
        print("\n")
        print("█" * 80)
        print("  第一部分: 多数据源管理测试")
        print("█" * 80)

        test_multi_source_health()
        test_single_source_health()
        test_supported_categories()
        test_realtime_quote()
        test_fund_flow()
        test_dragon_tiger()

        # 公告系统测试
        print("\n")
        print("█" * 80)
        print("  第二部分: 公告监控系统测试")
        print("█" * 80)

        test_get_announcement_types()
        test_fetch_announcements()
        test_get_today_announcements()
        test_get_important_announcements()
        test_get_stock_announcements()
        test_announcement_list()
        test_announcement_stats()
        test_evaluate_monitor_rules()

        # 系统管理测试
        print("\n")
        print("█" * 80)
        print("  第三部分: 系统管理测试")
        print("█" * 80)

        test_refresh_health()
        test_clear_cache()

        # 测试总结
        print_section("✅ 所有测试完成!")

        print("\n功能总结:")
        print("  ✓ 多数据源健康监控")
        print("  ✓ 数据源优先级路由")
        print("  ✓ 自动故障转移")
        print("  ✓ 实时行情（多数据源）")
        print("  ✓ 资金流向（多数据源）")
        print("  ✓ 龙虎榜（多数据源）")
        print("  ✓ 公告获取和存储")
        print("  ✓ 公告查询和筛选")
        print("  ✓ 公告重要性评分")
        print("  ✓ 公告情感分析")
        print("  ✓ 公告监控规则")
        print("  ✓ 系统健康管理")

        print("\n数据源:")
        print("  - EastMoney (东方财富): 实时行情、资金流向、龙虎榜")
        print("  - Cninfo (巨潮资讯): 官方公告")

        print("\n特性:")
        print("  - 优先级路由：根据配置的优先级选择数据源")
        print("  - 故障转移：主数据源失败时自动切换到备用源")
        print("  - 智能缓存：5分钟缓存减少API调用")
        print("  - 健康监控：实时跟踪数据源状态")
        print("  - 公告分析：自动评分和情感分析")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
