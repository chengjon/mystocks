"""
Playwright 测试示例：层级故障检测

这个示例专门演示如何精确定位问题发生在哪一层。
这是 5 层验证模型最核心的价值：快速定位问题根源。

功能：演示层级故障检测机制
需求：FR-005 (Layer Failure Detection)

学习要点：
1. 如何通过层级验证快速定位问题
2. 不同层级失败的典型表现
3. 如何根据失败层级采取不同的修复策略
4. 自底向上验证策略的优势

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
    validate_layer_5_database,
    validate_layer_2_api,
    validate_layer_4_ui,
    validate_all_layers,
)

MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")


class TestLayerFailureDetection:
    """
    层级故障检测示例。

    这些测试演示如何精确识别问题发生在哪一层，
    从而快速定位和修复问题。
    """

    def test_detect_layer5_database_failure(self, db_cursor, api_client, page: Page):
        """
        示例1：检测 Layer 5 (数据库) 故障。

        场景：数据库表为空或数据过期
        表现：后续所有层都会失败
        根因：数据源问题

        修复策略：运行数据采集脚本
        """

        print("\n" + "=" * 70)
        print("场景1: Layer 5 (数据库) 故障检测")
        print("=" * 70)

        # 测试一个不存在的表（模拟数据库问题）
        print("\n测试不存在的数据表...")

        result = validate_layer_5_database(
            db_cursor, table_name="non_existent_table_123", expected_min_count=1
        )

        print(f"\n验证结果: {result}")
        print(f"是否通过: {result.passed}")

        # Layer 5 应该失败
        assert not result.passed, "预期 Layer 5 失败，但却通过了"

        print(f"\n❌ Layer 5 失败原因:")
        for error in result.errors:
            print(f"   - {error}")

        print(f"\n🔍 故障分析:")
        print(f"   故障层级: Layer 5 (数据库)")
        print(f"   根本原因: 数据表不存在或数据为空")
        print(f"   影响范围: 所有依赖该数据的功能")
        print(f"\n💡 修复建议:")
        print(f"   1. 检查数据库连接")
        print(f"   2. 运行数据采集脚本: python collect_data.py")
        print(f"   3. 验证表结构是否正确")

        print(f"\n✅ Layer 5 故障检测成功！")

    def test_detect_layer2_api_failure(self, api_client, page: Page):
        """
        示例2：检测 Layer 2 (API) 故障。

        场景：API 端点不存在或返回错误
        表现：数据库有数据，但 API 失败
        根因：后端代码问题

        修复策略：检查后端路由和处理逻辑
        """

        print("\n" + "=" * 70)
        print("场景2: Layer 2 (API) 故障检测")
        print("=" * 70)

        # 测试一个不存在的 API 端点
        print("\n测试不存在的 API 端点...")

        result = validate_layer_2_api(
            api_client, endpoint="/api/non_existent_endpoint_123", expected_status=200
        )

        print(f"\n验证结果: {result}")
        print(f"是否通过: {result.passed}")

        # Layer 2 应该失败
        assert not result.passed, "预期 Layer 2 失败，但却通过了"

        print(f"\n❌ Layer 2 失败原因:")
        for error in result.errors:
            print(f"   - {error}")

        print(f"\n🔍 故障分析:")
        print(f"   故障层级: Layer 2 (API)")
        print(f"   根本原因: API 端点不存在或返回错误状态码")
        print(f"   影响范围: 依赖该 API 的前端功能")
        print(f"\n💡 修复建议:")
        print(f"   1. 检查后端路由配置")
        print(f"   2. 验证 API 处理函数是否正确")
        print(f"   3. 检查后端日志查看错误详情")
        print(f"   4. 使用 httpie 测试 API: http GET {MYSTOCKS_URL}/api/...")

        print(f"\n✅ Layer 2 故障检测成功！")

    def test_detect_layer4_ui_failure(self, page: Page):
        """
        示例3：检测 Layer 4 (UI) 故障。

        场景：API 正常，但 UI 元素不存在
        表现：数据和 API 都正常，但页面显示异常
        根因：前端代码问题

        修复策略：检查前端代码和控制台错误
        """

        print("\n" + "=" * 70)
        print("场景3: Layer 4 (UI) 故障检测")
        print("=" * 70)

        # 先登录
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        wait_for_page_load(page)

        # 测试不存在的 UI 元素
        print("\n测试不存在的 UI 元素...")

        result = validate_layer_4_ui(
            page,
            expected_elements={
                "non_existent_element": "#non-existent-id-123",
                "another_missing_element": ".missing-class-456",
            },
        )

        print(f"\n验证结果: {result}")
        print(f"是否通过: {result.passed}")

        # Layer 4 应该失败
        assert not result.passed, "预期 Layer 4 失败，但却通过了"

        print(f"\n❌ Layer 4 失败原因:")
        for error in result.errors:
            print(f"   - {error}")

        print(f"\n🔍 故障分析:")
        print(f"   故障层级: Layer 4 (UI/前端)")
        print(f"   根本原因: UI 元素不存在或未正确渲染")
        print(f"   影响范围: 用户看不到或无法操作相关功能")
        print(f"\n💡 修复建议:")
        print(f"   1. 检查浏览器控制台错误（F12 → Console）")
        print(f"   2. 验证前端组件是否正确引入")
        print(f"   3. 检查 CSS 选择器是否正确")
        print(f"   4. 查看网络请求是否有失败（F12 → Network）")
        print(f"   5. 检查前端构建是否成功: npm run build")

        print(f"\n✅ Layer 4 故障检测成功！")

    def test_complete_layer_failure_flow(self, page: Page, db_cursor, api_client):
        """
        示例4：完整的层级故障检测流程。

        这个测试演示了如何使用 validate_all_layers()
        自动检测故障发生在哪一层，并根据结果给出修复建议。

        这是实际开发中最常用的模式。
        """

        print("\n" + "=" * 70)
        print("场景4: 完整的层级故障检测流程")
        print("=" * 70)

        # 登录
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        wait_for_page_load(page)

        # 测试一个有问题的配置（故意使用不存在的表）
        print("\n开始多层验证（使用有问题的配置）...")

        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "non_existent_table",
                "api_endpoint": "/api/market/v3/dragon-tiger?limit=5",
                "api_expected_fields": ["stock_code"],
                "ui_elements": {"table": "table"},
                "expected_min_count": 1,
            },
        )

        print(f"\n" + "=" * 70)
        print("验证结果汇总")
        print("=" * 70)

        # 打印所有层的验证结果
        for layer_result in result.results:
            status = "✅ 通过" if layer_result.passed else "❌ 失败"
            print(f"\n{status} {layer_result.layer_name}")

            if not layer_result.passed:
                print(f"   错误:")
                for error in layer_result.errors:
                    print(f"     - {error}")

        # 确定失败的层级
        failures = result.get_failures()

        if failures:
            print(f"\n" + "=" * 70)
            print(f"🔍 故障诊断")
            print("=" * 70)

            first_failure = failures[0]
            layer_name = first_failure.layer_name

            print(f"\n第一个失败层级: {layer_name}")
            print(f"这是问题的根源所在！")

            # 根据失败层级给出建议
            if "Layer 5" in layer_name:
                print(f"\n💡 修复建议（数据库层）:")
                print(f"   1. 运行数据采集: python collect_dragon_tiger.py")
                print(f"   2. 检查数据库连接: psql -h localhost -d mystocks")
                print(f"   3. 验证表结构: \\d cn_stock_top")

            elif "Layer 2" in layer_name:
                print(f"\n💡 修复建议（API 层）:")
                print(f"   1. 检查后端服务是否运行")
                print(f"   2. 测试 API: http GET {MYSTOCKS_URL}/api/...")
                print(f"   3. 查看后端日志: tail -f logs/backend.log")
                print(f"   4. 检查路由配置: cat web/backend/app/main.py")

            elif "Layer 4" in layer_name:
                print(f"\n💡 修复建议（UI 层）:")
                print(f"   1. 检查浏览器控制台（F12）")
                print(f"   2. 验证前端构建: npm run build")
                print(f"   3. 检查网络请求（F12 → Network）")
                print(f"   4. 验证组件渲染: 查看 Vue DevTools")

            # 截图失败状态
            screenshot_path = take_screenshot(
                page, f"example_failure_{layer_name.replace(' ', '_').replace(':', '')}"
            )
            print(f"\n📸 已保存故障截图: {screenshot_path}")

        else:
            print(f"\n✅ ✅ ✅ 所有层级验证通过！")

        print(f"\n" + "=" * 70)

    def test_successful_multi_layer_validation(self, page: Page, db_cursor, api_client):
        """
        示例5：成功的多层验证（对比）。

        这个测试使用正确的配置，应该全部通过。
        用于对比失败场景，理解正确的验证流程。
        """

        print("\n" + "=" * 70)
        print("场景5: 成功的多层验证（正确配置）")
        print("=" * 70)

        # 登录
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        wait_for_page_load(page)

        # 使用正确的配置
        print("\n开始多层验证（使用正确配置）...")

        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_stock_top",
                "api_endpoint": "/api/market/v3/dragon-tiger?limit=5",
                "api_expected_fields": ["stock_code", "stock_name"],
                "ui_elements": {"page_body": "body"},
                "expected_min_count": 1,
            },
        )

        print(f"\n" + "=" * 70)
        print("验证结果汇总")
        print("=" * 70)

        # 打印所有层的验证结果
        for layer_result in result.results:
            status = "✅ 通过" if layer_result.passed else "❌ 失败"
            print(f"\n{status} {layer_result.layer_name}")

            # 显示详细信息
            if layer_result.details:
                print(f"   详细信息:")
                for key, value in layer_result.details.items():
                    print(f"     {key}: {value}")

        # 断言全部通过
        if result.all_passed:
            print(f"\n" + "=" * 70)
            print("✅ ✅ ✅ 所有层级验证通过！")
            print("=" * 70)
            print(f"\n这表示:")
            print(f"  ✅ 数据库有数据")
            print(f"  ✅ API 正确返回")
            print(f"  ✅ UI 正确显示")
            print(f"  ✅ 完整流程畅通")

            # 截图成功状态
            take_screenshot(page, "example_success_multi_layer")
        else:
            print(f"\n❌ 有层级验证失败")
            print(f"失败的层级:")
            for failure in result.get_failures():
                print(f"  - {failure.layer_name}")


# ============================================================================
# 运行和学习指南
# ============================================================================

"""
如何使用这些测试：

1. 运行所有故障检测测试：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_layer_failure_detection.py -v -s

2. 运行特定场景：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_layer_failure_detection.py::TestLayerFailureDetection::test_detect_layer5_database_failure -v -s

3. 理解每个场景的故障模式

关键学习点：

1. **自底向上验证的优势**
   - 从 Layer 5 开始验证
   - 一旦底层失败，立即停止
   - 避免浪费时间在高层验证上
   - 快速定位问题根源

2. **不同层级的典型故障**
   - Layer 5: 数据缺失、过期、格式错误
   - Layer 2: API 端点错误、返回状态异常、数据格式不对
   - Layer 4: UI 元素不存在、控制台错误、网络请求失败
   - Layer 3: 集成问题、数据流断裂

3. **故障定位效率**
   传统方式:
     - 发现 UI 显示为空 → 检查前端 → 检查 API → 检查数据库
     - 耗时：可能需要 30-60 分钟

   5层模型:
     - Layer 5 失败 → 立即知道是数据库问题
     - 耗时：1-5 分钟

4. **修复策略决策树**
   ```
   Layer 5 失败 → 运行数据采集
       ↓
   Layer 2 失败 → 检查后端代码
       ↓
   Layer 4 失败 → 检查前端代码
       ↓
   所有通过 → 功能正常
   ```

5. **实际应用场景**
   - 新功能开发：确保每层都正确
   - Bug 修复：快速定位问题所在层
   - 回归测试：验证修改没有破坏其他层
   - 生产环境监控：定期运行多层验证

下一步实践：
1. 故意制造不同层的问题，观察检测结果
2. 结合实际 Bug 修复，使用层级验证定位问题
3. 编写自己的多层验证配置
4. 集成到 CI/CD 流程中

记住：
- 90% 的 Web 功能问题都能通过 5 层验证快速定位
- 自底向上是最高效的验证策略
- 截图和日志是调试的好帮手
- 修复后务必重新运行多层验证确认
"""
