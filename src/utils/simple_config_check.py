#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础配置安全检查

个人项目简化版 - 启动时提醒，不强制退出
"""

import logging
import os

logger = logging.getLogger(__name__)


def check_config_strength():
    """
    检查配置强度，仅警告不强制

    个人项目使用，提供友好的提醒而不是强制退出
    """
    issues = []

    # 检查JWT密钥
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if not jwt_secret:
        issues.append("JWT密钥未设置")
    elif len(jwt_secret) < 32:
        issues.append(f"JWT密钥长度不足 ({len(jwt_secret)} < 32字符)")

    # 检查PostgreSQL密码
    pg_password = os.getenv("POSTGRESQL_PASSWORD", "")
    if not pg_password:
        issues.append("PostgreSQL密码未设置")
    elif len(pg_password) < 8:
        issues.append(f"PostgreSQL密码过短 ({len(pg_password)} < 8字符)")

    # 检查TDengine密码
    td_password = os.getenv("TDENGINE_PASSWORD", "")
    if not td_password:
        issues.append("TDengine密码未设置")
    elif len(td_password) < 8:
        issues.append(f"TDengine密码过短 ({len(td_password)} < 8字符)")

    # 输出结果
    if issues:
        logger.warning("⚠️  配置安全性提醒:")
        for issue in issues:
            logger.warning("  - %s", issue)
        logger.warning("")
        logger.warning("建议提升安全性:")
        logger.warning("  1. 使用 'openssl rand -hex 32' 生成强JWT密钥")
        logger.warning("  2. 使用 'openssl rand -base64 16' 生成强数据库密码")
        logger.warning("")
        logger.warning("💡 个人项目可以忽略此警告，不影响正常使用")
        logger.warning("   如需提升安全性，请更新 .env 文件中的配置")
    else:
        logger.info("✅ 配置检查通过 - 所有密钥强度符合要求")


def generate_strong_jwt_secret() -> str:
    """
    生成强JWT密钥

    Returns:
        32字节的十六进制字符串
    """
    import secrets

    return secrets.token_hex(32)


def generate_strong_db_password() -> str:
    """
    生成强数据库密码

    Returns:
        16字节的base64编码字符串
    """
    import secrets

    return secrets.token_urlsafe(16)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # 运行检查
    check_config_strength()

    # 如果配置不安全，提供生成命令
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if not jwt_secret or len(jwt_secret) < 32:
        print("\n" + "=" * 60)
        print("🔧 快速修复 - 生成强密钥")
        print("=" * 60)
        print("\n生成新的JWT密钥:")
        print(f"  JWT_SECRET_KEY={generate_strong_jwt_secret()}")
        print("\n生成新的数据库密码:")
        print(f"  POSTGRESQL_PASSWORD={generate_strong_db_password()}")
        print(f"  TDENGINE_PASSWORD={generate_strong_db_password()}")
        print("\n将以上配置添加到 .env 文件中即可")
        print("=" * 60)
