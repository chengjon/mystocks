def get_stock_basic(self, symbol: str) -> Dict:
    """
    获取股票基本信息

    Args:
        symbol: 股票代码

    Returns:
        Dict: 包含股票基本信息的字典
    """
    logger.info("尝试获取股票基本信息: %s", symbol)

    # 参数验证
    if not symbol:
        logger.error("股票代码不能为空")
        return {}

    # 使用symbol_utils标准化股票代码
    normalized_symbol = symbol_utils.normalize_stock_code(symbol)
    if not normalized_symbol:
        logger.error("无效的股票代码: %s", symbol)
        return {}

    # 首先尝试使用efinance获取数据
    if self.efinance_available:
        try:
            # 使用efinance获取股票基本信息
            logger.info("使用efinance获取股票基本信息")
            data = self.ef.stock.get_base_info(normalized_symbol)
            logger.info("efinance返回数据类型: %s", type(data))
            if data is not None:
                logger.info("efinance获取到股票基本信息")
                # 如果data是DataFrame，转换第一行为字典
                if isinstance(data, pd.DataFrame):
                    logger.info("efinance返回数据行数: %s", len(data))
                    if not data.empty:
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(data, "stock")
                        # 返回第一行数据的字典形式
                        return cleaned_data.iloc[0].to_dict()
                    else:
                        logger.warning("efinance返回空数据")
                        return {}
                # 如果data是Series，转换为字典
                elif isinstance(data, pd.Series):
                    # 验证和清洗数据
                    df_data = data.to_frame().T  # 转换为DataFrame
                    cleaned_data = self._validate_and_clean_data(df_data, "stock")
                    return cleaned_data.iloc[0].to_dict()
                # 如果data已经是字典，直接返回
                elif isinstance(data, dict):
                    return data
                else:
                    # 其他情况尝试直接返回
                    logger.warning("efinance返回数据类型不支持: %s", type(data))
                    return data if data else {}
            else:
                logger.warning("efinance未获取到股票基本信息")
        except Exception as e:
            logger.error("efinance获取股票基本信息失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())

    # 如果efinance不可用或失败，尝试使用easyquotation
    if self.easyquotation_available:
        try:
            logger.info("使用easyquotation获取股票基本信息")
            quotation = self.eq.use("sina")  # 使用sina源
            data = quotation.real([normalized_symbol])  # 获取实时数据，其中包含基本信息
            logger.info("easyquotation返回数据类型: %s", type(data))
            if data and normalized_symbol in data:
                logger.info("easyquotation获取到股票数据")
                # 转换为DataFrame格式
                df = pd.DataFrame([data[normalized_symbol]])
                logger.info("easyquotation返回数据行数: %s", len(df))
                # 验证和清洗数据
                cleaned_data = self._validate_and_clean_data(df, "stock")
                return cleaned_data.iloc[0].to_dict()
            else:
                logger.warning("easyquotation未获取到股票数据")
        except Exception as e:
            logger.error("easyquotation获取股票基本信息失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())

    logger.warning("所有方法均未能获取到股票基本信息")
    return {}
