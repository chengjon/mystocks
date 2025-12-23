#!/usr/bin/env python3
"""
Track A T2: BUGer 外部服务上报测试
按照 /opt/iflow/buger/docs/guides/B项目接入指南.md 执行
"""

import json
import os
import sys
from typing import Dict

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class BUGerReportingTest:
    def __init__(self):
        self.api_url = os.getenv("BUGER_API_URL", "http://localhost:3030/api")
        self.api_key = os.getenv("BUGER_API_KEY")
        self.project_id = os.getenv("PROJECT_ID", "mystocks-project")
        self.project_name = os.getenv("PROJECT_NAME", "MyStocks")
        self.project_root = os.getenv("PROJECT_ROOT", "/opt/claude/mystocks_spec")

        print("=" * 70)
        print("🔍 BUGer 外部服务上报测试")
        print("=" * 70)
        print(f"API URL: {self.api_url}")
        print(f"Project ID: {self.project_id}")
        print(f"Project Name: {self.project_name}")
        print()

    def validate_config(self) -> bool:
        """验证配置"""
        print("📋 验证配置...")
        errors = []

        if not self.api_key:
            errors.append("❌ BUGER_API_KEY 未设置")
        elif not self.api_key.startswith("sk_"):
            errors.append("❌ API Key 格式错误，必须以 'sk_' 开头")

        if not self.api_url:
            errors.append("❌ BUGER_API_URL 未设置")

        if not self.project_id:
            errors.append("❌ PROJECT_ID 未设置")

        if errors:
            for error in errors:
                print(error)
            return False

        print("✅ 配置验证成功\n")
        return True

    def test_health_check(self) -> bool:
        """测试健康检查"""
        print("🏥 测试健康检查...")
        try:
            base_url = self.api_url.replace("/api", "")
            response = requests.get(f"{base_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ BUGer 服务运行在端口: {data.get('server', {}).get('port', 'unknown')}"
                )
                print(f"   Status: {data.get('status')}")
                print()
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                print()
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            print(f"   请确保 BUGer 服务已启动在 {self.api_url}")
            print()
            return False

    def test_single_bug_report(self) -> bool:
        """测试单个 BUG 上报"""
        print("📝 测试单个 BUG 上报...")
        try:
            bug_data = {
                "errorCode": "TEST_TRACK_A_001",
                "title": "Track A T2 测试 - 单个上报",
                "message": "验证 BUGer 外部服务单个上报功能",
                "severity": "low",
                "stackTrace": "at track_a_t2.py:test_single_bug_report",
                "context": {
                    "project_name": self.project_name,
                    "project_root": self.project_root,
                    "component": "testing",
                    "module": "buger_integration",
                    "file": "scripts/tests/buger_integration_test.py",
                },
            }

            headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}

            response = requests.post(
                f"{self.api_url}/bugs", json=bug_data, headers=headers, timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json()
                bug_id = result.get("data", {}).get("bugId")
                print("✅ BUG 上报成功")
                print(f"   Bug ID: {bug_id}")
                print(f"   Status: {result.get('data', {}).get('status')}")
                print()
                return True
            else:
                print(f"❌ 上报失败: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                print()
                return False
        except Exception as e:
            print(f"❌ 上报异常: {e}")
            print()
            return False

    def test_batch_bug_report(self) -> bool:
        """测试批量 BUG 上报"""
        print("📦 测试批量 BUG 上报...")
        try:
            bugs = [
                {
                    "errorCode": "TEST_BATCH_001",
                    "title": "批量测试 - 错误1",
                    "message": "第一个测试 BUG",
                    "severity": "low",
                    "context": {
                        "project_name": self.project_name,
                        "project_root": self.project_root,
                        "component": "testing",
                    },
                },
                {
                    "errorCode": "TEST_BATCH_002",
                    "title": "批量测试 - 错误2",
                    "message": "第二个测试 BUG",
                    "severity": "medium",
                    "context": {
                        "project_name": self.project_name,
                        "project_root": self.project_root,
                        "component": "testing",
                    },
                },
            ]

            headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}

            response = requests.post(
                f"{self.api_url}/bugs/batch",
                json={"bugs": bugs},
                headers=headers,
                timeout=30,
            )

            if response.status_code in [
                200,
                201,
                207,
            ]:  # 207 = Multi-Status (partial success)
                result = response.json()
                print("✅ 批量上报成功")
                summary = result.get("data", {}).get("summary")
                if summary:
                    print(f"   Summary: {summary}")
                print()
                return True
            else:
                print(f"❌ 批量上报失败: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                print()
                return False
        except Exception as e:
            print(f"❌ 批量上报异常: {e}")
            print()
            return False

    def test_search_bugs(self) -> bool:
        """测试 BUG 搜索"""
        print("🔍 测试 BUG 搜索...")
        try:
            headers = {"X-API-Key": self.api_key}

            response = requests.get(
                f"{self.api_url}/bugs/search",
                params={"q": "TEST_TRACK_A_001"},
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                bugs = result.get("data", {}).get("bugs", [])
                print("✅ 搜索成功")
                print(f"   找到 {len(bugs)} 个结果")
                if bugs:
                    print(f"   第一条: {bugs[0].get('title')}")
                print()
                return True
            else:
                print(f"❌ 搜索失败: HTTP {response.status_code}")
                print()
                return False
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
            print()
            return False

    def test_get_stats(self) -> bool:
        """测试统计信息"""
        print("📊 测试统计信息获取...")
        try:
            headers = {"X-API-Key": self.api_key}

            response = requests.get(
                f"{self.api_url}/bugs/stats", headers=headers, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                print("✅ 统计信息获取成功")
                print(f"   总数: {data.get('total')}")
                print(
                    f"   按严重级别: {json.dumps(data.get('bySeverity', {}), ensure_ascii=False)}"
                )
                print()
                return True
            else:
                print(f"❌ 获取失败: HTTP {response.status_code}")
                print()
                return False
        except Exception as e:
            print(f"❌ 获取异常: {e}")
            print()
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        results = {}

        # 1. 验证配置
        results["config_validation"] = self.validate_config()
        if not results["config_validation"]:
            print("❌ 配置验证失败，停止测试")
            return results

        # 2. 健康检查
        results["health_check"] = self.test_health_check()
        if not results["health_check"]:
            print("⚠️  BUGer 服务不可用，跳过其他测试")
            return results

        # 3. 单个上报
        results["single_report"] = self.test_single_bug_report()

        # 4. 批量上报
        results["batch_report"] = self.test_batch_bug_report()

        # 5. 搜索
        results["search"] = self.test_search_bugs()

        # 6. 统计
        results["stats"] = self.test_get_stats()

        return results

    def print_summary(self, results: Dict[str, bool]):
        """打印测试总结"""
        print("=" * 70)
        print("📋 测试总结")
        print("=" * 70)

        test_names = {
            "config_validation": "配置验证",
            "health_check": "健康检查",
            "single_report": "单个上报",
            "batch_report": "批量上报",
            "search": "BUG搜索",
            "stats": "统计信息",
        }

        passed = 0
        failed = 0

        for key, name in test_names.items():
            if key in results:
                status = "✅ 通过" if results[key] else "❌ 失败"
                print(f"{status} - {name}")
                if results[key]:
                    passed += 1
                else:
                    failed += 1

        print()
        print(f"总计: {passed} 通过, {failed} 失败 ({passed}/{passed + failed})")
        print()

        if failed == 0:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  有 {failed} 个测试失败，请检查配置和网络连接")


def main():
    test = BUGerReportingTest()
    results = test.run_all_tests()
    test.print_summary(results)

    # 返回结果代码
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
