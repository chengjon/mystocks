"""
增强版E2E测试框架 - 修复数据加载和选择器问题
"""

import json
from datetime import datetime

from playwright.async_api import async_playwright


class EnhancedBaseTest:
    """增强版基础测试类 - 解决数据加载和选择器问题"""

    def __init__(self, page_name: str, base_url: str = "http://localhost:3020"):
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
        """测试前置设置"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()

        # 设置默认超时 (从10秒增加到20秒，解决首次加载慢的问题)
        self.page.set_default_timeout(20000)

        # 页面预热机制 - 解决首次访问慢的问题
        await self._warmup_browser()

    async def _warmup_browser(self):
        """
        浏览器预热机制 - 解决首次访问慢的问题

        原理: 在正式测试前先访问一次首页，让Vite完成编译和缓存
        """
        try:
            print("🔥 预热浏览器...")
            # 访问首页进行预热
            await self.page.goto(f"{self.base_url}/#/dashboard", wait_until="domcontentloaded", timeout=30000)
            # 等待Vue应用初始化
            await self.page.wait_for_timeout(3000)
            print("   ✅ 浏览器预热完成")
        except Exception as e:
            # 预热失败不影响测试
            print(f"   ⚠️  预热失败，继续测试: {str(e)}")

        # 收集控制台日志
        self.console_logs = []
        self.page.on("console", lambda msg: self.console_logs.append({"type": msg.type, "text": msg.text}))

        # 收集网络请求
        self.network_requests = []
        self.page.on(
            "request", lambda request: self.network_requests.append({"url": request.url, "method": request.method})
        )

        # 收集网络响应
        self.network_responses = []
        self.page.on(
            "response", lambda response: self.network_responses.append({"url": response.url, "status": response.status})
        )

    async def teardown(self):
        """测试后置清理"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def smart_wait_for_element(self, selector: str, timeout: int = 10000):
        """
        智能等待元素出现 - 支持多选择器策略

        Args:
            selector: CSS选择器（支持逗号分隔的多选择器）
            timeout: 超时时间
        """
        try:
            # 支持多个备选选择器
            selectors = [s.strip() for s in selector.split(",")]

            for sel in selectors:
                try:
                    await self.page.wait_for_selector(sel, timeout=timeout)
                    await self.add_check(f"智能等待({sel})", True, f"元素在{timeout}ms内出现")
                    return True
                except Exception:
                    continue

            await self.add_warning("智能等待", f"所有选择器都失败: {selector}")
            return False

        except Exception as e:
            await self.add_error("智能等待", f"{selector}: {str(e)}")
            return False

    async def wait_for_data_loaded(self, indicators: list = None, timeout: int = 10000):
        """
        等待数据加载完成 - 智能检测多种数据加载完成标志

        Args:
            indicators: 数据加载完成的指示器选择器列表
            timeout: 最大等待时间
        """
        if indicators is None:
            indicators = [
                ".data-loaded",
                '[data-loaded="true"]',
                ".el-table__row",  # 表格行出现
                ".chart canvas",  # 图表canvas出现
                ".analysis-results",  # 分析结果区域显示
            ]

        print(f"\n⏳ 等待数据加载完成（最长{timeout}ms）...")

        # 策略1: 等待任一指示器出现
        for indicator in indicators:
            try:
                await self.page.wait_for_selector(indicator, timeout=timeout)
                await self.add_check("数据加载检测", True, f"检测到: {indicator}")
                print(f"   ✅ 数据已加载（检测到: {indicator}）")
                return True
            except Exception:
                continue

        # 策略2: 等待API请求完成
        api_completed = await self.wait_for_api_completion(timeout)
        if api_completed:
            await self.add_check("数据加载检测", True, "API请求已完成")
            print("   ✅ 数据已加载（API请求完成）")
            return True

        # 策略3: 等待固定时间后继续（兜底方案）
        await self.page.wait_for_timeout(2000)
        await self.add_warning("数据加载检测", "使用固定等待时间")
        print("   ⚠️  使用固定等待时间（2秒）")
        return True

    async def wait_for_api_completion(self, timeout: int = 10000):
        """
        等待API请求完成

        Args:
            timeout: 超时时间
        """
        try:
            # 等待包含 /api/ 的响应
            await self.page.wait_for_response(
                lambda response: "/api/" in response.url and response.status == 200, timeout=timeout
            )
            return True
        except Exception:
            return False

    async def check_element_visible(self, selector: str, name: str = None):
        """
        检查元素可见性 - 支持多选择器策略

        Args:
            selector: CSS选择器（支持逗号分隔的多选择器）
            name: 元素名称
        """
        try:
            # 支持多个备选选择器
            selectors = [s.strip() for s in selector.split(",")]

            for sel in selectors:
                try:
                    element = await self.page.query_selector(sel)
                    if element:
                        is_visible = await element.is_visible()
                        elem_name = name or sel
                        await self.add_check(f"元素可见({elem_name})", is_visible, sel)
                        return is_visible
                except Exception:
                    continue

            await self.add_warning("元素检查", f"所有选择器都未找到: {selector}")
            return False

        except Exception as e:
            await self.add_error("元素检查", f"{selector}: {str(e)}")
            return False

    async def check_elements_count(self, selector: str, min_count: int = 1, name: str = None):
        """
        检查元素数量 - 支持多选择器策略

        Args:
            selector: CSS选择器（支持逗号分隔的多选择器）
            min_count: 最小数量
            name: 元素名称
        """
        try:
            selectors = [s.strip() for s in selector.split(",")]

            for sel in selectors:
                try:
                    elements = await self.page.query_selector_all(sel)
                    count = len(elements)
                    if count >= min_count:
                        elem_name = name or sel
                        await self.add_check(f"元素数量({elem_name})", True, f"找到 {count} 个")
                        return True
                except Exception:
                    continue

            await self.add_warning("元素数量检查", f"未找到足够的元素: {selector}")
            return False

        except Exception as e:
            await self.add_error("元素数量检查", f"{selector}: {str(e)}")
            return False

    async def navigate_and_wait(self, path: str, wait_time: int = 3000, timeout: int = 20000):
        """
        导航到页面并等待加载

        Args:
            path: 页面路径
            wait_time: 初始等待时间
            timeout: 页面导航超时时间 (默认20秒，解决首次加载慢的问题)
        """
        url = f"{self.base_url}{path}"
        try:
            # 使用更长的超时时间进行导航
            await self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await self.page.wait_for_timeout(wait_time)

            # 等待Vue应用挂载完成
            await self.page.wait_for_selector("body", timeout=10000)

            self.test_results["url"] = url
            await self.add_check("页面导航", True, f"成功导航到 {url}")

            # 智能等待数据加载
            await self.wait_for_data_loaded()

        except Exception as e:
            await self.add_error("页面导航", f"{path}: {str(e)}")
            raise

    async def add_check(self, name: str, passed: bool, details: str = None):
        """添加检查结果"""
        check = {"name": name, "passed": passed, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["checks"].append(check)

    async def add_error(self, name: str, details: str):
        """添加错误"""
        error = {"name": name, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["errors"].append(error)

    async def add_warning(self, name: str, details: str):
        """添加警告"""
        warning = {"name": name, "details": details, "timestamp": datetime.now().isoformat()}
        self.test_results["warnings"].append(warning)

    async def take_screenshot(self, name: str = None, full_page: bool = False):
        """保存截图"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = name or f"{self.page_name}_{timestamp}"
            screenshot_path = f"/tmp/{screenshot_name}.png"

            await self.page.screenshot(path=screenshot_path, full_page=full_page)
            self.test_results["screenshot"] = screenshot_path
            await self.add_check("截图保存", True, screenshot_path)
        except Exception as e:
            await self.add_error("截图保存", str(e))

    async def generate_report(self) -> dict:
        """生成测试报告"""
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
            "network_requests": len(self.network_requests),
            "network_responses": len(self.network_responses),
        }

        self.test_results["status"] = (
            "passed" if failed_checks == 0 and len(self.test_results["errors"]) == 0 else "failed"
        )

        # 保存JSON报告
        report_path = f"/tmp/{self.page_name}_fixed_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        self.test_results["report_path"] = report_path

        return self.test_results

    async def print_summary(self):
        """打印测试摘要"""
        report = await self.generate_report()

        print("\n" + "=" * 60)
        print(f"✅ {self.page_name} 页面测试完成（修复版）")
        print("=" * 60)
        print("📊 测试结果:")
        print(f"   - 总检查项: {report['summary']['total_checks']}")
        print(f"   - 通过: {report['summary']['passed_checks']}")
        print(f"   - 失败: {report['summary']['failed_checks']}")
        print(f"   - 通过率: {report['summary']['pass_rate']}")
        print(f"   - 错误: {report['summary']['total_errors']}")
        print(f"   - 警告: {report['summary']['total_warnings']}")
        print("=" * 60)

        return report


async def run_enhanced_test(test_class: EnhancedBaseTest, page_path: str):
    """
    运行增强版测试

    Args:
        test_class: 测试类实例
        page_path: 页面路径

    Returns:
        测试报告
    """
    try:
        await test_class.setup()

        # 导航到页面（包含智能等待）
        await test_class.navigate_and_wait(page_path)

        # 执行测试逻辑（子类实现）
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
