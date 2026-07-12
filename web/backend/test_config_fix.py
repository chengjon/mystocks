#!/usr/bin/env python3
"""测试配置修复 - 验证环境变量正确读取"""

import os
import sys


# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.core.config import settings, validate_required_settings

    print("✅ 配置模块导入成功")
except ImportError as e:
    print(f"❌ 配置模块导入失败: {e}")
    sys.exit(1)


def test_configuration():
    """测试配置是否正确读取"""
    print("\n🔍 测试配置读取...")

    # 测试数据库配置
    print("\n📊 数据库配置:")
    print(f"  PostgreSQL Host: {settings.postgresql_host}")
    print(f"  PostgreSQL Port: {settings.postgresql_port}")
    print(f"  PostgreSQL User: {settings.postgresql_user}")
    print(f"  PostgreSQL Database: {settings.postgresql_database}")
    print(f"  PostgreSQL Password: {'***' if settings.postgresql_password else 'NOT SET'}")

    # 测试Redis配置
    print("\n🔴 Redis配置:")
    print(f"  Redis Host: {settings.redis_host}")
    print(f"  Redis Port: {settings.redis_port}")
    print(f"  Redis DB: {settings.redis_db}")
    print(f"  Redis Password: {'***' if settings.redis_password else 'NOT SET'}")

    # 测试JWT配置
    print("\n🔐 JWT配置:")
    print(f"  JWT Secret Key: {'***' if settings.jwt_secret_key else 'NOT SET'}")
    print(f"  JWT Algorithm: {settings.algorithm}")
    print(f"  JWT Expire Minutes: {settings.access_token_expire_minutes}")

    # 测试管理员密码
    print("\n👤 管理员配置:")
    print(f"  Admin Initial Password: {'***' if settings.admin_initial_password else 'NOT SET'}")

    # 测试CORS配置
    print("\n🌐 CORS配置:")
    cors_origins = settings.cors_origins
    print(f"  CORS Origins Count: {len(cors_origins)}")
    print(f"  First 3 Origins: {cors_origins[:3] if cors_origins else 'NONE'}")

    print("\n🔐 验证必需配置...")
    try:
        validate_required_settings(settings)
        print("✅ 所有必需配置验证通过")
        return True
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 MyStocks 配置修复验证")
    print("=" * 50)

    success = test_configuration()

    if success:
        print("\n🎉 配置修复成功！所有设置正确从.env文件读取。")
        print("   不再使用硬编码的敏感信息。")
    else:
        print("\n💥 配置修复失败！请检查.env文件和配置设置。")
        sys.exit(1)
