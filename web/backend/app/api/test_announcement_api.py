"""
测试公告API端点
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.announcement import Announcement, AnnouncementMonitorRule, Base
from app.services.announcement_service import get_announcement_service


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_announcement.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_announcement_stats(client):
    """测试公告统计API"""
    response = client.get("/api/announcement/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "today_count" in data
    assert "important_count" in data


def test_get_announcement_types(client):
    """测试获取公告类型API"""
    response = client.get("/api/announcement/types")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "types" in data


def test_get_announcements(client):
    """测试获取公告列表API"""
    response = client.get("/api/announcement/list")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    assert "total" in data


def test_get_today_announcements(client):
    """测试获取今日公告API"""
    response = client.get("/api/announcement/today")
    assert response.status_code == 200


def test_get_important_announcements(client):
    """测试获取重要公告API"""
    response = client.get("/api/announcement/important")
    assert response.status_code == 200


def test_monitor_rules_crud(client):
    """测试监控规则的CRUD操作"""
    # 创建规则
    rule_data = {
        "rule_name": "测试监控规则",
        "keywords": ["测试", "公告"],
        "announcement_types": [],
        "stock_codes": ["000001"],
        "min_importance_level": 3,
        "notify_enabled": True,
        "notify_channels": ["email"]
    }
    
    # 创建
    response = client.post("/api/announcement/monitor-rules", json=rule_data)
    assert response.status_code == 200
    created_rule = response.json()
    assert created_rule["rule_name"] == "测试监控规则"
    rule_id = created_rule["id"]
    
    # 获取规则列表
    response = client.get("/api/announcement/monitor-rules")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) >= 1
    
    # 更新规则
    update_data = {
        "rule_name": "更新的测试监控规则",
        "min_importance_level": 4
    }
    response = client.put(f"/api/announcement/monitor-rules/{rule_id}", json=update_data)
    assert response.status_code == 200
    updated_rule = response.json()
    assert updated_rule["rule_name"] == "更新的测试监控规则"
    
    # 删除规则
    response = client.delete(f"/api/announcement/monitor-rules/{rule_id}")
    assert response.status_code == 200


def test_evaluate_monitor_rules(client):
    """测试评估监控规则API"""
    response = client.post("/api/announcement/monitor/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data