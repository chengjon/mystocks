#!/usr/bin/env python3
"""
MyStocks项目安全扫描器
集成多种安全扫描工具，提供全面的安全检测报告
"""

import os
import sys
import json
import logging
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class SecurityIssue:
    """安全问题数据类"""

    tool: str
    severity: str
    category: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    recommendation: str = ""
    cve_id: Optional[str] = None


@dataclass
class SecurityScanResult:
    """安全扫描结果"""

    scan_time: str
    duration: float
    tools_used: List[str]
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[SecurityIssue]
    summary: Dict[str, Any]


class SecurityScanner:
    """安全扫描器主类"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results_dir = self.project_root / "logs" / "security"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self.setup_logging()

        # 安全问题统计
        self.issues: List[SecurityIssue] = []

    def setup_logging(self):
        """设置日志配置"""
        log_file = (
            self.results_dir
            / f"security_scan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def run_bandit_scan(self) -> List[SecurityIssue]:
        """运行Bandit代码安全静态分析"""
        self.logger.info("🔍 开始Bandit代码安全静态分析...")

        try:
            cmd = [
                "bandit",
                "-r",
                str(self.project_root / "src"),
                "-f",
                "json",
                "--exclude",
                "*/test*,*/tests,*/__pycache__,*/venv/*,*/node_modules/*",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                issues = []

                for issue in data.get("results", []):
                    severity = issue.get("issue_severity", "LOW")
                    confidence = issue.get("issue_confidence", "LOW")

                    issues.append(
                        SecurityIssue(
                            tool="bandit",
                            severity=severity,
                            category=issue.get("test_id", "unknown"),
                            description=issue.get("issue_text", ""),
                            file_path=issue.get("filename", ""),
                            line_number=issue.get("line_number"),
                            recommendation=issue.get("more_info", ""),
                        )
                    )

                self.logger.info(f"✅ Bandit扫描完成，发现 {len(issues)} 个安全问题")
                return issues

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Bandit扫描超时")
        except Exception as e:
            self.logger.error(f"❌ Bandit扫描失败: {e}")

        return []

    def run_safety_scan(self) -> List[SecurityIssue]:
        """运行Safety依赖漏洞扫描"""
        self.logger.info("🔍 开始Safety依赖漏洞扫描...")

        try:
            cmd = ["safety", "check", "--json", "--full-report"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            issues = []
            if result.stdout:
                data = json.loads(result.stdout)

                for vuln in data:
                    severity = (
                        "HIGH"
                        if vuln.get("vulnerability_severity") == "high"
                        else "MEDIUM"
                    )

                    issues.append(
                        SecurityIssue(
                            tool="safety",
                            severity=severity,
                            category="dependency_vulnerability",
                            description=vuln.get("advisory", ""),
                            file_path=f"package:{vuln.get('package_name', '')}",
                            recommendation=vuln.get("recommendation", ""),
                            cve_id=vuln.get("cve"),
                        )
                    )

            self.logger.info(f"✅ Safety扫描完成，发现 {len(issues)} 个依赖漏洞")
            return issues

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Safety扫描超时")
        except Exception as e:
            self.logger.error(f"❌ Safety扫描失败: {e}")

        return []

    def run_pip_audit_scan(self) -> List[SecurityIssue]:
        """运行pip-audit Python包安全审计"""
        self.logger.info("🔍 开始pip-audit Python包安全审计...")

        try:
            cmd = ["pip-audit", "--format=json", "--local"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            issues = []
            if result.stdout:
                data = json.loads(result.stdout)

                for vuln in data.get("vulnerabilities", []):
                    issues.append(
                        SecurityIssue(
                            tool="pip-audit",
                            severity="HIGH",
                            category="dependency_vulnerability",
                            description=vuln.get("description", ""),
                            file_path=f"package:{vuln.get('name', '')}",
                            cve_id=vuln.get("id"),
                        )
                    )

            self.logger.info(f"✅ pip-audit扫描完成，发现 {len(issues)} 个包安全漏洞")
            return issues

        except subprocess.TimeoutExpired:
            self.logger.error("❌ pip-audit扫描超时")
        except Exception as e:
            self.logger.error(f"❌ pip-audit扫描失败: {e}")

        return []

    def check_sensitive_files(self) -> List[SecurityIssue]:
        """检查敏感文件"""
        self.logger.info("🔍 检查敏感文件...")

        sensitive_patterns = [
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            ".env*",
            "config.json",
            "secrets.yml",
            "id_rsa*",
            "id_dsa*",
            "*.p8",
        ]

        sensitive_files = []
        for pattern in sensitive_patterns:
            sensitive_files.extend(self.project_root.rglob(pattern))

        issues = []
        for file_path in sensitive_files:
            if not any(
                skip in str(file_path)
                for skip in ["node_modules", "__pycache__", ".git"]
            ):
                issues.append(
                    SecurityIssue(
                        tool="file_check",
                        severity="HIGH",
                        category="sensitive_file",
                        description=f"发现敏感文件: {file_path.name}",
                        file_path=str(file_path),
                        recommendation="敏感文件不应提交到版本控制系统",
                    )
                )

        self.logger.info(f"✅ 敏感文件检查完成，发现 {len(issues)} 个敏感文件")
        return issues

    def analyze_input_validation(self) -> List[SecurityIssue]:
        """分析输入验证机制"""
        self.logger.info("🔍 分析输入验证机制...")

        issues = []

        # 检查FastAPI路由中的输入验证
        api_dir = self.project_root / "src" / "api"
        if api_dir.exists():
            for py_file in api_dir.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 检查是否使用了Pydantic模型
                    if "BaseModel" not in content and "pydantic" not in content.lower():
                        issues.append(
                            SecurityIssue(
                                tool="validation_check",
                                severity="MEDIUM",
                                category="input_validation",
                                description=f"API文件缺少输入验证模型: {py_file.name}",
                                file_path=str(py_file),
                                recommendation="建议使用Pydantic模型进行输入验证",
                            )
                        )

                except Exception as e:
                    self.logger.warning(f"无法分析文件 {py_file}: {e}")

        self.logger.info(f"✅ 输入验证分析完成，发现 {len(issues)} 个验证问题")
        return issues

    def run_comprehensive_scan(self) -> SecurityScanResult:
        """运行综合安全扫描"""
        self.logger.info("🚀 开始MyStocks项目综合安全扫描...")
        start_time = datetime.datetime.now()

        # 并行执行各种扫描
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.run_bandit_scan): "bandit",
                executor.submit(self.run_safety_scan): "safety",
                executor.submit(self.run_pip_audit_scan): "pip_audit",
                executor.submit(self.check_sensitive_files): "file_check",
            }

            all_issues = []
            completed_tools = []

            for future in as_completed(futures):
                tool_name = futures[future]
                try:
                    issues = future.result()
                    all_issues.extend(issues)
                    completed_tools.append(tool_name)
                    self.logger.info(f"✅ {tool_name} 扫描完成")
                except Exception as e:
                    self.logger.error(f"❌ {tool_name} 扫描失败: {e}")
                    completed_tools.append(f"{tool_name}_failed")

        # 手动运行输入验证分析
        validation_issues = self.analyze_input_validation()
        all_issues.extend(validation_issues)
        completed_tools.append("validation_check")

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 统计问题严重性
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in all_issues:
            if issue.severity.upper() in severity_counts:
                severity_counts[issue.severity.upper()] += 1
            else:
                severity_counts["LOW"] += 1

        # 生成扫描结果
        result = SecurityScanResult(
            scan_time=start_time.isoformat(),
            duration=duration,
            tools_used=completed_tools,
            total_issues=len(all_issues),
            critical_issues=severity_counts["CRITICAL"],
            high_issues=severity_counts["HIGH"],
            medium_issues=severity_counts["MEDIUM"],
            low_issues=severity_counts["LOW"],
            issues=all_issues,
            summary={
                "scan_status": "completed",
                "tools_successfully_run": len(
                    [t for t in completed_tools if "_failed" not in t]
                ),
                "total_tools": 5,
                "average_severity": "HIGH"
                if severity_counts["HIGH"] > 0
                else "MEDIUM"
                if severity_counts["MEDIUM"] > 0
                else "LOW",
            },
        )

        # 保存结果
        self.save_results(result)

        self.logger.info(f"🎯 安全扫描完成，总计发现 {len(all_issues)} 个安全问题")
        self.logger.info(
            f"   - 严重: {result.critical_issues}, 高: {result.high_issues}, 中: {result.medium_issues}, 低: {result.low_issues}"
        )

        return result

    def save_results(self, result: SecurityScanResult):
        """保存扫描结果"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON格式保存
        json_file = self.results_dir / f"security_scan_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False, default=str)

        # HTML报告生成
        html_file = self.results_dir / f"security_report_{timestamp}.html"
        self.generate_html_report(result, html_file)

        self.logger.info(f"📊 安全扫描报告已保存到: {json_file}")

    def generate_html_report(self, result: SecurityScanResult, output_file: Path):
        """生成HTML格式的安全报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MyStocks 安全扫描报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #3498db; color: white; padding: 15px 20px; border-radius: 5px; text-align: center; flex: 1; }}
        .critical {{ background: #e74c3c; }}
        .high {{ background: #e67e22; }}
        .medium {{ background: #f39c12; }}
        .low {{ background: #27ae60; }}
        .issue {{ margin: 15px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }}
        .issue.critical {{ border-left-color: #e74c3c; }}
        .issue.high {{ border-left-color: #e67e22; }}
        .issue.medium {{ border-left-color: #f39c12; }}
        .issue.low {{ border-left-color: #27ae60; }}
        .tool {{ font-size: 0.9em; color: #7f8c8d; }}
        .recommendation {{ margin-top: 10px; font-style: italic; color: #34495e; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 MyStocks 项目安全扫描报告</h1>

        <div class="summary">
            <h2>📊 扫描概览</h2>
            <p><strong>扫描时间:</strong> {result.scan_time}</p>
            <p><strong>扫描时长:</strong> {result.duration:.2f} 秒</p>
            <p><strong>使用工具:</strong> {", ".join(result.tools_used)}</p>
        </div>

        <div class="stats">
            <div class="stat critical">
                <h3>🔴 严重</h3>
                <div style="font-size: 2em;">{result.critical_issues}</div>
            </div>
            <div class="stat high">
                <h3>🟠 高危</h3>
                <div style="font-size: 2em;">{result.high_issues}</div>
            </div>
            <div class="stat medium">
                <h3>🟡 中危</h3>
                <div style="font-size: 2em;">{result.medium_issues}</div>
            </div>
            <div class="stat low">
                <h3>🟢 低危</h3>
                <div style="font-size: 2em;">{result.low_issues}</div>
            </div>
        </div>

        <h2>🔍 详细安全问题</h2>
"""

        for issue in result.issues:
            severity_class = issue.severity.lower()
            html_content += f"""
        <div class="issue {severity_class}">
            <h3>{issue.category} - {issue.severity}</h3>
            <p><strong>工具:</strong> <span class="tool">{issue.tool}</span></p>
            <p><strong>描述:</strong> {issue.description}</p>
            <p><strong>文件:</strong> {issue.file_path}</p>
            {f"<p><strong>行号:</strong> {issue.line_number}</p>" if issue.line_number else ""}
            {f"<p><strong>CVE:</strong> {issue.cve_id}</p>" if issue.cve_id else ""}
            {f'<div class="recommendation"><strong>建议:</strong> {issue.recommendation}</div>' if issue.recommendation else ""}
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"📄 HTML安全报告已生成: {output_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks项目安全扫描器")
    parser.add_argument("--project-root", help="项目根目录路径")
    parser.add_argument("--output-dir", help="输出目录")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # 创建扫描器并运行
    scanner = SecurityScanner(args.project_root)

    try:
        result = scanner.run_comprehensive_scan()

        # 输出结果摘要
        if not args.quiet:
            print("\n" + "=" * 60)
            print("🔒 MyStocks 项目安全扫描完成")
            print("=" * 60)
            print(f"扫描时间: {result.scan_time}")
            print(f"扫描时长: {result.duration:.2f} 秒")
            print(f"总问题数: {result.total_issues}")
            print(f"  - 严重: {result.critical_issues}")
            print(f"  - 高危: {result.high_issues}")
            print(f"  - 中危: {result.medium_issues}")
            print(f"  - 低危: {result.low_issues}")
            print(f"使用工具: {', '.join(result.tools_used)}")
            print("=" * 60)

        # 设置退出代码
        if result.critical_issues > 0 or result.high_issues > 0:
            sys.exit(1)  # 有高危问题，退出代码为1

    except KeyboardInterrupt:
        print("\n⚠️  安全扫描被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 安全扫描失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
