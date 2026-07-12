#!/usr/bin/env python3
"""硬编码密钥检查脚本
检查代码中是否存在硬编码的密钥、密码等敏感信息
"""

import re
import sys
from pathlib import Path


def check_hardcoded_secrets():
    """检查硬编码密钥"""
    print("🔑 硬编码密钥检查...")

    violations = []
    src_path = Path("src")

    # 敏感信息模式
    secret_patterns = [
        # API密钥
        (r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "API密钥"),
        (r'secret[_-]?key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "密钥"),
        (r'access[_-]?token\s*=\s*["\'][a-zA-Z0-9\-_]{20,}["\']', "访问令牌"),
        # 数据库凭据
        (r'password\s*=\s*["\'][^"\'\s]{8,}["\']', "数据库密码"),
        (r'passwd\s*=\s*["\'][^"\'\s]{8,}["\']', "数据库密码"),
        (r'pwd\s*=\s*["\'][^"\'\s]{8,}["\']', "数据库密码"),
        # 加密密钥
        (r'encryption[_-]?key\s*=\s*["\'][a-zA-Z0-9+/]{32,}["\']', "加密密钥"),
        (r'signature[_-]?key\s*=\s*["\'][a-zA-Z0-9+/]{32,}["\']', "签名密钥"),
        # JWT密钥
        (r'jwt[_-]?secret\s*=\s*["\'][a-zA-Z0-9+/]{32,}["\']', "JWT密钥"),
        # 其他敏感信息
        (r'private[_-]?key\s*=\s*["\'][a-zA-Z0-9+/]{32,}["\']', "私钥"),
        (r'certificate\s*=\s*["\'][a-zA-Z0-9+/]{64,}["\']', "证书"),
    ]

    python_files = list(src_path.rglob("*.py"))
    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()

                    # 跳过注释行
                    if line_stripped.startswith("#"):
                        continue

                    # 检查敏感信息模式
                    for pattern, description in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append(
                                {
                                    "file": str(file_path),
                                    "line": i,
                                    "line_content": line.strip(),
                                    "violation": f"硬编码{description}",
                                    "severity": "critical",
                                },
                            )

        except Exception as e:
            print(f"⚠️  读取文件 {file_path} 时出错: {e}")

    # 输出检查结果
    print("\n📊 硬编码密钥检查结果:")
    print(f"   检查文件数: {len(python_files)}")
    print(f"   发现违规: {len(violations)}")

    if violations:
        print("\n❌ 硬编码密钥详情:")
        for violation in violations:
            print(f"   📁 {violation['file']}:{violation['line']}")
            print(f"   🔴 {violation['severity']}: {violation['violation']}")
            print(f"   💬 {violation['line_content']}")
            print()
    else:
        print("✅ 未发现硬编码密钥")

    return len(violations) == 0


if __name__ == "__main__":
    success = check_hardcoded_secrets()
    sys.exit(0 if success else 1)
