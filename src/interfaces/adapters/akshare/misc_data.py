# pylint: disable=undefined-variable  # 混入模块使用动态类型
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


def get_margin_account_info(self) -> pd.DataFrame:
    """获取两融账户信息-Akshare实现

    获取东方财富网的融资融券账户统计信息，包括融资余额、融券余额等。

    Returns:
        pd.DataFrame: 两融账户信息
            - 日期: 统计日期
            - 融资余额: 融资余额(亿)
            - 融券余额: 融券余额(亿)
            - 融资买入额: 融资买入额(亿)
            - 融券卖出额: 融券卖出额(亿)
            - 融资融券余额: 融资融券余额(亿)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> margin_info = adapter.get_margin_account_info()
        >>> logger.info(str(margin_info.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取两融账户信息...")

        @self._retry_api_call
        def _get_margin_info():
            return ak.stock_margin_account_info()

        df = _get_margin_info()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到两融账户信息")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取两融账户信息: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文（如果需要）
        column_mapping = {
            "日期": "trade_date",
            "融资余额": "margin_balance",
            "融券余额": "short_balance",
            "融资买入额": "margin_buy_amount",
            "融券卖出额": "short_sell_amount",
            "融资融券余额": "total_balance",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取两融账户信息失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_margin_detail_sse(self, date: str) -> pd.DataFrame:
    """获取上证所融资融券明细-Akshare实现

    获取上海证券交易所指定日期的融资融券交易明细数据。

    Args:
        date: str - 交易日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 上证所融资融券明细
            - 信用交易日期: 交易日期
            - 标的证券代码: 股票代码
            - 标的证券简称: 股票名称
            - 融资余额: 融资余额(元)
            - 融资买入额: 融资买入额(元)
            - 融资偿还额: 融资偿还额(元)
            - 融券余量: 融券余量
            - 融券卖出量: 融券卖出量
            - 融券偿还量: 融券偿还量

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> margin_detail = adapter.get_margin_detail_sse("20231201")
        >>> logger.info(str(margin_detail.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取上证所融资融券明细: 日期=%s", date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_sse_margin_detail():
            return ak.stock_margin_detail_sse(date=date)

        # 调用akshare接口获取上证所融资融券明细
        df = _get_sse_margin_detail()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到上证所融资融券明细")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取上证所融资融券明细: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "信用交易日期": "trade_date",
            "标的证券代码": "symbol",
            "标的证券简称": "name",
            "融资余额": "margin_balance",
            "融资买入额": "margin_buy_amount",
            "融资偿还额": "margin_repay_amount",
            "融券余量": "short_position",
            "融券卖出量": "short_sell_volume",
            "融券偿还量": "short_repay_volume",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取上证所融资融券明细失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_margin_detail_szse(self, date: str) -> pd.DataFrame:
    """获取深证所融资融券明细-Akshare实现

    获取深圳证券交易所指定日期的融资融券交易明细数据。

    Args:
        date: str - 交易日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 深证所融资融券明细
            - 证券代码: 股票代码
            - 证券简称: 股票名称
            - 融资买入额: 融资买入额(元)
            - 融资余额: 融资余额(元)
            - 融券卖出量: 融券卖出量(股)
            - 融券余量: 融券余量(股)
            - 融券余额: 融券余额(元)
            - 融资融券余额: 融资融券余额(元)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> margin_detail = adapter.get_margin_detail_szse("20231201")
        >>> logger.info(str(margin_detail.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取深证所融资融券明细: 日期=%s", date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_szse_margin_detail():
            return ak.stock_margin_detail_szse(date=date)

        # 调用akshare接口获取深证所融资融券明细
        df = _get_szse_margin_detail()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到深证所融资融券明细")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取深证所融资融券明细: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "证券代码": "symbol",
            "证券简称": "name",
            "融资买入额": "margin_buy_amount",
            "融资余额": "margin_balance",
            "融券卖出量": "short_sell_volume",
            "融券余量": "short_position",
            "融券余额": "short_balance",
            "融资融券余额": "total_balance",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取深证所融资融券明细失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_margin_summary_sse(self, start_date: str, end_date: str) -> pd.DataFrame:
    """获取上证所融资融券汇总-Akshare实现

    获取上海证券交易所指定时间段的融资融券汇总数据。

    Args:
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 上证所融资融券汇总
            - 信用交易日期: 交易日期
            - 融资余额: 融资余额(元)
            - 融资买入额: 融资买入额(元)
            - 融券余量: 融券余量
            - 融券余量金额: 融券余量金额(元)
            - 融券卖出量: 融券卖出量
            - 融资融券余额: 融资融券余额(元)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> margin_summary = adapter.get_margin_summary_sse("20231201", "20231205")
        >>> logger.info(str(margin_summary.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取上证所融资融券汇总: 开始日期=%s, 结束日期=%s", start_date, end_date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_sse_margin_summary():
            return ak.stock_margin_sse(start_date=start_date, end_date=end_date)

        # 调用akshare接口获取上证所融资融券汇总
        df = _get_sse_margin_summary()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到上证所融资融券汇总")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取上证所融资融券汇总: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "信用交易日期": "trade_date",
            "融资余额": "margin_balance",
            "融资买入额": "margin_buy_amount",
            "融券余量": "short_position",
            "融券余量金额": "short_position_amount",
            "融券卖出量": "short_sell_volume",
            "融资融券余额": "total_balance",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取上证所融资融券汇总失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_margin_summary_szse(self, date: str) -> pd.DataFrame:
    """获取深证所融资融券汇总-Akshare实现

    获取深圳证券交易所指定日期的融资融券汇总数据。

    Args:
        date: str - 交易日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 深证所融资融券汇总
            - 融资买入额: 融资买入额(亿元)
            - 融资余额: 融资余额(亿元)
            - 融券卖出量: 融券卖出量(亿股/亿份)
            - 融券余量: 融券余量(亿股/亿份)
            - 融券余额: 融券余额(亿元)
            - 融资融券余额: 融资融券余额(亿元)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> margin_summary = adapter.get_margin_summary_szse("20231201")
        >>> logger.info(str(margin_summary.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取深证所融资融券汇总: 日期=%s", date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_szse_margin_summary():
            return ak.stock_margin_szse(date=date)

        # 调用akshare接口获取深证所融资融券汇总
        df = _get_szse_margin_summary()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到深证所融资融券汇总")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取深证所融资融券汇总: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "融资买入额": "margin_buy_amount",
            "融资余额": "margin_balance",
            "融券卖出量": "short_sell_volume",
            "融券余量": "short_position",
            "融券余额": "short_balance",
            "融资融券余额": "total_balance",
        }
        df = df.rename(columns=column_mapping)

        # 添加交易日期列
        df["trade_date"] = date

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取深证所融资融券汇总失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_dragon_tiger_detail(self, start_date: str, end_date: str) -> pd.DataFrame:
    """获取龙虎榜详情-Akshare实现

    获取东方财富网的龙虎榜详情数据。

    Args:
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 龙虎榜详情
            - 序号: 序号
            - 代码: 股票代码
            - 名称: 股票名称
            - 上榜日: 上榜日期
            - 解读: 上榜解读
            - 收盘价: 收盘价
            - 涨跌幅: 涨跌幅(%)
            - 龙虎榜净买额: 龙虎榜净买额(元)
            - 龙虎榜买入额: 龙虎榜买入额(元)
            - 龙虎榜卖出额: 龙虎榜卖出额(元)
            - 龙虎榜成交额: 龙虎榜成交额(元)
            - 市场总成交额: 市场总成交额(元)
            - 净买额占总成交比: 净买额占总成交比(%)
            - 成交额占总成交比: 成交额占总成交比(%)
            - 换手率: 换手率(%)
            - 流通市值: 流通市值(元)
            - 上榜原因: 上榜原因
            - 上榜后1日: 上榜后1日涨跌幅(%)
            - 上榜后2日: 上榜后2日涨跌幅(%)
            - 上榜后5日: 上榜后5日涨跌幅(%)
            - 上榜后10日: 上榜后10日涨跌幅(%)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> dragon_tiger = adapter.get_dragon_tiger_detail("20231201", "20231205")
        >>> logger.info(str(dragon_tiger.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取龙虎榜详情: 开始日期=%s, 结束日期=%s", start_date, end_date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_dragon_tiger():
            return ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)

        # 调用akshare接口获取龙虎榜详情
        df = _get_dragon_tiger()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到龙虎榜详情")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取龙虎榜详情: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "序号": "rank",
            "代码": "symbol",
            "名称": "name",
            "上榜日": "list_date",
            "解读": "interpretation",
            "收盘价": "close_price",
            "涨跌幅": "change_percent",
            "龙虎榜净买额": "net_buy_amount",
            "龙虎榜买入额": "buy_amount",
            "龙虎榜卖出额": "sell_amount",
            "龙虎榜成交额": "total_amount",
            "市场总成交额": "market_total_amount",
            "净买额占总成交比": "net_buy_ratio",
            "成交额占总成交比": "total_ratio",
            "换手率": "turnover_rate",
            "流通市值": "market_cap",
            "上榜原因": "reason",
            "上榜后1日": "day1_change",
            "上榜后2日": "day2_change",
            "上榜后5日": "day5_change",
            "上榜后10日": "day10_change",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取龙虎榜详情失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_dragon_tiger_institution_daily(self, start_date: str, end_date: str) -> pd.DataFrame:
    """获取机构买卖每日统计-Akshare实现

    获取东方财富网的机构买卖每日统计数据。

    Args:
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD

    Returns:
        pd.DataFrame: 机构买卖每日统计
            - 序号: 序号
            - 代码: 股票代码
            - 名称: 股票名称
            - 收盘价: 收盘价
            - 涨跌幅: 涨跌幅(%)
            - 买方机构数: 买方机构数
            - 卖方机构数: 卖方机构数
            - 机构买入总额: 机构买入总额(元)
            - 机构卖出总额: 机构卖出总额(元)
            - 机构买入净额: 机构买入净额(元)
            - 市场总成交额: 市场总成交额(元)
            - 机构净买额占总成交额比: 机构净买额占总成交额比
            - 换手率: 换手率(%)
            - 流通市值: 流通市值(亿元)
            - 上榜原因: 上榜原因
            - 上榜日期: 上榜日期

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> institution_data = adapter.get_dragon_tiger_institution_daily("20231201", "20231205")
        >>> logger.info(str(institution_data.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取机构买卖每日统计: 开始日期=%s, 结束日期=%s", start_date, end_date)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_institution_data():
            return ak.stock_lhb_jgmmtj_em(start_date=start_date, end_date=end_date)

        # 调用akshare接口获取机构买卖每日统计
        df = _get_institution_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到机构买卖每日统计")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取机构买卖每日统计: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "序号": "rank",
            "代码": "symbol",
            "名称": "name",
            "收盘价": "close_price",
            "涨跌幅": "change_percent",
            "买方机构数": "buy_institution_count",
            "卖方机构数": "sell_institution_count",
            "机构买入总额": "institution_buy_total",
            "机构卖出总额": "institution_sell_total",
            "机构买入净额": "institution_net_buy",
            "市场总成交额": "market_total_amount",
            "机构净买额占总成交额比": "institution_net_buy_ratio",
            "换手率": "turnover_rate",
            "流通市值": "market_cap",
            "上榜原因": "reason",
            "上榜日期": "list_date",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取机构买卖每日统计失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_dragon_tiger_institution_stats(self, period: str = "近一月") -> pd.DataFrame:
    """获取机构席位追踪统计-Akshare实现

    获取东方财富网的机构席位追踪统计数据。

    Args:
        period: str - 统计周期，可选值: "近一月", "近三月", "近六月", "近一年"

    Returns:
        pd.DataFrame: 机构席位追踪统计
            - 序号: 序号
            - 代码: 股票代码
            - 名称: 股票名称
            - 收盘价: 收盘价
            - 涨跌幅: 涨跌幅(%)
            - 龙虎榜成交金额: 龙虎榜成交金额(元)
            - 上榜次数: 上榜次数
            - 机构买入额: 机构买入额(元)
            - 机构买入次数: 机构买入次数
            - 机构卖出额: 机构卖出额(元)
            - 机构卖出次数: 机构卖出次数
            - 机构净买额: 机构净买额(元)
            - 近1个月涨跌幅: 近1个月涨跌幅(%)
            - 近3个月涨跌幅: 近3个月涨跌幅(%)
            - 近6个月涨跌幅: 近6个月涨跌幅(%)
            - 近1年涨跌幅: 近1年涨跌幅(%)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> institution_stats = adapter.get_dragon_tiger_institution_stats("近一月")
        >>> logger.info(str(institution_stats.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取机构席位追踪统计: 周期=%s", period)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_institution_stats():
            return ak.stock_lhb_jgstatistic_em(symbol=period)

        # 调用akshare接口获取机构席位追踪统计
        df = _get_institution_stats()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到机构席位追踪统计")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取机构席位追踪统计: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "序号": "rank",
            "代码": "symbol",
            "名称": "name",
            "收盘价": "close_price",
            "涨跌幅": "change_percent",
            "龙虎榜成交金额": "dragon_tiger_amount",
            "上榜次数": "list_count",
            "机构买入额": "institution_buy_amount",
            "机构买入次数": "institution_buy_count",
            "机构卖出额": "institution_sell_amount",
            "机构卖出次数": "institution_sell_count",
            "机构净买额": "institution_net_amount",
            "近1个月涨跌幅": "month1_change",
            "近3个月涨跌幅": "month3_change",
            "近6个月涨跌幅": "month6_change",
            "近1年涨跌幅": "year1_change",
        }
        df = df.rename(columns=column_mapping)

        # 添加统计周期和数据获取时间戳
        df["period"] = period
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取机构席位追踪统计失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_dragon_tiger_stock_stats(self, period: str = "近一月") -> pd.DataFrame:
    """获取个股上榜统计-Akshare实现

    获取东方财富网的个股上榜统计数据。

    Args:
        period: str - 统计周期，可选值: "近一月", "近三月", "近六月", "近一年"

    Returns:
        pd.DataFrame: 个股上榜统计
            - 序号: 序号
            - 代码: 股票代码
            - 名称: 股票名称
            - 最近上榜日: 最近上榜日期
            - 收盘价: 收盘价
            - 涨跌幅: 涨跌幅(%)
            - 上榜次数: 上榜次数
            - 龙虎榜净买额: 龙虎榜净买额(元)
            - 龙虎榜买入额: 龙虎榜买入额(元)
            - 龙虎榜卖出额: 龙虎榜卖出额(元)
            - 龙虎榜总成交额: 龙虎榜总成交额(元)
            - 买方机构次数: 买方机构次数
            - 卖方机构次数: 卖方机构次数
            - 机构买入净额: 机构买入净额(元)
            - 机构买入总额: 机构买入总额(元)
            - 机构卖出总额: 机构卖出总额(元)
            - 近1个月涨跌幅: 近1个月涨跌幅(%)
            - 近3个月涨跌幅: 近3个月涨跌幅(%)
            - 近6个月涨跌幅: 近6个月涨跌幅(%)
            - 近1年涨跌幅: 近1年涨跌幅(%)

    示例用法:
        >>> adapter = AkshareDataSource()
        >>> stock_stats = adapter.get_dragon_tiger_stock_stats("近一月")
        >>> logger.info(str(stock_stats.head()))
    """
    try:
        logger.info(r"[Akshare] 开始获取个股上榜统计: 周期=%s", period)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_stock_stats():
            return ak.stock_lhb_stock_statistic_em(symbol=period)

        # 调用akshare接口获取个股上榜统计
        df = _get_stock_stats()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到个股上榜统计")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取个股上榜统计: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "序号": "rank",
            "代码": "symbol",
            "名称": "name",
            "最近上榜日": "last_list_date",
            "收盘价": "close_price",
            "涨跌幅": "change_percent",
            "上榜次数": "list_count",
            "龙虎榜净买额": "dragon_tiger_net_amount",
            "龙虎榜买入额": "dragon_tiger_buy_amount",
            "龙虎榜卖出额": "dragon_tiger_sell_amount",
            "龙虎榜总成交额": "dragon_tiger_total_amount",
            "买方机构次数": "buy_institution_count",
            "卖方机构次数": "sell_institution_count",
            "机构买入净额": "institution_net_buy",
            "机构买入总额": "institution_buy_total",
            "机构卖出总额": "institution_sell_total",
            "近1个月涨跌幅": "month1_change",
            "近3个月涨跌幅": "month3_change",
            "近6个月涨跌幅": "month6_change",
            "近1年涨跌幅": "year1_change",
        }
        df = df.rename(columns=column_mapping)

        # 添加统计周期和数据获取时间戳
        df["period"] = period
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取个股上榜统计失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


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
            r"[Akshare] 开始计算股指期货期现基差: symbol=%s, 开始日期=%s, 结束日期=%s", symbol, start_date, end_date
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
            logger.warning("无法确定期货 %(symbol)s 对应的现货指数")
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
