    def get_concept_classify(self) -> pd.DataFrame:
        """
        获取概念分类数据

        Returns:
            pd.DataFrame: 概念分类数据
                - index: 概念代码
                - name: 概念名称
                - stock_count: 成分股数量
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - leader_stock: 领涨股
        """
        try:
            logger.info(r"[Akshare] 开始获取概念分类数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_concept_classify():
                return ak.stock_board_concept_name_em()

            # 调用akshare接口获取概念分类数据
            df = _get_concept_classify()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到概念分类数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取概念分类数据，共 %s 条记录", len(df))

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
            logger.error("[Akshare] 获取概念分类数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """
        获取个股的行业和概念分类信息

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 个股行业和概念信息
                - symbol: 股票代码
                - industries: 行业列表
                - concepts: 概念列表
        """
        try:
            logger.info("[Akshare] 开始获取个股 %s 的行业和概念信息...", symbol)

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_stock_industry():
                return ak.stock_individual_info_em(symbol=symbol)

            # 调用akshare接口获取个股信息
            df = _get_stock_industry()

            if df is None or df.empty:
                logger.info("[Akshare] 未能获取到个股 %s 的信息", symbol)
                return {"symbol": symbol, "industries": [], "concepts": []}

            logger.info("[Akshare] 成功获取个股 %s 的信息", symbol)

            # 提取行业和概念信息
            industries = []
            concepts = []

            # 查找行业和概念相关的行
            for _, row in df.iterrows():
                if "行业" in str(row.get("item", "")) or "所属行业" in str(row.get("item", "")):
                    industry = row.get("value", "")
                    if industry and industry != "--":
                        industries.append(industry)
                elif "概念" in str(row.get("item", "")):
                    concept = row.get("value", "")
                    if concept and concept != "--":
                        # 概念可能包含多个，用逗号分隔
                        concept_list = [c.strip() for c in str(concept).split(",") if c.strip()]
                        concepts.extend(concept_list)

            return {
                "symbol": symbol,
                "industries": industries,
                "concepts": list(set(concepts)),  # 去重
            }

        except Exception as e:
            logger.error("[Akshare] 获取个股 %s 的行业和概念信息失败: %s", symbol, e)
            import traceback

            traceback.print_exc()
            return {"symbol": symbol, "industries": [], "concepts": []}
