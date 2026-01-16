#!/usr/bin/env python3
"""
测试环境状态检查工具
检查测试环境的完整性和依赖状态

作者: Claude Code
生成时间: 2025-11-14
"""

import os
import sys
import subprocess
import json
import platform
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional


class TestEnvironmentChecker:
    """测试环境检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.frontend_path = self.project_root / "web" / "frontend"
        self.backend_path = self.project_root / "web" / "backend"
        self.results = {
            "environment": {},
            "dependencies": {},
            "services": {},
            "files": {},
            "tests": {},
            "overall_status": "unknown",
        }

    def check_system_info(self) -> Dict[str, Any]:
        """检查系统信息"""
        print("🔍 检查系统信息...")

        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "current_directory": os.getcwd(),
            "project_root": str(self.project_root),
        }

        # 检查Node.js
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["node_version"] = result.stdout.strip()
            else:
                info["node_version"] = None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            info["node_version"] = None

        # 检查npm
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["npm_version"] = result.stdout.strip()
            else:
                info["npm_version"] = None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            info["npm_version"] = None

        # 检查Python包管理
        for package_manager in ["pip", "pip3"]:
            try:
                result = subprocess.run(
                    [package_manager, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    info[f"{package_manager}_version"] = result.stdout.strip()
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        self.results["environment"] = info
        return info

    def check_project_structure(self) -> Dict[str, Any]:
        """检查项目结构"""
        print("📁 检查项目结构...")

        structure = {
            "project_root_exists": self.project_root.exists(),
            "frontend_exists": self.frontend_path.exists(),
            "backend_exists": self.backend_path.exists(),
            "tests_exists": (self.project_root / "tests").exists(),
            "src_exists": (self.project_root / "src").exists(),
            "config_exists": (self.project_root / "config").exists(),
        }

        # 检查关键文件
        key_files = [
            ("frontend/package.json", self.frontend_path / "package.json"),
            ("backend/requirements.txt", self.backend_path / "requirements.txt"),
            ("tests/conftest.py", self.project_root / "tests" / "conftest.py"),
            (
                "tests/e2e/playwright.config.ts",
                self.project_root / "tests" / "e2e" / "playwright.config.ts",
            ),
        ]

        for name, file_path in key_files:
            structure[f"{name}_exists"] = file_path.exists()

        self.results["files"] = structure
        return structure

    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖安装状态"""
        print("📦 检查依赖安装状态...")

        deps = {
            "frontend": {"exists": False, "installed": False, "missing": []},
            "backend": {"exists": False, "installed": False, "missing": []},
            "playwright": {"exists": False, "installed": False, "browsers": False},
            "overall": "unknown",
        }

        # 检查前端依赖
        if (self.frontend_path / "package.json").exists():
            deps["frontend"]["exists"] = True
            node_modules = self.frontend_path / "node_modules"
            if node_modules.exists():
                deps["frontend"]["installed"] = True
                # 检查关键依赖
                key_deps = ["vue", "playwright"]
                for dep in key_deps:
                    if not (node_modules / dep).exists():
                        deps["frontend"]["missing"].append(dep)
            else:
                deps["frontend"]["missing"] = ["node_modules"]

        # 检查后端依赖
        if (self.backend_path / "requirements.txt").exists():
            deps["backend"]["exists"] = True
            try:
                # 尝试导入关键Python包
                test_imports = ["fastapi", "pytest", "playwright"]
                for package in test_imports:
                    try:
                        __import__(package)
                    except ImportError:
                        deps["backend"]["missing"].append(package)

                if not deps["backend"]["missing"]:
                    deps["backend"]["installed"] = True
            except Exception as e:
                deps["backend"]["error"] = str(e)

        # 检查Playwright浏览器
        try:
            result = subprocess.run(
                ["npx", "playwright", "install", "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                deps["playwright"]["exists"] = True
                deps["playwright"]["browsers"] = True
            else:
                deps["playwright"]["exists"] = True
                deps["playwright"]["browsers"] = False
        except Exception:
            deps["playwright"]["exists"] = False

        # 计算总体状态
        if (
            deps["frontend"]["installed"]
            and deps["backend"]["installed"]
            and deps["playwright"]["browsers"]
        ):
            deps["overall"] = "ready"
        elif deps["frontend"]["exists"] or deps["backend"]["exists"]:
            deps["overall"] = "partial"
        else:
            deps["overall"] = "missing"

        self.results["dependencies"] = deps
        return deps

    def check_services(self) -> Dict[str, Any]:
        """检查服务状态"""
        print("🌐 检查服务状态...")

        services = {
            "frontend": {
                "url": "http://localhost:5173",
                "status": "unknown",
                "response_time": None,
            },
            "backend": {
                "url": "http://localhost:8000",
                "status": "unknown",
                "response_time": None,
            },
        }

        # 检查前端服务
        try:
            start_time = time.time()
            response = requests.get(services["frontend"]["url"] + "/", timeout=5)
            end_time = time.time()
            if response.status_code == 200:
                services["frontend"]["status"] = "running"
                services["frontend"]["response_time"] = round(
                    (end_time - start_time) * 1000, 2
                )
            else:
                services["frontend"]["status"] = f"error_{response.status_code}"
        except requests.exceptions.ConnectionError:
            services["frontend"]["status"] = "not_running"
        except requests.exceptions.Timeout:
            services["frontend"]["status"] = "timeout"
        except Exception as e:
            services["frontend"]["status"] = f"error_{type(e).__name__}"

        # 检查后端服务
        try:
            start_time = time.time()
            response = requests.get(services["backend"]["url"] + "/docs", timeout=5)
            end_time = time.time()
            if response.status_code == 200:
                services["backend"]["status"] = "running"
                services["backend"]["response_time"] = round(
                    (end_time - start_time) * 1000, 2
                )
            else:
                services["backend"]["status"] = f"error_{response.status_code}"
        except requests.exceptions.ConnectionError:
            services["backend"]["status"] = "not_running"
        except requests.exceptions.Timeout:
            services["backend"]["status"] = "timeout"
        except Exception as e:
            services["backend"]["status"] = f"error_{type(e).__name__}"

        self.results["services"] = services
        return services

    def check_test_configuration(self) -> Dict[str, Any]:
        """检查测试配置"""
        print("🧪 检查测试配置...")

        test_config = {
            "playwright_config": False,
            "test_files": [],
            "page_objects": False,
            "test_helpers": False,
            "global_setup": False,
            "overall": "unknown",
        }

        # 检查Playwright配置
        config_file = self.project_root / "tests" / "e2e" / "playwright.config.ts"
        if config_file.exists():
            test_config["playwright_config"] = True

        # 检查测试文件
        test_files = [
            "tests/e2e/specs/auth.spec.ts",
            "tests/e2e/specs/dashboard.spec.ts",
            "tests/e2e/specs/trading.spec.ts",
        ]

        for test_file in test_files:
            file_path = self.project_root / test_file
            test_config["test_files"].append(
                {"file": test_file, "exists": file_path.exists()}
            )

        # 检查工具文件
        tools = [
            ("tests/e2e/utils/page-objects.ts", "page_objects"),
            ("tests/e2e/utils/test-helpers.ts", "test_helpers"),
            ("tests/setup/no-docker-setup.ts", "global_setup"),
        ]

        for file_path, key in tools:
            full_path = self.project_root / file_path
            test_config[key] = full_path.exists()

        # 计算测试配置状态
        if (
            test_config["playwright_config"]
            and test_config["page_objects"]
            and test_config["test_helpers"]
            and test_config["global_setup"]
        ):
            test_config["overall"] = "complete"
        elif test_config["playwright_config"]:
            test_config["overall"] = "partial"
        else:
            test_config["overall"] = "missing"

        self.results["tests"] = test_config
        return test_config

    def check_mock_data_system(self) -> Dict[str, Any]:
        """检查Mock数据系统"""
        print("📊 检查Mock数据系统...")

        mock_system = {
            "mock_directory_exists": False,
            "mock_files": [],
            "coverage": "unknown",
        }

        mock_dir = self.project_root / "src" / "mock"
        if mock_dir.exists():
            mock_system["mock_directory_exists"] = True

            # 检查主要Mock文件
            expected_files = [
                "mock_Dashboard.py",
                "mock_Stocks.py",
                "mock_TechnicalAnalysis.py",
                "mock_Wencai.py",
                "mock_StrategyManagement.py",
            ]

            for file_name in expected_files:
                file_path = mock_dir / file_name
                mock_system["mock_files"].append(
                    {
                        "file": file_name,
                        "exists": file_path.exists(),
                        "size": file_path.stat().st_size if file_path.exists() else 0,
                    }
                )

        # 计算覆盖率
        existing_files = sum(1 for f in mock_system["mock_files"] if f["exists"])
        total_files = len(mock_system["mock_files"])

        if total_files > 0:
            coverage_percent = (existing_files / total_files) * 100
            mock_system["coverage"] = (
                f"{coverage_percent:.1f}% ({existing_files}/{total_files})"
            )

        return mock_system

    def generate_report(self) -> Dict[str, Any]:
        """生成完整检查报告"""
        print("📋 生成检查报告...")

        # 执行所有检查
        self.check_system_info()
        self.check_project_structure()
        self.check_dependencies()
        self.check_services()
        self.check_test_configuration()

        # 添加Mock数据检查结果
        self.results["mock_data"] = self.check_mock_data_system()

        # 计算总体状态
        overall_score = 0
        max_score = 100

        # 环境检查 (20分)
        if self.results["environment"].get("python_version"):
            overall_score += 10
        if self.results["environment"].get("node_version"):
            overall_score += 10

        # 项目结构 (20分)
        if self.results["files"].get("project_root_exists"):
            overall_score += 5
        if self.results["files"].get("frontend_exists"):
            overall_score += 5
        if self.results["files"].get("backend_exists"):
            overall_score += 5
        if self.results["files"].get("tests_exists"):
            overall_score += 5

        # 依赖检查 (30分)
        deps = self.results["dependencies"]
        if deps["frontend"]["installed"]:
            overall_score += 10
        if deps["backend"]["installed"]:
            overall_score += 10
        if deps["playwright"]["browsers"]:
            overall_score += 10

        # 测试配置 (20分)
        tests = self.results["tests"]
        if tests["playwright_config"]:
            overall_score += 5
        if tests["page_objects"]:
            overall_score += 5
        if tests["test_helpers"]:
            overall_score += 5
        if tests["global_setup"]:
            overall_score += 5

        # 服务状态 (10分)
        services = self.results["services"]
        if services["frontend"]["status"] == "running":
            overall_score += 5
        if services["backend"]["status"] == "running":
            overall_score += 5

        # 确定总体状态
        if overall_score >= 90:
            self.results["overall_status"] = "excellent"
        elif overall_score >= 70:
            self.results["overall_status"] = "good"
        elif overall_score >= 50:
            self.results["overall_status"] = "fair"
        elif overall_score >= 30:
            self.results["overall_status"] = "poor"
        else:
            self.results["overall_status"] = "critical"

        self.results["overall_score"] = overall_score
        self.results["max_score"] = max_score

        return self.results

    def print_report(self):
        """打印检查报告"""
        print("\n" + "=" * 80)
        print("🔍 测试环境状态检查报告")
        print("=" * 80)

        # 总体状态
        status_icon = {
            "excellent": "🟢",
            "good": "🟡",
            "fair": "🟠",
            "poor": "🔴",
            "critical": "💀",
            "unknown": "❓",
        }

        icon = status_icon.get(self.results["overall_status"], "❓")
        print(f"\n{icon} 总体状态: {self.results['overall_status'].upper()}")
        print(f"📊 评分: {self.results['overall_score']}/{self.results['max_score']}")

        # 系统信息
        env = self.results["environment"]
        print("\n💻 系统信息:")
        print(
            f"   平台: {env.get('platform', 'Unknown')} {env.get('platform_version', '')}"
        )
        print(f"   Python: {env.get('python_version', 'Not found')}")
        print(f"   Node.js: {env.get('node_version', 'Not found')}")
        print(f"   npm: {env.get('npm_version', 'Not found')}")

        # 项目结构
        files = self.results["files"]
        print("\n📁 项目结构:")
        for key, value in files.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key.replace('_', ' ').title()}")

        # 依赖状态
        deps = self.results["dependencies"]
        print("\n📦 依赖状态:")
        print(f"   前端: {'✅' if deps['frontend']['installed'] else '❌'}")
        if deps["frontend"]["missing"]:
            print(f"      缺失: {', '.join(deps['frontend']['missing'])}")
        print(f"   后端: {'✅' if deps['backend']['installed'] else '❌'}")
        if deps["backend"]["missing"]:
            print(f"      缺失: {', '.join(deps['backend']['missing'])}")
        print(f"   Playwright: {'✅' if deps['playwright']['browsers'] else '❌'}")

        # 服务状态
        services = self.results["services"]
        print("\n🌐 服务状态:")
        for service_name, service_info in services.items():
            status = service_info["status"]
            response_time = service_info.get("response_time")
            time_info = f" ({response_time}ms)" if response_time else ""
            status_icon = "✅" if status == "running" else "❌"
            print(f"   {service_name.title()}: {status_icon} {status}{time_info}")

        # 测试配置
        tests = self.results["tests"]
        print("\n🧪 测试配置:")
        print(f"   Playwright配置: {'✅' if tests['playwright_config'] else '❌'}")
        print(f"   页面对象: {'✅' if tests['page_objects'] else '❌'}")
        print(f"   测试助手: {'✅' if tests['test_helpers'] else '❌'}")
        print(f"   全局设置: {'✅' if tests['global_setup'] else '❌'}")

        # Mock数据
        mock_data = self.results.get("mock_data", {})
        if mock_data:
            print("\n📊 Mock数据系统:")
            print(f"   覆盖率: {mock_data.get('coverage', 'Unknown')}")
            existing = sum(1 for f in mock_data.get("mock_files", []) if f["exists"])
            total = len(mock_data.get("mock_files", []))
            print(f"   文件: {existing}/{total}")

        # 建议
        print("\n💡 建议:")
        if self.results["overall_status"] in ["critical", "poor"]:
            print("   • 请先安装缺失的依赖")
            print("   • 检查项目结构是否完整")
            print("   • 运行安装脚本")
        elif self.results["overall_status"] == "fair":
            print("   • 完善缺失的测试文件")
            print("   • 启动缺失的服务")
        elif self.results["overall_status"] == "good":
            print("   • 测试环境基本就绪，可以运行测试")
            print("   • 考虑优化性能配置")
        else:
            print("   • 测试环境完全就绪，可以开始测试")

        print("\n" + "=" * 80)

    def save_report(self, file_path: Optional[str] = None):
        """保存报告到文件"""
        if file_path is None:
            file_path = (
                self.project_root / "test-results" / "environment-check-report.json"
            )

        # 确保目录存在
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存JSON报告
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"📄 报告已保存到: {file_path}")


def main():
    """主函数"""
    print("🔍 MyStocks 测试环境状态检查工具")
    print("生成时间: 2025-11-14")
    print()

    checker = TestEnvironmentChecker()

    try:
        # 生成报告
        results = checker.generate_report()

        # 打印报告
        checker.print_report()

        # 保存报告
        checker.save_report()

        # 返回适当的退出码
        if results["overall_status"] in ["excellent", "good"]:
            sys.exit(0)  # 成功
        elif results["overall_status"] == "fair":
            sys.exit(1)  # 警告
        else:
            sys.exit(2)  # 错误

    except KeyboardInterrupt:
        print("\n\n⚠️ 检查被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 检查过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
