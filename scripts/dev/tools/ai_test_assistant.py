#!/usr/bin/env python3
"""MyStocks AI测试助手集成模块
Phase 4.2: 实施AI助手集成优化

功能：
- 配置AI助手访问测试结果和日志
- 实现智能化错误诊断和建议生成
- 创建测试优化推荐机制

作者：Claude Code Assistant
日期：2026-01-18
"""

import glob
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """测试结果数据类"""

    phase: str
    test_type: str
    status: str
    duration: float
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime
    file_path: str


@dataclass
class DiagnosticResult:
    """诊断结果数据类"""

    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    root_cause: str
    suggestions: List[str]
    confidence: float  # 0.0 to 1.0


@dataclass
class OptimizationRecommendation:
    """优化推荐数据类"""

    category: str
    priority: str
    title: str
    description: str
    impact: str
    effort: str
    implementation_steps: List[str]


class AITestAssistant:
    """AI测试助手主类"""

    def __init__(self, project_root: str = None):
        """初始化AI测试助手

        Args:
            project_root: 项目根目录路径，默认自动检测

        """
        if project_root is None:
            project_root = self._find_project_root()

        self.project_root = Path(project_root)
        self.test_reports_dir = self.project_root / "test-reports"
        self.logs_dir = self.project_root / "var" / "log"
        self.scripts_dir = self.project_root / "scripts"

        # 确保目录存在
        self.test_reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # 诊断规则配置
        self.diagnostic_rules = self._load_diagnostic_rules()

        logger.info(f"AI测试助手初始化完成，项目根目录: {self.project_root}")

    def _find_project_root(self) -> Path:
        """自动查找项目根目录"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "CLAUDE.md").exists() or (current / "README.md").exists():
                return current
            current = current.parent
        return Path.cwd()  # 回退到当前目录

    def _load_diagnostic_rules(self) -> Dict[str, Any]:
        """加载诊断规则配置"""
        return {
            # 端口相关错误
            "port_conflicts": {
                "patterns": [
                    r"端口 (\d+) 已被占用",
                    r"Port (\d+) is already in use",
                    r"Address already in use.*:(\d+)",
                ],
                "severity": "high",
                "category": "environment",
            },
            # 服务启动失败
            "service_failures": {
                "patterns": [
                    r"后端服务.*启动.*失败",
                    r"前端服务.*启动.*失败",
                    r"Backend service.*failed to start",
                    r"Frontend service.*failed to start",
                ],
                "severity": "critical",
                "category": "service",
            },
            # ESM相关错误
            "esm_errors": {
                "patterns": [r"does not provide an export named", r"ESM import.*failed", r"Cannot resolve module.*esm"],
                "severity": "high",
                "category": "compatibility",
            },
            # API测试失败
            "api_failures": {
                "patterns": [r"API.*failed", r"HTTP.*[45]\d{2}", r"Connection refused", r"Timeout"],
                "severity": "medium",
                "category": "api",
            },
            # 性能问题
            "performance_issues": {
                "patterns": [r"测试执行时间.*超时", r"Performance.*degraded", r"Slow.*response.*time"],
                "severity": "medium",
                "category": "performance",
            },
        }

    def collect_test_results(self) -> List[TestResult]:
        """收集所有测试结果

        Returns:
            测试结果列表

        """
        results = []

        # 收集不同类型的测试结果
        result_patterns = {
            "esm": "**/esm-validation*.log",
            "environment": "**/start-environment*.log",
            "schemathesis": "**/schemathesis*.json",
            "playwright": "**/playwright*.json",
            "performance": "**/performance*.json",
            "orchestration": "**/orchestration*.log",
        }

        for test_type, pattern in result_patterns.items():
            for file_path in glob.glob(str(self.test_reports_dir / pattern), recursive=True):
                result = self._parse_test_result(file_path, test_type)
                if result:
                    results.append(result)

        # 按时间戳排序
        results.sort(key=lambda x: x.timestamp, reverse=True)

        logger.info(f"收集到 {len(results)} 个测试结果")
        return results

    def _parse_test_result(self, file_path: str, test_type: str) -> Optional[TestResult]:
        """解析单个测试结果文件"""
        try:
            file_path = Path(file_path)

            # 提取Phase信息从文件路径或内容
            phase = self._extract_phase_from_path(file_path)

            # 读取文件内容
            if file_path.suffix == ".json":
                with open(file_path, encoding="utf-8") as f:
                    content = json.load(f)
                status = content.get("status", "unknown")
                duration = content.get("duration", 0)
                errors = content.get("errors", [])
                warnings = content.get("warnings", [])
                metrics = content.get("metrics", {})
            else:
                # 日志文件处理
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # 分析日志内容
                status, duration, errors, warnings, metrics = self._analyze_log_content(content)

            # 提取时间戳
            timestamp = self._extract_timestamp_from_file(file_path)

            return TestResult(
                phase=phase,
                test_type=test_type,
                status=status,
                duration=duration,
                errors=errors,
                warnings=warnings,
                metrics=metrics,
                timestamp=timestamp,
                file_path=str(file_path),
            )

        except Exception as e:
            logger.warning(f"解析测试结果失败 {file_path}: {e}")
            return None

    def _extract_phase_from_path(self, file_path: Path) -> str:
        """从文件路径提取Phase信息"""
        path_str = str(file_path)
        phase_match = re.search(r"phase[_-](\d+)", path_str, re.IGNORECASE)
        if phase_match:
            return f"phase_{phase_match.group(1)}"

        # 从文件名或内容推断
        if "esm" in path_str.lower():
            return "phase_0"
        if "environment" in path_str.lower():
            return "phase_1"
        if "schemathesis" in path_str.lower():
            return "phase_2"
        if "playwright" in path_str.lower():
            return "phase_3"
        if "orchestration" in path_str.lower():
            return "phase_4"
        if "performance" in path_str.lower():
            return "phase_5"

        return "unknown"

    def _analyze_log_content(self, content: str) -> Tuple[str, float, List[str], List[str], Dict[str, Any]]:
        """分析日志文件内容"""
        status = "unknown"
        duration = 0.0
        errors = []
        warnings = []
        metrics = {}

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 状态判断
            if "✅" in line or "SUCCESS" in line or "成功" in line:
                if status == "unknown":
                    status = "passed"
            elif "❌" in line or "ERROR" in line or "失败" in line:
                status = "failed"
            elif "⚠️" in line or "WARN" in line or "警告" in line:
                if status != "failed":
                    status = "warning"

            # 错误信息提取
            if "ERROR" in line or "❌" in line or "失败" in line:
                errors.append(line)

            # 警告信息提取
            if "WARN" in line or "⚠️" in line or "警告" in line:
                warnings.append(line)

            # 时间信息提取
            duration_match = re.search(r"耗时[:\s]+([\d.]+)s", line)
            if duration_match:
                duration = float(duration_match.group(1))

        return status, duration, errors, warnings, metrics

    def _extract_timestamp_from_file(self, file_path: Path) -> datetime:
        """从文件名提取时间戳"""
        filename = file_path.name

        # 尝试匹配时间戳格式
        timestamp_patterns = [
            r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})",  # YYYYMMDD_HHMMSS
            r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})",  # ISO格式
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if len(match.groups()) == 6:
                        year, month, day, hour, minute, second = map(int, match.groups())
                        return datetime(year, month, day, hour, minute, second)
                except ValueError:
                    continue

        # 默认使用文件修改时间
        return datetime.fromtimestamp(file_path.stat().st_mtime)

    def diagnose_issues(self, test_results: List[TestResult]) -> List[DiagnosticResult]:
        """基于测试结果进行智能诊断

        Args:
            test_results: 测试结果列表

        Returns:
            诊断结果列表

        """
        diagnostics = []

        for result in test_results:
            # 分析错误信息
            for error in result.errors:
                diagnostic = self._analyze_error(error, result)
                if diagnostic:
                    diagnostics.append(diagnostic)

            # 分析警告信息
            for warning in result.warnings:
                diagnostic = self._analyze_warning(warning, result)
                if diagnostic:
                    diagnostics.append(diagnostic)

            # 分析性能指标
            if result.metrics:
                perf_diagnostics = self._analyze_performance(result)
                diagnostics.extend(perf_diagnostics)

        # 去重和排序
        seen = set()
        unique_diagnostics = []
        for diag in diagnostics:
            key = (diag.issue_type, diag.description)
            if key not in seen:
                seen.add(key)
                unique_diagnostics.append(diag)

        unique_diagnostics.sort(
            key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity],
            reverse=True,
        )

        logger.info(f"生成 {len(unique_diagnostics)} 个诊断结果")
        return unique_diagnostics

    def _analyze_error(self, error: str, result: TestResult) -> Optional[DiagnosticResult]:
        """分析单个错误信息"""
        for rule_name, rule_config in self.diagnostic_rules.items():
            patterns = rule_config["patterns"]
            severity = rule_config["severity"]
            category = rule_config["category"]

            for pattern in patterns:
                if re.search(pattern, error, re.IGNORECASE):
                    return DiagnosticResult(
                        issue_type=rule_name,
                        severity=severity,
                        description=f"检测到{category}问题: {error[:100]}...",
                        root_cause=self._get_root_cause(rule_name, error),
                        suggestions=self._get_suggestions(rule_name, result),
                        confidence=0.8,
                    )

        # 通用错误处理
        return DiagnosticResult(
            issue_type="general_error",
            severity="medium",
            description=f"未知错误: {error[:100]}...",
            root_cause="无法确定具体原因",
            suggestions=["检查详细日志文件", "查看系统资源使用情况", "尝试重新运行测试"],
            confidence=0.5,
        )

    def _analyze_warning(self, warning: str, result: TestResult) -> Optional[DiagnosticResult]:
        """分析警告信息"""
        return DiagnosticResult(
            issue_type="warning",
            severity="low",
            description=f"警告信息: {warning[:100]}...",
            root_cause="系统警告，可能影响稳定性",
            suggestions=["监控相关指标", "考虑优化配置", "检查日志趋势"],
            confidence=0.6,
        )

    def _analyze_performance(self, result: TestResult) -> List[DiagnosticResult]:
        """分析性能指标"""
        diagnostics = []

        # 检查执行时间
        if result.duration > 300:  # 超过5分钟
            diagnostics.append(
                DiagnosticResult(
                    issue_type="slow_execution",
                    severity="medium",
                    description=f"{result.phase}执行时间过长: {result.duration:.1f}秒",
                    root_cause="可能存在性能瓶颈或资源不足",
                    suggestions=["检查系统资源使用情况", "优化测试配置", "考虑并行执行", "分析性能瓶颈"],
                    confidence=0.7,
                ),
            )

        return diagnostics

    def _get_root_cause(self, rule_name: str, error: str) -> str:
        """根据规则获取根本原因"""
        causes = {
            "port_conflicts": "端口被其他进程占用或上一次测试未正确清理",
            "service_failures": "服务依赖未满足或配置错误",
            "esm_errors": "ESM模块导入配置不正确或依赖版本冲突",
            "api_failures": "API服务未启动或网络配置问题",
            "performance_issues": "系统资源不足或测试配置不优",
        }
        return causes.get(rule_name, "未知原因")

    def _get_suggestions(self, rule_name: str, result: TestResult) -> List[str]:
        """根据规则获取修复建议"""
        suggestions_map = {
            "port_conflicts": [
                "运行 'pkill -f \"vite|uvicorn\"' 清理残留进程",
                "检查端口占用: 'lsof -i :端口号'",
                "修改配置文件中的端口设置",
                "使用 'pm2 kill' 停止所有PM2进程",
            ],
            "service_failures": [
                "检查服务依赖是否已安装",
                "验证配置文件正确性",
                "查看详细错误日志",
                "尝试手动启动服务进行调试",
            ],
            "esm_errors": [
                "检查Vite配置中的optimizeDeps设置",
                "验证dayjs版本是否支持ESM",
                "更新相关依赖包",
                "检查import语句语法",
            ],
            "api_failures": ["确保后端服务已启动", "检查API端点URL配置", "验证网络连接", "查看API服务器日志"],
            "performance_issues": ["增加系统内存或CPU资源", "优化测试并发配置", "减少测试数据量", "使用性能分析工具"],
        }
        return suggestions_map.get(rule_name, ["查看详细日志", "联系技术支持"])

    def generate_optimization_recommendations(
        self,
        test_results: List[TestResult],
        diagnostics: List[DiagnosticResult],
    ) -> List[OptimizationRecommendation]:
        """生成测试优化推荐

        Args:
            test_results: 测试结果列表
            diagnostics: 诊断结果列表

        Returns:
            优化推荐列表

        """
        recommendations = []

        # 基于测试结果分析
        failed_phases = [r.phase for r in test_results if r.status == "failed"]
        if failed_phases:
            recommendations.append(
                OptimizationRecommendation(
                    category="reliability",
                    priority="high",
                    title="修复失败的测试阶段",
                    description=f"以下测试阶段存在失败: {', '.join(set(failed_phases))}",
                    impact="提高测试成功率和系统稳定性",
                    effort="medium",
                    implementation_steps=[
                        "分析失败原因和错误模式",
                        "修复配置或代码问题",
                        "添加错误处理和重试机制",
                        "更新测试脚本和配置",
                    ],
                ),
            )

        # 基于诊断结果分析
        error_categories = {}
        for diag in diagnostics:
            error_categories[diag.issue_type] = error_categories.get(diag.issue_type, 0) + 1

        if error_categories.get("port_conflicts", 0) > 0:
            recommendations.append(
                OptimizationRecommendation(
                    category="environment",
                    priority="high",
                    title="优化端口管理",
                    description="检测到多次端口冲突，影响测试稳定性",
                    impact="减少环境相关失败，提高测试效率",
                    effort="low",
                    implementation_steps=[
                        "实现自动端口清理脚本",
                        "添加端口占用检查和等待机制",
                        "优化PM2进程管理配置",
                        "使用随机端口分配策略",
                    ],
                ),
            )

        if error_categories.get("performance_issues", 0) > 0:
            recommendations.append(
                OptimizationRecommendation(
                    category="performance",
                    priority="medium",
                    title="性能优化",
                    description="测试执行时间过长，存在性能瓶颈",
                    impact="加快测试执行速度，提高开发效率",
                    effort="medium",
                    implementation_steps=[
                        "分析性能瓶颈（CPU、内存、网络）",
                        "优化测试配置和并发设置",
                        "实现测试结果缓存",
                        "考虑分布式测试执行",
                    ],
                ),
            )

        # 通用优化建议
        recommendations.extend(
            [
                OptimizationRecommendation(
                    category="monitoring",
                    priority="medium",
                    title="增强测试监控",
                    description="添加更详细的测试指标收集和可视化",
                    impact="更好地理解测试表现和问题趋势",
                    effort="low",
                    implementation_steps=["集成测试指标收集", "添加Grafana仪表板", "实现告警机制", "生成测试报告"],
                ),
                OptimizationRecommendation(
                    category="automation",
                    priority="low",
                    title="提高自动化程度",
                    description="减少手动干预，增加测试流程自动化",
                    impact="降低人工成本，提高一致性",
                    effort="medium",
                    implementation_steps=["实现自动环境清理", "添加智能重试机制", "优化CI/CD集成", "创建一键测试脚本"],
                ),
            ],
        )

        # 按优先级排序
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: priority_order[x.priority], reverse=True)

        logger.info(f"生成 {len(recommendations)} 个优化推荐")
        return recommendations

    def generate_report(self, output_file: str = None) -> str:
        """生成完整的AI助手分析报告

        Args:
            output_file: 输出文件路径，如果为None则返回字符串

        Returns:
            分析报告内容

        """
        logger.info("开始生成AI助手分析报告...")

        # 收集测试结果
        test_results = self.collect_test_results()

        # 进行诊断分析
        diagnostics = self.diagnose_issues(test_results)

        # 生成优化推荐
        recommendations = self.generate_optimization_recommendations(test_results, diagnostics)

        # 生成报告
        report = self._format_report(test_results, diagnostics, recommendations)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"分析报告已保存到: {output_file}")
        else:
            logger.info("分析报告生成完成")

        return report

    def _format_report(
        self,
        test_results: List[TestResult],
        diagnostics: List[DiagnosticResult],
        recommendations: List[OptimizationRecommendation],
    ) -> str:
        """格式化分析报告"""
        report_lines = []

        # 报告头部
        report_lines.append("# AI测试助手分析报告")
        report_lines.append("")
        report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**测试结果数量**: {len(test_results)}")
        report_lines.append(f"**诊断问题数量**: {len(diagnostics)}")
        report_lines.append(f"**优化建议数量**: {len(recommendations)}")
        report_lines.append("")

        # 测试结果摘要
        report_lines.append("## 测试结果摘要")
        report_lines.append("")

        status_counts = {}
        for result in test_results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        for status, count in status_counts.items():
            status_icon = {"passed": "✅", "failed": "❌", "warning": "⚠️", "unknown": "❓"}.get(status, "❓")
            report_lines.append(f"- {status_icon} {status}: {count} 个")

        report_lines.append("")

        # 详细测试结果
        report_lines.append("## 详细测试结果")
        report_lines.append("")

        for result in test_results[:10]:  # 只显示最近10个
            report_lines.append(f"### {result.phase} - {result.test_type}")
            report_lines.append(f"- **状态**: {result.status}")
            report_lines.append(f"- **耗时**: {result.duration:.1f}秒")
            report_lines.append(f"- **时间**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if result.errors:
                report_lines.append(f"- **错误**: {len(result.errors)} 个")
            if result.warnings:
                report_lines.append(f"- **警告**: {len(result.warnings)} 个")
            report_lines.append("")

        # 诊断结果
        if diagnostics:
            report_lines.append("## 诊断结果")
            report_lines.append("")

            severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

            for diag in diagnostics[:10]:  # 只显示前10个
                icon = severity_icons.get(diag.severity, "⚪")
                report_lines.append(f"### {icon} {diag.issue_type} ({diag.severity})")
                report_lines.append(f"**描述**: {diag.description}")
                report_lines.append(f"**根本原因**: {diag.root_cause}")
                report_lines.append("**建议**:")
                for suggestion in diag.suggestions[:3]:  # 只显示前3个建议
                    report_lines.append(f"  - {suggestion}")
                report_lines.append(f"**置信度**: {diag.confidence:.1%}")
                report_lines.append("")

        # 优化推荐
        if recommendations:
            report_lines.append("## 优化推荐")
            report_lines.append("")

            priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            for rec in recommendations[:10]:  # 只显示前10个
                icon = priority_icons.get(rec.priority, "⚪")
                report_lines.append(f"### {icon} {rec.title} ({rec.category})")
                report_lines.append(f"**描述**: {rec.description}")
                report_lines.append(f"**影响**: {rec.impact}")
                report_lines.append(f"**难度**: {rec.effort}")
                report_lines.append("**实施步骤**:")
                for step in rec.implementation_steps[:5]:  # 只显示前5个步骤
                    report_lines.append(f"  - {step}")
                report_lines.append("")

        # 总结
        report_lines.append("## 总结")
        report_lines.append("")
        report_lines.append("此报告由AI测试助手自动生成，基于测试结果的智能分析。")
        report_lines.append("建议优先处理高优先级的诊断问题和优化推荐。")

        return "\n".join(report_lines)


def main():
    """主函数，用于命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks AI测试助手")
    parser.add_argument("--project-root", help="项目根目录路径")
    parser.add_argument("--output", "-o", help="输出报告文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 初始化AI助手
        assistant = AITestAssistant(args.project_root)

        # 生成分析报告
        report = assistant.generate_report(args.output)

        if not args.output:
            print(report)

        print("\n🎉 AI测试助手分析完成!")
        print("建议查看生成的报告以了解测试问题和优化建议。")

    except Exception as e:
        logger.error(f"AI助手执行失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()
