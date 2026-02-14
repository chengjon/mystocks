
def get_futures_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股指期货日线数据-Akshare实现

    获取中国金融期货交易所的股指期货日线数据，包括IF、IH、IC、IM等合约。

    Args:
        symbol: str - 期货合约代码，如 "IF2401", "IH2401", "IC2401", "IM2401"
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 股指期货日线数据
            - date: 交易日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - open_interest: 持仓量
            - settlement_price: 结算价

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> futures_data = adapter.get_futures_index_daily("IF2401", "20240101", "20240131")
        >>> logger.info(str(futures_data.head()))
    """
    try:
        logger.info(
            r"[Akshare] 开始获取股指期货日线数据: symbol=%s, 开始日期=%s, 结束日期=%s",
            symbol,
            start_date,
            end_date,
        )

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_futures_data():
            return ak.futures_zh_daily_sina(symbol=symbol)

        # 调用akshare接口获取股指期货日线数据
        df = _get_futures_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货日线数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货日线数据: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "日期": "date",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "收盘价": "close",
            "成交量": "volume",
            "持仓量": "open_interest",
            "结算价": "settlement_price",
        }
        df = df.rename(columns=column_mapping)

        # 筛选日期范围
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            mask = (df["date"] >= start_date) & (df["date"] <= end_date)
            df = df[mask]

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货日线数据失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_index_realtime(self, symbol: str) -> pd.DataFrame:
    """获取股指期货实时行情-Akshare实现

    获取中国金融期货交易所的股指期货实时行情数据。

    Args:
        symbol: str - 期货合约代码，如 "IF2401", "IH2401", "IC2401", "IM2401"

    Returns:
        pd.DataFrame: 股指期货实时行情
            - symbol: 合约代码
            - name: 合约名称
            - price: 最新价
            - change: 涨跌
            - change_pct: 涨跌幅(%)
            - volume: 成交量
            - open_interest: 持仓量
            - bid_price: 买价
            - ask_price: 卖价

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> realtime_data = adapter.get_futures_index_realtime("IF2401")
        >>> logger.info(str(realtime_data.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取股指期货实时行情: symbol=%s", symbol)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_realtime_data():
            return ak.futures_zh_spot(symbol=symbol, market="FF", adjust="0")

        # 调用akshare接口获取股指期货实时行情
        df = _get_realtime_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货实时行情")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货实时行情: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "symbol": "symbol",
            "name": "name",
            "trade": "price",
            "settlement": "settlement_price",
            "presettlement": "pre_settlement",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "amount": "amount",
            "open_interest": "open_interest",
            "change": "change",
            "change_pct": "change_pct",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货实时行情失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_index_main_contract(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股指期货主力连续合约-Akshare实现

    获取中国金融期货交易所的股指期货主力连续合约历史数据。

    Args:
        symbol: str - 主力连续合约代码，如 "IF0", "IH0", "IC0", "IM0"
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 股指期货主力连续合约数据
            - date: 交易日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - open_interest: 持仓量
            - settlement_price: 结算价

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> main_contract_data = adapter.get_futures_index_main_contract("IF0", "20240101", "20240131")
        >>> logger.info(str(main_contract_data.head()))
    """
    try:
        logger.info(
            r"[Akshare] 开始获取股指期货主力连续合约: symbol=%s, 开始日期=%s, 结束日期=%s",
            symbol,
            start_date,
            end_date,
        )

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_main_contract_data():
            return ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)

        # 调用akshare接口获取股指期货主力连续合约
        df = _get_main_contract_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货主力连续合约数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货主力连续合约: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "日期": "date",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "收盘价": "close",
            "成交量": "volume",
            "持仓量": "open_interest",
            "动态结算价": "settlement_price",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货主力连续合约失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_basis_analysis(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股指期货期现基差分析-Akshare实现

    计算股指期货与对应现货指数的基差数据，用于套利分析。

    Args:
        symbol: str - 期货合约代码，如 "IF2401", "IH2401", "IC2401", "IM2401"
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 期现基差分析数据
            - date: 交易日期
            - futures_price: 期货价格
            - spot_index: 现货指数
            - basis: 基差(期货-现货)
            - basis_rate: 基差率(%)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> basis_data = adapter.get_futures_basis_analysis("IF2401", "20240101", "20240131")
        >>> logger.info(str(basis_data.head()))
    """
    try:
        logger.info(
            r"[Akshare] 开始计算股指期货期现基差: symbol=%s, 开始日期=%s, 结束日期=%s",
            symbol,
            start_date,
            end_date,
        )

        # 获取期货数据
        futures_df = self.get_futures_index_daily(symbol, start_date, end_date)
        if futures_df.empty:
            logger.warning("无法获取期货数据，跳过基差分析")
            return pd.DataFrame()

        # 根据期货代码确定对应的现货指数
        spot_index_mapping = {
            "IF": "000300",  # 沪深300
            "IH": "000016",  # 上证50
            "IC": "000905",  # 中证500
            "IM": "000852",  # 中证1000
        }

        futures_type = symbol[:2]  # IF, IH, IC, IM
        spot_symbol = spot_index_mapping.get(futures_type)

        if not spot_symbol:
            logger.warning("无法确定期货 %s 对应的现货指数", symbol)
            return pd.DataFrame()

        # 获取现货指数数据
        spot_df = self.get_stock_daily(spot_symbol, start_date, end_date)
        if spot_df.empty:
            logger.warning("无法获取现货指数数据，跳过基差分析")
            return pd.DataFrame()

        # 合并数据并计算基差
        merged_df = pd.merge(
            futures_df[["date", "close"]].rename(columns={"close": "futures_price"}),
            spot_df[["date", "close"]].rename(columns={"close": "spot_index"}),
            on="date",
            how="inner",
        )

        if merged_df.empty:
            logger.warning("无法匹配期货和现货数据")
            return pd.DataFrame()

        # 计算基差
        merged_df["basis"] = merged_df["futures_price"] - merged_df["spot_index"]
        merged_df["basis_rate"] = (merged_df["basis"] / merged_df["spot_index"] * 100).round(4)

        # 选择输出列
        result_df = merged_df[["date", "futures_price", "spot_index", "basis", "basis_rate"]]

        # 添加数据获取时间戳
        result_df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("[Akshare] 成功计算股指期货期现基差: %s行", len(result_df))
        return result_df

    except Exception as e:
        logger.error("[Akshare] 计算股指期货期现基差失败: %s", e)
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


