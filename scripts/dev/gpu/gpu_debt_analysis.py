#!/usr/bin/env python3
"""GPU加速引擎技术债务分析工具
分析现有GPU代码库的技术债务问题，确定重构优先级
"""

import ast
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# 添加项目根路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def analyze_gpu_codebase_structure():
    """分析GPU代码库结构"""
    print("🔍 分析GPU代码库结构...")

    gpu_directories = [
        "src/gpu",
        "src/gpu/accelerated",
        "src/gpu/api_system",
        "src/gpu/api_system/services",
        "src/gpu/api_system/tests",
    ]

    structure_analysis = {}

    for gpu_dir in gpu_directories:
        if os.path.exists(gpu_dir):
            files = []
            for root, dirs, filenames in os.walk(gpu_dir):
                for filename in filenames:
                    if filename.endswith(".py"):
                        filepath = os.path.join(root, filename)
                        relative_path = os.path.relpath(filepath, gpu_dir)
                        files.append(relative_path)

            structure_analysis[gpu_dir] = {
                "exists": True,
                "file_count": len(files),
                "files": files,
            }
        else:
            structure_analysis[gpu_dir] = {
                "exists": False,
                "file_count": 0,
                "files": [],
            }

    return structure_analysis


def analyze_technical_debt_issues(file_path: str) -> Dict[str, Any]:
    """分析单个文件的技术债务问题"""
    issues = {
        "file_path": file_path,
        "lines": 0,
        "complexity_issues": [],
        "maintainability_issues": [],
        "performance_issues": [],
        "security_issues": [],
        "documentation_issues": [],
        "error_handling_issues": [],
    }

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            issues["lines"] = len(lines)

            # 分析技术债务问题
            issues.update(identify_issues_by_type(content, lines, file_path))

    except Exception as e:
        issues["read_error"] = str(e)

    return issues


def identify_issues_by_type(
    content: str,
    lines: List[str],
    file_path: str,
) -> Dict[str, Any]:
    """识别各类技术债务问题"""
    issues = {
        "complexity_issues": [],
        "maintainability_issues": [],
        "performance_issues": [],
        "security_issues": [],
        "documentation_issues": [],
        "error_handling_issues": [],
    }

    # 1. 复杂度问题
    issues["complexity_issues"].extend(
        analyze_complexity_issues(content, lines, file_path),
    )

    # 2. 可维护性问题
    issues["maintainability_issues"].extend(
        analyze_maintainability_issues(content, lines, file_path),
    )

    # 3. 性能问题
    issues["performance_issues"].extend(
        analyze_performance_issues(content, lines, file_path),
    )

    # 4. 安全问题
    issues["security_issues"].extend(analyze_security_issues(content, lines, file_path))

    # 5. 文档问题
    issues["documentation_issues"].extend(
        analyze_documentation_issues(content, lines, file_path),
    )

    # 6. 错误处理问题
    issues["error_handling_issues"].extend(
        analyze_error_handling_issues(content, lines, file_path),
    )

    return issues


def analyze_complexity_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析代码复杂度问题"""
    complexity_issues = []

    # 长函数
    for i, line in enumerate(lines, 1):
        if len(line.strip()) > 150:
            complexity_issues.append(
                {
                    "type": "long_line",
                    "severity": "medium",
                    "line": i,
                    "description": f"代码行过长 ({len(line)} 字符)",
                    "suggestion": "将长行拆分为多行",
                },
            )

    # 复杂函数定义
    if "def " in content:
        complexity_issues.extend(analyze_function_complexity(content, file_path))

    # 深层嵌套
    complexity_issues.extend(analyze_nesting_complexity(content, lines, file_path))

    # 复杂表达式
    complexity_issues.extend(analyze_expression_complexity(content, lines, file_path))

    return complexity_issues


def analyze_function_complexity(content: str, file_path: str) -> List[Dict[str, Any]]:
    """分析函数复杂度"""
    function_issues = []

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数复杂度
                complexity = calculate_cyclomatic_complexity(node)

                if complexity > 10:
                    severity = "high" if complexity > 20 else "medium"
                    function_issues.append(
                        {
                            "type": "complex_function",
                            "severity": severity,
                            "function": node.name,
                            "line": node.lineno,
                            "complexity": complexity,
                            "description": f"函数复杂度过高 ({complexity})",
                            "suggestion": "考虑拆分函数或简化逻辑",
                        },
                    )

                # 检查参数数量
                args_count = len(node.args.args) + len(node.args.defaults)
                if args_count > 7:
                    function_issues.append(
                        {
                            "type": "too_many_parameters",
                            "severity": "medium",
                            "function": node.name,
                            "line": node.lineno,
                            "parameters": args_count,
                            "description": f"函数参数过多 ({args_count})",
                            "suggestion": "考虑使用配置对象或数据类",
                        },
                    )

    except Exception:
        # 如果AST解析失败，使用简单方法
        function_count = content.count("def ")
        if function_count > 10:
            function_issues.append(
                {
                    "type": "too_many_functions",
                    "severity": "medium",
                    "file": file_path,
                    "count": function_count,
                    "description": f"文件中函数过多 ({function_count})",
                    "suggestion": "考虑将相关功能组织到类或模块中",
                },
            )

    return function_issues


def analyze_nesting_complexity(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析嵌套复杂度"""
    nesting_issues = []

    max_nesting = 0
    current_nesting = 0

    for i, line in enumerate(lines, 1):
        # 简单的嵌套检测
        open_brackets = line.count("{") + line.count("if ") + line.count("for ") + line.count("while ")
        close_brackets = line.count("}") + line.count("elif ") + line.count(":") * 2  # 简化处理

        current_nesting += open_brackets - close_brackets
        max_nesting = max(max_nesting, current_nesting)

        if current_nesting > 5:
            nesting_issues.append(
                {
                    "type": "deep_nesting",
                    "severity": "high",
                    "line": i,
                    "nesting_level": current_nesting,
                    "description": f"嵌套层次过深 ({current_nesting} 层)",
                    "suggestion": "考虑使用早期返回或提取函数",
                },
            )

    if max_nesting > 3:
        nesting_issues.append(
            {
                "type": "max_nesting_too_deep",
                "severity": "medium",
                "file": file_path,
                "max_nesting": max_nesting,
                "description": f"最大嵌套层次过深 ({max_nesting} 层)",
                "suggestion": "优化代码结构，减少嵌套层次",
            },
        )

    return nesting_issues


def analyze_expression_complexity(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析表达式复杂度"""
    expression_issues = []

    for i, line in enumerate(lines, 1):
        # 检查长表达式
        if len(line) > 120:
            expression_issues.append(
                {
                    "type": "long_expression",
                    "severity": "medium",
                    "line": i,
                    "description": f"表达式过长 ({len(line)} 字符)",
                    "suggestion": "将长表达式拆分为多行或使用中间变量",
                },
            )

        # 检查复杂的链式调用
        if line.count(".") > 5:
            expression_issues.append(
                {
                    "type": "complex_chaining",
                    "severity": "medium",
                    "line": i,
                    "description": f"方法链过长 ({line.count('.')} 个调用)",
                    "suggestion": "考虑使用中间变量存储中间结果",
                },
            )

    return expression_issues


def calculate_cyclomatic_complexity(node: ast.FunctionDef) -> int:
    """计算圈复杂度"""
    complexity = 1  # 基础复杂度

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1

    return complexity


def analyze_maintainability_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析可维护性问题"""
    maintainability_issues = []

    # 硬编码值
    hardcode_patterns = [
        (r"\b[0-9]+", "硬编码二进制数据"),
        (r'"\d{1,2}[/-]\d{2}[/-]\d{4}', "硬编码日期"),
        (r"https?://[^\s\)]+", "硬编码URL"),
        (r"\d+\.\d+\.\d+\.\d+", "硬编码IP地址"),
        (r'password[^"\']*', "硬编码密码"),
        (r"mysql://[^\s\)]+", "硬编码数据库连接"),
    ]

    for pattern, description in hardcode_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            maintainability_issues.append(
                {
                    "type": "hardcoded_value",
                    "severity": "high",
                    "pattern": description,
                    "description": f"发现硬编码值: {description}",
                    "suggestion": "使用配置文件或环境变量",
                },
            )

    # 缺少注释
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

    if code_lines > 0 and comment_lines / code_lines < 0.1:
        maintainability_issues.append(
            {
                "type": "insufficient_comments",
                "severity": "medium",
                "ratio": comment_lines / code_lines,
                "description": f"注释比例过低 ({comment_lines}/{code_lines})",
                "suggestion": "增加代码注释和文档说明",
            },
        )

    # 长类
    class_count = content.count("class ")
    if class_count > 10:
        maintainability_issues.append(
            {
                "type": "too_many_classes",
                "severity": "medium",
                "file": file_path,
                "count": class_count,
                "description": f"类数量过多 ({class_count})",
                "suggestion": "考虑拆分模块或组织相关功能",
            },
        )

    return maintainability_issues


def analyze_performance_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析性能问题"""
    performance_issues = []

    # GPU相关性能问题
    gpu_patterns = [
        (r"cuda\.synchronize\(\)", "同步GPU操作可能阻塞"),
        (r"torch\.cuda\.empty_cache\(\)", "清空缓存可能影响性能"),
        (r"torch\.no_grad\(\)", "禁用梯度可能影响优化"),
        (r"\.cpu\(\)", "频繁的CPU-GPU数据传输"),
        (r"\.cuda\(\)", "频繁的CPU-GPU数据传输"),
        (r"np\.array\(.*\.cuda\(\)\)", "numpy数组GPU转换"),
    ]

    for i, line in enumerate(lines, 1):
        for pattern, description in gpu_patterns:
            if re.search(pattern, line):
                performance_issues.append(
                    {
                        "type": "gpu_performance_issue",
                        "severity": "high",
                        "line": i,
                        "pattern": description,
                        "description": f"GPU性能问题: {description}",
                        "suggestion": "优化GPU操作和内存管理",
                    },
                )

    # 内存泄漏风险
    memory_patterns = [
        (r"global\s+\w+\s*=", "全局变量可能导致内存泄漏"),
        (r"while\s+True:", "无限循环可能导致内存泄漏"),
        (r"\.append\(.*\)", "频繁的append操作"),
    ]

    for i, line in enumerate(lines, 1):
        for pattern, description in memory_patterns:
            if re.search(pattern, line):
                performance_issues.append(
                    {
                        "type": "memory_leak_risk",
                        "severity": "high",
                        "line": i,
                        "pattern": description,
                        "description": f"内存泄漏风险: {description}",
                        "suggestion": "使用内存管理工具或重新设计",
                    },
                )

    return performance_issues


def analyze_security_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析安全问题"""
    security_issues = []

    # SQL注入风险
    if "SELECT" in content or "INSERT" in content or "UPDATE" in content:
        if "execute(" in content and "%" in content:
            security_issues.append(
                {
                    "type": "sql_injection_risk",
                    "severity": "critical",
                    "description": "可能存在SQL注入风险",
                    "suggestion": "使用参数化查询",
                },
            )

    # 硬编码凭证
    credential_patterns = [
        (r'password\s*=\s*[\'"][^\'\']*["\']*', "硬编码密码"),
        (r'api_key\s*=\s*[\'"][^\'\']*["\']*', "硬编码API密钥"),
        (r'token\s*=\s*[\'"][^\'\']*["\']*', "硬编码令牌"),
        (r'secret\s*=\s*[\'"][^\'\']*["\']*', "硬编码密钥"),
    ]

    for pattern, description in credential_patterns:
        if re.search(pattern, content):
            security_issues.append(
                {
                    "type": "hardcoded_credentials",
                    "severity": "critical",
                    "pattern": description,
                    "description": f"安全问题: {description}",
                    "suggestion": "使用环境变量或配置文件",
                },
            )

    # 不安全的文件操作
    if "open(" in content and "w" in content:
        security_issues.append(
            {
                "type": "unsafe_file_operation",
                "severity": "medium",
                "description": "可能存在不安全的文件写入操作",
                "suggestion": "验证文件路径并使用适当的权限",
            },
        )

    return security_issues


def analyze_documentation_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析文档问题"""
    documentation_issues = []

    # 缺少模块文档字符串
    if not content.startswith('"""'):
        documentation_issues.append(
            {
                "type": "missing_module_docstring",
                "severity": "medium",
                "file": file_path,
                "description": "缺少模块级别的文档字符串",
                "suggestion": "添加模块说明和功能概述",
            },
        )

    # 检查类和函数文档
    docstring_count = content.count('"""') + content.count("'''")
    class_count = content.count("class ")
    function_count = content.count("def ")

    if class_count > 0:
        if docstring_count < class_count:
            documentation_issues.append(
                {
                    "type": "insufficient_class_documentation",
                    "severity": "medium",
                    "file": file_path,
                    "classes": class_count,
                    "docstrings": docstring_count,
                    "description": f"类文档不足 ({docstring_count}/{class_count})",
                    "suggestion": "为所有类添加详细的文档字符串",
                },
            )

    return documentation_issues


def analyze_error_handling_issues(
    content: str,
    lines: List[str],
    file_path: str,
) -> List[Dict[str, Any]]:
    """分析错误处理问题"""
    error_handling_issues = []

    # 缺少异常处理
    try_blocks = content.count("try:")
    except_blocks = content.count("except:")

    if try_blocks > 0 and except_blocks == 0:
        error_handling_issues.append(
            {
                "type": "missing_exception_handling",
                "severity": "high",
                "file": file_path,
                "try_blocks": try_blocks,
                "except_blocks": except_blocks,
                "description": f"try块没有对应的except处理 ({try_blocks} 个try块)",
                "suggestion": "添加适当的异常处理逻辑",
            },
        )

    # 宽泛的异常处理
    broad_except_patterns = [
        (r"except:\s*pass\s*$", "空的异常处理"),
        (r"except\s*Exception\s*as\s*e:\s*print", "仅打印异常"),
        (r"except:\s*except\s*Exception:", "过于宽泛的异常捕获"),
    ]

    for pattern, description in broad_except_patterns:
        if re.search(pattern, content):
            error_handling_issues.append(
                {
                    "type": "broad_exception_handling",
                    "severity": "medium",
                    "pattern": description,
                    "description": f"异常处理过于宽泛: {description}",
                    "suggestion": "使用特定的异常类型和适当的处理逻辑",
                },
            )

    return error_handling_issues


def generate_debt_prioritization(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """生成技术债务优先级"""
    priorities = {"high_priority": [], "medium_priority": [], "low_priority": []}

    total_issues = 0
    critical_count = 0
    high_count = 0
    medium_count = 0

    for file_path, file_analysis in analysis_results.items():
        if "read_error" in file_analysis:
            continue

        file_total = 0
        file_critical = 0
        file_high = 0
        file_medium = 0

        for issue_type in [
            "security_issues",
            "performance_issues",
            "complexity_issues",
            "maintainability_issues",
            "error_handling_issues",
        ]:
            issues = file_analysis.get(issue_type, [])
            for issue in issues:
                file_total += 1
                severity = issue.get("severity", "medium")
                if severity == "critical":
                    file_critical += 1
                    critical_count += 1
                elif severity == "high":
                    file_high += 1
                    high_count += 1
                elif severity == "medium":
                    file_medium += 1
                    medium_count += 1

        # 添加到优先级列表
        if file_critical > 0:
            priorities["high_priority"].append(
                {
                    "file": file_path,
                    "severity": "critical",
                    "count": file_critical,
                    "total_issues": file_total,
                    "details": file_analysis,
                },
            )
        elif file_high > 0 or file_total > 10:
            priorities["medium_priority"].append(
                {
                    "file": file_path,
                    "severity": "high",
                    "count": file_high,
                    "total_issues": file_total,
                    "details": file_analysis,
                },
            )
        elif file_medium > 0 or file_total > 5:
            priorities["low_priority"].append(
                {
                    "file": file_path,
                    "severity": "medium",
                    "count": file_medium,
                    "total_issues": file_total,
                    "details": file_analysis,
                },
            )

        total_issues += file_total

    return {
        "total_issues": total_issues,
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "priorities": priorities,
        "analysis_results": analysis_results,
    }


def main():
    """主分析函数"""
    print("=" * 80)
    print("🚀 Phase 6: GPU加速引擎技术债务评估")
    print("=" * 80)

    # 1. 分析GPU代码库结构
    print("\n📊 GPU代码库结构分析...")
    structure_analysis = analyze_gpu_codebase_structure()

    for directory, info in structure_analysis.items():
        if info["exists"]:
            print(f"   {directory}:")
            print(f"     - 文件数量: {info['file_count']}")
            print(f"     - 核心文件: {info['files'][:5]}")  # 显示前5个文件
            if len(info["files"]) > 5:
                print(f"     - 其他文件: {len(info['files']) - 5} 个文件")
        else:
            print(f"   {directory}: ❌ 目录不存在")

    # 2. 分析技术债务
    print("\n🔍 分析GPU技术债务...")
    analysis_results = {}

    for directory, info in structure_analysis.items():
        if info["exists"]:
            for file in info["files"]:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    analysis_results[file_path] = analyze_technical_debt_issues(
                        file_path,
                    )

    # 3. 生成优先级报告
    print("\n📈 生成技术债务优先级报告...")
    prioritization = generate_debt_prioritization(analysis_results)

    # 4. 输出分析结果
    priorities = prioritization["priorities"]
    print("\n📊 GPU技术债务统计:")
    print(f"   总问题数: {prioritization['total_issues']}")
    print(f"   严重问题: {prioritization['critical_count']}")
    print(f"   高优先级: {len(priorities['high_priority'])} 个文件")
    print(f"   中优先级: {len(priorities['medium_priority'])} 个文件")
    print(f"   低优先级: {len(priorities['low_priority'])} 个文件")

    print("\n🎯 高优先级问题:")
    for item in priorities["high_priority"][:5]:
        print(f"   - {item['file']}: {item['count']} 个问题")

    print("\n🔧 建议重构顺序:")
    print("   1. 修复安全问题和性能问题 (Critical + High)")
    print("   2. 重构复杂度过高的模块 (High)")
    print("   3. 优化GPU内存管理和数据传输")
    print("   4. 改善错误处理和日志记录")
    print("   5. 添加和完善文档和注释")

    # 保存分析报告
    import json

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "phase": "6.1",
        "title": "GPU加速引擎技术债务评估",
        "structure_analysis": structure_analysis,
        "prioritization": prioritization,
        "recommendations": [
            "优先处理安全问题和性能瓶颈",
            "重构复杂的GPU计算模块",
            "优化GPU内存管理和数据传输",
            "建立统一的错误处理机制",
            "完善GPU代码的文档和注释",
            "实施GPU性能监控和指标收集",
        ],
    }

    report_path = "docs/reports/gpu_debt_analysis.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n📄 分析报告已保存到: {report_path}")

    print("\n✅ Phase 6.1 GPU加速引擎技术债务评估完成!")
    print("\n🎯 下一步行动:")
    print("   1. 开始 Phase 6.2: GPU加速引擎架构重构")
    print("   2. 根据优先级开始重构高技术债务模块")
    print("   3. 实施GPU性能优化和内存管理改进")
    print("   4. 建立GPU监控和指标收集体系")


if __name__ == "__main__":
    main()
