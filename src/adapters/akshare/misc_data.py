    def get_ths_industry_names(self) -> pd.DataFrame:
        """获取同花顺行业名称列表-Akshare实现

        该接口获取同花顺的所有行业名称和代码。

        Returns:
            pd.DataFrame: 同花顺行业名称列表
                - name: 行业名称
                - code: 行业代码

        示例用法:
            >>> adapter = AkshareDataSource()
            >>> industry_names = adapter.get_ths_industry_names()
            >>> logger.info(str(industry_names.head()))
        """
        try:
            logger.info(r"[Akshare] 开始获取同花顺行业名称列表...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_names():
                return ak.stock_board_industry_name_ths()

            # 调用akshare接口获取同花顺行业名称列表
            df = _get_industry_names()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到同花顺行业名称列表")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取同花顺行业名称列表: %s行, 列名=%s", len(df), df.columns.tolist())

            # 添加数据获取时间戳
            df["数据获取时间"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error("[Akshare] 获取同花顺行业名称列表失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取分钟K线数据（通过TDX适配器获取，AkShare本身不直接支持分钟K线）

        Args:
            symbol: str - 股票代码
            period: str - 周期 (1m/5m/15m/30m/60m)
            start_date: str - 开始日期
            end_date: str - 结束日期

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        # AkShare本身不直接支持分钟K线，需要通过TDX适配器获取
        # 这里返回空DataFrame，实际通过统一数据源调用TDX适配器
        logger.info("[Akshare] 注意：AkShare不直接支持分钟K线数据，建议使用TDX适配器")
        return pd.DataFrame()

    def get_industry_classify(self) -> pd.DataFrame:
        """
        获取行业分类数据

        Returns:
            pd.DataFrame: 行业分类数据
                - index: 行业代码
                - name: 行业名称
                - stock_count: 成分股数量
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - leader_stock: 领涨股
        """
        try:
            logger.info(r"[Akshare] 开始获取行业分类数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_classify():
                return ak.stock_board_industry_name_em()

            # 调用akshare接口获取行业分类数据
            df = _get_industry_classify()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到行业分类数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取行业分类数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股": "leader_stock",
                }
            )

            # 添加股票数量列（如果不存在）
            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            return df

        except Exception as e:
            logger.error("[Akshare] 获取行业分类数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()
