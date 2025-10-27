#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证脚本

验证生产环境配置的完整性和安全性

使用方法:
    python deployment/verify_config.py

创建日期: 2025-10-25
版本: 1.0.0
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# 必需的环境变量
REQUIRED_VARS = [
    'POSTGRESQL_HOST',
    'POSTGRESQL_PORT',
    'POSTGRESQL_USER',
    'POSTGRESQL_PASSWORD',
    'POSTGRESQL_DATABASE',
    'TDENGINE_HOST',
    'TDENGINE_PORT',
    'TDENGINE_USER',
    'TDENGINE_PASSWORD',
    'TDENGINE_DATABASE',
    'JWT_SECRET_KEY',
    'ENVIRONMENT',
]

# 不安全的默认值
INSECURE_DEFAULTS = {
    'JWT_SECRET_KEY': ['CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_AT_LEAST_32_CHARS', 'secret', 'changeme'],
    'POSTGRESQL_PASSWORD': ['postgres', 'password', 'your_secure_password_here'],
    'TDENGINE_PASSWORD': ['taosdata'],
    'GRAFANA_ADMIN_PASSWORD': ['admin', 'change_this_password'],
}


def load_env_file(env_file: str = '.env') -> bool:
    """加载.env文件"""
    if not os.path.exists(env_file):
        print(f"❌ 错误: 找不到环境配置文件 {env_file}")
        print(f"   请先复制模板: cp deployment/production.env.template .env")
        return False

    # 读取.env文件并设置环境变量
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

    return True


def check_required_vars() -> List[str]:
    """检查必需的环境变量"""
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    return missing


def check_insecure_defaults() -> List[Tuple[str, str]]:
    """检查不安全的默认值"""
    insecure = []
    for var, defaults in INSECURE_DEFAULTS.items():
        value = os.getenv(var, '')
        if value in defaults:
            insecure.append((var, value))
    return insecure


def check_jwt_secret() -> bool:
    """检查JWT密钥强度"""
    secret = os.getenv('JWT_SECRET_KEY', '')
    if len(secret) < 32:
        print(f"⚠️  警告: JWT_SECRET_KEY长度不足 (当前: {len(secret)}, 推荐: >= 32)")
        return False
    return True


def check_environment() -> bool:
    """检查运行环境设置"""
    env = os.getenv('ENVIRONMENT', 'development')
    debug = os.getenv('DEBUG', 'false').lower()

    if env == 'production' and debug == 'true':
        print(f"❌ 错误: 生产环境不应启用DEBUG模式")
        return False

    return True


def check_database_ports() -> List[str]:
    """检查数据库端口"""
    errors = []

    pg_port = os.getenv('POSTGRESQL_PORT', '')
    tdengine_port = os.getenv('TDENGINE_PORT', '')

    if not pg_port.isdigit() or not (1 <= int(pg_port) <= 65535):
        errors.append(f"PostgreSQL端口无效: {pg_port}")

    if not tdengine_port.isdigit() or not (1 <= int(tdengine_port) <= 65535):
        errors.append(f"TDengine端口无效: {tdengine_port}")

    return errors


def check_log_directory() -> bool:
    """检查日志目录"""
    log_dir = os.getenv('LOG_DIR', '/opt/mystocks/logs')
    if not os.path.exists(log_dir):
        print(f"⚠️  警告: 日志目录不存在: {log_dir}")
        print(f"   将自动创建...")
        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 日志目录已创建")
            return True
        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            return False
    return True


def main():
    """主函数"""
    print("=" * 70)
    print("MyStocks 配置验证")
    print("=" * 70)

    # 加载.env文件
    if not load_env_file():
        sys.exit(1)

    print(f"\n✅ 环境配置文件加载成功\n")

    errors = []
    warnings = []

    # 检查必需变量
    print("检查必需的环境变量...")
    missing = check_required_vars()
    if missing:
        errors.append(f"缺少必需的环境变量: {', '.join(missing)}")
    else:
        print(f"✅ 所有必需变量已配置\n")

    # 检查不安全的默认值
    print("检查安全配置...")
    insecure = check_insecure_defaults()
    if insecure:
        for var, value in insecure:
            errors.append(f"检测到不安全的默认值: {var}={value}")
    else:
        print(f"✅ 未检测到不安全的默认值\n")

    # 检查JWT密钥
    print("检查JWT密钥强度...")
    if check_jwt_secret():
        print(f"✅ JWT密钥强度符合要求\n")

    # 检查环境设置
    print("检查运行环境...")
    if check_environment():
        print(f"✅ 环境配置正确\n")

    # 检查数据库端口
    print("检查数据库配置...")
    port_errors = check_database_ports()
    if port_errors:
        errors.extend(port_errors)
    else:
        print(f"✅ 数据库端口配置正确\n")

    # 检查日志目录
    print("检查日志目录...")
    check_log_directory()
    print()

    # 输出摘要
    print("=" * 70)
    print("验证摘要")
    print("=" * 70)

    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:\n")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")

    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:\n")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")

    if not errors and not warnings:
        print(f"\n🎉 配置验证通过！所有检查项目符合要求。\n")
        print(f"建议:")
        print(f"   1. 定期更新密码")
        print(f"   2. 启用SSL/TLS加密")
        print(f"   3. 配置防火墙规则")
        print(f"   4. 启用监控告警")
        sys.exit(0)
    else:
        print(f"\n⚠️  请修复上述问题后重新验证。\n")
        sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
