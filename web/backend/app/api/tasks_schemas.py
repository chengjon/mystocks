"""
任务管理 API 请求模型定义。
"""

import json
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TaskRegistrationRequest(BaseModel):
    """任务注册请求"""

    name: str = Field(..., description="任务名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="任务描述", max_length=500)
    task_type: str = Field(
        ...,
        description="任务类型",
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    )
    config: Dict[str, Any] = Field(..., description="任务配置参数")
    tags: Optional[List[str]] = Field(None, description="任务标签")
    enabled: bool = Field(True, description="是否启用")
    schedule: Optional[str] = Field(None, description="调度表达式(cron格式)", max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """验证任务名称"""
        if not value.strip():
            raise ValueError("任务名称不能为空")
        if re.search(r'[<>"\'/\\]', value):
            raise ValueError("任务名称不能包含特殊字符: < > \" ' / \\")
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        """验证任务描述"""
        if value is None:
            return value
        if re.search(r"<script|javascript:|onload=|onerror=", value, re.IGNORECASE):
            raise ValueError("任务描述包含不安全的脚本或标签")
        return value.strip()

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        """验证任务配置"""
        if not value:
            raise ValueError("任务配置不能为空")
        if len(json.dumps(value)) > 10000:
            raise ValueError("任务配置过大，请减小配置内容")

        config_str = json.dumps(value).lower()
        dangerous_patterns = [
            "__import__",
            "eval(",
            "exec(",
            "subprocess",
            "os.system",
            "popen",
            "shell=True",
            "$(",
            "&&",
            "||",
            ";",
            "><",
            "`",
        ]
        for pattern in dangerous_patterns:
            if pattern in config_str:
                raise ValueError(f"任务配置包含不安全的操作: {pattern}")

        for pattern in ["/etc/", "/bin/", "/usr/bin", "/var/", "system32"]:
            if pattern in config_str:
                raise ValueError(f"任务配置包含不安全的路径操作: {pattern}")

        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """验证任务标签"""
        if value is None:
            return value
        if len(value) > 10:
            raise ValueError("任务标签数量不能超过10个")

        for tag in value:
            if not tag:
                raise ValueError("标签不能为空")
            if len(tag) > 20:
                raise ValueError(f'标签 "{tag}" 长度超过限制')
            if re.search(r'[<>"\'/\\]', tag):
                raise ValueError(f'标签 "{tag}" 包含特殊字符')

        return [tag.strip() for tag in value]

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: Optional[str]) -> Optional[str]:
        """验证调度表达式"""
        if value is None:
            return value

        cron_pattern = (
            r"^(\*|([0-9]|[1-5][0-9])\/\d+|([0-9]|[1-5][0-9])|"
            r"([0-9]|[1-5][0-9])-([0-9]|[1-5][0-9])|"
            r"([0-9]|[1-5][0-9])(,([0-9]|[1-5][0-9]))*)\s+"
            r"(\*|([0-9]|1[0-9]|2[0-3])\/\d+|([0-9]|1[0-9]|2[0-3])|"
            r"([0-9]|1[0-9]|2[0-3])-([0-9]|1[0-9]|2[0-3])|"
            r"([0-9]|1[0-9]|2[0-3])(,([0-9]|1[0-9]|2[0-3]))*)\s+"
            r"(\*|([1-9]|[1-2][0-9]|3[0-1])\/\d+|([1-9]|[1-2][0-9]|3[0-1])|"
            r"([1-9]|[1-2][0-9]|3[0-1])-([1-9]|[1-2][0-9]|3[0-1])|"
            r"([1-9]|[1-2][0-9]|3[0-1])(,([1-9]|[1-2][0-9]|3[0-1]))*)\s+"
            r"(\*|([1-9]|1[0-2])\/\d+|([1-9]|1[0-2])|"
            r"([1-9]|1[0-2])-([1-9]|1[0-2])|([1-9]|1[0-2])(,([1-9]|1[0-2]))*)\s+"
            r"(\*|([0-6])\/\d+|([0-6])|([0-6])-([0-6])|([0-6])(,([0-6]))*)$"
        )
        if not re.match(cron_pattern, value):
            raise ValueError("无效的cron表达式格式")
        return value


class TaskQueryParams(BaseModel):
    """任务查询参数"""

    task_type: Optional[str] = Field(
        None,
        description="任务类型",
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    )
    tags: Optional[str] = Field(None, description="逗号分隔的任务标签", max_length=200)
    status: Optional[str] = Field(None, description="任务状态", pattern=r"^(PENDING|RUNNING|SUCCESS|FAILED|CANCELLED)$")
    enabled: Optional[bool] = Field(None, description="是否启用")
    limit: int = Field(50, description="返回数量", ge=1, le=200)
    offset: int = Field(0, description="偏移量", ge=0, le=10000)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[str]) -> Optional[str]:
        """验证标签参数"""
        if value is None:
            return value

        tags = value.split(",")
        if len(tags) > 10:
            raise ValueError("查询标签数量不能超过10个")
        for tag in tags:
            tag = tag.strip()
            if not tag:
                raise ValueError("标签不能为空")
            if len(tag) > 20:
                raise ValueError(f'标签 "{tag}" 长度超过限制')
        return value


class TaskExecutionRequest(BaseModel):
    """任务执行请求"""

    task_id: str = Field(..., description="任务ID", min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    force: bool = Field(False, description="是否强制执行")
    params: Optional[Dict[str, Any]] = Field(None, description="执行参数")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, value: str) -> str:
        """验证任务ID"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError("任务ID只能包含字母、数字、下划线和连字符")
        return value
