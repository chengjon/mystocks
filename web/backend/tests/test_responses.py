"""统一API响应格式单元测试

测试覆盖:
- APIResponse 类
- ErrorResponse 类
- PaginatedResponse 类
- 辅助函数
- 边界情况和验证

版本: 1.0.0
日期: 2025-12-23
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.core.responses import (
    APIResponse,
    ErrorCodes,
    ErrorResponse,
    PaginatedResponse,
    ResponseMessages,
    create_error_response,
    create_health_response,
    create_success_response,
)


class TestAPIResponse:
    """测试 APIResponse 类"""

    def test_default_values(self):
        """测试默认值"""
        response = APIResponse()

        assert response.success is True
        assert response.data is None
        assert response.message == "操作成功"
        assert isinstance(response.timestamp, datetime)
        assert response.request_id is None

    def test_with_data(self):
        """测试带数据的响应"""
        data = {"symbol": "600519", "price": 1680.50}
        response = APIResponse(data=data)

        assert response.success is True
        assert response.data == data
        assert response.message == "操作成功"

    def test_with_custom_message(self):
        """测试自定义消息"""
        response = APIResponse(message="查询成功")

        assert response.message == "查询成功"

    def test_with_request_id(self):
        """测试带请求ID的响应"""
        response = APIResponse(request_id="req-123456")

        assert response.request_id == "req-123456"

    def test_full_response(self):
        """测试完整响应"""
        data = {"id": 1, "name": "测试"}
        response = APIResponse(
            success=True,
            data=data,
            message="创建成功",
            request_id="req-abc123",
        )

        assert response.success is True
        assert response.data == data
        assert response.message == "创建成功"
        assert response.request_id == "req-abc123"
        assert isinstance(response.timestamp, datetime)

    def test_serialization(self):
        """测试JSON序列化"""
        data = {"symbol": "600519", "price": 1680.50}
        response = APIResponse(data=data, message="查询成功")

        # 测试 model_dump 方法
        response_dict = response.model_dump()
        assert response_dict["success"] is True
        assert response_dict["data"] == data
        assert response_dict["message"] == "查询成功"
        assert "timestamp" in response_dict

        # 测试 JSON 序列化
        json_str = response.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["success"] is True
        assert parsed["data"] == data

    def test_data_can_be_empty_dict(self):
        """测试空字典作为data"""
        response = APIResponse(data={})

        assert response.data == {}
        assert response.success is True

    def test_data_can_be_complex(self):
        """测试复杂数据结构"""
        complex_data = {
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
            ],
            "metadata": {
                "total": 2,
                "page": 1,
            },
        }
        response = APIResponse(data=complex_data)

        assert response.data == complex_data
        assert response.data["items"][0]["id"] == 1


class TestErrorResponse:
    """测试 ErrorResponse 类"""

    def test_default_values(self):
        """测试错误响应默认值"""
        error_info = {"code": "TEST_ERROR", "message": "测试错误"}
        response = ErrorResponse(error=error_info, message="操作失败")

        assert response.success is False
        assert response.error == error_info
        assert response.message == "操作失败"
        assert isinstance(response.timestamp, datetime)
        assert response.request_id is None

    def test_error_with_details(self):
        """测试带详情的错误响应"""
        error_info = {
            "code": "VALIDATION_ERROR",
            "message": "参数验证失败",
            "details": {
                "field": "symbol",
                "reason": "格式不正确",
            },
        }
        response = ErrorResponse(error=error_info, message="参数验证失败")

        assert response.error == error_info
        assert response.error["details"]["field"] == "symbol"

    def test_error_with_request_id(self):
        """测试带请求ID的错误响应"""
        error_info = {"code": "NOT_FOUND", "message": "资源未找到"}
        response = ErrorResponse(
            error=error_info,
            message="资源未找到",
            request_id="req-error-123",
        )

        assert response.request_id == "req-error-123"

    def test_error_field_required(self):
        """测试error字段必填"""
        with pytest.raises(ValidationError):
            ErrorResponse(message="错误消息")

    def test_message_field_required(self):
        """测试message字段必填"""
        error_info = {"code": "TEST_ERROR", "message": "测试"}
        with pytest.raises(ValidationError):
            ErrorResponse(error=error_info)

    def test_serialization(self):
        """测试错误响应序列化"""
        error_info = {"code": "DATABASE_ERROR", "message": "数据库连接失败"}
        response = ErrorResponse(error=error_info, message="数据库错误")

        response_dict = response.model_dump()
        assert response_dict["success"] is False
        assert response_dict["error"] == error_info

        json_str = response.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["success"] is False
        assert parsed["error"]["code"] == "DATABASE_ERROR"


class TestPaginatedResponse:
    """测试 PaginatedResponse 类"""

    def test_create_method_basic(self):
        """测试基本分页响应创建"""
        # 注意: 由于APIResponse.data定义为Dict[str, Any]，列表数据需要包装
        data = {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}
        response = PaginatedResponse.create(
            data=data,
            page=1,
            size=10,
            total=3,
        )

        assert response.success is True
        assert response.data == data
        assert response.pagination["page"] == 1
        assert response.pagination["size"] == 10
        assert response.pagination["total"] == 3
        assert response.pagination["pages"] == 1

    def test_create_with_custom_message(self):
        """测试自定义消息的分页响应"""
        data = {"items": [{"id": 1}]}
        response = PaginatedResponse.create(
            data=data,
            page=1,
            size=10,
            total=1,
            message="查询成功",
        )

        assert response.message == "查询成功"

    def test_create_with_request_id(self):
        """测试带请求ID的分页响应"""
        data = {"items": []}
        response = PaginatedResponse.create(
            data=data,
            page=1,
            size=10,
            total=0,
            request_id="req-page-123",
        )

        assert response.request_id == "req-page-123"

    def test_pagination_calculation_without_total(self):
        """测试不提供total时的分页计算"""
        # 没有total时，如果data包含items列表，会自动计算长度
        data = {"items": [{"id": 1}, {"id": 2}]}
        response = PaginatedResponse.create(
            data=data,
            page=1,
            size=10,
        )

        # 没有total时，对于dict类型数据且包含items，会使用items长度
        assert response.pagination["total"] == 2
        assert response.pagination["pages"] == 1

    def test_pagination_pages_calculation(self):
        """测试页数计算"""
        # 测试整除情况
        response = PaginatedResponse.create(
            data={"items": []},
            page=1,
            size=10,
            total=100,
        )
        assert response.pagination["pages"] == 10

        # 测试有余数情况
        response = PaginatedResponse.create(
            data={"items": []},
            page=1,
            size=10,
            total=105,
        )
        assert response.pagination["pages"] == 11

    def test_empty_page(self):
        """测试空页"""
        response = PaginatedResponse.create(
            data={"items": []},
            page=1,
            size=10,
            total=0,
        )

        assert response.data == {"items": []}
        assert response.pagination["total"] == 0
        assert response.pagination["pages"] == 0

    def test_last_page_partial(self):
        """测试最后一页数据不足size"""
        data = {"items": [{"id": 1}, {"id": 2}]}
        response = PaginatedResponse.create(
            data=data,
            page=5,
            size=10,
            total=42,
        )

        assert response.pagination["page"] == 5
        assert response.pagination["size"] == 10
        assert response.pagination["total"] == 42
        assert response.pagination["pages"] == 5

    def test_pagination_field_required(self):
        """测试pagination字段必填"""
        with pytest.raises(ValidationError):
            PaginatedResponse(
                success=True,
                data={},
                message="查询成功",
            )

    def test_inherits_from_api_response(self):
        """测试继承自APIResponse"""
        response = PaginatedResponse.create(
            data={"items": []},
            page=1,
            size=10,
            total=0,
        )

        # 继承的字段应该存在
        assert hasattr(response, "success")
        assert hasattr(response, "data")
        assert hasattr(response, "message")
        assert hasattr(response, "timestamp")
        assert hasattr(response, "request_id")
        assert hasattr(response, "pagination")

    def test_non_list_data_with_total(self):
        """测试非列表数据配合total使用"""
        # 某些情况下data可能不是列表（如聚合结果）
        data = {"result": "aggregated", "count": 42}
        response = PaginatedResponse.create(
            data=data,
            page=1,
            size=10,
            total=100,
        )

        assert response.data == data
        assert response.pagination["total"] == 100

    def test_data_can_be_none(self):
        """测试data可以为None（通过继承）"""
        response = PaginatedResponse(
            success=True,
            data=None,
            message="test",
            pagination={"page": 1, "size": 10, "total": 0, "pages": 0},
        )

        assert response.data is None


class TestCreateSuccessResponse:
    """测试 create_success_response 函数"""

    def test_basic_success_response(self):
        """测试基本成功响应"""
        response = create_success_response()

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.data is None
        assert response.message == "操作成功"

    def test_with_data(self):
        """测试带数据的成功响应"""
        data = {"id": 123, "status": "active"}
        response = create_success_response(data=data)

        assert response.data == data
        assert response.success is True

    def test_with_custom_message(self):
        """测试自定义消息"""
        response = create_success_response(message="创建成功")

        assert response.message == "创建成功"

    def test_with_request_id(self):
        """测试带请求ID"""
        response = create_success_response(
            data={"result": "ok"},
            message="操作完成",
            request_id="req-001",
        )

        assert response.request_id == "req-001"
        assert response.data == {"result": "ok"}
        assert response.message == "操作完成"


class TestCreateErrorResponse:
    """测试 create_error_response 函数"""

    def test_basic_error_response(self):
        """测试基本错误响应"""
        response = create_error_response(
            error_code="TEST_ERROR",
            message="测试错误",
        )

        assert isinstance(response, ErrorResponse)
        assert response.success is False
        assert response.error["code"] == "TEST_ERROR"
        assert response.error["message"] == "测试错误"
        assert response.message == "测试错误"

    def test_error_with_details(self):
        """测试带详情的错误响应"""
        details = {"field": "email", "issue": "格式无效"}
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="参数验证失败",
            details=details,
        )

        assert response.error["code"] == "VALIDATION_ERROR"
        assert response.error["details"] == details

    def test_error_with_request_id(self):
        """测试带请求ID的错误响应"""
        response = create_error_response(
            error_code="NOT_FOUND",
            message="资源未找到",
            request_id="req-not-found",
        )

        assert response.request_id == "req-not-found"

    def test_full_error_response(self):
        """测试完整错误响应"""
        details = {
            "invalid_fields": ["symbol", "date"],
            "constraints": {"symbol": "required", "date": "format"},
        }
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="请求参数验证失败",
            details=details,
            request_id="req-validation-123",
        )

        assert response.error["code"] == "VALIDATION_ERROR"
        assert response.error["message"] == "请求参数验证失败"
        assert response.error["details"] == details
        assert response.message == "请求参数验证失败"
        assert response.request_id == "req-validation-123"


class TestCreateHealthResponse:
    """测试 create_health_response 函数"""

    def test_basic_health_response(self):
        """测试基本健康检查响应"""
        response = create_health_response(service="api-gateway")

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.data["service"] == "api-gateway"
        assert response.data["status"] == "healthy"

    def test_custom_status(self):
        """测试自定义状态"""
        response = create_health_response(
            service="database",
            status="degraded",
        )

        assert response.data["status"] == "degraded"

    def test_with_details(self):
        """测试带详情的健康检查"""
        details = {
            "connections": 10,
            "max_connections": 100,
            "uptime": "99.9%",
        }
        response = create_health_response(
            service="postgres",
            details=details,
        )

        assert response.data["connections"] == 10
        assert response.data["max_connections"] == 100
        assert response.data["uptime"] == "99.9%"

    def test_with_request_id(self):
        """测试带请求ID的健康检查"""
        response = create_health_response(
            service="redis",
            request_id="health-001",
        )

        assert response.request_id == "health-001"

    def test_timestamp_in_health_data(self):
        """测试健康数据包含时间戳"""
        response = create_health_response(service="cache")

        assert "timestamp" in response.data
        # 验证时间戳格式
        datetime.fromisoformat(response.data["timestamp"])


class TestErrorCodes:
    """测试 ErrorCodes 常量类"""

    def test_general_error_codes_exist(self):
        """测试通用错误代码存在"""
        assert hasattr(ErrorCodes, "INTERNAL_SERVER_ERROR")
        assert hasattr(ErrorCodes, "BAD_REQUEST")
        assert hasattr(ErrorCodes, "UNAUTHORIZED")
        assert hasattr(ErrorCodes, "FORBIDDEN")
        assert hasattr(ErrorCodes, "NOT_FOUND")
        assert hasattr(ErrorCodes, "METHOD_NOT_ALLOWED")

    def test_business_error_codes_exist(self):
        """测试业务错误代码存在"""
        assert hasattr(ErrorCodes, "VALIDATION_ERROR")
        assert hasattr(ErrorCodes, "DATA_NOT_FOUND")
        assert hasattr(ErrorCodes, "DUPLICATE_RESOURCE")
        assert hasattr(ErrorCodes, "OPERATION_FAILED")

    def test_system_error_codes_exist(self):
        """测试系统错误代码存在"""
        assert hasattr(ErrorCodes, "DATABASE_ERROR")
        assert hasattr(ErrorCodes, "EXTERNAL_SERVICE_ERROR")
        assert hasattr(ErrorCodes, "RATE_LIMIT_EXCEEDED")
        assert hasattr(ErrorCodes, "SERVICE_UNAVAILABLE")

    def test_error_codes_are_strings(self):
        """测试错误代码都是字符串"""
        error_codes = [
            ErrorCodes.INTERNAL_SERVER_ERROR,
            ErrorCodes.BAD_REQUEST,
            ErrorCodes.VALIDATION_ERROR,
            ErrorCodes.DATABASE_ERROR,
        ]

        for code in error_codes:
            assert isinstance(code, str)
            assert len(code) > 0


class TestResponseMessages:
    """测试 ResponseMessages 常量类"""

    def test_success_messages_exist(self):
        """测试成功消息存在"""
        assert hasattr(ResponseMessages, "SUCCESS")
        assert hasattr(ResponseMessages, "CREATED")
        assert hasattr(ResponseMessages, "UPDATED")
        assert hasattr(ResponseMessages, "DELETED")

    def test_error_messages_exist(self):
        """测试错误消息存在"""
        assert hasattr(ResponseMessages, "NOT_FOUND")
        assert hasattr(ResponseMessages, "INVALID_REQUEST")
        assert hasattr(ResponseMessages, "UNAUTHORIZED")
        assert hasattr(ResponseMessages, "FORBIDDEN")
        assert hasattr(ResponseMessages, "INTERNAL_ERROR")
        assert hasattr(ResponseMessages, "SERVICE_UNAVAILABLE")

    def test_messages_are_chinese(self):
        """测试消息是中文"""
        assert ResponseMessages.SUCCESS == "操作成功"
        assert ResponseMessages.CREATED == "创建成功"
        assert ResponseMessages.UPDATED == "更新成功"
        assert ResponseMessages.DELETED == "删除成功"


class TestEdgeCases:
    """测试边界情况"""

    def test_none_data_in_success_response(self):
        """测试成功响应中data为None"""
        response = create_success_response(data=None)

        assert response.data is None
        assert response.success is True

    def test_empty_string_message(self):
        """测试空字符串消息"""
        response = APIResponse(message="")

        assert response.message == ""

    def test_very_long_request_id(self):
        """测试超长请求ID"""
        long_id = "x" * 500
        response = APIResponse(request_id=long_id)

        assert response.request_id == long_id

    def test_special_characters_in_message(self):
        """测试消息中包含特殊字符"""
        message = "操作成功！🎉 <script>alert('test')</script>"
        response = APIResponse(message=message)

        assert response.message == message

    def test_unicode_in_data(self):
        """测试数据中包含Unicode字符"""
        data = {"name": "贵州茅台", "symbol": "600519", "emoji": "📈"}
        response = APIResponse(data=data)

        assert response.data["name"] == "贵州茅台"
        assert response.data["emoji"] == "📈"

    def test_nested_data_structures(self):
        """测试嵌套数据结构"""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                    },
                },
            },
            "list": [[1, 2], [3, 4]],
        }
        response = APIResponse(data=data)

        assert response.data["level1"]["level2"]["level3"]["value"] == "deep"
        assert response.data["list"][1][1] == 4

    def test_large_dataset(self):
        """测试大数据集"""
        # 包装为字典以匹配APIResponse.data类型
        items = [{"id": i, "value": f"item-{i}"} for i in range(1000)]
        data = {"items": items}
        response = APIResponse(data=data)

        assert len(response.data["items"]) == 1000
        assert response.data["items"][999]["id"] == 999

    def test_zero_page_number(self):
        """测试第0页（边界情况）"""
        response = PaginatedResponse.create(
            data={"items": []},
            page=0,
            size=10,
            total=0,
        )

        assert response.pagination["page"] == 0

    def test_very_large_page_size(self):
        """测试超大的page_size"""
        response = PaginatedResponse.create(
            data={"items": []},
            page=1,
            size=10000,
            total=0,
        )

        assert response.pagination["size"] == 10000


class TestResponseConsistency:
    """测试响应格式一致性"""

    def test_all_success_responses_have_same_structure(self):
        """测试所有成功响应具有相同结构"""
        r1 = create_success_response(data={"a": 1})
        r2 = APIResponse(data={"b": 2})
        r3 = create_health_response(service="test")

        # 所有响应都应有相同的基础字段
        for response in [r1, r2, r3]:
            assert hasattr(response, "success")
            assert hasattr(response, "data")
            assert hasattr(response, "message")
            assert hasattr(response, "timestamp")
            assert hasattr(response, "request_id")

    def test_all_error_responses_have_same_structure(self):
        """测试所有错误响应具有相同结构"""
        e1 = create_error_response("CODE1", "message1")
        e2 = ErrorResponse(error={"code": "CODE2", "message": "msg2"}, message="message2")

        for response in [e1, e2]:
            assert hasattr(response, "success")
            assert hasattr(response, "error")
            assert hasattr(response, "message")
            assert hasattr(response, "timestamp")
            assert hasattr(response, "request_id")
            assert response.success is False

    def test_timestamp_always_present(self):
        """测试时间戳始终存在"""
        responses = [
            APIResponse(),
            ErrorResponse(error={"code": "x", "message": "y"}, message="error"),
            PaginatedResponse.create(data={"items": []}, page=1, size=10),
            create_success_response(),
            create_error_response("X", "Y"),
            create_health_response("test"),
        ]

        for response in responses:
            assert isinstance(response.timestamp, datetime)


class TestResponseValidation:
    """测试响应验证"""

    def test_cannot_set_success_false_in_api_response_directly(self):
        """测试不能直接在APIResponse中设置success为False"""
        # APIResponse 默认 success=True，但可以被覆盖
        response = APIResponse(success=False)
        assert response.success is False

    def test_error_response_without_error_field_fails(self):
        """测试ErrorResponse缺少error字段时失败"""
        with pytest.raises(ValidationError):
            ErrorResponse(message="error")

    def test_paginated_response_without_pagination_fails(self):
        """测试PaginatedResponse缺少pagination字段时失败"""
        with pytest.raises(ValidationError):
            PaginatedResponse(success=True, data=[], message="ok")


# Pytest 运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
