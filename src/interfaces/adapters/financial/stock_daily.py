# pylint: disable=undefined-variable  # 混入模块使用动态类型
def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
        获取股票日线数据

    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        DataFrame: 包含股票日线数据的DataFrame
    """
    logger.info("尝试获取股票日线数据: %s", symbol)

    # 参数验证
    if not symbol:
        logger.error("股票代码不能为空")
        return pd.DataFrame()

    # 使用symbol_utils标准化股票代码
    normalized_symbol = symbol_utils.normalize_stock_code(symbol)
    if not normalized_symbol:
        logger.error("无效的股票代码: %s", symbol)
        return pd.DataFrame()

    # 使用date_utils标准化日期
    try:
        normalized_start_date = date_utils.normalize_date(start_date) if start_date else None
        normalized_end_date = date_utils.normalize_date(end_date) if end_date else None
    except ValueError as e:
        logger.error("日期格式错误: %s", e)
        return pd.DataFrame()

    if not normalized_start_date or not normalized_end_date:
        logger.warning("日期参数不完整，将使用默认日期范围")

    # 首先尝试使用efinance获取数据
    if self.efinance_available:
        try:
            # 使用efinance获取股票日线数据
            logger.info("使用efinance获取股票日线数据")
            logger.info(
                "请求参数: symbol=%s, beg=%s, end=%s", normalized_symbol, normalized_start_date, normalized_end_date
            )
            data = self.ef.stock.get_quote_history(
                normalized_symbol,
                beg=normalized_start_date,
                end=normalized_end_date,
            )
            logger.info("efinance返回数据类型: %s", type(data))
            if isinstance(data, pd.DataFrame):
                logger.info("efinance返回数据行数: %s", len(data))
                if not data.empty:
                    logger.info("efinance获取到%s行日线数据", len(data))
                    # 确保列名是中文
                    expected_columns = [
                        "日期",
                        "开盘",
                        "收盘",
                        "最高",
                        "最低",
                        "成交量",
                        "成交额",
                    ]
                    if all(col in data.columns for col in expected_columns):
                        logger.info("数据格式正确")
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(data, "stock")
                        return cleaned_data
                    else:
                        logger.warning("数据列名不匹配，实际列名: %s", list(data.columns))
                        # 尝试重命名列
                        renamed_data = self._rename_columns(data)
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(renamed_data, "stock")
                        return cleaned_data
                else:
                    logger.warning("efinance返回空数据")
                    # 尝试更广泛的日期范围
                    logger.info("尝试更广泛的日期范围...")
                    broader_data = self.ef.stock.get_quote_history(normalized_symbol, beg="2020-01-01", end="2024-12-31")
                    if not broader_data.empty:
                        logger.info("更广泛日期范围获取到%s行数据", len(broader_data))
                        # 过滤日期范围
                        broader_data["日期"] = pd.to_datetime(broader_data["日期"])
                        start_date_dt = pd.to_datetime(date_utils.normalize_date(normalized_start_date))
                        end_date_dt = pd.to_datetime(date_utils.normalize_date(normalized_end_date))
                        filtered_data = broader_data[
                            (broader_data["日期"] >= start_date_dt) & (broader_data["日期"] <= end_date_dt)
                        ]
                        if not filtered_data.empty:
                            logger.info("过滤后得到%s行数据", len(filtered_data))
                            # 验证和清洗数据
                            cleaned_data = self._validate_and_clean_data(filtered_data, "stock")
                            return cleaned_data
                        else:
                            logger.warning("过滤后数据为空")
                            return pd.DataFrame()
                    else:
                        logger.warning("更广泛日期范围也未获取到数据")
                        return pd.DataFrame()
            else:
                logger.error("efinance返回数据类型不正确: %s", type(data))
                return pd.DataFrame()
        except Exception as e:
            logger.error("efinance获取日线数据失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    # 如果efinance不可用或失败，尝试使用easyquotation
    if self.easyquotation_available:
        try:
            logger.info("使用easyquotation获取股票数据")
            # 使用easyquotation获取实时数据作为替代
            quotation = self.eq.use("sina")  # 使用sina源
            data = quotation.real([normalized_symbol])  # 获取实时数据
            if data and normalized_symbol in data:
                logger.info("easyquotation获取到股票数据")
                # 转换为DataFrame格式
                df_data = data[normalized_symbol]
                df = pd.DataFrame([df_data])
                # 添加必要的列以匹配预期格式
                if "date" not in df.columns and "datetime" in df.columns:
                    df["date"] = df["datetime"].str[:10]  # 从datetime提取日期
                elif "date" not in df.columns:
                    df["date"] = date_utils.normalize_date(datetime.now())
                # 重命名列以匹配预期格式
                column_mapping = {
                    "date": "日期",
                    "open": "开盘",
                    "close": "收盘",
                    "high": "最高",
                    "low": "最低",
                    "volume": "成交量",
                    "amount": "成交额",
                }
                df = df.rename(columns=column_mapping)
                # 确保包含所有必要列
                expected_columns = [
                    "日期",
                    "开盘",
                    "收盘",
                    "最高",
                    "最低",
                    "成交量",
                    "成交额",
                ]
                for col in expected_columns:
                    if col not in df.columns:
                        df[col] = 0  # 默认值
                # 验证和清洗数据
                cleaned_data = self._validate_and_clean_data(df[expected_columns], "stock")  # 按预期顺序返回列
                return cleaned_data
            else:
                logger.warning("easyquotation未获取到股票数据")
        except Exception as e:
            logger.error("easyquotation获取股票数据失败: %s", e)
            import traceback

            logger.error(traceback.format_exc())

    logger.warning("所有方法均未能获取到股票日线数据")
    return pd.DataFrame()


def _rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
    """重命名列名"""
    column_map = {
        "日期": "trade_date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
    }
    return data.rename(columns=column_map)
