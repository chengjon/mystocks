#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码策略检查脚本
验证代码中的密码处理是否符合安全策略
"""

import sys
import re
from pathlib import Path


def check_password_policy():
    """检查密码策略合规性"""
    print("🔐 密码策略检查...")

    violations = []
    src_path = Path("src")

    # 密码相关文件模式
    password_patterns = [
        r"password",
        r"passwd",
        r"pwd",
        r"credential",
        r"token",
        r"secret",
        r"hash.*password",
        r"verify.*password",
    ]

    # 检查Python文件
    python_files = list(src_path.rglob("*.py"))
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # 检查密码相关代码
                    for pattern in password_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 检查是否使用了弱哈希算法
                            if re.search(r"md5|sha1|crypt", line, re.IGNORECASE):
                                violations.append(
                                    {
                                        "file": str(file_path),
                                        "line": i,
                                        "line_content": line.strip(),
                                        "violation": "使用弱哈希算法",
                                        "severity": "high",
                                    }
                                )

                            # 检查是否明文存储密码
                            if (
                                "password" in line.lower()
                                and "=" in line
                                and "getenv" not in line
                            ):
                                violations.append(
                                    {
                                        "file": str(file_path),
                                        "line": i,
                                        "line_content": line.strip(),
                                        "violation": "可能明文存储密码",
                                        "severity": "critical",
                                    }
                                )

                            # 检查密码长度验证
                            if "len(password)" in line and "< 8" in line:
                                violations.append(
                                    {
                                        "file": str(file_path),
                                        "line": i,
                                        "line_content": line.strip(),
                                        "violation": "密码长度验证不足",
                                        "severity": "medium",
                                    }
                                )

        except Exception as e:
            print(f"⚠️  读取文件 {file_path} 时出错: {e}")

    # 输出检查结果
    print("\n📊 密码策略检查结果:")
    print(f"   检查文件数: {len(python_files)}")
    print(f"   发现违规: {len(violations)}")

    if violations:
        print("\n❌ 违规详情:")
        for violation in violations:
            print(f"   📁 {violation['file']}:{violation['line']}")
            print(f"   🔴 {violation['severity']}: {violation['violation']}")
            print(f"   💬 {violation['line_content']}")
            print()
    else:
        print("✅ 未发现密码策略违规")

    return len(violations) == 0


if __name__ == "__main__":
    success = check_password_policy()
    sys.exit(0 if success else 1)
