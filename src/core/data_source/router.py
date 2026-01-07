    def find_endpoints(
        self,
        data_category: str = None,
        classification_level: int = None,
        source_type: str = None,
        only_enabled: bool = True,
        only_healthy: bool = False,
        sort_by_priority: bool = True,
    ) -> List[Dict]:
        """
        查找可用的数据端点

        Args:
            data_category: 数据分类（如 DAILY_KLINE、TICK_DATA）
            classification_level: 分类层级（1-5）
            source_type: 数据源类型（akshare、tushare等）
            only_enabled: 仅返回启用的接口
            only_healthy: 仅返回健康状态正常的接口
            sort_by_priority: 按优先级和质量评分排序

        Returns:
            匹配的端点列表

        示例:
            # 查找所有日线数据接口
            apis = manager.find_endpoints(data_category="DAILY_KLINE")

            # 查找第1层分类（市场数据）的所有接口
            apis = manager.find_endpoints(classification_level=1)

            # 查找健康的akshare接口
            apis = manager.find_endpoints(source_type="akshare", only_healthy=True)
        """
        matches = []

        for endpoint_name, source in self.registry.items():
            config = source["config"]

            # 状态过滤
            if only_enabled and config.get("status") != "active":
                continue

            if only_healthy and config.get("health_status") == "failed":
                continue

            # 分类过滤
            if data_category and config.get("data_category") != data_category:
                continue

            if classification_level and config.get("classification_level") != classification_level:
                continue

            if source_type and config.get("source_type") != source_type:
                continue

            matches.append(
                {
                    "endpoint_name": endpoint_name,
                    "source_name": config.get("source_name"),
                    "source_type": config.get("source_type"),
                    "data_category": config.get("data_category"),
                    "data_classification": config.get("data_classification"),
                    "classification_level": config.get("classification_level"),
                    "target_db": config.get("target_db"),
                    "table_name": config.get("table_name"),
                    "quality_score": config.get("data_quality_score", 0),
                    "priority": config.get("priority", 999),
                    "health_status": config.get("health_status", "unknown"),
                    "success_rate": config.get("success_rate", 100),
                    "avg_response_time": config.get("avg_response_time", 0),
                    "total_calls": config.get("total_calls", 0),
                    "description": config.get("description", ""),
                    "tags": config.get("tags", []),
                }
            )

        # 排序：优先级（数字越小优先级越高）→ 质量评分（分数越高越好）
        if sort_by_priority:
            matches.sort(key=lambda x: (x["priority"], -x["quality_score"]))

        return matches
