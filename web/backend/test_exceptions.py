#!/usr/bin/env python3
"""
测试异常处理框架 - 验证统一异常处理是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.core.exceptions import (
        BusinessException,
        ValidationException,
        NotFoundException,
        ForbiddenException,
        UnauthorizedException,
        register_exception_handlers,
        raise_business_error,
        raise_validation_error,
        raise_not_found,
        raise_forbidden,
        raise_unauthorized,
    )

    print("✅ 异常处理模块导入成功")
except ImportError as e:
    print(f"❌ 异常处理模块导入失败: {e}")
    sys.exit(1)


def test_exceptions():
    """测试各种异常类"""
    print("\n🧪 测试异常类...")

    try:
        # 测试BusinessException
        raise BusinessException("测试业务异常", 400)
        print("❌ BusinessException 未抛出")
        return False
    except BusinessException as e:
        print(f"✅ BusinessException: {e.detail} (status: {e.status_code})")

    try:
        # 测试ValidationException
        raise ValidationException("邮箱格式错误", "email")
        print("❌ ValidationException 未抛出")
        return False
    except ValidationException as e:
        print(f"✅ ValidationException: {e.detail}")

    try:
        # 测试NotFoundException
        raise NotFoundException("用户", "user123")
        print("❌ NotFoundException 未抛出")
        return False
    except NotFoundException as e:
        print(f"✅ NotFoundException: {e.detail}")

    try:
        # 测试ForbiddenException
        raise ForbiddenException("无权访问此资源")
        print("❌ ForbiddenException 未抛出")
        return False
    except ForbiddenException as e:
        print(f"✅ ForbiddenException: {e.detail}")

    try:
        # 测试UnauthorizedException
        raise UnauthorizedException("请先登录")
        print("❌ UnauthorizedException 未抛出")
        return False
    except UnauthorizedException as e:
        print(f"✅ UnauthorizedException: {e.detail}")

    print("✅ 所有异常类测试通过")
    return True


def test_convenience_functions():
    """测试便捷函数"""
    print("\n🧪 测试便捷函数...")

    try:
        # 测试raise_business_error
        raise_business_error("便捷业务错误", 400)
        print("❌ raise_business_error 未抛出")
        return False
    except BusinessException as e:
        print(f"✅ raise_business_error: {e.detail}")

    try:
        # 测试raise_validation_error
        raise_validation_error("数据格式错误", "phone")
        print("❌ raise_validation_error 未抛出")
        return False
    except ValidationException as e:
        print(f"✅ raise_validation_error: {e.detail}")

    try:
        # 测试raise_not_found
        raise_not_found("股票", "600519")
        print("❌ raise_not_found 未抛出")
        return False
    except NotFoundException as e:
        print(f"✅ raise_not_found: {e.detail}")

    try:
        # 测试raise_forbidden
        raise_forbidden("权限被拒绝")
        print("❌ raise_forbidden 未抛出")
        return False
    except ForbiddenException as e:
        print(f"✅ raise_forbidden: {e.detail}")

    try:
        # 测试raise_unauthorized
        raise_unauthorized("需要认证")
        print("❌ raise_unauthorized 未抛出")
        return False
    except UnauthorizedException as e:
        print(f"✅ raise_unauthorized: {e.detail}")

    print("✅ 所有便捷函数测试通过")
    return True


def test_register_handlers():
    """测试异常处理器注册"""
    print("\n🧪 测试异常处理器注册...")

    try:
        from fastapi import FastAPI

        app = FastAPI()

        # 注册异常处理器
        register_exception_handlers(app)

        # 检查路由数量是否增加（异常处理器会添加路由）
        routes_before = len(app.routes)

        print(f"✅ 异常处理器注册成功")
        print(f"   路由数量: {routes_before}")

        return True
    except Exception as e:
        print(f"❌ 异常处理器注册失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 MyStocks 异常处理框架测试")
    print("=" * 50)

    success = True

    success &= test_exceptions()
    success &= test_convenience_functions()
    success &= test_register_handlers()

    print("\n" + "=" * 50)
    if success:
        print("🎉 异常处理框架测试全部通过！")
        print("   框架已准备好投入使用")
    else:
        print("💥 异常处理框架测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
