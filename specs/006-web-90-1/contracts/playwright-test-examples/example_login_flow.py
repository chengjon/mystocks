"""
Playwright 测试示例：用户登录流程

这是一个完整的示例，展示如何使用 Playwright 进行端到端集成测试。
这个示例演示了完整的 5 层验证模型应用。

功能：测试用户登录流程
覆盖层级：Layer 5 (数据库) → Layer 2 (API) → Layer 4 (UI) → Layer 3 (集成)

学习要点：
1. 如何设置 Playwright 测试
2. 如何使用 fixtures（db_cursor, api_client, page）
3. 如何实现多层验证
4. 如何捕获截图和控制台错误
5. 如何编写清晰的断言

作者：MyStocks 开发团队
创建日期：2025-10-29
"""

import pytest
import os
from playwright.sync_api import Page, expect
from tests.integration.utils import (
    login,
    take_screenshot,
    wait_for_page_load,
    CommonSelectors,
    ConsoleCapture,
)

# ============================================================================
# 配置部分
# ============================================================================

# 从环境变量读取配置（推荐做法，避免硬编码）
MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")


# ============================================================================
# 测试类：用户登录流程
# ============================================================================


class TestUserLoginFlowExample:
    """
    用户登录流程测试示例。

    这个测试类演示如何测试完整的用户认证流程。
    每个测试方法都是独立的，可以单独运行。
    """

    def test_step_by_step_login_with_all_layers(
        self,
        page: Page,  # Playwright 页面对象 (来自 conftest.py fixture)
        db_cursor,  # 数据库游标 (来自 conftest.py fixture)
        api_client,  # API 客户端 (来自 conftest.py fixture)
    ):
        """
        完整示例：逐步验证登录流程的所有层级。

        这个测试演示了如何按照自底向上的策略验证每一层：
        1. Layer 5: 验证用户存在于数据库
        2. Layer 2: 验证登录 API 返回正确的 token
        3. Layer 4: 验证登录页面 UI 元素正确
        4. Layer 3: 验证完整的登录流程（填表、提交、跳转）

        Args:
            page: Playwright 页面对象，用于 UI 操作
            db_cursor: 数据库游标，用于数据库查询
            api_client: API 客户端，用于 API 调用
        """

        print("\n" + "=" * 70)
        print("开始完整的 5 层登录流程验证")
        print("=" * 70)

        # ====================================================================
        # Layer 5: 数据库验证
        # ====================================================================
        print("\n【Layer 5: 数据库验证】")
        print("-" * 70)

        # 查询用户是否存在
        db_cursor.execute(
            """
            SELECT username, role, is_active
            FROM users
            WHERE username = %s
        """,
            (MYSTOCKS_USER,),
        )

        user_record = db_cursor.fetchone()

        # 断言：用户必须存在
        assert user_record is not None, f"❌ 用户 {MYSTOCKS_USER} 不存在于数据库中"

        username, role, is_active = user_record

        # 断言：用户必须是激活状态
        assert is_active is True, f"❌ 用户 {username} 未激活"

        print(f"✅ 用户存在: {username}")
        print(f"   角色: {role}")
        print(f"   状态: {'激活' if is_active else '未激活'}")

        # ====================================================================
        # Layer 2: API 验证
        # ====================================================================
        print("\n【Layer 2: API 验证】")
        print("-" * 70)

        # 直接调用登录 API
        response = page.request.post(
            f"{MYSTOCKS_URL}/api/auth/login",
            data={"username": MYSTOCKS_USER, "password": MYSTOCKS_PASS},
        )

        # 断言：API 必须返回成功状态
        assert response.ok, f"❌ 登录 API 失败: HTTP {response.status}"

        print(f"✅ API 响应状态: {response.status} OK")

        # 解析响应 JSON
        data = response.json()

        # 断言：响应必须包含 access_token
        assert "access_token" in data, "❌ API 响应缺少 access_token 字段"

        token = data["access_token"]

        # 断言：token 不能为空
        assert token and len(token) > 20, "❌ Token 无效或太短"

        print(f"✅ 收到有效 JWT Token")
        print(f"   Token 长度: {len(token)} 字符")
        print(f"   Token 预览: {token[:20]}...")

        # ====================================================================
        # Layer 4: UI 验证 - 登录页面
        # ====================================================================
        print("\n【Layer 4: UI 验证 - 登录页面】")
        print("-" * 70)

        # 访问登录页面
        page.goto(f"{MYSTOCKS_URL}/login")
        wait_for_page_load(page)

        print(f"✅ 已导航到登录页面")
        print(f"   URL: {page.url}")

        # 验证 URL 正确
        assert (
            "login" in page.url.lower()
        ), f"❌ 未正确导航到登录页面，当前 URL: {page.url}"

        # 查找表单元素
        username_input = page.locator(CommonSelectors.USERNAME_INPUT)
        password_input = page.locator(CommonSelectors.PASSWORD_INPUT)
        login_button = page.locator(CommonSelectors.LOGIN_BUTTON)

        # 断言：所有表单元素必须可见
        expect(username_input).to_be_visible()
        expect(password_input).to_be_visible()
        expect(login_button).to_be_visible()

        print(f"✅ 登录表单元素全部可见")
        print(f"   - 用户名输入框")
        print(f"   - 密码输入框")
        print(f"   - 登录按钮")

        # 截图：登录页面（用于文档）
        screenshot_path = take_screenshot(page, "example_login_page")
        print(f"📸 已保存截图: {screenshot_path}")

        # ====================================================================
        # Layer 3: 集成验证 - 完整登录流程
        # ====================================================================
        print("\n【Layer 3: 集成验证 - 完整登录流程】")
        print("-" * 70)

        # 设置控制台错误捕获
        console = ConsoleCapture(page)

        # 填写用户名
        username_input.fill(MYSTOCKS_USER)
        print(f"✅ 已填写用户名: {MYSTOCKS_USER}")

        # 填写密码
        password_input.fill(MYSTOCKS_PASS)
        print(f"✅ 已填写密码: {'*' * len(MYSTOCKS_PASS)}")

        # 截图：表单已填写
        take_screenshot(page, "example_login_form_filled")

        # 点击登录按钮
        login_button.click()
        print(f"✅ 已点击登录按钮")

        # 等待导航到仪表盘
        page.wait_for_url("**/dashboard**", timeout=10000)
        print(f"✅ 已跳转到仪表盘")

        # 验证 URL 包含 dashboard
        assert (
            "dashboard" in page.url.lower()
        ), f"❌ 登录后未跳转到仪表盘，当前 URL: {page.url}"

        print(f"   当前 URL: {page.url}")

        # 截图：登录成功后的仪表盘
        screenshot_path = take_screenshot(page, "example_dashboard_after_login")
        print(f"📸 已保存截图: {screenshot_path}")

        # 验证无控制台错误
        errors = console.get_errors()
        assert len(errors) == 0, f"❌ 发现 {len(errors)} 个控制台错误: {errors}"

        print(f"✅ 无控制台错误")

        # ====================================================================
        # 测试总结
        # ====================================================================
        print("\n" + "=" * 70)
        print("✅ ✅ ✅ 所有层级验证通过！")
        print("=" * 70)
        print("\n验证结果：")
        print("  ✅ Layer 5 (数据库): 用户存在且已激活")
        print("  ✅ Layer 2 (API): 登录 API 返回有效 Token")
        print("  ✅ Layer 4 (UI): 登录页面元素正确显示")
        print("  ✅ Layer 3 (集成): 完整登录流程成功")
        print("  ✅ 无控制台错误")
        print("=" * 70 + "\n")


# ============================================================================
# 如何运行这个测试
# ============================================================================

"""
运行方式：

1. 运行单个测试：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py -v -s

2. 运行并显示详细输出：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py::TestUserLoginFlowExample::test_step_by_step_login_with_all_layers -v -s

3. 运行并生成 HTML 报告：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py --html=report.html

4. 运行时启用截图：
   pytest specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py -v --screenshot=on

注意事项：
- 确保后端服务运行在 http://localhost:8000
- 确保数据库中存在用户 admin/admin123
- 确保 Playwright 已正确安装（playwright install chromium）
- 所有截图保存在 docs/verification-screenshots/ 目录

预期结果：
- 测试应该全部通过（绿色）
- 生成 3 张截图
- 控制台输出详细的验证步骤
- 最后显示 "所有层级验证通过！"
"""


# ============================================================================
# 学习要点总结
# ============================================================================

"""
从这个示例中你应该学到：

1. **5 层验证模型的实际应用**
   - Layer 5: 使用 SQL 查询验证数据库状态
   - Layer 2: 使用 API 客户端验证 API 响应
   - Layer 4: 使用 Playwright 验证 UI 元素
   - Layer 3: 验证完整的用户交互流程

2. **Fixtures 的使用**
   - page: Playwright 页面对象（自动管理浏览器）
   - db_cursor: 数据库连接（自动清理）
   - api_client: API 客户端（自动认证）

3. **最佳实践**
   - 使用环境变量配置（不要硬编码）
   - 清晰的断言消息（失败时易于调试）
   - 适当的截图（记录关键步骤）
   - 控制台错误检查（发现 JS 问题）
   - 详细的日志输出（方便理解流程）

4. **常见模式**
   - 使用 expect() 进行 UI 断言
   - 使用 assert 进行数据断言
   - 使用辅助函数（login, take_screenshot）
   - 使用 CommonSelectors（避免重复选择器）

5. **调试技巧**
   - 使用 -s 参数显示 print 输出
   - 查看截图了解 UI 状态
   - 检查控制台错误消息
   - 使用 --headed 模式看浏览器操作（去掉 HEADLESS=true）

下一步：
- 修改这个示例测试不同的用户
- 添加更多的验证点
- 尝试测试登录失败的情况
- 查看 test_dashboard_data_display.py 学习数据表格测试
"""
