#!/usr/bin/env python3
"""
MyStocks项目基础安全检查
在没有外部工具依赖的情况下的基础安全检查
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class BasicSecurityChecker:
    """基础安全检查器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.issues = []

    def check_sensitive_files(self) -> List[Dict[str, Any]]:
        """检查敏感文件"""
        issues = []

        # 敏感文件模式
        sensitive_patterns = [
            r"\.env.*",
            r".*\.key$",
            r".*\.pem$",
            r".*\.p12$",
            r".*\.p8$",
            r"config\.json$",
            r"secrets\.yml",
            r"id_rsa.*",
            r"id_dsa.*",
        ]

        for pattern in sensitive_patterns:
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and re.search(
                    pattern, file_path.name, re.IGNORECASE
                ):
                    # 排除已知的安全文件
                    if not any(
                        skip in str(file_path)
                        for skip in ["__pycache__", "node_modules", ".git"]
                    ):
                        issues.append(
                            {
                                "type": "sensitive_file",
                                "file": str(file_path),
                                "pattern": pattern,
                                "severity": "HIGH",
                                "description": f"发现敏感文件模式: {pattern}",
                            }
                        )

        return issues

    def check_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """检查硬编码密钥"""
        issues = []

        # 敏感关键词模式
        secret_patterns = [
            (r'(?i)(password\s*=\s*["\'][^"\']+["\']?)', "hardcoded_password"),
            (r'(?i)(api[_-]?key\s*=\s*["\'][^"\']+["\']?)', "hardcoded_api_key"),
            (r'(?i)(secret[_-]?key\s*=\s*["\'][^"\']+["\']?)', "hardcoded_secret"),
            (r'(?i)(token\s*=\s*["\'][^"\']+["\']?)', "hardcoded_token"),
            (
                r'(?i)(private[_-]?key\s*=\s*["\'][^"\']+["\']?)',
                "hardcoded_private_key",
            ),
        ]

        # 检查Python文件
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, secret_type in secret_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        issues.append(
                            {
                                "type": "hardcoded_secret",
                                "file": str(py_file),
                                "line": line_num,
                                "secret_type": secret_type,
                                "severity": "HIGH",
                                "description": f"发现硬编码敏感信息: {secret_type}",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def check_sql_injection_risks(self) -> List[Dict[str, Any]]:
        """检查SQL注入风险"""
        issues = []

        sql_patterns = [
            r'execute\s*\(\s*["\'][^"\']*\+',  # 直接字符串拼接
            r'cursor\.execute\s*\(\s*f["\']',  # f-string拼接
            r"cursor\.execute\s*\(\s*.*\+",  # 字符串拼接
        ]

        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        issues.append(
                            {
                                "type": "sql_injection",
                                "file": str(py_file),
                                "line": line_num,
                                "severity": "HIGH",
                                "description": "潜在的SQL注入风险",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def check_insecure_random(self) -> List[Dict[str, Any]]:
        """检查不安全的随机数生成"""
        issues = []

        random_patterns = [
            r"import\s+random",
            r"random\.random\(\)",
            r"random\.randint\(",
            r"random\.choice\(",
        ]

        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern in random_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        issues.append(
                            {
                                "type": "insecure_random",
                                "file": str(py_file),
                                "line": line_num,
                                "severity": "MEDIUM",
                                "description": "使用不安全的随机数生成器，建议使用secrets模块",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def check_insecure_network_calls(self) -> List[Dict[str, Any]]:
        """检查不安全的网络调用"""
        issues = []

        insecure_patterns = [
            (r"http://", "insecure_http"),  # 使用HTTP而不是HTTPS
            (r"urllib\.request\.urlopen", "insecure_urlopen"),
            (r"requests\.get\([^)]*verify\s*=\s*False", "disabled_ssl_verification"),
        ]

        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, issue_type in insecure_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        severity = "HIGH" if issue_type == "insecure_http" else "MEDIUM"

                        issues.append(
                            {
                                "type": issue_type,
                                "file": str(py_file),
                                "line": line_num,
                                "severity": severity,
                                "description": f"发现{issue_type.replace('_', ' ')}风险",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def check_insecure_file_operations(self) -> List[Dict[str, Any]]:
        """检查不安全的文件操作"""
        issues = []

        insecure_patterns = [
            (r"os\.system\s*\(", "os_system_call"),
            (r"subprocess\.call\s*\([^)]*shell\s*=\s*True", "shell_injection"),
            (r"exec\s*\(", "code_injection"),
            (r"eval\s*\(", "code_injection"),
        ]

        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, issue_type in insecure_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        issues.append(
                            {
                                "type": issue_type,
                                "file": str(py_file),
                                "line": line_num,
                                "severity": "HIGH",
                                "description": f"发现{issue_type.replace('_', ' ')}风险",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def check_insecure_crypto(self) -> List[Dict[str, Any]]:
        """检查不安全的加密使用"""
        issues = []

        insecure_patterns = [
            (r"import\s+md5", "weak_md5"),
            (r"import\s+sha1", "weak_sha1"),
            (r"hashlib\.md5\(\)", "weak_md5"),
            (r"hashlib\.sha1\(\)", "weak_sha1"),
            (r"DES\(\)", "weak_des"),
            (r"RC4\(\)", "weak_rc4"),
        ]

        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, issue_type in insecure_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        issues.append(
                            {
                                "type": issue_type,
                                "file": str(py_file),
                                "line": line_num,
                                "severity": "MEDIUM",
                                "description": f"使用{issue_type.replace('_', ' ')}弱加密算法",
                                "content": match.group(0),
                            }
                        )

            except Exception:
                continue

        return issues

    def run_basic_security_scan(self) -> Dict[str, Any]:
        """运行基础安全扫描"""
        print("🔍 开始基础安全扫描...")

        all_issues = []

        # 执行各项检查
        check_functions = [
            ("sensitive_files", self.check_sensitive_files),
            ("hardcoded_secrets", self.check_hardcoded_secrets),
            ("sql_injection", self.check_sql_injection_risks),
            ("insecure_random", self.check_insecure_random),
            ("insecure_network_calls", self.check_insecure_network_calls),
            ("insecure_file_operations", self.check_insecure_file_operations),
            ("insecure_crypto", self.check_insecure_crypto),
        ]

        for check_name, check_func in check_functions:
            try:
                issues = check_func()
                all_issues.extend(issues)
                print(f"✅ {check_name}: 发现 {len(issues)} 个问题")
            except Exception as e:
                print(f"❌ {check_name}: 检查失败 - {e}")

        # 统计问题严重性
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in all_issues:
            severity_counts[issue["severity"]] = (
                severity_counts.get(issue["severity"], 0) + 1
            )

        # 生成扫描结果
        result = {
            "scan_time": datetime.now().isoformat(),
            "total_issues": len(all_issues),
            "severity_counts": severity_counts,
            "issues": all_issues,
            "summary": {
                "scan_status": "completed",
                "tools_used": ["basic_security_checker"],
                "average_severity": "HIGH"
                if severity_counts["HIGH"] > 0
                else "MEDIUM"
                if severity_counts["MEDIUM"] > 0
                else "LOW",
            },
        }

        # 保存结果
        self.save_results(result)

        print("\n🎯 基础安全扫描完成")
        print(f"📊 总计发现 {len(all_issues)} 个安全问题")
        print(f"   🔴 严重: {severity_counts['HIGH']}")
        print(f"   🟡 中危: {severity_counts['MEDIUM']}")
        print(f"   🟢 低危: {severity_counts['LOW']}")

        return result

    def save_results(self, result: Dict[str, Any]):
        """保存扫描结果"""
        log_dir = self.project_root / "logs" / "security"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON格式保存
        json_file = log_dir / f"basic_security_scan_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        # 生成简单的HTML报告
        html_file = log_dir / f"basic_security_report_{timestamp}.html"
        self.generate_simple_html_report(result, html_file)

        print("📊 基础安全报告已保存到:")
        print(f"   - JSON: {json_file}")
        print(f"   - HTML: {html_file}")

    def generate_simple_html_report(self, result: Dict[str, Any], output_file: Path):
        """生成简单的HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MyStocks 基础安全扫描报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #3498db; color: white; padding: 15px 20px; border-radius: 5px; text-align: center; flex: 1; }}
        .high {{ background: #e74c3c; }}
        .medium {{ background: #f39c12; }}
        .low {{ background: #27ae60; }}
        .issue {{ margin: 15px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }}
        .issue.high {{ border-left-color: #e74c3c; }}
        .issue.medium {{ border-left-color: #f39c12; }}
        .issue.low {{ border-left-color: #27ae60; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 MyStocks 基础安全扫描报告</h1>

        <div class="stats">
            <div class="stat high">
                <h3>🔴 严重</h3>
                <div style="font-size: 2em;">{result["severity_counts"].get("HIGH", 0)}</div>
            </div>
            <div class="stat medium">
                <h3>🟡 中危</h3>
                <div style="font-size: 2em;">{result["severity_counts"].get("MEDIUM", 0)}</div>
            </div>
            <div class="stat low">
                <h3>🟢 低危</h3>
                <div style="font-size: 2em;">{result["severity_counts"].get("LOW", 0)}</div>
            </div>
        </div>

        <h2>🔍 详细安全问题</h2>
"""

        for issue in result["issues"]:
            severity_class = issue["severity"].lower()
            html_content += f"""
        <div class="issue {severity_class}">
            <h3>{issue["type"].replace("_", " ").title()} - {issue["severity"]}</h3>
            <p><strong>文件:</strong> {issue["file"]}</p>
            {f"<p><strong>行号:</strong> {issue['line']}</p>" if "line" in issue else ""}
            <p><strong>描述:</strong> {issue["description"]}</p>
            {f"<p><strong>代码:</strong> <code>{issue['content']}</code></p>" if "content" in issue else ""}
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks基础安全扫描器")
    parser.add_argument("--project-root", help="项目根目录路径")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    # 创建扫描器并运行
    checker = BasicSecurityChecker(args.project_root)

    try:
        result = checker.run_basic_security_scan()

        # 设置退出代码
        if result["severity_counts"].get("HIGH", 0) > 0:
            sys.exit(1)  # 有高危问题，退出代码为1

    except KeyboardInterrupt:
        print("\n⚠️  安全扫描被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 安全扫描失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
