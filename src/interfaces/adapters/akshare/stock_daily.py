# pylint: disable=undefined-variable  # 混入模块使用动态类型
def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股票日线数据-Akshare实现"""
    try:
        # 处理股票代码格式 - 使用专门的格式化函数
        stock_code = format_stock_code_for_source(symbol, "akshare")

        # 处理日期格式
        start_date = normalize_date(start_date)
        end_date = normalize_date(end_date)

        logger.info(
            "Akshare尝试获取股票日线数据: 代码=%s, 开始日期=%s, 结束日期=%s",
            stock_code,
            start_date,
            end_date,
        )

        # 尝试多种API获取股票数据
        df = None

        # 方法1: stock_zh_a_hist (主要API)
        try:
            # 根据文档要求，日期格式应为YYYYMMDD
            start_date_fmt = start_date.replace("-", "")
            end_date_fmt = end_date.replace("-", "")

            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date_fmt,
                end_date=end_date_fmt,
                adjust="qfq",  # 前复权
                timeout=self.api_timeout,
            )
            logger.info(
                "主要API调用成功，参数: symbol=%s, start_date=%s, end_date=%s",
                stock_code,
                start_date_fmt,
                end_date_fmt,
            )
        except Exception as e:
            logger.error("主要API调用失败: %s", e)
            df = None

        # 方法2: stock_zh_a_spot (备用API)
        if df is None or df.empty:
            try:
                logger.info(r"尝试备用API(stock_zh_a_spot)")
                spot_df = ak.stock_zh_a_spot()
                if spot_df is not None and not spot_df.empty:
                    # 筛选指定股票代码
                    spot_df = spot_df[spot_df["代码"] == stock_code]
                    if not spot_df.empty:
                        # 转换为日线格式
                        df = pd.DataFrame(
                            {
                                "date": [normalize_date(datetime.datetime.now())],
                                "open": [spot_df.iloc[0]["今开"]],
                                "close": [spot_df.iloc[0]["最新价"]],
                                "high": [spot_df.iloc[0]["最高"]],
                                "low": [spot_df.iloc[0]["最低"]],
                                "volume": [spot_df.iloc[0]["成交量"]],
                                "amount": [spot_df.iloc[0]["成交额"]],
                            }
                        )
            except Exception as e:
                logger.error("备用API调用失败: %s", e)

        if df is None or df.empty:
            logger.info(r"Akshare返回的数据为空")
            return pd.DataFrame()

        logger.info("Akshare获取到原始数据: %s行, 列名=%s", len(df), df.columns.tolist())

        # 使用统一列名映射器标准化列名
        df = ColumnMapper.to_english(df)

        return df
    except Exception as e:
        logger.error("Akshare获取股票日线数据失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()
