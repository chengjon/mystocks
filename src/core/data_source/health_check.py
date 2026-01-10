def _save_call_history_async(self, **kwargs):
    """异步保存调用历史（避免阻塞）"""
    try:
        query = """
            INSERT INTO data_source_call_history
            (endpoint_name, call_time, success, response_time, record_count, error_message, caller)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        db_manager = self._get_db_manager()
        with db_manager.get_postgresql_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    kwargs.get("endpoint_name"),
                    datetime.now(),
                    kwargs.get("success", True),
                    kwargs.get("response_time"),
                    kwargs.get("record_count"),
                    kwargs.get("error_message"),
                    kwargs.get("caller", "unknown"),
                ),
            )
            conn.commit()
    except Exception as e:
        logger.error(f"保存调用历史失败: {e}")

# ==========================================================================
# 健康检查
# ==========================================================================

def health_check(self, endpoint_name: str = None) -> Dict:
    """
    执行健康检查

    Args:
        endpoint_name: 指定端点名称，None表示检查所有

    Returns:
        健康检查结果
    """
    if endpoint_name:
        return self._check_single_endpoint(endpoint_name)
    else:
        return self._check_all_endpoints()

def _check_single_endpoint(self, endpoint_name: str) -> Dict:
    """检查单个端点"""
    source = self.registry.get(endpoint_name)
    if not source:
        return {"endpoint_name": endpoint_name, "status": "not_found"}

    config = source["config"]
    test_params = config.get("test_parameters", {})

    try:
        # 获取或创建handler
        if source["handler"] is None:
            source["handler"] = self._create_handler(config)

        handler = source["handler"]

        # 使用测试参数调用
        start_time = time.time()
        data = handler.fetch(**test_params)
        response_time = time.time() - start_time

        # 验证返回数据
        self._validate_data(endpoint_name, data)

        return {
            "endpoint_name": endpoint_name,
            "status": "healthy",
            "response_time": round(response_time, 3),
            "record_count": len(data) if hasattr(data, "__len__") else "N/A",
            "sample": data.head(1).to_dict() if hasattr(data, "head") else str(data)[:100],
        }
    except Exception as e:
        return {"endpoint_name": endpoint_name, "status": "unhealthy", "error": str(e)}
