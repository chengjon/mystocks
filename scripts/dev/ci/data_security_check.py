#!/usr/bin/env python3
"""
MyStocks 数据安全检查脚本
检查量化交易平台的数据安全配置和潜在风险
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DataSecurityChecker:
    """数据安全检查器"""

    def __init__(self):
        self.project_root = project_root
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def log_issue(
        self,
        severity: str,
        category: str,
        message: str,
        file: str = "",
        line: int = 0,
        suggestion: str = "",
    ):
        """记录安全问题"""
        issue = {
            "severity": severity,
            "category": category,
            "message": message,
            "file": file,
            "line": line,
            "suggestion": suggestion,
        }

        if severity == "high" or severity == "critical":
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

    def check_sensitive_data_leakage(self):
        """检查敏感数据泄露"""
        print("🔍 检查敏感数据泄露...")

        # 敏感信息模式
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^$][^"\']*["\']', "硬编码密码"),
            (r'secret\s*=\s*["\'][^$][^"\']*["\']', "硬编码密钥"),
            (r'api_key\s*=\s*["\'][^$][^"\']*["\']', "硬编码API密钥"),
            (r'token\s*=\s*["\'][^$][^"\']*["\']', "硬编码令牌"),
            (r'private_key\s*=\s*["\'][^$][^"\']*["\']', "硬编码私钥"),
        ]

        # 排除的文件和目录
        exclude_patterns = [
            r"__pycache__",
            r"\.git",
            r"tests/",
            r"\.env\.example",
            r"config/secrets\.template\.py",
            r"docs/",
        ]

        for root, dirs, files in os.walk(self.project_root):
            # 跳过排除的目录
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    re.search(pattern, os.path.join(root, d))
                    for pattern in exclude_patterns
                )
            ]

            for file in files:
                if not file.endswith((".py", ".js", ".ts", ".json", ".yaml", ".yml")):
                    continue

                filepath = os.path.join(root, file)

                # 跳过排除的文件
                if any(re.search(pattern, filepath) for pattern in exclude_patterns):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern, description in sensitive_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.log_issue(
                                    "critical",
                                    "敏感数据泄露",
                                    f"{description}: {line.strip()[:100]}...",
                                    filepath,
                                    line_num,
                                    "使用环境变量或配置文件管理敏感数据",
                                )
                except Exception as e:
                    print(f"⚠️ 无法检查文件 {filepath}: {e}")

    def check_sql_injection_risks(self):
        """检查SQL注入风险"""
        print("🔍 检查SQL注入风险...")

        sql_injection_patterns = [
            (r"SELECT.*%s.*%s", "字符串格式化SQL查询"),
            (r"INSERT.*%s.*%s", "字符串格式化SQL插入"),
            (r"UPDATE.*%s.*%s", "字符串格式化SQL更新"),
            (r"DELETE.*%s.*%s", "字符串格式化SQL删除"),
            (r"\.format\(.*sql", "format()格式化SQL"),
            (r'f".*SELECT.*\{.*\}"', "f-string SQL查询"),
            (r'f".*INSERT.*\{.*\}"', "f-string SQL插入"),
            (r'f".*UPDATE.*\{.*\}"', "f-string SQL更新"),
            (r'f".*DELETE.*\{.*\}"', "f-string SQL删除"),
        ]

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if not file.endswith(".py"):
                    continue

                filepath = os.path.join(root, file)

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    for pattern, description in sql_injection_patterns:
                        matches = re.findall(
                            pattern, content, re.IGNORECASE | re.DOTALL
                        )
                        if matches:
                            for match in matches[:3]:  # 只报告前3个匹配
                                self.log_issue(
                                    "high",
                                    "SQL注入风险",
                                    f"{description}: {match[:100]}...",
                                    filepath,
                                    0,
                                    "使用参数化查询或ORM框架",
                                )
                except Exception as e:
                    print(f"⚠️ 无法检查文件 {filepath}: {e}")

    def check_encryption_configuration(self):
        """检查加密配置"""
        print("🔍 检查加密配置...")

        # 检查配置文件
        config_files = [
            "src/core/config.py",
            "web/backend/app/core/config.py",
            "config/database.yaml",
            "config/security.yaml",
        ]

        encryption_found = False

        for config_file in config_files:
            filepath = self.project_root / config_file
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 检查加密相关配置
                    if re.search(r"encryption|encrypt|cipher", content, re.IGNORECASE):
                        encryption_found = True
                        print(f"✅ 发现加密配置: {config_file}")
                        break
                except Exception as e:
                    print(f"⚠️ 无法检查配置文件 {config_file}: {e}")

        if not encryption_found:
            self.log_issue(
                "medium",
                "加密配置缺失",
                "未发现数据加密配置",
                "",
                0,
                "配置数据加密，特别是敏感的交易数据和用户密码",
            )

    def check_access_control(self):
        """检查访问控制配置"""
        print("🔍 检查访问控制配置...")

        # 检查认证配置
        auth_indicators = [
            "JWT",
            "jwt",
            "auth",
            "authentication",
            "login",
            "session",
            "token",
            "oauth",
        ]

        cors_indicators = ["CORS", "cors", "cross_origin"]

        auth_found = False
        cors_found = False

        # 检查主要配置文件
        config_files = [
            "src/core/config.py",
            "web/backend/app/core/config.py",
            "config/auth.yaml",
            "config/security.yaml",
        ]

        for config_file in config_files:
            filepath = self.project_root / config_file
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if any(indicator in content for indicator in auth_indicators):
                        auth_found = True
                        print(f"✅ 发现认证配置: {config_file}")

                    if any(indicator in content for indicator in cors_indicators):
                        cors_found = True
                        print(f"✅ 发现CORS配置: {config_file}")

                except Exception as e:
                    print(f"⚠️ 无法检查配置文件 {config_file}: {e}")

        if not auth_found:
            self.log_issue(
                "high",
                "认证配置缺失",
                "未发现用户认证配置",
                "",
                0,
                "配置JWT或其他认证机制",
            )

        if not cors_found:
            self.log_issue(
                "low",
                "CORS配置缺失",
                "未发现CORS跨域配置",
                "",
                0,
                "配置适当的CORS策略以支持前端访问",
            )

    def check_data_validation(self):
        """检查数据验证"""
        print("🔍 检查数据验证配置...")

        # 检查量化策略数据验证
        strategy_files = list(self.project_root.glob("src/strategies/**/*.py"))

        validation_found = False

        for strategy_file in strategy_files:
            try:
                with open(strategy_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 检查数据验证相关代码
                if re.search(
                    r"validate|validation|check|verify", content, re.IGNORECASE
                ):
                    validation_found = True
                    break
            except Exception as e:
                continue

        if not validation_found:
            self.log_issue(
                "medium",
                "数据验证缺失",
                "量化策略缺少数据验证逻辑",
                "",
                0,
                "添加数据输入验证，防止无效数据影响策略计算",
            )

    def generate_report(self) -> Dict[str, Any]:
        """生成安全检查报告"""
        return {
            "summary": {
                "issues_count": len(self.issues),
                "warnings_count": len(self.warnings),
                "total_findings": len(self.issues) + len(self.warnings),
            },
            "issues": self.issues,
            "warnings": self.warnings,
        }

    def run_all_checks(self):
        """运行所有安全检查"""
        print("🚀 开始MyStocks数据安全检查...")
        print("=" * 50)

        self.check_sensitive_data_leakage()
        self.check_sql_injection_risks()
        self.check_encryption_configuration()
        self.check_access_control()
        self.check_data_validation()

        print("=" * 50)

        # 生成报告
        report = self.generate_report()

        if report["summary"]["issues_count"] > 0:
            print(f"❌ 发现 {report['summary']['issues_count']} 个安全问题")
            for issue in report["issues"][:5]:  # 只显示前5个
                print(f"  🔴 {issue['category']}: {issue['message']}")
        else:
            print("✅ 未发现严重安全问题")

        if report["summary"]["warnings_count"] > 0:
            print(f"⚠️ 发现 {report['summary']['warnings_count']} 个警告")
            for warning in report["warnings"][:3]:  # 只显示前3个
                print(f"  🟡 {warning['category']}: {warning['message']}")

        return report


def main():
    """主函数"""
    checker = DataSecurityChecker()
    report = checker.run_all_checks()

    # 如果有严重问题，退出码为1
    if report["summary"]["issues_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
