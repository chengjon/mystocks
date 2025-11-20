"""
监控系统 API 测试脚本
Real-time Monitoring System Test
"""

import requests
import json
from datetime import date, datetime

# API base URL
BASE_URL = "http://localhost:8000"

# 测试用的 Bearer Token (如果需要认证)
# TOKEN = "your_auth_token_here"
# headers = {"Authorization": f"Bearer {TOKEN}"}
headers = {}


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health_check():
    """测试系统健康检查"""
    print_section("测试 1: 系统健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_get_alert_rules():
    """测试获取告警规则列表"""
    print_section("测试 2: 获取告警规则列表")
    response = requests.get(f"{BASE_URL}/api/monitoring/alert-rules", headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"规则数量: {len(data)}")
    print("\n前3个规则:")
    for rule in data[:3]:
        print(
            f"  - {rule['rule_name']} ({rule['rule_type']}) - 优先级: {rule['priority']}"
        )


def test_create_alert_rule():
    """测试创建告警规则"""
    print_section("测试 3: 创建告警规则")
    new_rule = {
        "rule_name": "测试规则-茅台涨停",
        "rule_type": "limit_up",
        "description": "监控贵州茅台涨停情况",
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "parameters": {"include_st": False, "consecutive_days": 1},
        "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
        "priority": 5,
        "is_active": True,
    }

    response = requests.post(
        f"{BASE_URL}/api/monitoring/alert-rules", json=new_rule, headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"创建成功! 规则ID: {data['id']}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data["id"]
    else:
        print(f"创建失败: {response.text}")
        return None


def test_update_alert_rule(rule_id):
    """测试更新告警规则"""
    print_section(f"测试 4: 更新告警规则 (ID: {rule_id})")
    updates = {"description": "监控贵州茅台涨停情况(已更新)", "priority": 4}

    response = requests.put(
        f"{BASE_URL}/api/monitoring/alert-rules/{rule_id}",
        json=updates,
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"更新成功!")
        print(f"  描述: {data['description']}")
        print(f"  优先级: {data['priority']}")


def test_fetch_realtime_data():
    """测试获取实时数据"""
    print_section("测试 5: 手动获取实时数据")

    # 测试获取指定股票的实时数据
    test_symbols = ["600519", "000001", "600000"]
    payload = {"symbols": test_symbols}

    response = requests.post(
        f"{BASE_URL}/api/monitoring/realtime/fetch", json=payload, headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"数据获取成功!")
        print(json.dumps(data, indent=2, ensure_ascii=False))


def test_get_realtime_monitoring():
    """测试查询实时监控数据"""
    print_section("测试 6: 查询实时监控数据")

    # 查询贵州茅台的实时数据
    response = requests.get(
        f"{BASE_URL}/api/monitoring/realtime/600519", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票: {data.get('stock_name')} ({data.get('symbol')})")
        print(f"价格: {data.get('price')}")
        print(f"涨跌幅: {data.get('change_percent')}%")
        print(f"成交量: {data.get('volume')}")
    elif response.status_code == 404:
        print("未找到该股票的监控数据，请先运行测试5获取数据")


def test_get_realtime_list():
    """测试查询实时监控列表"""
    print_section("测试 7: 查询实时监控列表")

    response = requests.get(
        f"{BASE_URL}/api/monitoring/realtime?limit=10", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"获取到 {len(data)} 条记录")
        for record in data[:3]:
            print(
                f"  - {record['stock_name']} ({record['symbol']}): "
                f"{record['price']} ({record['change_percent']}%)"
            )


def test_get_alerts():
    """测试查询告警记录"""
    print_section("测试 8: 查询告警记录")

    response = requests.get(
        f"{BASE_URL}/api/monitoring/alerts?limit=20", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"总告警数: {data['total']}")
        print(f"返回记录数: {len(data['data'])}")

        if data["data"]:
            print("\n最近3条告警:")
            for alert in data["data"][:3]:
                print(
                    f"  - [{alert['alert_level']}] {alert['alert_title']}: {alert['alert_message']}"
                )
                print(f"    时间: {alert['alert_time']}, 已读: {alert['is_read']}")


def test_monitoring_summary():
    """测试获取监控摘要"""
    print_section("测试 9: 获取监控摘要")

    response = requests.get(f"{BASE_URL}/api/monitoring/summary", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


def test_today_statistics():
    """测试获取今日统计"""
    print_section("测试 10: 获取今日统计数据")

    response = requests.get(f"{BASE_URL}/api/monitoring/stats/today", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


def test_fetch_dragon_tiger():
    """测试获取龙虎榜数据"""
    print_section("测试 11: 获取龙虎榜数据")

    today = date.today().isoformat()
    response = requests.post(
        f"{BASE_URL}/api/monitoring/dragon-tiger/fetch?trade_date={today}",
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_get_dragon_tiger_list():
    """测试查询龙虎榜列表"""
    print_section("测试 12: 查询龙虎榜列表")

    response = requests.get(
        f"{BASE_URL}/api/monitoring/dragon-tiger?limit=10", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"获取到 {len(data)} 条龙虎榜记录")
        for record in data[:3]:
            print(f"  - {record['stock_name']} ({record['symbol']})")
            print(f"    上榜原因: {record.get('reason', 'N/A')}")
            print(f"    净买入额: {record.get('net_amount', 0):,.2f}")


def test_delete_alert_rule(rule_id):
    """测试删除告警规则"""
    print_section(f"测试 13: 删除告警规则 (ID: {rule_id})")

    response = requests.delete(
        f"{BASE_URL}/api/monitoring/alert-rules/{rule_id}", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"删除成功!")
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("  MyStocks 监控系统 API 测试")
    print("  Phase 1:  Migration")
    print("=" * 80)

    try:
        # 测试 1-2: 基础测试
        test_health_check()
        test_get_alert_rules()

        # 测试 3-4: 规则管理
        created_rule_id = test_create_alert_rule()

        if created_rule_id:
            test_update_alert_rule(created_rule_id)

        # 测试 5-7: 实时数据
        test_fetch_realtime_data()
        test_get_realtime_monitoring()
        test_get_realtime_list()

        # 测试 8-10: 告警和统计
        test_get_alerts()
        test_monitoring_summary()
        test_today_statistics()

        # 测试 11-12: 龙虎榜
        test_fetch_dragon_tiger()
        test_get_dragon_tiger_list()

        # 测试 13: 清理 - 删除测试规则
        if created_rule_id:
            test_delete_alert_rule(created_rule_id)

        print_section("✅ 所有测试完成!")
        print("\n测试总结:")
        print("  - 告警规则管理: ✓")
        print("  - 实时数据获取: ✓")
        print("  - 告警记录查询: ✓")
        print("  - 监控统计摘要: ✓")
        print("  - 龙虎榜数据: ✓")
        print("\n⚠️  注意:")
        print("  - 某些测试可能因为市场休市或数据源问题而失败")
        print("  - 龙虎榜数据通常在收盘后才会更新")
        print("  - 建议在交易时间内运行测试以获得最佳效果")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
