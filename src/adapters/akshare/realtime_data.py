# pylint: disable=undefined-variable  # 混入模块使用动态类型
def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
    """获取实时数据-Akshare实现"""
    try:
        # 使用stock_zh_a_spot接口获取股票实时数据
        df = ak.stock_zh_a_spot()

        if df is None or df.empty:
            logger.info("未能获取到股票 %s 的实时数据", symbol)
            return {}

        # 筛选指定股票
        filtered_df = df[df["代码"] == symbol]
        if filtered_df.empty:
            logger.info("未能找到股票 %s 的实时数据", symbol)
            return {}

        # 转换为字典
        return filtered_df.iloc[0].to_dict()
    except Exception as e:
        logger.error("Akshare获取实时数据失败: %s", e)
        return {}
        return {}


def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
    """获取交易日历-Akshare实现"""
    try:
        # 使用tool_trade_date_hist_sina接口获取交易日历
        df = ak.tool_trade_date_hist_sina()

        if df is None or df.empty:
            logger.info(r"未能获取到交易日历数据")
            return pd.DataFrame()

        # 筛选日期范围
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        start_date = pd.to_datetime(normalize_date(start_date))
        end_date = pd.to_datetime(normalize_date(end_date))

        mask = (df["trade_date"] >= start_date) & (df["trade_date"] <= end_date)
        filtered_df = df[mask]

        return filtered_df
    except Exception as e:
        logger.error("Akshare获取交易日历失败: %s", e)
        return pd.DataFrame()
