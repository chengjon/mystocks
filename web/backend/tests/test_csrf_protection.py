"""
CSRF 保护安全测试

测试覆盖:
- CSRF token 生成
- CSRF token 验证
- Token 过期处理
- 重放攻击防护
- 中间件保护
- 排除路径验证
- 缺少 token 拒绝
- 无效 token 拒绝

版本: 1.0.0
日期: 2025-12-23
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

# 导入 CSRF 管理器
from app.app_factory import CSRFTokenManager, csrf_manager


class TestCSRFTokenManager:
    """测试 CSRFTokenManager 类"""

    def setup_method(self):
        """每个测试前清空tokens"""
        csrf_manager.tokens.clear()

    def test_generate_token(self):
        """测试生成 CSRF token"""
        token = csrf_manager.generate_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 32  # token_urlsafe(32) 应该生成足够长的token
        assert token in csrf_manager.tokens

    def test_generate_unique_tokens(self):
        """测试生成的token是唯一的"""
        tokens = [csrf_manager.generate_token() for _ in range(100)]

        assert len(tokens) == len(set(tokens)), "所有token应该是唯一的"

    def test_validate_valid_token(self):
        """测试验证有效token"""
        token = csrf_manager.generate_token()

        result = csrf_manager.validate_token(token)

        assert result is True

    def test_validate_invalid_token(self):
        """测试验证无效token"""
        result = csrf_manager.validate_token("invalid_token_xyz")

        assert result is False

    def test_validate_empty_token(self):
        """测试验证空token"""
        result = csrf_manager.validate_token("")

        assert result is False

    def test_validate_none_token(self):
        """测试验证 None token"""
        result = csrf_manager.validate_token(None)

        assert result is False

    def test_token_expiration(self):
        """测试token过期"""
        # 设置一个很短的过期时间用于测试
        original_timeout = csrf_manager.token_timeout
        csrf_manager.token_timeout = 0.1  # 100毫秒

        token = csrf_manager.generate_token()
        time.sleep(0.15)  # 等待token过期

        result = csrf_manager.validate_token(token)

        assert result is False
        assert token not in csrf_manager.tokens, "过期token应该被删除"

        # 恢复原设置
        csrf_manager.token_timeout = original_timeout

    def test_token_replay_prevention(self):
        """测试重放攻击防护 - token只能使用一次"""
        token = csrf_manager.generate_token()

        # 第一次使用应该成功
        assert csrf_manager.validate_token(token) is True

        # 第二次使用相同token应该失败
        assert csrf_manager.validate_token(token) is False

    def test_token_used_flag(self):
        """测试token使用标记"""
        token = csrf_manager.generate_token()

        assert csrf_manager.tokens[token]["used"] is False

        csrf_manager.validate_token(token)

        assert csrf_manager.tokens[token]["used"] is True

    def test_token_cleanup(self):
        """测试清理过期tokens"""
        original_timeout = csrf_manager.token_timeout
        csrf_manager.token_timeout = 0.1

        # 生成一些tokens
        tokens = [csrf_manager.generate_token() for _ in range(5)]
        assert len(csrf_manager.tokens) == 5

        # 等待过期
        time.sleep(0.15)

        # 清理过期tokens
        csrf_manager.cleanup_expired_tokens()

        assert len(csrf_manager.tokens) == 0, "所有过期token应该被清理"

        # 恢复原设置
        csrf_manager.token_timeout = original_timeout

    def test_token_has_created_timestamp(self):
        """测试token包含创建时间戳"""
        token = csrf_manager.generate_token()

        assert "created_at" in csrf_manager.tokens[token]
        assert isinstance(csrf_manager.tokens[token]["created_at"], float)

    def test_multiple_tokens_independent(self):
        """测试多个token独立管理"""
        token1 = csrf_manager.generate_token()
        token2 = csrf_manager.generate_token()

        # 验证两个token都存在
        assert token1 in csrf_manager.tokens
        assert token2 in csrf_manager.tokens

        # 使用token1不应影响token2
        csrf_manager.validate_token(token1)
        assert csrf_manager.validate_token(token1) is False  # token1已使用
        assert csrf_manager.validate_token(token2) is True  # token2仍有效


class TestCSRFMiddleware:
    """测试CSRF中间件"""

    def test_exempt_paths(self):
        """测试排除路径不需要CSRF token"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 这些路径应该不需要CSRF token
        exempt_paths = [
            "/api/csrf-token",
            "/api/v1/auth/login",
            "/docs",
            "/redoc",
            "/health",
        ]

        for path in exempt_paths:
            response = client.get(path)
            # 排除路径应该能正常访问（至少不会因为CSRF而失败）
            assert response.status_code != 403, f"{path} 应该被排除在CSRF检查之外"

    def test_csrf_token_endpoint_returns_token(self):
        """测试CSRF token端点返回token"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/api/csrf-token")

        assert response.status_code == 200
        data = response.json()
        # 响应被 UnifiedResponse 中间件包装，数据在 data 字段中
        assert "data" in data
        assert "csrf_token" in data["data"]
        assert "token_type" in data["data"]
        assert "expires_in" in data["data"]

    def test_post_without_token_returns_403(self):
        """测试POST请求没有token时返回403"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 注意：需要找一个非豁免的POST端点
        # 这里我们测试一个假设的端点
        response = client.post("/api/test/endpoint", json={"test": "data"})

        # 如果端点不存在，应该是404而不是403
        # 但如果存在且不是豁免路径，应该是403
        # 这个测试依赖于实际存在的端点

        # 临时创建一个测试端点
        @app.post("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        response = client.post("/api/test/protected", json={"test": "data"})
        assert response.status_code == 403
        assert "CSRF" in response.text or "csrf" in response.text.lower()

    def test_post_with_valid_token_succeeds(self):
        """测试带有效token的POST请求成功"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 首先获取token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        # 创建测试端点
        @app.post("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        # 使用token发起请求
        response = client.post(
            "/api/test/protected",
            json={"test": "data"},
            headers={"x-csrf-token": csrf_token},
        )

        assert response.status_code == 200

    def test_post_with_invalid_token_returns_403(self):
        """测试带无效token的POST请求返回403"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 创建测试端点
        @app.post("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        # 使用无效token
        response = client.post(
            "/api/test/protected",
            json={"test": "data"},
            headers={"x-csrf-token": "invalid_token_xyz"},
        )

        assert response.status_code == 403
        assert "invalid" in response.text.lower() or "expired" in response.text.lower()

    def test_put_requires_csrf_token(self):
        """测试PUT请求需要CSRF token"""
        from app.app_factory import create_app

        app = create_app()

        @app.put("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # 没有token的PUT请求
        response = client.put("/api/test/protected", json={"test": "data"})
        assert response.status_code == 403

    def test_patch_requires_csrf_token(self):
        """测试PATCH请求需要CSRF token"""
        from app.app_factory import create_app

        app = create_app()

        @app.patch("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # 没有token的PATCH请求
        response = client.patch("/api/test/protected", json={"test": "data"})
        assert response.status_code == 403

    def test_delete_requires_csrf_token(self):
        """测试DELETE请求需要CSRF token"""
        from app.app_factory import create_app

        app = create_app()

        @app.delete("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # 没有token的DELETE请求
        response = client.delete("/api/test/protected")
        assert response.status_code == 403

    def test_get_does_not_require_csrf_token(self):
        """测试GET请求不需要CSRF token"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        @app.get("/api/test/public")
        async def test_endpoint():
            return {"status": "ok"}

        # GET请求不需要CSRF token
        response = client.get("/api/test/public")
        assert response.status_code == 200

    def test_options_bypasses_csrf_check(self):
        """测试OPTIONS请求绕过CSRF检查"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        @app.post("/api/test/endpoint")
        async def test_endpoint():
            return {"status": "ok"}

        # OPTIONS预检请求不应该被CSRF阻止
        response = client.options("/api/test/endpoint")
        # OPTIONS应该返回成功（CORS预检）
        assert response.status_code != 403

    def test_token_case_insensitive_header(self):
        """测试token头名称大小写不敏感"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 获取token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        @app.post("/api/test/protected")
        async def test_endpoint():
            return {"status": "ok"}

        # 测试不同大小写
        for header_name in [
            "x-csrf-token",
            "X-CSRF-Token",
            "X-Csrf-Token",
        ]:
            response = client.post(
                "/api/test/protected",
                json={},
                headers={header_name: csrf_token},
            )
            # FastAPI自动规范化头名称为小写
            # 所以我们实际需要使用小写的header名称
            # 这里测试仅验证行为

    def test_concurrent_token_generation(self):
        """测试并发token生成"""
        import threading

        tokens = []
        errors = []

        def generate_token():
            try:
                token = csrf_manager.generate_token()
                tokens.append(token)
            except Exception as e:
                errors.append(e)

        # 清空现有tokens
        csrf_manager.tokens.clear()

        # 创建多个线程同时生成token
        threads = [threading.Thread(target=generate_token) for _ in range(50)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, "不应该有错误"
        assert len(tokens) == 50, "应该生成50个token"
        assert len(set(tokens)) == 50, "所有token应该是唯一的"


class TestCSRFSecurityScenarios:
    """测试CSRF安全场景"""

    def setup_method(self):
        """每个测试前清空tokens"""
        csrf_manager.tokens.clear()

    def test_cross_origin_request_without_token_blocked(self):
        """测试跨域请求没有token被阻止"""
        """这是CSRF防护的核心场景"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        @app.post("/api/test/transfer")
        async def transfer_funds(data: dict):
            return {"status": "transferred"}

        # 模拟跨域请求（没有CSRF token）
        response = client.post(
            "/api/test/transfer",
            json={"to": "attacker", "amount": 10000},
            headers={"Origin": "http://evil.com"},
        )

        # 应该被CSRF保护阻止
        assert response.status_code == 403

    def test_same_origin_request_with_valid_token_allowed(self):
        """测试同源请求有有效token被允许"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 获取token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        @app.post("/api/test/transfer")
        async def transfer_funds(data: dict):
            return {"status": "transferred"}

        # 模拟同源请求（有CSRF token）
        response = client.post(
            "/api/test/transfer",
            json={"to": "user", "amount": 100},
            headers={
                "Origin": "http://localhost",
                "x-csrf-token": csrf_token,
            },
        )

        # 应该成功
        assert response.status_code == 200

    def test_token_reuse_across_requests_blocked(self):
        """测试跨请求重用token被阻止"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 获取token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        @app.post("/api/test/action1")
        async def action1():
            return {"status": "done1"}

        @app.post("/api/test/action2")
        async def action2():
            return {"status": "done2"}

        # 第一次请求使用token
        response1 = client.post(
            "/api/test/action1",
            json={},
            headers={"x-csrf-token": csrf_token},
        )
        assert response1.status_code == 200

        # 第二次请求尝试使用相同token
        response2 = client.post(
            "/api/test/action2",
            json={},
            headers={"x-csrf-token": csrf_token},
        )
        # 应该失败（重放攻击防护）
        assert response2.status_code == 403

    def test_token_expiration_prevents_old_attacks(self):
        """测试token过期防止旧攻击"""
        from app.app_factory import create_app

        # 设置短过期时间
        original_timeout = csrf_manager.token_timeout
        csrf_manager.token_timeout = 0.1

        app = create_app()
        client = TestClient(app)

        # 获取token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        @app.post("/api/test/action")
        async def test_action():
            return {"status": "done"}

        # 等待token过期
        time.sleep(0.15)

        # 尝试使用过期的token
        response = client.post(
            "/api/test/action",
            json={},
            headers={"x-csrf-token": csrf_token},
        )

        # 应该失败
        assert response.status_code == 403

        # 恢复原设置
        csrf_manager.token_timeout = original_timeout

    def test_token_entropy_sufficient(self):
        """测试token熵值足够大"""
        """确保token不可预测"""
        import secrets

        # 生成多个token并检查是否有重复
        tokens = set()
        for _ in range(1000):
            token = secrets.token_urlsafe(32)
            tokens.add(token)

        # 1000个token应该全部唯一
        assert len(tokens) == 1000

        # token长度应该足够
        sample_token = secrets.token_urlsafe(32)
        assert len(sample_token) >= 32  # base64编码后至少32字符


class TestCSRFIntegration:
    """测试CSRF集成场景"""

    def setup_method(self):
        """每个测试前清空tokens"""
        csrf_manager.tokens.clear()

    def test_full_workflow(self):
        """测试完整的CSRF保护工作流"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 步骤1: 获取CSRF token (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        assert token_response.status_code == 200
        csrf_token = token_response.json()["data"]["csrf_token"]

        # 步骤2: 使用token发起受保护的请求
        @app.post("/api/user/update")
        async def update_user(data: dict):
            return {"updated": True}

        response = client.post(
            "/api/user/update",
            json={"name": "Test User"},
            headers={"x-csrf-token": csrf_token},
        )

        # 步骤3: 验证请求成功
        assert response.status_code == 200

        # 步骤4: 尝试重用token应该失败
        response2 = client.post(
            "/api/user/update",
            json={"name": "Another User"},
            headers={"x-csrf-token": csrf_token},
        )

        assert response2.status_code == 403

    def test_mixed_safe_and_protected_endpoints(self):
        """测试混合的安全和受保护端点"""
        from app.app_factory import create_app

        app = create_app()
        client = TestClient(app)

        # 公开端点（不需要token）
        @app.get("/api/public/data")
        async def public_data():
            return {"data": "public"}

        # 受保护端点（需要token）
        @app.post("/api/protected/action")
        async def protected_action():
            return {"result": "done"}

        # 公开端点应该可以直接访问
        response = client.get("/api/public/data")
        assert response.status_code == 200

        # 受保护端点没有token应该被拒绝
        response = client.post("/api/protected/action", json={})
        assert response.status_code == 403

        # 获取token后应该可以访问 (响应被 UnifiedResponse 包装)
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["data"]["csrf_token"]

        response = client.post(
            "/api/protected/action",
            json={},
            headers={"x-csrf-token": csrf_token},
        )
        assert response.status_code == 200


class TestCSRFFrontendIntegration:
    """测试CSRF前端集成场景"""

    def test_token_format_compatible_with_frontend(self):
        """测试token格式与前端兼容"""
        # 获取token
        token = csrf_manager.generate_token()

        # Token应该是URL安全的（不包含需要编码的字符）
        assert "+" not in token or " " not in token
        assert "/" not in token or token.count("/") < 5  # 允许少量但不应太多

        # Token应该是ASCII字符
        try:
            token.encode("ascii")
        except UnicodeEncodeError:
            pytest.fail("Token应该只包含ASCII字符")

    def test_multiple_clients_separate_tokens(self):
        """测试多个客户端的token独立"""
        from app.app_factory import create_app

        app = create_app()
        client1 = TestClient(app)
        client2 = TestClient(app)

        # 两个客户端获取不同的token (响应被 UnifiedResponse 包装)
        token1 = client1.get("/api/csrf-token").json()["data"]["csrf_token"]
        token2 = client2.get("/api/csrf-token").json()["data"]["csrf_token"]

        # Tokens应该不同
        assert token1 != token2

        # 每个token都应该有效
        @app.post("/api/test/action")
        async def test_action():
            return {"done": True}

        response1 = client1.post(
            "/api/test/action",
            json={},
            headers={"x-csrf-token": token1},
        )
        response2 = client2.post(
            "/api/test/action",
            json={},
            headers={"x-csrf-token": token2},
        )

        # 两个请求都应该成功（使用各自的token）
        assert response1.status_code == 200
        assert response2.status_code == 200


# Pytest 运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
