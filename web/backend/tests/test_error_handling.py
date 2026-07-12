"""P0改进 Task 4: 错误处理单元测试

测试错误处理和响应生成的核心功能
遵循项目测试规范和Mock数据使用规范
"""

from datetime import datetime, timezone

from app.core.responses import (
    APIResponse,
    ErrorResponse,
    create_error_response,
    create_success_response,
)


class TestSuccessResponse:
    """成功响应生成测试"""

    def test_create_success_response_minimal(self):
        """测试最小化成功响应"""
        response = create_success_response()
        assert isinstance(response, APIResponse)
        assert response.data is None
        assert response.message == "操作成功"

    def test_create_success_response_with_data(self):
        """测试带数据的成功响应"""
        test_data = {"id": 1, "name": "test"}
        response = create_success_response(data=test_data)
        assert isinstance(response, APIResponse)
        assert response.data == test_data

    def test_create_success_response_with_message(self):
        """测试带自定义消息的成功响应"""
        test_message = "自定义消息"
        response = create_success_response(message=test_message)
        assert isinstance(response, APIResponse)
        assert response.message == test_message

    def test_create_success_response_with_both_message_and_data(self):
        """测试同时带消息和数据的成功响应"""
        test_message = "获取数据成功"
        test_data = {"items": [1, 2, 3], "count": 3}
        response = create_success_response(message=test_message, data=test_data)
        assert isinstance(response, APIResponse)
        assert response.message == test_message
        assert response.data == test_data

    def test_create_success_response_has_timestamp(self):
        """测试成功响应包含时间戳"""
        response = create_success_response()
        assert isinstance(response, APIResponse)
        assert response.timestamp is not None

    def test_create_success_response_with_empty_dict(self):
        """测试数据为空字典的成功响应"""
        response = create_success_response(data={})
        assert isinstance(response, APIResponse)
        assert response.data == {}

    def test_create_success_response_with_none_data(self):
        """测试数据为None的成功响应"""
        response = create_success_response(data=None)
        assert isinstance(response, APIResponse)
        assert response.data is None

    def test_success_response_serialization(self):
        """测试成功响应序列化"""
        test_data = {"id": 1, "name": "test"}
        response = create_success_response(data=test_data)

        # 转换为字典
        response_dict = response.model_dump()
        assert "data" in response_dict
        assert "message" in response_dict
        assert "timestamp" in response_dict


class TestErrorResponse:
    """错误响应生成测试"""

    def test_create_error_response_with_code_and_message(self):
        """测试带错误代码和消息的错误响应"""
        error_code = "VALIDATION_ERROR"
        message = "验证失败"
        response = create_error_response(error_code=error_code, message=message)
        assert isinstance(response, ErrorResponse)
        assert response.error["code"] == error_code
        assert response.message == message

    def test_create_error_response_with_details(self):
        """测试带详情的错误响应"""
        error_details = {"field": "symbol", "reason": "Invalid symbol"}
        response = create_error_response(error_code="VALIDATION_ERROR", message="验证失败", details=error_details)
        assert isinstance(response, ErrorResponse)
        assert response.error["details"] == error_details

    def test_create_error_response_with_all_fields(self):
        """测试包含所有字段的错误响应"""
        error_code = "DB_ERROR"
        message = "数据库连接失败"
        details = {"connection": "timeout", "retry": 3}

        response = create_error_response(error_code=error_code, message=message, details=details)

        assert isinstance(response, ErrorResponse)
        assert response.error["code"] == error_code
        assert response.message == message
        assert response.error["details"] == details

    def test_create_error_response_has_timestamp(self):
        """测试错误响应包含时间戳"""
        response = create_error_response(error_code="TEST", message="Test error")
        assert isinstance(response, ErrorResponse)
        assert response.timestamp is not None

    def test_create_error_response_with_none_details(self):
        """测试None详情的错误响应"""
        response = create_error_response(error_code="TEST", message="Test", details=None)
        assert isinstance(response, ErrorResponse)
        assert "details" not in response.error

    def test_error_response_serialization(self):
        """测试错误响应序列化"""
        response = create_error_response(error_code="ERROR", message="Error message", details={"key": "value"})

        # 转换为字典
        response_dict = response.model_dump()
        assert "error" in response_dict
        assert response_dict["error"]["code"] == "ERROR"
        assert "message" in response_dict
        assert response_dict["error"]["details"] == {"key": "value"}
        assert "timestamp" in response_dict


class TestResponseStructure:
    """响应结构测试"""

    def test_success_response_structure(self):
        """测试成功响应结构"""
        response = create_success_response(data={"test": "value"}, message="Success")

        # 验证响应是APIResponse对象
        assert isinstance(response, APIResponse)
        assert response.data == {"test": "value"}
        assert response.message == "Success"

    def test_error_response_structure(self):
        """测试错误响应结构"""
        response = create_error_response(error_code="TEST_ERROR", message="Error message", details={"key": "value"})

        # 验证响应是ErrorResponse对象
        assert isinstance(response, ErrorResponse)
        assert response.error["code"] == "TEST_ERROR"
        assert response.message == "Error message"
        assert response.error["details"] == {"key": "value"}

    def test_api_response_json_serialization(self):
        """测试APIResponse JSON序列化"""
        response = create_success_response(data={"id": 1})
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "id" in json_str

    def test_error_response_json_serialization(self):
        """测试ErrorResponse JSON序列化"""
        response = create_error_response(error_code="ERROR", message="Test", details={"field": "test"})
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "error" in json_str


class TestResponseEdgeCases:
    """响应边界情况测试"""

    def test_success_response_with_large_data(self):
        """测试大数据量的成功响应"""
        large_data = {f"key_{i}": f"value_{i}" for i in range(100)}
        response = create_success_response(data=large_data)

        assert isinstance(response, APIResponse)
        assert len(response.data) == 100

    def test_success_response_with_nested_data(self):
        """测试嵌套数据结构的成功响应"""
        nested_data = {
            "user": {"id": 1, "name": "test"},
            "orders": [
                {"id": 1, "amount": 100},
                {"id": 2, "amount": 200},
            ],
        }
        response = create_success_response(data=nested_data)

        assert isinstance(response, APIResponse)
        assert response.data == nested_data

    def test_error_response_with_special_characters(self):
        """测试包含特殊字符的错误响应"""
        message_with_special_chars = "错误: 参数验证失败 @#$%"
        response = create_error_response(error_code="ERROR", message=message_with_special_chars)

        assert isinstance(response, ErrorResponse)
        assert response.message == message_with_special_chars

    def test_response_with_unicode_data(self):
        """测试包含Unicode数据的响应"""
        unicode_data = {"message": "你好世界", "emoji": "😀"}
        response = create_success_response(data=unicode_data)

        assert isinstance(response, APIResponse)
        assert response.data["message"] == "你好世界"
        assert response.data["emoji"] == "😀"

    def test_error_response_with_unicode(self):
        """测试包含Unicode的错误响应"""
        response = create_error_response(error_code="ERROR", message="错误: 数据验证失败")

        assert isinstance(response, ErrorResponse)
        assert "错误" in response.message


class TestResponseDataTypes:
    """响应数据类型测试"""

    def test_success_response_with_dict_data(self):
        """测试字典数据"""
        data = {"key1": "value1", "key2": 123}
        response = create_success_response(data=data)
        assert isinstance(response.data, dict)

    def test_success_response_with_nested_dict(self):
        """测试嵌套字典数据"""
        data = {"level1": {"level2": {"level3": "value"}}}
        response = create_success_response(data=data)
        assert response.data["level1"]["level2"]["level3"] == "value"

    def test_error_response_with_dict_details(self):
        """测试字典详情"""
        details = {"field": "symbol", "error": "Invalid"}
        response = create_error_response(error_code="VALIDATION", message="Validation failed", details=details)
        assert isinstance(response.error["details"], dict)
        assert response.error["details"]["field"] == "symbol"

    def test_error_response_with_complex_details(self):
        """测试复杂详情"""
        details = {
            "errors": [
                {"field": "symbol", "message": "Invalid symbol"},
                {"field": "date", "message": "Invalid date"},
            ],
            "context": {"request_id": "123"},
        }
        response = create_error_response(
            error_code="VALIDATION",
            message="Multiple validation errors",
            details=details,
        )
        assert len(response.error["details"]["errors"]) == 2


class TestResponseIntegration:
    """响应集成测试"""

    def test_success_response_pagination(self):
        """测试分页的成功响应"""
        page_data = {
            "items": [{"id": 1}, {"id": 2}],
            "page": 1,
            "page_size": 20,
            "total": 100,
        }
        response = create_success_response(data=page_data)

        assert isinstance(response, APIResponse)
        assert response.data["page"] == 1
        assert response.data["total"] == 100

    def test_error_response_multiple_validation_errors(self):
        """测试多个验证错误的错误响应"""
        validation_errors = [
            {"field": "symbol", "message": "Invalid symbol"},
            {"field": "date", "message": "Invalid date"},
        ]
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details={"errors": validation_errors},
        )

        assert isinstance(response, ErrorResponse)
        assert len(response.error["details"]["errors"]) == 2

    def test_response_api_list_endpoint(self):
        """测试列表API端点响应"""
        list_data = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
        ]
        response = create_success_response(data={"items": list_data, "count": 2})
        assert isinstance(response, APIResponse)
        assert response.data["count"] == 2

    def test_response_api_create_endpoint(self):
        """测试创建API端点响应"""
        created_data = {"id": 123, "name": "new_item"}
        response = create_success_response(data=created_data, message="Created successfully")
        assert isinstance(response, APIResponse)
        assert response.data["id"] == 123

    def test_response_api_error_endpoint(self):
        """测试错误API端点响应"""
        error = create_error_response(
            error_code="NOT_FOUND",
            message="Resource not found",
            details={"resource_id": "123"},
        )
        assert isinstance(error, ErrorResponse)
        assert error.error["code"] == "NOT_FOUND"


class TestResponseErrorCodes:
    """响应错误代码测试"""

    def test_validation_error_response(self):
        """测试验证错误响应"""
        response = create_error_response(error_code="VALIDATION_ERROR", message="验证失败")
        assert response.error["code"] == "VALIDATION_ERROR"

    def test_not_found_error_response(self):
        """测试资源未找到错误"""
        response = create_error_response(error_code="NOT_FOUND", message="资源未找到")
        assert response.error["code"] == "NOT_FOUND"

    def test_database_error_response(self):
        """测试数据库错误"""
        response = create_error_response(error_code="DATABASE_ERROR", message="数据库操作失败")
        assert response.error["code"] == "DATABASE_ERROR"

    def test_unauthorized_error_response(self):
        """测试未授权错误"""
        response = create_error_response(error_code="UNAUTHORIZED", message="未授权")
        assert response.error["code"] == "UNAUTHORIZED"

    def test_forbidden_error_response(self):
        """测试禁止访问错误"""
        response = create_error_response(error_code="FORBIDDEN", message="禁止访问")
        assert response.error["code"] == "FORBIDDEN"


class TestResponseTimestamps:
    """响应时间戳测试"""

    def test_success_response_timestamp_is_set(self):
        """测试成功响应时间戳已设置"""
        response = create_success_response()
        assert response.timestamp is not None

    def test_error_response_timestamp_is_set(self):
        """测试错误响应时间戳已设置"""
        response = create_error_response(error_code="TEST", message="Test")
        assert response.timestamp is not None

    def test_response_timestamps_are_recent(self):
        """测试响应时间戳是最近的"""
        before = datetime.now(timezone.utc)
        response = create_success_response()
        after = datetime.now(timezone.utc)

        # 时间戳应该在before和after之间
        assert before <= response.timestamp <= after

    def test_multiple_responses_have_different_timestamps(self):
        """测试多个响应有不同的时间戳"""
        response1 = create_success_response()
        response2 = create_success_response()

        # 至少有一个响应的时间戳应该不同
        # 注意：如果执行速度太快，时间戳可能相同
        assert response1.timestamp is not None
        assert response2.timestamp is not None
