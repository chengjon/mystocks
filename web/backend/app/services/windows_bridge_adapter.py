"""分布式任务调度适配器 (方案 B 扩展)
支持 Windows 下的 Wind, Choice, MiniQMT 多源触发。
"""

from datetime import datetime
from typing import Any, Dict

import httpx

from app.services.data_source_interface import HealthStatus, HealthStatusEnum, IDataSource


logger = __import__("logging").getLogger(__name__)

class MultiSourceBridgeAdapter(IDataSource):
    """多源桥接适配器 - 负责调度远程 Windows 代理"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "distributed_bridge"
        # 节点注册表: { "wind": "http://example.local:8001", "qmt": "http://example.local:8001" }
        self.providers = config.get("providers", {})
        self.timeout = config.get("timeout", 30.0) # 采集可能较慢，增加超时

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """按需触发数据采集逻辑
        
        Args:
            endpoint: 格式为 "provider/method", 如 "wind/wsd" 或 "qmt/position"

        """
        try:
            provider_name, method = endpoint.split("/")
        except ValueError:
            raise ValueError(f"Invalid endpoint format: {endpoint}. Use 'provider/method'.")

        base_url = self.providers.get(provider_name)
        if not base_url:
            raise RuntimeError(f"Provider '{provider_name}' not configured in registry")

        # 发起按需采集指令
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.info(f"🚀 Triggering remote task: {provider_name} via {method}")

            response = await client.post(
                f"{base_url}/api/v1/task/execute",
                json={
                    "method": method,
                    "params": params,
                    "write_to_nas": True, # 强制要求 Windows 端写入 NAS
                },
            )
            response.raise_for_status()
            task_result = response.json()

            # 自动化逻辑：采集完成后，数据已经在 NAS 中
            # 返回任务状态及元数据
            return {
                "status": "success",
                "task_id": task_result.get("task_id"),
                "source": provider_name,
                "timestamp": datetime.now().isoformat(),
            }

    async def health_check(self) -> HealthStatus:
        """检查所有 Provider 的在线状态"""
        results = []
        async with httpx.AsyncClient(timeout=2.0) as client:
            for name, url in self.providers.items():
                try:
                    resp = await client.get(f"{url}/health")
                    if resp.status_code == 200:
                        results.append(f"{name}:OK")
                except:
                    results.append(f"{name}:OFFLINE")

        return HealthStatus(
            status=HealthStatusEnum.HEALTHY if "OK" in "".join(results) else HealthStatusEnum.FAILED,
            response_time=0,
            message=" | ".join(results),
            timestamp=datetime.now(),
        )
