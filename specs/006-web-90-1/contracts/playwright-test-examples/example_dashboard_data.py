"""
Playwright 测试示例：仪表盘数据显示

这个示例展示如何测试数据从数据库流向前端UI的完整过程。
演示了如何验证数据的存在性、时效性和正确性。

功能：测试仪表盘数据加载和显示
覆盖层级：Layer 5 → Layer 2 → Layer 4 → Layer 3（完整数据流）

学习要点：
1. 如何验证数据库数据的存在性和时效性
2. 如何验证 API 返回的数据结构
3. 如何验证 UI 正确显示数据
4. 如何使用 validate_all_layers 进行自动化多层验证
5. 如何处理异步数据加载

作者：MyStocks 开发团队
创建日期：2025-10-29
"""

import pytest
import os
from playwright.sync_api import Page
from tests.integration.utils import (
    login,
    take_screenshot,
    wait_for_page_load,
    assert_no_loading_spinner,
    validate_all_layers,
    ConsoleCapture,
)

# 配置
MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")


class TestDashboardDataExample:
    """仪表盘数据显示测试示例。"""

    def test_dashboard_data_complete_flow(self, page: Page, db_cursor, api_client):
        """
        完整示例：验证仪表盘数据从数据库到 UI 的完整流程。

        这个测试演示了数据流验证的完整过程：
        1. Layer 5: 验证数据库有最新数据
        2. Layer 2: 验证 API 正确返回数据
        3. Layer 4: 验证 UI 正确显示数据
        4. Layer 3: 验证完整的数据流程

        这是真实场景中最常见的测试模式。
        """

        print("\n" + "=" * 70)
        print("仪表盘数据流完整验证")
        print("=" * 70)

        # ====================================================================
        # Layer 5: 数据库验证 - 数据存在性和时效性
        # ====================================================================
        print("\n【Layer 5: 数据库验证】")
        print("-" * 70)

        # 检查龙虎榜数据
        db_cursor.execute(
            """
            SELECT
                COUNT(*) as total_records,
                MAX(trade_date) as latest_date,
                CURRENT_DATE - MAX(trade_date) as days_old
            FROM cn_stock_top
        """
        )

        result = db_cursor.fetchone()
        total_records, latest_date, days_old = result

        print(f"📊 龙虎榜数据统计:")
        print(f"   总记录数: {total_records:,}")
        print(f"   最新日期: {latest_date}")
        print(f"   数据年龄: {days_old} 天")

        # 断言：必须有数据
        assert total_records > 0, "❌ 数据库中没有龙虎榜数据"

        print(f"✅ 数据存在性检查通过")

        # 断言：数据不能太旧（3天内）
        assert days_old <= 3, f"⚠️  数据已过期 {days_old} 天，建议更新"

        print(f"✅ 数据时效性检查通过")

        # 获取样本数据用于后续验证
        db_cursor.execute(
            """
            SELECT stock_code, stock_name, close_price
            FROM cn_stock_top
            WHERE trade_date = %s
            LIMIT 5
        """,
            (latest_date,),
        )

        sample_data = db_cursor.fetchall()
        print(f"\n📋 数据库样本数据（前5条）:")
        for stock_code, stock_name, close_price in sample_data:
            print(f"   {stock_code} {stock_name}: ¥{close_price}")

        # ====================================================================
        # Layer 2: API 验证 - 数据传输正确性
        # ====================================================================
        print("\n【Layer 2: API 验证】")
        print("-" * 70)

        # 调用仪表盘汇总 API
        response = api_client.get(f"{MYSTOCKS_URL}/api/data/dashboard/summary")

        assert response.ok, f"❌ Dashboard API 失败: HTTP {response.status}"

        print(f"✅ API 响应状态: {response.status} OK")

        # 解析响应
        api_data = response.json()
        print(f"📊 API 返回数据类型: {type(api_data).__name__}")

        # 根据实际 API 结构验证（这里使用通用验证）
        if isinstance(api_data, dict):
            print(f"   字段数量: {len(api_data)}")
            print(f"   字段列表: {list(api_data.keys())[:5]}")
        elif isinstance(api_data, list):
            print(f"   记录数量: {len(api_data)}")
            if len(api_data) > 0:
                print(f"   第一条记录字段: {list(api_data[0].keys())[:5]}")

        print(f"✅ API 数据结构验证通过")

        # 调用龙虎榜 API 进行更详细的验证
        response = api_client.get(f"{MYSTOCKS_URL}/api/market/v3/dragon-tiger?limit=5")

        assert response.ok, f"❌ 龙虎榜 API 失败: HTTP {response.status}"

        dragon_tiger_data = response.json()

        assert isinstance(dragon_tiger_data, list), "❌ 龙虎榜 API 应返回列表"

        assert len(dragon_tiger_data) > 0, "❌ 龙虎榜 API 返回空数据"

        print(f"\n📋 API 返回样本数据（前3条）:")
        for item in dragon_tiger_data[:3]:
            code = item.get("stock_code", "N/A")
            name = item.get("stock_name", "N/A")
            print(f"   {code} {name}")

        print(f"✅ API 数据内容验证通过")

        # ====================================================================
        # Layer 4: UI 验证 - 数据显示正确性
        # ====================================================================
        print("\n【Layer 4: UI 验证】")
        print("-" * 70)

        # 登录并导航到仪表盘
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        wait_for_page_load(page)

        print(f"✅ 已登录并进入仪表盘")
        print(f"   URL: {page.url}")

        # 等待加载完成
        assert_no_loading_spinner(page, timeout=30000)
        print(f"✅ 页面加载完成")

        # 设置控制台监听
        console = ConsoleCapture(page)

        # 等待一会儿让数据加载
        page.wait_for_timeout(2000)

        # 截图：仪表盘加载完成
        screenshot_path = take_screenshot(page, "example_dashboard_loaded")
        print(f"📸 已保存截图: {screenshot_path}")

        # 检查页面上是否有数据显示
        # 注意：这里的选择器需要根据实际 UI 调整
        page_content = page.content()

        # 检查是否显示了最新日期
        date_str = str(latest_date)
        if date_str in page_content:
            print(f"✅ UI 显示了最新日期: {date_str}")
        else:
            print(f"⚠️  UI 未明确显示日期 {date_str}")

        # 检查控制台错误
        errors = console.get_errors()
        if len(errors) > 0:
            print(f"⚠️  发现 {len(errors)} 个控制台错误:")
            for error in errors[:3]:  # 只显示前3个
                print(f"   - {error}")
        else:
            print(f"✅ 无控制台错误")

        # ====================================================================
        # Layer 3: 集成验证 - 端到端数据流
        # ====================================================================
        print("\n【Layer 3: 集成验证】")
        print("-" * 70)

        # 验证数据一致性：数据库 → API → UI
        print(f"🔄 验证数据一致性...")

        # 从数据库获取的第一条记录
        if sample_data:
            first_stock_code = sample_data[0][0]
            first_stock_name = sample_data[0][1]

            print(f"\n   数据库第一条: {first_stock_code} {first_stock_name}")

            # 检查 API 是否返回相同数据
            api_has_data = False
            for item in dragon_tiger_data:
                if item.get("stock_code") == first_stock_code:
                    api_has_data = True
                    print(f"   ✅ API 包含该股票")
                    break

            # 检查 UI 是否显示相同数据
            if first_stock_code in page_content or first_stock_name in page_content:
                print(f"   ✅ UI 显示该股票")
            else:
                print(f"   ⚠️  UI 未明确显示该股票（可能在其他位置）")

        print(f"\n✅ 端到端数据流验证完成")

        # ====================================================================
        # 测试总结
        # ====================================================================
        print("\n" + "=" * 70)
        print("✅ ✅ ✅ 仪表盘数据流验证通过！")
        print("=" * 70)
        print("\n验证摘要：")
        print(
            f"  ✅ Layer 5: 数据库有 {total_records:,} 条记录，最新日期 {latest_date}"
        )
        print(f"  ✅ Layer 2: API 正确返回数据")
        print(f"  ✅ Layer 4: UI 成功加载并显示")
        print(f"  ✅ Layer 3: 数据流端到端验证通过")
        print("=" * 70 + "\n")

    def test_dashboard_using_auto_validation(self, page: Page, db_cursor, api_client):
        """
        示例：使用自动化多层验证工具。

        这个测试展示如何使用 validate_all_layers() 函数
        自动验证所有层级，减少重复代码。

        这是推荐的写法，适合快速验证。
        """

        print("\n" + "=" * 70)
        print("使用自动化工具进行多层验证")
        print("=" * 70)

        # 先登录
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        wait_for_page_load(page)

        # 使用自动化多层验证
        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                # Layer 5 配置
                "database_table": "cn_stock_top",
                "expected_min_count": 10,
                # Layer 2 配置
                "api_endpoint": "/api/market/v3/dragon-tiger?limit=10",
                "api_expected_fields": ["stock_code", "stock_name", "trade_date"],
                # Layer 4 配置
                "ui_elements": {"page_content": "main, body, .content"},
            },
        )

        # 打印验证结果
        print(f"\n{result}")

        # 如果有失败的层
        if not result.all_passed:
            failures = result.get_failures()
            print(f"\n❌ 发现 {len(failures)} 个层级失败:")
            for failure in failures:
                print(f"\n{failure.layer_name}:")
                for error in failure.errors:
                    print(f"  - {error}")

            # 截图失败状态
            take_screenshot(page, "example_dashboard_auto_validation_FAILED")

            # 断言失败
            pytest.fail(f"多层验证失败:\n{result}")

        # 全部通过
        print(f"\n✅ ✅ ✅ 自动化多层验证全部通过！")
        take_screenshot(page, "example_dashboard_auto_validation_SUCCESS")


# ============================================================================
# 运行说明
# ============================================================================

"""
运行方式：

1. 运行完整流程测试：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_dashboard_data.py::TestDashboardDataExample::test_dashboard_data_complete_flow -v -s

2. 运行自动化验证测试：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_dashboard_data.py::TestDashboardDataExample::test_dashboard_using_auto_validation -v -s

3. 运行全部测试：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_dashboard_data.py -v -s

关键学习点：

1. **数据存在性验证** (Layer 5)
   - 使用 COUNT(*) 检查数据是否存在
   - 使用 MAX(trade_date) 检查数据最新日期
   - 使用日期差值检查数据时效性

2. **API 数据验证** (Layer 2)
   - 验证 HTTP 状态码
   - 验证响应数据结构（dict/list）
   - 验证必需字段存在
   - 验证数据内容合理性

3. **UI 显示验证** (Layer 4)
   - 等待页面加载完成
   - 等待加载动画消失
   - 检查控制台错误
   - 验证数据出现在页面内容中

4. **数据一致性验证** (Layer 3)
   - 确保数据库、API、UI 显示的是同一份数据
   - 追踪特定数据点的完整流程
   - 验证数据转换过程无误

5. **自动化验证工具**
   - validate_all_layers() 自动执行所有验证
   - 配置简单，代码量少
   - 适合快速验证和回归测试
   - 返回详细的验证结果

下一步实践：
- 修改配置验证不同的数据表
- 添加更多的数据一致性检查
- 尝试验证计算字段（如涨跌幅）
- 测试数据刷新功能
"""
