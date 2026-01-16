#!/usr/bin/env python3
"""
自动化基础设施和代码质量检查脚本
Automated Infrastructure and Code Quality Check Script

执行全面的系统健康检查，包括：
- 基础设施验证（数据库、环境变量、文件权限）
- 代码质量检查（语法错误、导入问题、类型检查）
- 配置一致性验证
- 依赖完整性检查

使用方法：
python scripts/check_system_health.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple


class SystemHealthChecker:
    """系统健康检查器"""

    def __init__(self):
        self.results = {
            "infrastructure": {},
            "code_quality": {},
            "configuration": {},
            "dependencies": {},
        }
        self.errors = []
        self.warnings = []

    def log_error(self, message: str):
        """记录错误"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """记录警告"""
        self.warnings.append(message)
        print(f"⚠️ {message}")

    def log_success(self, message: str):
        """记录成功"""
        print(f"✅ {message}")

    def check_infrastructure(self) -> bool:
        """检查基础设施"""
        print("\n🔧 检查基础设施...")

        success = True

        # 检查Python版本
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.log_success(
                f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}"
            )
        else:
            self.log_error(
                f"Python版本过低: {python_version.major}.{python_version.minor} (需要3.8+)"
            )
            success = False

        # 检查环境变量
        required_env_vars = [
            "POSTGRESQL_HOST",
            "POSTGRESQL_USER",
            "POSTGRESQL_PASSWORD",
            "TDENGINE_HOST",
            "TDENGINE_USER",
            "TDENGINE_PASSWORD",
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log_error(f"缺少环境变量: {', '.join(missing_vars)}")
            success = False
        else:
            self.log_success("所有必需环境变量已配置")

        # 检查数据库连接
        if not self._check_database_connections():
            success = False

        # 检查文件权限
        if not self._check_file_permissions():
            success = False

        # 检查磁盘空间
        if not self._check_disk_space():
            success = False

        self.results["infrastructure"]["overall_success"] = success
        return success

    def _check_database_connections(self) -> bool:
        """检查数据库连接"""
        success = True

        # PostgreSQL连接检查
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=os.getenv("POSTGRESQL_HOST"),
                user=os.getenv("POSTGRESQL_USER"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
                port=os.getenv("POSTGRESQL_PORT", "5438"),
                database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
                connect_timeout=5,
            )
            conn.close()
            self.log_success("PostgreSQL连接正常")
        except Exception as e:
            self.log_error(f"PostgreSQL连接失败: {e}")
            success = False

        # TDengine连接检查 (可选)
        try:
            import taos

            conn = taos.connect(
                host=os.getenv("TDENGINE_HOST", "localhost"),
                user=os.getenv("TDENGINE_USER", "root"),
                password=os.getenv("TDENGINE_PASSWORD", "taosdata"),
                port=int(os.getenv("TDENGINE_PORT", "6030")),
                timeout=5,
            )
            conn.close()
            self.log_success("TDengine连接正常")
        except Exception as e:
            self.log_warning(f"TDengine连接失败 (可选): {e}")

        return success

    def _check_file_permissions(self) -> bool:
        """检查文件权限"""
        success = True

        critical_files = ["src/", "web/backend/", "config/", "scripts/"]

        for path in critical_files:
            if os.path.exists(path):
                if os.access(path, os.R_OK):
                    self.log_success(f"文件权限正常: {path}")
                else:
                    self.log_error(f"文件权限问题: {path}")
                    success = False
            else:
                self.log_warning(f"路径不存在: {path}")

        return success

    def _check_disk_space(self) -> bool:
        """检查磁盘空间"""
        try:
            stat = os.statvfs(".")
            # 可用空间 (GB)
            available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)

            if available_gb > 1:
                self.log_success(f"磁盘可用空间: {available_gb:.2f} GB")
            else:
                self.log_error(f"磁盘空间不足: {available_gb:.2f} GB (需要至少1GB)")
                return False
        except Exception as e:
            self.log_warning(f"无法检查磁盘空间: {e}")

        return True

    def check_code_quality(self) -> bool:
        """检查代码质量"""
        print("\n💻 检查代码质量...")

        success = True

        # 检查语法错误
        if not self._check_syntax_errors():
            success = False

        # 检查导入问题
        if not self._check_imports():
            success = False

        # 检查代码格式 (可选)
        if not self._check_code_formatting():
            success = False

        self.results["code_quality"]["overall_success"] = success
        return success

    def _check_syntax_errors(self) -> bool:
        """检查语法错误"""
        print("  检查语法错误...")

        error_files = []

        # 检查关键目录
        check_dirs = ["src", "web/backend", "scripts"]

        for check_dir in check_dirs:
            if os.path.exists(check_dir):
                for root, dirs, files in os.walk(check_dir):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            try:
                                subprocess.run(
                                    [sys.executable, "-m", "py_compile", file_path],
                                    capture_output=True,
                                    check=True,
                                    timeout=10,
                                )
                            except subprocess.CalledProcessError:
                                error_files.append(file_path)

        if error_files:
            self.log_error(f"发现 {len(error_files)} 个语法错误文件")
            for file in error_files[:5]:  # 只显示前5个
                print(f"    - {file}")
            if len(error_files) > 5:
                print(f"    ... 和其他 {len(error_files) - 5} 个文件")
            return False
        else:
            self.log_success("未发现语法错误")
            return True

    def _check_imports(self) -> bool:
        """检查导入问题"""
        print("  检查导入问题...")

        # 测试关键模块导入
        critical_imports = [
            ("src.core", "from src.core import DataClassification"),
            (
                "database_manager",
                "from src.storage.database import DatabaseTableManager",
            ),
            ("adapters", "from src.adapters.base_adapter import BaseDataSourceAdapter"),
            ("fastapi_app", "from web.backend.app.main import app"),
        ]

        failed_imports = []

        for module_name, import_stmt in critical_imports:
            try:
                # 设置开发模式以跳过数据库
                os.environ["DEVELOPMENT_MODE"] = "true"
                exec(import_stmt)
                self.log_success(f"模块导入成功: {module_name}")
            except Exception as e:
                failed_imports.append((module_name, str(e)))
                self.log_error(f"模块导入失败: {module_name} - {e}")

        return len(failed_imports) == 0

    def _check_code_formatting(self) -> bool:
        """检查代码格式 (可选检查)"""
        print("  检查代码格式...")

        try:
            # 检查是否安装了black
            subprocess.run(["black", "--version"], capture_output=True, check=True)

            # 运行black检查 (不修改文件)
            result = subprocess.run(
                ["black", "--check", "--diff", "src/"], capture_output=True, text=True
            )

            if result.returncode == 0:
                self.log_success("代码格式符合black标准")
                return True
            else:
                self.log_warning("代码格式不符合black标准 (可选择性修复)")
                return True  # 不算错误，只是警告

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_warning("black未安装，跳过格式检查")
            return True

    def check_configuration(self) -> bool:
        """检查配置"""
        print("\n⚙️ 检查配置...")

        success = True

        # 检查YAML配置
        if not self._check_yaml_configs():
            success = False

        # 检查环境变量一致性
        if not self._check_env_consistency():
            success = False

        self.results["configuration"]["overall_success"] = success
        return success

    def _check_yaml_configs(self) -> bool:
        """检查YAML配置文件"""
        import yaml

        config_files = [
            "config/data_sources_registry.yaml",
            "config/table_config.yaml",
        ]

        success = True

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                    self.log_success(f"YAML配置有效: {config_file}")
                except yaml.YAMLError as e:
                    self.log_error(f"YAML配置无效: {config_file} - {e}")
                    success = False
            else:
                self.log_warning(f"配置文件不存在: {config_file}")

        return success

    def _check_env_consistency(self) -> bool:
        """检查环境变量一致性"""
        # 检查数据库配置一致性
        pg_vars = [
            "POSTGRESQL_HOST",
            "POSTGRESQL_USER",
            "POSTGRESQL_PASSWORD",
            "POSTGRESQL_PORT",
        ]
        td_vars = [
            "TDENGINE_HOST",
            "TDENGINE_USER",
            "TDENGINE_PASSWORD",
            "TDENGINE_PORT",
        ]

        pg_configured = all(os.getenv(var) for var in pg_vars)
        td_configured = all(os.getenv(var) for var in td_vars)

        if pg_configured:
            self.log_success("PostgreSQL环境变量完整")
        else:
            self.log_warning("PostgreSQL环境变量不完整")

        if td_configured:
            self.log_success("TDengine环境变量完整")
        else:
            self.log_warning("TDengine环境变量不完整 (可选)")

        return True  # 这不是硬性要求

    def check_dependencies(self) -> bool:
        """检查依赖"""
        print("\n📦 检查依赖...")

        success = True

        # 检查Python包
        required_packages = [
            "pandas",
            "numpy",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "psycopg2",
            "taos",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                self.log_success(f"包可用: {package}")
            except ImportError:
                missing_packages.append(package)
                self.log_error(f"包缺失: {package}")

        if missing_packages:
            success = False

        self.results["dependencies"]["overall_success"] = success
        return success

    def generate_report(self) -> Dict:
        """生成检查报告"""
        total_checks = len(self.results)
        successful_checks = sum(
            1
            for category in self.results.values()
            if category.get("overall_success", False)
        )

        report = {
            "summary": {
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "success_rate": successful_checks / total_checks
                if total_checks > 0
                else 0,
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings),
            },
            "details": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []

        if self.errors:
            recommendations.append("🔴 优先修复错误问题以确保系统稳定")

        if len(self.warnings) > 5:
            recommendations.append("⚠️ 关注警告信息，及时处理潜在问题")

        if not self.results.get("infrastructure", {}).get("overall_success"):
            recommendations.append("🏗️ 完善基础设施配置（数据库连接、环境变量）")

        if not self.results.get("code_quality", {}).get("overall_success"):
            recommendations.append("💻 修复代码质量问题（语法错误、导入问题）")

        if not self.results.get("dependencies", {}).get("overall_success"):
            recommendations.append("📦 安装缺失的Python依赖包")

        return recommendations

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("🚀 开始系统健康检查")
        print("=" * 50)

        # 执行检查
        infra_ok = self.check_infrastructure()
        code_ok = self.check_code_quality()
        config_ok = self.check_configuration()
        deps_ok = self.check_dependencies()

        print("\n" + "=" * 50)
        print("📊 检查结果汇总")

        # 生成报告
        report = self.generate_report()

        print(f"总检查项目: {report['summary']['total_checks']}")
        print(f"成功率: {report['summary']['success_rate']:.1f}")
        print(f"错误数量: {report['summary']['errors_count']}")
        print(f"警告数量: {report['summary']['warnings_count']}")

        if report["recommendations"]:
            print("\n💡 修复建议:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        # 保存详细报告
        report_file = "system_health_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存到: {report_file}")

        overall_success = infra_ok and code_ok and config_ok and deps_ok
        if overall_success:
            print("\n🎉 所有检查通过！系统健康状态良好")
        else:
            print("\n⚠️ 发现问题需要修复，请查看详细报告")

        return overall_success


def main():
    """主函数"""
    checker = SystemHealthChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
