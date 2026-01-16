def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
    """
    获取股票财务数据

    Args:
        symbol: 股票代码
        period: 报告期类型 ("annual" 年报或 "quarterly" 季报)

    Returns:
        DataFrame: 包含股票财务数据的DataFrame
    """
    logger.info("尝试获取财务数据: %s, period: %s", symbol, period)

    # 参数验证
    if not symbol:
        logger.error("股票代码不能为空")
        return pd.DataFrame()

    # 使用symbol_utils标准化股票代码
    normalized_symbol = symbol_utils.normalize_stock_code(symbol)
    if not normalized_symbol:
        logger.error("无效的股票代码: %s", symbol)
        return pd.DataFrame()

    if period not in ["annual", "quarterly"]:
        logger.warning("不支持的报告期类型: %s，将使用默认年报类型", period)
        period = "annual"

    if not self.efinance_available:
        logger.warning("efinance库不可用")
        return pd.DataFrame()

    # 生成缓存键
    cache_key = self._get_cache_key(normalized_symbol, "financial", period=period)

    # 尝试从缓存中获取数据
    cached_data = self._get_from_cache(cache_key)
    if cached_data is not None:
        logger.info("使用缓存数据: %s", cache_key)
        return cached_data

    try:
        # 根据报告期类型选择不同的数据获取方式
        if period == "annual":
            # 获取年报数据
            logger.info("使用efinance获取年报数据")
            # 尝试直接获取指定股票的财务数据，而不是获取所有公司的数据
            # 注意：efinance库可能没有get_stock_financial_analysis方法，直接使用传统方法
            try:
                # 注释掉不存在的方法调用
                # financial_summary = self.ef.stock.get_stock_financial_analysis(normalized_symbol)
                # if financial_summary is not None and not financial_summary.empty:
                #     logger.info("efinance获取到个股财务摘要数据: %s行", len(financial_summary))
                #     # 验证和清洗数据
                #     cleaned_data = self._validate_and_clean_data(financial_summary, "financial")
                #     # 保存到缓存
                #     self._save_to_cache(cache_key, cleaned_data)
                #     return cleaned_data
                pass  # 占位符，避免空的try块
            except Exception as e:
                logger.error("获取个股财务摘要数据失败: %s", e)
                import traceback

                logger.error(traceback.format_exc())

            # 如果无法获取个股摘要数据，则获取所有公司数据后筛选
            logger.info("使用传统方法获取财务数据")
            all_data = self.ef.stock.get_all_company_performance()

            if not all_data.empty:
                # 筛选出指定股票的数据
                filtered_data = all_data[
                    (all_data["股票代码"] == normalized_symbol)
                    | (all_data["股票简称"].str.contains(normalized_symbol, na=False))
                ]

                if not filtered_data.empty:
                    logger.info("efinance获取到%s行财务数据", len(filtered_data))
                    # 添加报告期类型标识
                    filtered_data = filtered_data.copy()  # 创建副本避免SettingWithCopyWarning
                    filtered_data.loc[:, "报告期类型"] = "annual"
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(filtered_data, "financial")
                    # 保存到缓存
                    self._save_to_cache(cache_key, cleaned_data)
                    return cleaned_data
                else:
                    logger.warning("未找到指定股票的财务数据")
                    return pd.DataFrame()
            else:
                logger.warning("efinance未获取到财务数据")
                return pd.DataFrame()
        else:
            # 获取季报数据
            logger.info("使用efinance获取季报数据")
            try:
                # 尝试获取季度财务数据
                # pylint: disable=no-member
                quarterly_data = self.ef.stock.get_quarterly_performance(normalized_symbol)
                if quarterly_data is not None and not quarterly_data.empty:
                    logger.info("efinance获取到%s行季报数据", len(quarterly_data))
                    # 添加报告期类型标识
                    quarterly_data = quarterly_data.copy()  # 创建副本避免SettingWithCopyWarning
                    quarterly_data.loc[:, "报告期类型"] = "quarterly"
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(quarterly_data, "financial")
                    # 保存到缓存
                    self._save_to_cache(cache_key, cleaned_data)
                    return cleaned_data
                else:
                    logger.warning("efinance未获取到季报数据")
                    return pd.DataFrame()
            except Exception as e:
                logger.error("获取季报数据失败: %s", e)
                import traceback

                logger.error(traceback.format_exc())
                return pd.DataFrame()
    except Exception as e:
        logger.error("efinance获取财务数据失败: %s", e)
        import traceback

        logger.error(traceback.format_exc())
        return pd.DataFrame()
