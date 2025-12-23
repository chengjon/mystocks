#!/usr/bin/env python3
"""
环境变量安全验证脚本
验证所有必需的安全配置项是否已正确设置
"""

import os
import sys
from pathlib import Path


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    检查密码强度

    Args:
        password: 要检查的密码

    Returns:
        tuple: (是否通过, 错误信息)
    """
    if not password or password == "":
        return False, "密码不能为空"

    if len(password) < 12:
        return False, "密码长度必须至少12个字符"

    # 检查是否包含大小写字母、数字和特殊字符
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    missing_requirements = []
    if not has_upper:
        missing_requirements.append("大写字母")
    if not has_lower:
        missing_requirements.append("小写字母")
    if not has_digit:
        missing_requirements.append("数字")
    if not has_special:
        missing_requirements.append("特殊字符")

    if missing_requirements:
        return False, f"密码必须包含: {', '.join(missing_requirements)}"

    return True, "密码强度符合要求"


def validate_environment() -> tuple[bool, list[str]]:
    """
    验证环境变量配置

    Returns:
        tuple: (是否通过, 错误列表)
    """
    errors = []

    # 定义必需的环境变量
    required_vars = {
        "POSTGRESQL_HOST": "PostgreSQL主机地址",
        "POSTGRESQL_PORT": "PostgreSQL端口",
        "POSTGRESQL_USER": "PostgreSQL用户名",
        "POSTGRESQL_PASSWORD": "PostgreSQL密码",
        "JWT_SECRET_KEY": "JWT密钥",
    }

    # 检查必需的环境变量
    for var_name, description in required_vars.items():
        value = os.getenv(var_name, "")
        if not value or value == "":
            errors.append(f"缺少必需的环境变量: {var_name} ({description})")
        elif var_name == "POSTGRESQL_PASSWORD":
            is_strong, message = check_password_strength(value)
            if not is_strong:
                errors.append(f"{description}强度不足: {message}")

    # 检查JWT密钥强度
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret and len(jwt_secret) < 32:
        errors.append("JWT密钥长度不足，建议至少32个字符")

    # 检查管理员密码强度
    admin_password = os.getenv("ADMIN_INITIAL_PASSWORD", "")
    if admin_password:
        is_strong, message = check_password_strength(admin_password)
        if not is_strong:
            errors.append(f"管理员初始密码强度不足: {message}")

    # 检查是否使用了默认或弱密码
    weak_passwords = ["admin123", "password", "123456", "qwerty", "letmein"]
    for var_name in ["POSTGRESQL_PASSWORD", "ADMIN_INITIAL_PASSWORD"]:
        password = os.getenv(var_name, "")
        if password.lower() in weak_passwords:
            errors.append(f"{var_name}使用了弱密码，请设置更强的密码")

    # 检查数据库端口是否使用默认端口
    db_port = os.getenv("POSTGRESQL_PORT", "5432")
    if db_port == "5432":
        errors.append("建议更改PostgreSQL默认端口(5432)以提高安全性")

    return len(errors) == 0, errors


def generate_security_report():
    """生成安全配置报告"""
    print("=" * 60)
    print("MyStocks 环境安全配置报告")
    print("=" * 60)

    # 检查环境变量
    is_valid, errors = validate_environment()

    if is_valid:
        print("✅ 所有安全配置检查通过！")
    else:
        print("❌ 发现以下安全配置问题：")
        print()
        for error in errors:
            print(f"  • {error}")
        print()

    # 显示当前配置
    print("\n当前环境变量配置：")
    print("-" * 40)

    # 显示配置的环境变量
    config_vars = [
        "POSTGRESQL_HOST",
        "POSTGRESQL_PORT",
        "POSTGRESQL_USER",
        "POSTGRESQL_PASSWORD",
        "POSTGRESQL_DATABASE",
        "MONITOR_DB_HOST",
        "MONITOR_DB_USER",
        "MONITOR_DB_PASSWORD",
        "JWT_SECRET_KEY",
        "ADMIN_INITIAL_PASSWORD",
    ]

    for var in config_vars:
        value = os.getenv(var, "")
        if value:
            # 隐藏敏感信息
            if "password" in var.lower() or "secret" in var.lower():
                masked = (
                    "*" * max(8, len(value) - 4) + value[-4:]
                    if len(value) > 4
                    else "*" * len(value)
                )
                print(f"  {var}: {masked}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: [未设置]")

    print()

    # 生成建议
    print("安全建议：")
    print("-" * 40)
    print("1. 定期轮换数据库密码和JWT密钥")
    print("2. 启用数据库连接的SSL/TLS加密")
    print("3. 使用防火墙限制数据库访问")
    print("4. 启用API访问日志和监控")
    print("5. 定期备份重要配置")
    print("6. 遵循最小权限原则分配数据库用户权限")

    print("\n" + "=" * 60)

    return is_valid


if __name__ == "__main__":
    # 设置环境变量路径
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path)
        print(f"✅ 已加载环境变量文件: {env_path}")

    # 生成报告并检查是否通过
    is_valid = generate_security_report()

    sys.exit(0 if is_valid else 1)
