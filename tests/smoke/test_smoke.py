"""
MyStocks 烟雾测试套件

执行关键功能验证，确保系统核心功能正常工作。
所有测试必须通过才能部署到生产环境。

执行方法:
    pytest tests/smoke/test_smoke.py -v
    pytest tests/smoke/test_smoke.py -v -x  # 失败时立即停止
"""

import pytest
import requests
import psycopg2
from playwright.sync_api import Page, expect
import time
import os

# 配置
BASE_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DB_CONFIG = {
    "host": os.getenv("POSTGRESQL_HOST", "localhost"),
    "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
    "user": os.getenv("POSTGRESQL_USER", "mystocks_user"),
    "password": os.getenv("POSTGRESQL_PASSWORD", "mystocks2025"),
    "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
}


class TestSmokeTests:
    """烟雾测试套件 - 7 项关键测试"""

    def test_01_system_health(self):
        """
        测试 1: 系统健康检查

        验证:
        - 后端服务可访问
        - 健康检查端点返回正常
        """
        print("\n[测试 1/7] 系统健康检查...")

        # 后端健康检查
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, f"后端健康检查失败: {response.status_code}"

        data = response.json()
        assert data.get("status") in ["healthy", "ok"], f"健康状态异常: {data}"

        # 前端可访问
        response = requests.get(FRONTEND_URL, timeout=5)
        assert response.status_code == 200, f"前端服务不可访问: {response.status_code}"

        print("✅ 系统健康检查通过")

    def test_02_database_connectivity(self):
        """
        测试 2: 数据库连接和数据验证

        验证:
        - PostgreSQL 可连接
        - 核心表有数据
        - 数据时效性合格
        """
        print("\n[测试 2/7] 数据库连接测试...")

        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        try:
            # 检查核心表数据
            cursor.execute("SELECT COUNT(*) FROM cn_stock_top;")
            count = cursor.fetchone()[0]
            assert count > 0, f"cn_stock_top 表无数据 (count={count})"

            # 检查数据时效性（不超过2天）
            cursor.execute(
                """
                SELECT MAX(trade_date) FROM cn_stock_top;
            """
            )
            latest_date = cursor.fetchone()[0]

            if latest_date:
                from datetime import datetime, timedelta

                if isinstance(latest_date, str):
                    latest_date = datetime.strptime(latest_date, "%Y-%m-%d").date()

                days_old = (datetime.now().date() - latest_date).days
                assert days_old <= 2, f"数据过期 ({days_old} 天前)"

            print(f"✅ 数据库连接通过 (数据量: {count}, 最新: {latest_date})")

        finally:
            cursor.close()
            conn.close()

    def test_03_user_login(self):
        """
        测试 3: 用户登录流程

        验证:
        - 登录 API 可访问
        - 凭据验证正确
        - 返回有效 token
        """
        print("\n[测试 3/7] 用户登录测试...")

        # 登录请求
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5,
        )

        assert response.status_code == 200, f"登录失败: {response.status_code}"

        data = response.json()
        assert "access_token" in data, "响应中缺少 access_token"
        assert data["access_token"], "access_token 为空"
        assert len(data["access_token"]) > 50, "access_token 长度异常"

        print(f"✅ 用户登录通过 (token: {data['access_token'][:20]}...)")

        # 保存 token 供后续测试使用
        self.token = data["access_token"]

    def test_04_dashboard_loads(self):
        """
        测试 4: 仪表盘加载

        验证:
        - 仪表盘 API 返回数据
        - 数据结构正确
        - 响应时间合理
        """
        print("\n[测试 4/7] 仪表盘 API 测试...")

        # 如果没有 token，先登录
        if not hasattr(self, "token"):
            self.test_03_user_login()

        # 请求仪表盘数据
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/data/dashboard/summary",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=10,
        )
        response_time = time.time() - start_time

        assert response.status_code == 200, f"仪表盘 API 失败: {response.status_code}"
        assert response_time < 5.0, f"响应时间过长: {response_time:.2f}s"

        data = response.json()
        assert data.get("success"), "API 返回 success=false"
        assert "data" in data, "响应中缺少 data 字段"

        # 验证数据结构
        dashboard_data = data["data"]
        expected_keys = ["dragon_tiger", "etf_data", "fund_flow", "chip_race"]
        for key in expected_keys:
            assert key in dashboard_data, f"缺少字段: {key}"

        print(f"✅ 仪表盘 API 通过 (响应时间: {response_time:.2f}s)")

    def test_05_critical_apis(self):
        """
        测试 5: 关键 API 端点

        验证:
        - 龙虎榜 API
        - 资金流向 API
        - ETF 数据 API
        """
        print("\n[测试 5/7] 关键 API 测试...")

        # 如果没有 token，先登录
        if not hasattr(self, "token"):
            self.test_03_user_login()

        headers = {"Authorization": f"Bearer {self.token}"}

        # 测试龙虎榜 API
        response = requests.get(
            f"{BASE_URL}/api/market/v3/dragon-tiger?limit=5", headers=headers, timeout=5
        )
        assert response.status_code == 200, f"龙虎榜 API 失败: {response.status_code}"
        data = response.json()
        assert data.get("success"), "龙虎榜 API 返回 success=false"

        # 测试资金流向 API
        response = requests.get(
            f"{BASE_URL}/api/market/v3/fund-flow?limit=5", headers=headers, timeout=5
        )
        assert response.status_code == 200, f"资金流向 API 失败: {response.status_code}"

        # 测试 ETF 数据 API
        response = requests.get(
            f"{BASE_URL}/api/market/v3/etf-data?limit=5", headers=headers, timeout=5
        )
        assert response.status_code == 200, f"ETF 数据 API 失败: {response.status_code}"

        print("✅ 关键 API 测试通过 (3个端点)")

    def test_06_frontend_assets(self):
        """
        测试 6: 前端资源加载

        验证:
        - 前端页面可访问
        - 主要资源文件加载成功
        """
        print("\n[测试 6/7] 前端资源测试...")

        # 访问前端首页
        response = requests.get(FRONTEND_URL, timeout=5)
        assert response.status_code == 200, f"前端首页不可访问: {response.status_code}"

        # 检查 Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "html" in content_type.lower(), f"前端响应类型异常: {content_type}"

        print("✅ 前端资源测试通过")

    @pytest.mark.usefixtures("page")
    def test_07_data_table_rendering(self, page: Page):
        """
        测试 7: 数据表格渲染

        验证:
        - 龙虎榜页面加载
        - 数据表格渲染
        - 数据显示正常
        """
        print("\n[测试 7/7] 数据表格渲染测试...")

        # 访问龙虎榜页面
        page.goto(f"{FRONTEND_URL}/dragon-tiger", wait_until="networkidle")

        # 等待表格加载
        try:
            # 等待表格元素出现（最多等待10秒）
            page.wait_for_selector("table, .el-table, [role='table']", timeout=10000)

            # 检查是否有数据行
            rows = page.locator("tbody tr, .el-table__body tr").count()
            assert rows > 0, f"表格无数据行 (rows={rows})"

            # 检查是否没有"无数据"提示
            no_data_elements = page.locator("text=/暂无数据|无数据|No Data/i")
            assert no_data_elements.count() == 0, "表格显示'无数据'"

            print(f"✅ 数据表格渲染通过 (数据行: {rows})")

        except Exception as e:
            # 如果失败，截图帮助诊断
            screenshot_path = "docs/verification-screenshots/smoke-test-table-fail.png"
            page.screenshot(path=screenshot_path)
            print(f"❌ 表格渲染失败，截图已保存: {screenshot_path}")
            raise


# Pytest 配置
@pytest.fixture(scope="session")
def page(browser):
    """创建 Playwright 页面实例"""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (compatible; MyStocks-SmokeTest/1.0)",
    )
    page = context.new_page()
    yield page
    context.close()


if __name__ == "__main__":
    # 直接运行此文件时的行为
    pytest.main([__file__, "-v", "-s"])
