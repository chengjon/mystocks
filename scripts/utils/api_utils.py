import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def call_api(
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    通用API调用函数。

    Args:
        method: HTTP方法 ('GET', 'POST', 'PUT', 'DELETE')。
        url: API完整URL。
        params: URL查询参数。
        json: POST/PUT请求的JSON Body。
        data: POST/PUT请求的表单数据。
        headers: 请求头。
        timeout: 请求超时时间。

    Returns:
        Dict[str, Any]: API响应结果（JSON格式）。

    Raises:
        requests.exceptions.RequestException: 如果请求失败。
    """
    try:
        response = requests.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()  # 检查HTTP响应状态码，如果不是2xx，则抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败 ({method} {url}): {e}")
        raise e


def refresh_data_via_api(
    endpoint: str,
    payload: Dict[str, Any],
    base_url: str = "http://localhost:8000",
    method: str = "POST",
) -> Dict[str, Any]:
    """
    通过API刷新数据的通用函数。

    Args:
        endpoint: API路径（例如："/api/market/lhb/refresh"）。
        payload: 发送给API的参数或数据。
        base_url: API基础URL。
        method: HTTP方法 ('GET', 'POST')。

    Returns:
        Dict[str, Any]: API响应结果。
    """
    url = f"{base_url}{endpoint}"

    try:
        if method.upper() == "POST":
            result = call_api("POST", url, json=payload)
        elif method.upper() == "GET":
            result = call_api("GET", url, params=payload)
        else:
            raise ValueError(f"Unsupported method for refresh_data_via_api: {method}")

        if result.get("success"):
            logger.info(
                f"✅ 数据刷新成功 ({endpoint}): {result.get('message', '成功')}"
            )
        else:
            logger.warning(
                f"⚠️  数据刷新失败 ({endpoint}): {result.get('message', '失败')}"
            )

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 数据刷新请求失败 ({endpoint}): {e}")
        return {"success": False, "message": str(e)}
    except ValueError as e:
        logger.error(f"❌ 数据刷新配置错误: {e}")
        return {"success": False, "message": str(e)}
