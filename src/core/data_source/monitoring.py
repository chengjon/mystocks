    def _create_handler(self, endpoint_info: Dict):
        """创建数据源处理器（工厂方法）"""
        source_type = endpoint_info["source_type"]

        # 延迟导入（避免循环依赖）
        from src.core.data_source_handlers_v2 import (
            AkshareHandler,
            TushareHandler,
            BaostockHandler,
            TdxHandler,
            WebCrawlerHandler,
            MockHandler,
        )

        handler_map = {
            "akshare": AkshareHandler,
            "tushare": TushareHandler,
            "baostock": BaostockHandler,
            "tdx": TdxHandler,
            "database": TdxHandler,
            "crawler": WebCrawlerHandler,
            "mock": MockHandler,
            "api_library": self._select_api_handler(endpoint_info["source_name"]),
        }

        handler_class = handler_map.get(source_type)
        if not handler_class:
            raise ValueError(f"不支持的数据源类型: {source_type}")

        return handler_class(endpoint_info)

    def _select_api_handler(self, source_name: str):
        """根据数据源名称选择处理器"""
        from src.core.data_source_handlers_v2 import AkshareHandler, TushareHandler

        handler_map = {"akshare": AkshareHandler, "tushare": TushareHandler, "baostock": TushareHandler}  # 复用

        return handler_map.get(source_name, AkshareHandler)

    def _identify_caller(self) -> str:
        """识别调用方"""
        import traceback

        stack = traceback.extract_stack()

        # 找到调用者（跳过内部调用）
        for frame in reversed(stack[:-2]):
            filename = frame.filename
            if "data_source_manager" not in filename:
                return f"{Path(filename).name}:{frame.lineno}"

        return "unknown"

    # ==========================================================================
    # 监控和记录
    # ==========================================================================

    def _record_success(self, endpoint_name: str, response_time: float, record_count: int, caller: str):
        """记录成功调用"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        config = source["config"]

        # 更新内存统计
        total_calls = config.get("total_calls", 0)
        failed_calls = config.get("failed_calls", 0)

        # 更新平均响应时间
        old_avg = config.get("avg_response_time", 0)
        new_avg = (old_avg * total_calls + response_time) / (total_calls + 1)

        config["avg_response_time"] = new_avg
        config["total_calls"] = total_calls + 1
        config["success_rate"] = (total_calls + 1 - failed_calls) / (total_calls + 1) * 100
        config["consecutive_failures"] = 0
        config["last_success_time"] = datetime.now()

        # 更新健康状态
        if response_time > 5.0:
            config["health_status"] = "degraded"
        else:
            config["health_status"] = "healthy"

        # 保存到数据库（异步，避免阻塞）
        self._save_call_history_async(
            endpoint_name=endpoint_name,
            success=True,
            response_time=response_time,
            record_count=record_count,
            caller=caller,
        )

    def _record_failure(self, endpoint_name: str, response_time: float, error_message: str, caller: str):
        """记录失败调用"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        config = source["config"]

        # 更新失败统计
        config["failed_calls"] = config.get("failed_calls", 0) + 1
        config["consecutive_failures"] = config.get("consecutive_failures", 0) + 1
        config["last_failure_time"] = datetime.now()

        # 连续失败3次标记为失败
        if config["consecutive_failures"] >= 3:
            config["health_status"] = "failed"

        # 保存到数据库
        self._save_call_history_async(
            endpoint_name=endpoint_name,
            success=False,
            response_time=response_time,
            error_message=error_message,
            caller=caller,
        )
