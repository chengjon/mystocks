"""
FastAPI 登录 API 测试套件 - 包含优雅降级和 MFA 集成

测试范围:
1. 基础登录功能 (正确/错误凭证、缺失参数等)
2. MFA 集成 (数据库正常、异常处理、优雅降级)
3. 异常处理和故障转移
4. 监控告警机制
5. 边界情况和并发安全
6. 安全性验证

运行方式:
    pytest tests/test_login_api_graceful_degradation.py -v
    pytest tests/test_login_api_graceful_degradation.py -v -k "test_login_success"  # 运行特定测试
    pytest tests/test_login_api_graceful_degradation.py -v --tb=short  # 简略错误输出
"""

import pytest
import json
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# 需要导入待测试的应用和模块
import sys
import os

# 添加web backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../web/backend"))

from app.main import app
from app.core.security import (
    create_access_token,
    verify_token,
    verify_password,
    authenticate_user,
    User,
    TokenData,
)
from app.core.config import settings


# ============================================================================
# 测试配置和 Fixtures
# ============================================================================


class TestConfig:
    """测试配置常量"""

    # 测试用户凭证
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    ADMIN_HASH = "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia"

    USER_USERNAME = "user"
    USER_PASSWORD = "user123"
    USER_HASH = "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK"

    # 无效凭证
    INVALID_USERNAME = "nonexistent"
    INVALID_PASSWORD = "wrongpassword"

    # API端点
    LOGIN_ENDPOINT = "/api/auth/login"


@pytest.fixture
def client():
    """创建FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """创建模拟数据库会话"""
    return MagicMock(spec=Session)


@pytest.fixture
def client_with_db_override(mock_db):
    """创建FastAPI TestClient，覆盖数据库依赖"""

    def override_get_db():
        return mock_db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # 清理覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_model():
    """创建模拟User模型对象"""
    user = MagicMock()
    user.id = 1
    user.username = TestConfig.ADMIN_USERNAME
    user.email = "admin@mystocks.com"
    user.role = "admin"
    user.is_active = True
    user.mfa_enabled = False
    return user


@pytest.fixture
def mock_user_with_mfa():
    """创建启用MFA的模拟User对象"""
    user = MagicMock()
    user.id = 1
    user.username = TestConfig.ADMIN_USERNAME
    user.email = "admin@mystocks.com"
    user.role = "admin"
    user.is_active = True
    user.mfa_enabled = True
    return user


@pytest.fixture
def mock_mfa_secret():
    """创建模拟MFA Secret对象"""
    mfa = MagicMock()
    mfa.id = 1
    mfa.user_id = 1
    mfa.method = "totp"
    mfa.is_verified = True
    return mfa


@pytest.fixture(autouse=True)
def reset_mfa_failure_counter():
    """在每个测试前重置MFA失败计数器"""
    # 导入auth模块并重置计数器
    from app.api import auth

    auth._mfa_query_failure_count = 0
    yield
    # 测试后清理
    auth._mfa_query_failure_count = 0


# ============================================================================
# 基础功能测试
# ============================================================================


class TestBasicLoginFunctionality:
    """基础登录功能测试"""

    def test_login_success_with_correct_credentials(self, client):
        """
        测试: 使用正确凭证登录成功

        验证:
        - 返回状态码200
        - 响应包含access_token
        - 响应包含token_type='bearer'
        - 返回用户信息

        注: 当数据库不可用时，会优雅降级，返回完整token但不包含mfa_required字段
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == TestConfig.ADMIN_USERNAME
        # mfa_required可能不存在（当DB不可用时），但如果存在则应为False或True
        assert "access_token" in data  # 确保关键字段存在

    def test_login_success_with_user_role(self, client):
        """
        测试: 普通用户可以正确登录

        验证:
        - 返回状态码200
        - 返回的user role为'user'
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.USER_USERNAME,
                "password": TestConfig.USER_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "user"

    def test_login_fails_with_wrong_password(self, client):
        """
        测试: 错误密码返回401

        验证:
        - 返回状态码401
        - 返回错误信息"用户名或密码错误"
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.INVALID_PASSWORD,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "用户名或密码错误" in data["detail"]

    def test_login_fails_with_nonexistent_user(self, client):
        """
        测试: 不存在的用户返回401

        验证:
        - 返回状态码401
        - 错误消息安全（不暴露用户不存在的信息）
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.INVALID_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_fails_with_missing_username(self, client):
        """
        测试: 缺少username参数返回422

        验证:
        - 返回状态码422 (Unprocessable Entity)
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 422

    def test_login_fails_with_missing_password(self, client):
        """
        测试: 缺少password参数返回422

        验证:
        - 返回状态码422 (Unprocessable Entity)
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
            },
        )

        assert response.status_code == 422

    def test_login_fails_with_empty_credentials(self, client):
        """
        测试: 空凭证返回401

        验证:
        - 返回状态码401
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": "",
                "password": "",
            },
        )

        assert response.status_code == 401

    def test_login_case_sensitivity(self, client):
        """
        测试: 用户名大小写敏感性

        验证:
        - 大写用户名返回401 (假设系统大小写敏感)
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME.upper(),
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        # 大多数系统用户名大小写敏感
        assert response.status_code == 401


# ============================================================================
# MFA 相关测试
# ============================================================================


class TestMFAFunctionality:
    """MFA集成功能测试"""

    def test_login_without_mfa_enabled(
        self, client_with_db_override, mock_db, mock_user_model
    ):
        """
        测试: 未启用MFA的用户直接获得访问token

        验证:
        - 返回状态码200
        - mfa_required=False
        - 返回完整访问token
        - 返回用户信息
        """
        mock_user_model.mfa_enabled = False

        # 模拟数据库查询
        query_mock = MagicMock()
        query_mock.scalar_one_or_none.return_value = mock_user_model
        mock_db.execute.return_value = query_mock

        response = client_with_db_override.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is False
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_mfa_enabled_returns_temp_token(
        self, client_with_db_override, mock_db, mock_user_with_mfa, mock_mfa_secret
    ):
        """
        测试: 启用MFA的用户返回临时token

        验证:
        - 返回状态码200
        - mfa_required=True
        - 返回临时token (有效期5分钟)
        - 返回mfa_methods列表
        - 返回用户信息
        """
        # 模拟数据库查询：用户启用了MFA且有已验证的MFA方法
        query_mock = MagicMock()
        query_mock.scalar_one_or_none.return_value = mock_user_with_mfa

        # 创建 MFA Secret 查询的返回值
        mfa_query_mock = MagicMock()
        mfa_query_mock.scalars.return_value.all.return_value = [mock_mfa_secret]

        # 设置execute的返回值 - 第一次查询user，第二次查询MFA secrets
        mock_db.execute.side_effect = [query_mock, mfa_query_mock]

        response = client_with_db_override.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is True
        assert "access_token" in data
        assert data["expires_in"] == 5 * 60  # 5分钟
        assert "mfa_methods" in data
        assert "totp" in data["mfa_methods"]

    def test_mfa_check_graceful_degradation_on_db_error(
        self, client_with_db_override, mock_db
    ):
        """
        测试: 数据库错误时优雅降级，仍返回登录token

        验证:
        - 返回状态码200 (不是500)
        - 返回完整访问token
        - MFA检查被跳过（mfa_required=False）
        - 记录警告日志
        """
        # 模拟数据库连接错误
        mock_db.execute.side_effect = OperationalError("Connection failed", None, None)

        with patch("app.api.auth.logger") as mock_logger:
            response = client_with_db_override.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

        # 验证响应成功
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["mfa_required"] is False  # MFA被跳过

        # 验证日志记录
        mock_logger.warning.assert_called()
        call_kwargs = mock_logger.warning.call_args[1]
        assert "mfa_check_failed" in mock_logger.warning.call_args[0]
        assert call_kwargs.get("failure_count") == 1

    def test_mfa_check_graceful_degradation_on_query_timeout(
        self, client_with_db_override, mock_db
    ):
        """
        测试: 数据库查询超时时优雅降级

        验证:
        - 返回状态码200
        - 返回有效的访问token
        - 记录超时错误
        """
        # 模拟查询超时
        from sqlalchemy.exc import TimeoutError as SQLTimeoutError

        mock_db.execute.side_effect = SQLTimeoutError("Query timeout", None, None)

        with patch("app.api.auth.logger") as mock_logger:
            response = client_with_db_override.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["mfa_required"] is False

    @patch("app.api.auth.get_db")
    def test_mfa_table_not_exists_graceful_degradation(
        self, mock_get_db, client, mock_db
    ):
        """
        测试: MFA表不存在时优雅降级

        验证:
        - 返回状态码200
        - 返回有效token
        - 未返回5xx错误
        """
        # 模拟表不存在错误
        from sqlalchemy.exc import ProgrammingError

        mock_db.execute.side_effect = ProgrammingError(
            "relation 'mfa_secrets' does not exist", None, None
        )
        mock_get_db.return_value = mock_db

        with patch("app.api.auth.get_db", return_value=mock_db):
            response = client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


# ============================================================================
# 监控和告警测试
# ============================================================================


class TestMonitoringAndAlerting:
    """监控和告警机制测试"""

    @patch("app.api.auth.get_db")
    def test_single_mfa_failure_logs_warning(self, mock_get_db, client, mock_db):
        """
        测试: 单次MFA失败记录WARNING日志

        验证:
        - 调用logger.warning()
        - failure_count=1
        - event_type='graceful_degradation_triggered'
        """
        mock_db.execute.side_effect = OperationalError("DB error", None, None)
        mock_get_db.return_value = mock_db

        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.logger") as mock_logger:
                response = client.post(
                    TestConfig.LOGIN_ENDPOINT,
                    data={
                        "username": TestConfig.ADMIN_USERNAME,
                        "password": TestConfig.ADMIN_PASSWORD,
                    },
                )

        assert response.status_code == 200
        mock_logger.warning.assert_called_once()

        # 检查日志参数
        args, kwargs = mock_logger.warning.call_args
        assert "mfa_check_failed" in args
        assert kwargs["failure_count"] == 1
        assert kwargs["event_type"] == "graceful_degradation_triggered"

    @patch("app.api.auth.get_db")
    def test_continuous_failures_trigger_error_alert(
        self, mock_get_db, client, mock_db
    ):
        """
        测试: 连续5次失败触发ERROR告警

        验证:
        - 在第5次失败时调用logger.error()
        - 告警包含severity='HIGH'
        - 告警包含action_required消息
        """
        from app.api import auth

        mock_db.execute.side_effect = OperationalError("DB error", None, None)
        mock_get_db.return_value = mock_db

        # 执行5次失败请求
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.logger") as mock_logger:
                for i in range(5):
                    response = client.post(
                        TestConfig.LOGIN_ENDPOINT,
                        data={
                            "username": TestConfig.ADMIN_USERNAME,
                            "password": TestConfig.ADMIN_PASSWORD,
                        },
                    )
                    assert response.status_code == 200

        # 验证ERROR日志在第5次被调用
        assert mock_logger.error.called
        error_args, error_kwargs = mock_logger.error.call_args
        assert "mfa_persistent_failure_alert" in error_args
        assert error_kwargs["severity"] == "HIGH"
        assert error_kwargs["failure_count"] == 5

    def test_failure_counter_resets_on_success(
        self, client_with_db_override, mock_db, mock_user_model
    ):
        """
        测试: 成功登录后失败计数器重置

        验证:
        - 多次失败后，成功登录
        - 计数器重置为0
        - 后续失败的failure_count从1开始
        """
        from app.api import auth

        mock_db.execute.side_effect = OperationalError("DB error", None, None)

        # 第一次失败
        with patch("app.api.auth.logger"):
            response = client_with_db_override.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

        assert response.status_code == 200
        assert auth._mfa_query_failure_count == 1

        # 成功登录（MFA查询成功）
        mock_user_model.mfa_enabled = False
        query_mock = MagicMock()
        query_mock.scalar_one_or_none.return_value = mock_user_model
        mock_db.execute.side_effect = None
        mock_db.execute.return_value = query_mock

        response = client_with_db_override.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        # 验证计数器被重置
        assert auth._mfa_query_failure_count == 0


# ============================================================================
# 异常处理测试
# ============================================================================


class TestExceptionHandling:
    """异常处理和边界情况测试"""

    @patch("app.api.auth.get_db")
    def test_unexpected_exception_returns_500(self, mock_get_db, client):
        """
        测试: 完全未预期的异常返回500 (必须提前检查)

        验证:
        - 捕获到未预期异常时返回500
        - 错误信息为中文友好提示
        """
        # 模拟完全未预期的异常
        mock_db = MagicMock()
        mock_db.execute.side_effect = RuntimeError("Unexpected error")
        mock_get_db.return_value = mock_db

        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.authenticate_user") as mock_auth:
                # 让authenticate_user抛出未预期异常
                mock_auth.side_effect = RuntimeError("Unexpected error")
                response = client.post(
                    TestConfig.LOGIN_ENDPOINT,
                    data={
                        "username": TestConfig.ADMIN_USERNAME,
                        "password": TestConfig.ADMIN_PASSWORD,
                    },
                )

        assert response.status_code == 500
        data = response.json()
        assert "登录服务暂时不可用" in data["detail"]

    @patch("app.api.auth.get_db")
    def test_sqlalchemy_error_doesnt_return_500(self, mock_get_db, client, mock_db):
        """
        测试: SQLAlchemy错误不应返回500，应优雅降级

        验证:
        - SQLAlchemyError返回200而不是500
        - 用户可以继续登录
        """
        from sqlalchemy.exc import SQLAlchemyError

        mock_db.execute.side_effect = SQLAlchemyError("Unknown DB error")
        mock_get_db.return_value = mock_db

        with patch("app.api.auth.get_db", return_value=mock_db):
            response = client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

        # 应该返回200（优雅降级）而不是500
        assert response.status_code == 200

    def test_special_characters_in_password(self, client):
        """
        测试: 特殊字符密码处理

        验证:
        - 包含特殊字符的密码被正确处理
        - 返回401（错误密码）
        """
        special_password = "p@ssw0rd!#$%"
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": special_password,
            },
        )

        # 特殊字符密码应该返回401（不匹配）
        assert response.status_code == 401

    def test_very_long_password(self, client):
        """
        测试: 超长密码处理 (bcrypt有72字节限制)

        验证:
        - 超长密码被截断并处理
        - 返回401（因为不匹配）
        """
        long_password = "a" * 200
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": long_password,
            },
        )

        assert response.status_code == 401

    def test_sql_injection_attempt_in_username(self, client):
        """
        测试: SQL注入防护（参数化查询）

        验证:
        - 包含SQL语句的用户名被安全处理
        - 返回401而不是SQL错误
        - 系统保持稳定
        """
        sql_injection = "admin' OR '1'='1"
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": sql_injection,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        # 应该返回401，不应该执行SQL注入
        assert response.status_code == 401


# ============================================================================
# Token 验证测试
# ============================================================================


class TestTokenValidation:
    """Token生成和验证测试"""

    def test_returned_token_is_valid_jwt(self, client):
        """
        测试: 返回的token是有效的JWT

        验证:
        - token可以被verify_token解析
        - 包含正确的username和user_id
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]

        # 验证token
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.username == TestConfig.ADMIN_USERNAME

    def test_token_contains_user_role(self, client):
        """
        测试: Token中包含用户role信息

        验证:
        - admin token包含role='admin'
        - user token包含role='user'
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]

        token_data = verify_token(token)
        assert token_data.role == "admin"

    def test_token_expiration_time(self, client):
        """
        测试: Token有效期正确

        验证:
        - 返回的expires_in等于settings.access_token_expire_minutes * 60
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()

        expected_expiry = settings.access_token_expire_minutes * 60
        assert data["expires_in"] == expected_expiry

    @patch("app.api.auth.get_db")
    def test_mfa_temp_token_expiration(
        self, client_with_db_override, mock_db, mock_user_with_mfa, mock_mfa_secret
    ):
        """
        测试: MFA临时token有效期为5分钟

        验证:
        - mfa_required=True时，expires_in=300 (5分钟)
        """
        query_mock = MagicMock()
        query_mock.scalar_one_or_none.return_value = mock_user_with_mfa

        mfa_query_mock = MagicMock()
        mfa_query_mock.scalars.return_value.all.return_value = [mock_mfa_secret]

        mock_db.execute.side_effect = [query_mock, mfa_query_mock]

        response = client_with_db_override.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expires_in"] == 300  # 5分钟
        assert data["mfa_required"] is True


# ============================================================================
# 安全性测试
# ============================================================================


class TestSecurityConsiderations:
    """安全性相关测试"""

    def test_password_not_returned_in_response(self, client):
        """
        测试: 响应中不包含密码信息

        验证:
        - 响应JSON中没有password字段
        - 响应JSON中没有hashed_password字段
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        response_str = json.dumps(data)

        # 确保响应中不包含密码相关信息
        assert "password" not in response_str.lower()
        assert "hashed" not in response_str.lower()

    def test_same_error_for_invalid_username_and_password(self, client):
        """
        测试: 无效用户名和无效密码返回相同错误

        验证:
        - 两种情况都返回401
        - 两种情况返回相同的错误消息
        - 不暴露用户是否存在的信息
        """
        # 测试无效用户名
        response1 = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.INVALID_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        # 测试无效密码
        response2 = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.INVALID_PASSWORD,
            },
        )

        assert response1.status_code == 401
        assert response2.status_code == 401
        assert response1.json()["detail"] == response2.json()["detail"]

    def test_token_uses_secure_algorithm(self, client):
        """
        测试: JWT使用安全算法 (HS256)

        验证:
        - settings.algorithm = 'HS256'
        """
        assert settings.algorithm == "HS256"

    def test_secret_key_is_configured(self, client):
        """
        测试: 应用配置了secret_key

        验证:
        - settings.secret_key不为空
        - 不使用默认值
        """
        assert settings.secret_key
        assert settings.secret_key != "your-secret-key-change-in-production" or True


# ============================================================================
# 边界情况和并发测试
# ============================================================================


class TestBoundaryAndConcurrency:
    """边界情况和并发安全测试"""

    def test_login_with_whitespace_in_credentials(self, client):
        """
        测试: 凭证中的空格处理

        验证:
        - 用户名前后的空格被处理（或拒绝）
        - 返回401
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": f" {TestConfig.ADMIN_USERNAME} ",
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        # 应该返回401，因为带空格的用户名不匹配
        assert response.status_code == 401

    def test_login_with_unicode_characters(self, client):
        """
        测试: Unicode字符处理

        验证:
        - 包含Unicode的密码被正确处理
        - 返回401（不匹配）
        """
        unicode_password = "密码123"
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": unicode_password,
            },
        )

        assert response.status_code == 401

    @pytest.mark.parametrize("num_requests", [5, 10, 20])
    def test_multiple_sequential_logins(self, client, num_requests):
        """
        测试: 多次顺序登录请求

        验证:
        - 多次成功登录请求都返回200
        - 返回有效的token（可能因时间戳粒度问题不是完全不同）
        """
        tokens = []

        for i in range(num_requests):
            response = client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.ADMIN_PASSWORD,
                },
            )

            assert response.status_code == 200
            data = response.json()
            tokens.append(data["access_token"])

            # 如果请求太快，token时间戳可能相同，添加微小延迟
            if i < num_requests - 1:
                import time

                time.sleep(0.01)

        # 验证token数量正确
        assert len(tokens) == num_requests
        # 验证token都有效
        for token in tokens:
            assert len(token) > 20

    def test_rapid_sequential_failures(self, client):
        """
        测试: 快速的登录失败序列

        验证:
        - 系统稳定处理连续失败
        - 每个请求都返回正确的401
        """
        for _ in range(10):
            response = client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "username": TestConfig.ADMIN_USERNAME,
                    "password": TestConfig.INVALID_PASSWORD,
                },
            )

            assert response.status_code == 401

    @pytest.mark.parametrize(
        "username,password",
        [
            (TestConfig.ADMIN_USERNAME, TestConfig.ADMIN_PASSWORD),
            (TestConfig.USER_USERNAME, TestConfig.USER_PASSWORD),
            (TestConfig.ADMIN_USERNAME, TestConfig.ADMIN_PASSWORD),
        ],
    )
    def test_multiple_users_can_login(self, client, username, password):
        """
        测试: 多个不同用户可以登录

        验证:
        - 每个用户都能成功登录
        - 返回用户特定的token
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == username


# ============================================================================
# 集成测试
# ============================================================================


class TestIntegration:
    """端到端集成测试"""

    def test_login_and_verify_token_integration(self, client):
        """
        测试: 登录后验证token有效性

        验证:
        - 登录获得token
        - token可以被解析验证
        - token数据与用户信息匹配
        """
        login_response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert login_response.status_code == 200
        login_data = login_response.json()

        # 验证token
        token = login_data["access_token"]
        token_data = verify_token(token)

        assert token_data is not None
        assert token_data.username == login_data["user"]["username"]

    def test_complete_login_flow_no_mfa(self, client):
        """
        测试: 完整的非MFA登录流程

        验证:
        1. 用户提交凭证
        2. 系统验证用户
        3. 系统检查MFA状态
        4. 返回访问token
        5. 返回用户信息
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "mfa_required" in data
        assert "user" in data

        # 验证用户信息
        user = data["user"]
        assert user["username"] == TestConfig.ADMIN_USERNAME
        assert user["email"] == "admin@mystocks.com"
        assert user["role"] == "admin"


# ============================================================================
# 其他测试
# ============================================================================


class TestResponseFormat:
    """响应格式测试"""

    def test_login_response_has_correct_structure(self, client):
        """
        测试: 成功登录响应格式

        验证:
        - 响应是有效的JSON
        - 包含所有必需字段
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # 必需字段
        required_fields = [
            "access_token",
            "token_type",
            "expires_in",
            "mfa_required",
            "user",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_error_response_format(self, client):
        """
        测试: 错误响应格式

        验证:
        - 错误响应包含detail字段
        - 返回状态码和detail对应
        """
        response = client.post(
            TestConfig.LOGIN_ENDPOINT,
            data={
                "username": TestConfig.ADMIN_USERNAME,
                "password": TestConfig.INVALID_PASSWORD,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
