#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL注入防护检查脚本
检查代码中是否存在SQL注入风险
"""

import sys
import re
from pathlib import Path


def check_sql_injection():
    """检查SQL注入防护"""
    print("🛡️  SQL注入防护检查...")

    violations = []
    src_path = Path("src")

    # 危险的模式
    dangerous_patterns = [
        # 字符串格式化SQL
        (r"cursor\.execute\(f.*SELECT.*WHERE.*\{.*\}", "f-string SQL查询"),
        (r'cursor\.execute\(".*SELECT.*WHERE.*\%s', "百分号格式化SQL查询"),
        (r'cursor\.execute\(".*SELECT.*WHERE.*format\(', "format()方法SQL查询"),
        # 直接拼接SQL
        (r"SELECT.*\+.*WHERE", "SQL字符串拼接"),
        (r"INSERT.*\+.*VALUES", "SQL字符串拼接"),
        (r"UPDATE.*\+.*SET", "SQL字符串拼接"),
        # 危险的execute调用
        (r"execute\(.*\+.*\)", "execute中使用+拼接"),
        # 原生SQL查询
        (r"raw_sql|execute_raw", "原生SQL查询"),
    ]

    safe_patterns = [
        r"execute\s*\([^)]*%s[^)]*\)",  # 参数化查询
        r"execute\s*\([^)]*\?[^)]*\)",  # 问号参数
        r"execute\s*\([^)]*\$[0-9]+[^)]*\)",  # 美元符号参数
        r"sql\.SQL",  # psycopg2的SQL类
        r"query.*=.*select",  # ORM查询
        r"SelectQuery",  # 查询构建器
    ]

    python_files = list(src_path.rglob("*.py"))
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    line_lower = line.lower()

                    # 检查危险模式
                    for pattern, description in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 排除安全模式
                            is_safe = False
                            for safe_pattern in safe_patterns:
                                if re.search(safe_pattern, line, re.IGNORECASE):
                                    is_safe = True
                                    break

                            if not is_safe:
                                violations.append(
                                    {
                                        "file": str(file_path),
                                        "line": i,
                                        "line_content": line.strip(),
                                        "violation": f"SQL注入风险: {description}",
                                        "severity": "critical",
                                    }
                                )

        except Exception as e:
            print(f"⚠️  读取文件 {file_path} 时出错: {e}")

    # 输出检查结果
    print("\n📊 SQL注入防护检查结果:")
    print(f"   检查文件数: {len(python_files)}")
    print(f"   发现风险: {len(violations)}")

    if violations:
        print("\n❌ SQL注入风险详情:")
        for violation in violations:
            print(f"   📁 {violation['file']}:{violation['line']}")
            print(f"   🔴 {violation['severity']}: {violation['violation']}")
            print(f"   💬 {violation['line_content']}")
            print()
    else:
        print("✅ 未发现SQL注入风险")

    return len(violations) == 0


if __name__ == "__main__":
    success = check_sql_injection()
    sys.exit(0 if success else 1)
