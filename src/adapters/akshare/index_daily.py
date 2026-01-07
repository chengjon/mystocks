    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据-Akshare实现
        使用优先级：
        1. 新浪接口(stock_zh_index_daily)
        2. 东方财富接口(stock_zh_index_daily_em)
        3. 通用接口(index_zh_a_hist)
        """
        try:
            # 处理日期格式
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            logger.info("尝试获取指数数据: %s", symbol)

            # 使用专门的格式化函数处理指数代码
            index_code = format_index_code_for_source(symbol, "akshare")
            logger.info("处理指数: %s", index_code)

            # 方法1: 新浪接口 (stock_zh_index_daily)
            try:
                logger.info(r"尝试新浪接口(stock_zh_index_daily)")
                df = ak.stock_zh_index_daily(symbol=index_code)

                if df is not None and not df.empty:
                    # 筛选日期范围
                    df["date"] = pd.to_datetime(df["date"])
                    mask = (df["date"] >= pd.to_datetime(normalize_date(start_date))) & (
                        df["date"] <= pd.to_datetime(normalize_date(end_date))
                    )
                    df = df[mask]

                    if not df.empty:
                        logger.info("新浪接口获取到%s行数据", len(df))
                        return self._process_index_data(df)
            except Exception as e:
                logger.error("新浪接口调用失败: %s", e)

            # 方法2: 东方财富接口 (stock_zh_index_daily_em)
            try:
                logger.info(r"尝试东方财富接口(stock_zh_index_daily_em)")
                df = ak.stock_zh_index_daily_em(symbol=index_code)

                if df is not None and not df.empty:
                    # 筛选日期范围
                    df["date"] = pd.to_datetime(df["date"])
                    mask = (df["date"] >= pd.to_datetime(normalize_date(start_date))) & (
                        df["date"] <= pd.to_datetime(normalize_date(end_date))
                    )
                    df = df[mask]

                    if not df.empty:
                        logger.info("东方财富接口获取到%s行数据", len(df))
                        return self._process_index_data(df)
            except Exception as e:
                logger.error("东方财富接口调用失败: %s", e)

            # 方法3: 通用接口 (index_zh_a_hist)
            try:
                logger.info(r"尝试通用接口(index_zh_a_hist)")
                # 提取纯数字代码
                pure_code = "".join(c for c in index_code if c.isdigit())
                start_date_fmt = start_date.replace("-", "")
                end_date_fmt = end_date.replace("-", "")

                df = ak.index_zh_a_hist(
                    symbol=pure_code,
                    period="daily",
                    start_date=start_date_fmt,
                    end_date=end_date_fmt,
                )

                if df is not None and not df.empty:
                    logger.info("通用接口获取到%s行数据", len(df))
                    return self._process_index_data(df)
            except Exception as e:
                logger.error("通用接口调用失败: %s", e)

            logger.info("所有接口均未能获取到指数 %s 的数据", index_code)
            return pd.DataFrame()

        except Exception as e:
            logger.error("Akshare获取指数日线数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()
