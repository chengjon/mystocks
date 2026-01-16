def get_real_time_data(self, symbol: str = None) -> pd.DataFrame:
    """
    获取实时数据（仅支持A股市场）

    Args:
        symbol: 股票代码（可选）

    Returns:
        DataFrame: 包含实时数据的DataFrame
    """
    logger.info("尝试获取实时数据: symbol=%s", symbol)

    # 参数验证
    if symbol and not isinstance(symbol, str):
        logger.error("股票代码必须是字符串类型")
        return pd.DataFrame()

    # 生成缓存键
    cache_key = self._get_cache_key(symbol or "market_snapshot", "realtime")

    # 尝试从缓存中获取数据
    cached_data = self._get_from_cache(cache_key)
    if cached_data is not None:
        logger.info("使用缓存数据: %s", cache_key)
        return cached_data

    # 首先尝试使用efinance获取数据
    if self.efinance_available:
        try:
            if symbol:
                # 使用symbol_utils标准化股票代码
                normalized_symbol = symbol_utils.normalize_stock_code(symbol)
                if not normalized_symbol:
                    logger.error("无效的股票代码: %s", symbol)
                    return pd.DataFrame()

                # 获取特定股票的实时数据
                logger.info("获取特定股票实时数据: %s", normalized_symbol)
                data = self.ef.stock.get_realtime_quotes(symbol=normalized_symbol)
            else:
                # 获取市场快照（仅支持A股市场）
                logger.info("获取A股市场快照")
                # 对于A股市场，获取主要指数的实时数据作为市场快照
                major_indices = [
                    "000001",
                    "399001",
                    "399006",
                ]  # 上证指数、深证成指、创业板指
                data = pd.DataFrame()
                for index_code in major_indices:
                    try:
                        index_data = self.ef.stock.get_realtime_quotes(symbol=index_code)
                        if isinstance(index_data, pd.DataFrame) and not index_data.empty:
                            data = pd.concat([data, index_data], ignore_index=True)
                    except Exception as e:
                        logger.error("获取指数%s数据失败: %s", index_code, e)
                        import traceback

                        logger.error(traceback.format_exc())

            logger.info("efinance返回数据类型: %s", type(data))
            if isinstance(data, pd.DataFrame):
                logger.info("efinance返回数据行数: %s", len(data))
                if not data.empty:
                    logger.info("efinance获取到%s行实时数据", len(data))
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(data, "stock")
                    # 保存到缓存
                    self._save_to_cache(cache_key, cleaned_data)
                    return cleaned_data
                else:
                    logger.warning("efinance返回空数据")
                    return pd.DataFrame()
            else:
                logger.error("efinance返回数据类型不正确: %s", type(data))
                return pd.DataFrame()
        except Exception as e:
            logger.error("efinance获取实时数据失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    # 如果efinance不可用或失败，尝试使用easyquotation
    if self.easyquotation_available:
        try:
            logger.info("使用easyquotation获取实时数据")
            quotation = self.eq.use("sina")  # 使用sina源

            if symbol:
                # 使用symbol_utils标准化股票代码
                normalized_symbol = symbol_utils.normalize_stock_code(symbol)
                if not normalized_symbol:
                    logger.error("无效的股票代码: %s", symbol)
                    return pd.DataFrame()

                # 获取特定股票的实时数据
                logger.info("获取特定股票实时数据: %s", normalized_symbol)
                data = quotation.real([normalized_symbol])
                if data and normalized_symbol in data:
                    logger.info("easyquotation获取到股票数据")
                    # 转换为DataFrame格式
                    df = pd.DataFrame([data[normalized_symbol]])
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(df, "stock")
                    # 保存到缓存
                    self._save_to_cache(cache_key, cleaned_data)
                    return cleaned_data
                else:
                    logger.warning("easyquotation未获取到指定股票数据")
                    return pd.DataFrame()
            else:
                # 获取市场快照（仅支持A股市场）
                logger.info("获取A股市场快照")
                # 获取A股市场快照（需要提供股票代码列表）
                # 扩展股票代码列表以获取更全面的市场快照
                stock_codes = [
                    "000001",
                    "000002",
                    "600000",
                    "600036",  # 平安银行、万科A、浦发银行、招商银行
                    "600519",
                    "000858",
                    "002594",
                    "300750",  # 贵州茅台、五粮液、比亚迪、宁德时代
                    "399001",
                    "399006",
                    "000001",  # 深证成指、创业板指、上证指数
                ]
                data = quotation.real(stock_codes)
                if data:
                    logger.info("easyquotation获取到%s只股票数据", len(data))
                    # 转换为DataFrame格式
                    df = pd.DataFrame(data).T  # 转置以使每行代表一只股票
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(df, "stock")
                    # 保存到缓存
                    self._save_to_cache(cache_key, cleaned_data)
                    return cleaned_data
                else:
                    logger.warning("easyquotation未获取到市场快照数据")
                    return pd.DataFrame()

        except Exception as e:
            logger.error("easyquotation获取实时数据失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    logger.warning("所有方法均未能获取到实时数据")
    return pd.DataFrame()
