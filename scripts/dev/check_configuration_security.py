#!/usr/bin/env python3
"""配置安全检查脚本
检查配置文件中的安全设置
"""

import re
import sys
from pathlib import Path

import yaml


def check_configuration_security():
    """检查配置文件安全"""
    print("⚙️  配置安全检查...")

    violations = []
    config_path = Path()

    # 检查的配置文件
    config_files = [
        "config/mystocks_table_config.yaml",
        ".env",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example",
        "config/settings.yaml",
        "config/settings.yml",
    ]

    # 安全配置检查规则
    security_rules = [
        {
            "name": "禁用调试模式",
            "files": ["*.yaml", "*.yml", ".env"],
            "checks": [
                {
                    "pattern": r"DEBUG\s*=\s*true",
                    "severity": "high",
                    "message": "调试模式应该关闭",
                },
                {
                    "pattern": r"debug\s*:\s*true",
                    "severity": "high",
                    "message": "调试模式应该关闭",
                },
            ],
        },
        {
            "name": "使用HTTPS",
            "files": ["*.yaml", "*.yml", "docker-compose.*"],
            "checks": [
                {
                    "pattern": r"protocol\s*:\s*http",
                    "severity": "critical",
                    "message": "应该使用HTTPS",
                },
                {
                    "pattern": r"URL\s*:\s*http://",
                    "severity": "critical",
                    "message": "应该使用HTTPS",
                },
            ],
        },
        {
            "name": "设置超时时间",
            "files": ["*.yaml", "*.yml"],
            "checks": [
                {
                    "pattern": r"timeout\s*:\s*0",
                    "severity": "medium",
                    "message": "超时时间不应该为0",
                },
                {
                    "pattern": r"connect_timeout\s*:\s*0",
                    "severity": "medium",
                    "message": "连接超时时间不应该为0",
                },
            ],
        },
        {
            "name": "限制文件上传大小",
            "files": ["*.yaml", "*.yml"],
            "checks": [
                {
                    "pattern": r"max_file_size\s*:\s*0",
                    "severity": "high",
                    "message": "应该限制文件上传大小",
                },
                {
                    "pattern": r"upload_limit\s*:\s*unlimited",
                    "severity": "high",
                    "message": "应该限制文件上传大小",
                },
            ],
        },
        {
            "name": "设置请求限制",
            "files": ["*.yaml", "*.yml"],
            "checks": [
                {
                    "pattern": r"rate_limit\s*:\s*0",
                    "severity": "medium",
                    "message": "应该设置请求频率限制",
                },
                {
                    "pattern": r"request_limit\s*:\s*0",
                    "severity": "medium",
                    "message": "应该设置请求数量限制",
                },
            ],
        },
    ]

    for config_file in config_files:
        file_path = config_path / config_file
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                    # 根据文件类型选择检查规则
                    file_extension = file_path.suffix.lower()
                    if file_extension in [".yaml", ".yml"]:
                        try:
                            data = yaml.safe_load(content)
                            # 检查YAML中的安全配置
                            if data:
                                if data.get("debug", False):
                                    violations.append(
                                        {
                                            "file": str(file_path),
                                            "line": "N/A",
                                            "line_content": "debug: true",
                                            "violation": "调试模式开启",
                                            "severity": "high",
                                        },
                                    )
                                if data.get("database", {}).get("password"):
                                    violations.append(
                                        {
                                            "file": str(file_path),
                                            "line": "N/A",
                                            "line_content": "database.password: [值]",
                                            "violation": "数据库密码应该使用环境变量",
                                            "severity": "critical",
                                        },
                                    )
                        except yaml.YAMLError:
                            # YAML解析失败，继续文本检查
                            pass

                    # 文本检查
                    for i, line in enumerate(lines, 1):
                        for rule in security_rules:
                            if any(
                                rule["files"].count("*" + ext) > 0
                                for ext in [
                                    file_path.suffix,
                                    file_path.stem if file_path.suffix == ".yml" or file_path.suffix == ".yaml" else "",
                                ]
                            ):
                                for check in rule["checks"]:
                                    if re.search(check["pattern"], line, re.IGNORECASE):
                                        violations.append(
                                            {
                                                "file": str(file_path),
                                                "line": i,
                                                "line_content": line.strip(),
                                                "violation": check["message"],
                                                "severity": check["severity"],
                                            },
                                        )

            except Exception as e:
                print(f"⚠️  读取配置文件 {file_path} 时出错: {e}")

    # 输出检查结果
    print("\n📊 配置安全检查结果:")
    print(
        f"   检查文件数: {len([f for f in config_files if (config_path / f).exists()])}",
    )
    print(f"   发现违规: {len(violations)}")

    if violations:
        print("\n❌ 配置安全违规详情:")
        for violation in violations:
            print(f"   📁 {violation['file']}:{violation['line']}")
            print(f"   🔴 {violation['severity']}: {violation['violation']}")
            print(f"   💬 {violation['line_content']}")
            print()
    else:
        print("✅ 配置文件安全检查通过")

    return len(violations) == 0


if __name__ == "__main__":
    success = check_configuration_security()
    sys.exit(0 if success else 1)
