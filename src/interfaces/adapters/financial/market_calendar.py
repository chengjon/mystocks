def get_market_calendar(self) -> pd.DataFrame:
    """
    获取交易日历

    Returns:
        DataFrame: 包含交易日历的DataFrame
    """
    logger.info("尝试获取交易日历")
    if not self.efinance_available:
        logger.warning("efinance库不可用")
        return pd.DataFrame()

    # 生成缓存键
    cache_key = self._get_cache_key("market_calendar", "calendar")

    # 尝试从缓存中获取数据
    cached_data = self._get_from_cache(cache_key)
    if cached_data is not None:
        logger.info("使用缓存数据: %s", cache_key)
        return cached_data

    try:
        # 使用efinance获取交易日历
        logger.info("使用efinance获取交易日历")
        data = self.ef.stock.get_all_report_dates()
        logger.info("efinance返回数据类型: %s", type(data))
        if isinstance(data, pd.DataFrame):
            logger.info("efinance返回数据行数: %s", len(data))
            if not data.empty:
                logger.info("efinance获取到%s个交易日", len(data))
                # 保存到缓存
                self._save_to_cache(cache_key, data)
                return data
            else:
                logger.warning("efinance未获取到交易日历")
                return pd.DataFrame()
        else:
            logger.error("efinance返回数据类型不正确: %s", type(data))
            return pd.DataFrame()
    except Exception as e:
        logger.error("efinance获取交易日历失败: %s", e)
        import traceback

        logger.error(traceback.format_exc())
        return pd.DataFrame()
