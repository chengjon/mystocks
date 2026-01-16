def get_index_components(self, index_code):
    """
    获取指数的成分股数据

    Args:
        index_code (str): 指数代码或名称

    Returns:
        pd.DataFrame: 指数成分股数据
    """
    logger.info("尝试获取指数 %s 的成分股数据...", index_code)

    # 参数验证
    if not index_code:
        logger.error("指数代码不能为空")
        return pd.DataFrame()

    # 使用symbol_utils标准化股票代码
    normalized_index_code = symbol_utils.normalize_stock_code(index_code)
    if not normalized_index_code:
        logger.error("无效的指数代码: %s", index_code)
        return pd.DataFrame()

    if not self.efinance_available and not self.easyquotation_available:
        logger.warning("数据源未初始化或不可用")
        return pd.DataFrame()

    try:
        # 使用efinance的stock.get_members方法获取指数成分股
        logger.info("使用efinance获取指数 %s 的成分股数据", index_code)
        df = self.ef.stock.get_members(normalized_index_code)

        # 检查返回的数据是否有效
        logger.info("efinance返回数据类型: %s", type(df))
        if df is not None and not df.empty:
            logger.info("成功获取指数%s的成分股数据，共%s只股票", index_code, len(df))
            # 验证和清洗数据
            cleaned_data = self._validate_and_clean_data(df, "stock")
            return cleaned_data
        else:
            logger.warning("获取指数%s的成分股数据为空", index_code)
            return pd.DataFrame()
    except Exception as e:
        logger.error("获取指数%s的成分股数据时发生错误: %s", index_code, str(e))
        import traceback

        logger.error(traceback.format_exc())
        return pd.DataFrame()
