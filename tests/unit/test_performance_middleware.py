import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../web/backend")))

from app.main import app

client = TestClient(app)

def test_performance_headers():
    """验证响应头中是否包含性能追踪信息"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
    print(f"✓ Found headers: Request-ID={response.headers['x-request-id']}, Process-Time={response.headers['x-process-time']}")

def test_unified_response_format():
    """验证响应是否被正确包装为 UnifiedResponse"""
    response = client.get("/api/v1/auth/me")
    # Even if 401 (Unauthorized), it should be wrapped
    data = response.json()
    assert "success" in data
    assert "request_id" in data
    print(f"✓ Unified format verified: success={data['success']}, request_id={data['request_id']}")

if __name__ == "__main__":
    test_performance_headers()
    test_unified_response_format()
