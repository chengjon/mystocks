#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档一致性验证脚本
验证所有关键文档与代码实现的一致性

验证项:
1. 数据分类总数 (应为23, 不是34)
2. 数据库类型 (仅TDengine和PostgreSQL)
3. TDengine路由 (应为3项)
4. PostgreSQL路由 (应为20项)
5. 无MySQL/Redis引用
6. 环境变量配置正确
"""

import os
import re
from typing import Dict, List, Tuple


# 颜色输出
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}\n")


def print_pass(msg: str):
    """打印通过信息"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_fail(msg: str):
    """打印失败信息"""
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def read_file_safely(filepath: str) -> str:
    """安全读取文件内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print_fail(f"文件不存在: {filepath}")
        return ""
    except Exception as e:
        print_fail(f"读取文件失败 {filepath}: {e}")
        return ""


def check_data_classification_count(
    content: str, filename: str
) -> Tuple[bool, List[str]]:
    """检查数据分类数量声明"""
    issues = []

    # 检查是否有错误的34项声明
    patterns_34 = [
        r"34\s*项.*数据分类",
        r"34\s*种.*数据分类",
        r"数据分类.*34",
        r"共\s*34\s*项",
    ]

    for pattern in patterns_34:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append("发现错误的34项数据分类声明 (应为23项)")
            break

    # 检查是否有正确的23项声明
    has_correct_count = False
    patterns_23 = [
        r"23\s*项.*数据分类",
        r"23\s*种.*数据分类",
        r"数据分类.*23",
        r"共\s*23\s*项",
    ]

    for pattern in patterns_23:
        if re.search(pattern, content, re.IGNORECASE):
            has_correct_count = True
            break

    return len(issues) == 0, issues


def check_database_types(content: str, filename: str) -> Tuple[bool, List[str]]:
    """检查数据库类型声明"""
    issues = []

    # 对于历史总结文档，跳过MySQL/Redis检查（这些文档专门记录迁移历史）
    historical_docs = [
        "T037_COMPLETION_SUMMARY.md",
        "MIGRATION_SUMMARY.md",
        "CHANGELOG.md",
        "T037_CRITICAL_FINDING.md",
    ]
    if any(doc in filename for doc in historical_docs):
        # 历史文档允许提及被移除的组件
        return True, []

    # 检查是否有MySQL引用 (应移除)
    mysql_patterns = [
        r"MySQL\s*数据库",
        r"pymysql",
        r"MYSQL_HOST",
        r"mysql_access",
        r"MySQLDataAccess",
    ]

    for pattern in mysql_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            # 排除说明已移除的情况
            if not re.search(
                r"(已移除|removed|废弃|deprecated|迁移|migrated).*" + pattern,
                content,
                re.IGNORECASE,
            ):
                if not re.search(
                    pattern + r".*(已移除|removed|废弃|deprecated|迁移|migrated)",
                    content,
                    re.IGNORECASE,
                ):
                    issues.append(f"发现MySQL引用: {pattern}")
                    break

    # 检查是否有Redis引用 (应移除)
    redis_patterns = [
        r"Redis\s*数据库",
        r"redis\.Redis",
        r"REDIS_HOST",
        r"redis_access",
        r"RedisDataAccess",
    ]

    for pattern in redis_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            # 排除说明已移除的情况
            if not re.search(
                r"(已移除|removed|废弃|deprecated).*" + pattern, content, re.IGNORECASE
            ):
                if not re.search(
                    pattern + r".*(已移除|removed|废弃|deprecated)",
                    content,
                    re.IGNORECASE,
                ):
                    issues.append(f"发现Redis引用: {pattern}")
                    break

    # 检查应有TDengine和PostgreSQL引用
    has_tdengine = bool(re.search(r"TDengine", content))
    has_postgresql = bool(re.search(r"PostgreSQL", content))

    # 对于核心文档,必须同时有两者
    critical_files = [
        "CLAUDE.md",
        "README.md",
        "DATASOURCE_AND_DATABASE_ARCHITECTURE.md",
        "core.py",
        "unified_manager.py",
    ]

    if any(cf in filename for cf in critical_files):
        if not has_tdengine:
            issues.append("缺少TDengine引用")
        if not has_postgresql:
            issues.append("缺少PostgreSQL引用")

    return len(issues) == 0, issues


def check_database_routing(content: str, filename: str) -> Tuple[bool, List[str]]:
    """检查数据库路由声明"""
    issues = []

    # 检查TDengine路由项数 (应为3项)
    tdengine_count_patterns = [
        r"TDengine.*[：:]\s*(\d+)\s*项",
        r"(\d+)\s*项.*TDengine",
        r"TDengine.*\((\d+)项\)",
    ]

    for pattern in tdengine_count_patterns:
        match = re.search(pattern, content)
        if match:
            count = int(match.group(1))
            if count != 3:
                issues.append(f"TDengine路由项数错误: {count} (应为3)")
            break

    # 检查PostgreSQL路由项数 (应为20项)
    postgresql_count_patterns = [
        r"PostgreSQL.*[：:]\s*(\d+)\s*项",
        r"(\d+)\s*项.*PostgreSQL",
        r"PostgreSQL.*\((\d+)项\)",
    ]

    for pattern in postgresql_count_patterns:
        match = re.search(pattern, content)
        if match:
            count = int(match.group(1))
            if count != 20:
                issues.append(f"PostgreSQL路由项数错误: {count} (应为20)")
            break

    return len(issues) == 0, issues


def check_environment_variables(content: str, filename: str) -> Tuple[bool, List[str]]:
    """检查环境变量配置"""
    issues = []

    # 应有的环境变量
    required_vars = {
        "TDengine": [
            "TDENGINE_HOST",
            "TDENGINE_PORT",
            "TDENGINE_USER",
            "TDENGINE_PASSWORD",
            "TDENGINE_DATABASE",
        ],
        "PostgreSQL": [
            "POSTGRESQL_HOST",
            "POSTGRESQL_PORT",
            "POSTGRESQL_USER",
            "POSTGRESQL_PASSWORD",
            "POSTGRESQL_DATABASE",
        ],
    }

    # 不应有的环境变量
    deprecated_vars = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD",
    ]

    # 检查是否有废弃的环境变量
    for var in deprecated_vars:
        # 查找环境变量定义 (排除注释行)
        pattern = r"^[^#]*" + var + r"\s*="
        if re.search(pattern, content, re.MULTILINE):
            issues.append(f"发现废弃的环境变量: {var}")

    return len(issues) == 0, issues


def validate_document(filepath: str) -> Dict:
    """验证单个文档"""
    filename = os.path.basename(filepath)
    print(f"\n{Colors.BOLD}正在验证: {filename}{Colors.ENDC}")

    content = read_file_safely(filepath)
    if not content:
        return {
            "filename": filename,
            "passed": False,
            "total_checks": 0,
            "passed_checks": 0,
            "issues": ["文件无法读取"],
        }

    all_issues = []
    checks = []

    # 检查1: 数据分类数量
    passed, issues = check_data_classification_count(content, filename)
    checks.append(("数据分类数量", passed, issues))

    # 检查2: 数据库类型
    passed, issues = check_database_types(content, filename)
    checks.append(("数据库类型", passed, issues))

    # 检查3: 数据库路由
    passed, issues = check_database_routing(content, filename)
    checks.append(("数据库路由", passed, issues))

    # 检查4: 环境变量 (仅对配置文件)
    if filename in [".env.example", "deployment/README.md", "CLAUDE.md"]:
        passed, issues = check_environment_variables(content, filename)
        checks.append(("环境变量", passed, issues))

    # 汇总结果
    for check_name, passed, issues in checks:
        if passed:
            print_pass(f"{check_name}: 通过")
        else:
            print_fail(f"{check_name}: 失败")
            for issue in issues:
                print(f"  - {issue}")
            all_issues.extend(issues)

    total_checks = len(checks)
    passed_checks = sum(1 for _, passed, _ in checks if passed)

    return {
        "filename": filename,
        "passed": len(all_issues) == 0,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "issues": all_issues,
    }


def main():
    """主函数"""
    print_section("MyStocks 文档一致性验证")

    # 定义要验证的10个关键文档
    documents = [
        "CLAUDE.md",
        "README.md",
        "DATASOURCE_AND_DATABASE_ARCHITECTURE.md",
        "core.py",
        "unified_manager.py",
        "data_access/__init__.py",
        ".env.example",
        "docs/HOW_TO_ADD_NEW_DATA_CLASSIFICATION.md",
        "docs/deployment/README.md",
        "T037_COMPLETION_SUMMARY.md",
    ]

    results = []

    # 验证每个文档
    for doc in documents:
        filepath = os.path.join("/opt/claude/mystocks_spec", doc)
        result = validate_document(filepath)
        results.append(result)

    # 打印汇总报告
    print_section("验证汇总报告")

    total_docs = len(results)
    passed_docs = sum(1 for r in results if r["passed"])
    failed_docs = total_docs - passed_docs

    print(f"总文档数: {total_docs}")
    print(f"通过文档: {passed_docs} {Colors.GREEN}✅{Colors.ENDC}")
    print(f"失败文档: {failed_docs} {Colors.RED}❌{Colors.ENDC}")
    print(f"通过率: {passed_docs / total_docs * 100:.1f}%")

    # 详细结果
    print_section("详细验证结果")

    for result in results:
        status = (
            f"{Colors.GREEN}✅ PASS{Colors.ENDC}"
            if result["passed"]
            else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
        )
        print(
            f"{result['filename']:50s} {status}  ({result['passed_checks']}/{result['total_checks']})"
        )

        if not result["passed"]:
            for issue in result["issues"]:
                print(f"  {Colors.RED}• {issue}{Colors.ENDC}")

    # 生成验证报告文件
    print_section("生成验证报告")

    report_path = "/opt/claude/mystocks_spec/docs/DOCUMENTATION_VALIDATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 文档一致性验证报告\n\n")
        f.write(f"**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## 验证摘要\n\n")
        f.write(f"- 总文档数: {total_docs}\n")
        f.write(f"- 通过文档: {passed_docs} ✅\n")
        f.write(f"- 失败文档: {failed_docs} ❌\n")
        f.write(f"- 通过率: {passed_docs / total_docs * 100:.1f}%\n\n")

        f.write("## 详细结果\n\n")
        f.write("| 文档 | 状态 | 通过检查 | 总检查 | 问题 |\n")
        f.write("|------|------|----------|--------|------|\n")

        for result in results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            issues_str = "; ".join(result["issues"][:2]) if result["issues"] else "-"
            if len(result["issues"]) > 2:
                issues_str += "..."
            f.write(
                f"| {result['filename']} | {status} | {result['passed_checks']} | {result['total_checks']} | {issues_str} |\n"
            )

        f.write("\n## 验证标准\n\n")
        f.write("1. **数据分类数量**: 应为23项 (不是34项)\n")
        f.write("2. **数据库类型**: 仅TDengine和PostgreSQL (无MySQL/Redis)\n")
        f.write("3. **数据库路由**: TDengine 3项, PostgreSQL 20项\n")
        f.write("4. **环境变量**: 仅TDengine和PostgreSQL配置\n\n")

        if failed_docs > 0:
            f.write("## 需要修复的问题\n\n")
            for result in results:
                if not result["passed"]:
                    f.write(f"### {result['filename']}\n\n")
                    for issue in result["issues"]:
                        f.write(f"- {issue}\n")
                    f.write("\n")

        f.write("---\n\n")
        f.write("**验证完成** ✅\n")

    print_pass(f"验证报告已生成: {report_path}")

    # 返回状态码
    return 0 if passed_docs == total_docs else 1


if __name__ == "__main__":
    from datetime import datetime

    exit(main())
