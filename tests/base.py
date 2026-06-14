"""
E2E测试基础框架
提供所有测试的基类和通用功能
"""

import json
from datetime import datetime

from playwright.async_api import async_playwright


class BaseTest:
    """所有E2E测试的基类"""

    def __init__(self, page_name: str, base_url: str = "http://localhost:3020"):
        """
        初始化测试基类

        Args:
            page_name: 页面名称
            base_url: 基础URL
        """
        self.page_name = page_name
        self.base_url = base_url
        self.page = None
        self.browser = None
        self.playwright = None
        self.test_results = {
            "page_name": page_name,
            "start_time": datetime.now().isoformat(),
            "checks": [],
            "errors": [],
            "warnings": [],
        }

    async def setup(self, headless: bool = False):
        """
        测试前置设置

        Args:
            headless: 是否无头模式运行
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()

        # 设置控制台日志收集
        self.console_logs = []
        self.page.on("console", lambda msg: self.console_logs.append({"type": msg.type, "text": msg.text}))

        # 设置网络请求监听
        self.network_errors = []
        self.page.on("response", lambda response: self._check_response(response))

    async def teardown(self):
        """测试后置清理"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate_to_page(self, path: str, wait_time: int = 3000):
        """
        导航到指定页面

        Args:
            path: 页面路径
            wait_time: 等待时间(毫秒)
        """
        url = f"{self.base_url}{path}"
        try:
            await self.page.goto(url)
            await self.page.wait_for_timeout(wait_time)
            self.test_results["url"] = url
            await self.add_check("页面导航", True, f"成功导航到 {url}")
        except Exception as e:
            await self.add_error("页面导航", f"导航失败: {str(e)}")
            raise

    async def check_page_title(self, expected_title: str = None) -> bool:
        """
        检查页面标题

        Args:
            expected_title: 预期的页面标题

        Returns:
            是否通过
        """
        try:
            title = await self.page.title()
            if expected_title:
                passed = expected_title in title
                await self.add_check("页面标题", passed, f"实际: {title}, 预期包含: {expected_title}")
                return passed
            else:
                await self.add_check("页面标题", True, f"页面标题: {title}")
                return True
        except Exception as e:
            await self.add_error("页面标题", str(e))
            return False

    async def check_element_visible(self, selector: str, name: str = None) -> bool:
        """
        检查元素是否可见

        Args:
            selector: CSS选择器
            name: 元素名称（用于报告）

        Returns:
            是否可见
        """
        try:
            element = await self.page.query_selector(selector)
            if not element:
                await self.add_warning("元素检查", f"元素未找到: {selector}")
                return False

            is_visible = await element.is_visible()
            elem_name = name or selector
            await self.add_check(f"元素可见({elem_name})", is_visible, selector)
            return is_visible
        except Exception as e:
            await self.add_error("元素检查", f"{selector}: {str(e)}")
            return False

    async def check_elements_count(self, selector: str, min_count: int = 1, name: str = None) -> bool:
        """
        检查元素数量

        Args:
            selector: CSS选择器
            min_count: 最小数量
            name: 元素名称

        Returns:
            是否满足要求
        """
        try:
            elements = await self.page.query_selector_all(selector)
            count = len(elements)
            passed = count >= min_count
            elem_name = name or selector
            await self.add_check(f"元素数量({elem_name})", passed, f"实际: {count}, 预期: >={min_count}")
            return passed
        except Exception as e:
            await self.add_error("元素数量检查", f"{selector}: {str(e)}")
            return False

    async def check_no_console_errors(self) -> bool:
        """
        检查无控制台错误

        Returns:
            是否无错误
        """
        errors = [log for log in self.console_logs if log["type"] == "error"]
        error_count = len(errors)

        if error_count > 0:
            for error in errors[:5]:  # 只记录前5个
                await self.add_warning("控制台错误", error["text"][:100])

        await self.add_check("无控制台错误", error_count == 0, f"发现 {error_count} 个错误")
        return error_count == 0

    async def take_screenshot(self, name: str = None, full_page: bool = False):
        """
        保存截图

        Args:
            name: 截图名称
            full_page: 是否完整页面截图
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = name or f"{self.page_name}_{timestamp}"
            screenshot_path = f"/tmp/{screenshot_name}.png"

            await self.page.screenshot(path=screenshot_path, full_page=full_page)
            self.test_results["screenshot"] = screenshot_path
            await self.add_check("截图保存", True, screenshot_path)
        except Exception as e:
            await self.add_error("截图保存", str(e))

    async def click_element(self, selector: str, name: str = None):
        """
        点击元素

        Args:
            selector: CSS选择器
            name: 元素名称
        """
        try:
            element = await self.page.query_selector(selector)
            if not element:
                await self.add_warning("元素点击", f"元素未找到: {selector}")
                return False

            await element.click()
            elem_name = name or selector
            await self.add_check(f"点击元素({elem_name})", True, selector)
            return True
        except Exception as e:
            await self.add_error("元素点击", f"{selector}: {str(e)}")
            return False

    async def wait_for_element(self, selector: str, timeout: int = 5000):
        """
        等待元素出现

        Args:
            selector: CSS选择器
            timeout: 超时时间(毫秒)
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.add_check(f"等待元素({selector})", True, f"在{timeout}ms内出现")
            return True
        except Exception as e:
            await self.add_warning("等待元素", f"{selector}: {str(e)}")
            return False

    async def fill_input(self, selector: str, value: str, name: str = None):
        """
        填写输入框

        Args:
            selector: CSS选择器
            value: 填写值
            name: 输入框名称
        """
        try:
            await self.page.fill(selector, value)
            input_name = name or selector
            await self.add_check(f"填写输入({input_name})", True, f"值: {value}")
        except Exception as e:
            await self.add_error("填写输入", f"{selector}: {str(e)}")

    async def add_check(self, name: str, passed: bool, details: str = None):
        """
        添加检查结果

        Args:
            name: 检查项名称
            passed: 是否通过
            details: 详细信息
        """
        check = {"name": name, "passed": passed, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["checks"].append(check)

    async def add_error(self, name: str, details: str):
        """
        添加错误

        Args:
            name: 错误名称
            details: 详细信息
        """
        error = {"name": name, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["errors"].append(error)

    async def add_warning(self, name: str, details: str):
        """
        添加警告

        Args:
            name: 警告名称
            details: 详细信息
        """
        warning = {"name": name, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["warnings"].append(warning)

    def _check_response(self, response):
        """检查网络响应"""
        if response.status >= 400:
            self.network_errors.append({"url": response.url, "status": response.status})

    async def generate_report(self) -> dict:
        """
        生成测试报告

        Returns:
            测试报告字典
        """
        self.test_results["end_time"] = datetime.now().isoformat()

        # 计算统计
        total_checks = len(self.test_results["checks"])
        passed_checks = sum(1 for c in self.test_results["checks"] if c["passed"])
        failed_checks = total_checks - passed_checks

        self.test_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "pass_rate": f"{(passed_checks / total_checks * 100):.1f}%" if total_checks > 0 else "0%",
            "total_errors": len(self.test_results["errors"]),
            "total_warnings": len(self.test_results["warnings"]),
            "network_errors": len(self.network_errors),
        }

        self.test_results["status"] = (
            "passed" if failed_checks == 0 and len(self.test_results["errors"]) == 0 else "failed"
        )

        # 保存JSON报告
        report_path = f"/tmp/{self.page_name}_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        self.test_results["report_path"] = report_path

        return self.test_results

    async def print_summary(self):
        """打印测试摘要"""
        report = await self.generate_report()

        print("\n" + "=" * 60)
        print(f"✅ {self.page_name} 页面测试完成")
        print("=" * 60)
        print("📊 测试结果:")
        print(f"   - 总检查项: {report['summary']['total_checks']}")
        print(f"   - 通过: {report['summary']['passed_checks']}")
        print(f"   - 失败: {report['summary']['failed_checks']}")
        print(f"   - 通过率: {report['summary']['pass_rate']}")
        print(f"   - 错误: {report['summary']['total_errors']}")
        print(f"   - 警告: {report['summary']['total_warnings']}")
        print(f"   - 网络错误: {report['summary']['network_errors']}")

        if report["summary"]["failed_checks"] > 0:
            print("\n❌ 失败的检查项:")
            for check in report["checks"]:
                if not check["passed"]:
                    print(f"   - {check['name']}: {check.get('details', 'N/A')}")

        if report["summary"]["total_errors"] > 0:
            print("\n🔴 错误:")
            for error in report["errors"][:5]:
                print(f"   - {error['name']}: {error['details'][:100]}")

        if report["summary"]["total_warnings"] > 0:
            print("\n⚠️  警告:")
            for warning in report["warnings"][:5]:
                print(f"   - {warning['name']}: {warning['details'][:100]}")

        print(f"\n📄 报告: {report['report_path']}")
        print("=" * 60)


async def run_test(test_class: BaseTest, page_path: str):
    """
    运行单个测试

    Args:
        test_class: 测试类实例
        page_path: 页面路径

    Returns:
        测试报告
    """
    try:
        await test_class.setup()

        # 导航到页面
        await test_class.navigate_to_page(page_path)

        # 执行测试（子类实现）
        await test_class.run_test_logic()

        # 生成报告
        report = await test_class.generate_report()
        await test_class.print_summary()

        return report

    except Exception as e:
        print(f"\n❌ 测试执行失败: {str(e)}")
        import traceback

        traceback.print_exc()

        await test_class.take_screenshot(f"{test_class.page_name}_error")
        await test_class.add_error("测试执行", str(e))

        return await test_class.generate_report()

    finally:
        await test_class.teardown()
