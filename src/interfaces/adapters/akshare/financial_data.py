def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
    """获取财务数据-Akshare实现"""
    try:
        # 使用stock_financial_abstract接口获取财务摘要数据
        stock_code = format_stock_code_for_source(symbol, "akshare")
        df = ak.stock_financial_abstract(symbol=stock_code)

        if df is None or df.empty:
            logger.info("未能获取到股票 %s 的财务数据", symbol)
            return pd.DataFrame()

        return df
    except Exception as e:
        logger.error("Akshare获取财务数据失败: %s", e)
        return pd.DataFrame()


def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取新闻数据-Akshare实现"""
    try:
        # 如果提供了股票代码，获取个股新闻；否则获取市场新闻
        if symbol:
            # 获取个股新闻
            stock_code = format_stock_code_for_source(symbol, "akshare")
            df = ak.stock_news_em(symbol=stock_code)
        else:
            # 获取市场新闻
            df = ak.stock_news_em()

        if df is None or df.empty:
            logger.info(r"未能获取到新闻数据")
            return []

        # 限制返回数量
        if limit and len(df) > limit:
            df = df.head(limit)

        # 转换为字典列表
        return df.to_dict("records")
    except Exception as e:
        logger.error("Akshare获取新闻数据失败: %s", e)
        return []
