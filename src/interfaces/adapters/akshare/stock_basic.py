def _process_index_data(self, df: pd.DataFrame) -> pd.DataFrame:
    """处理指数数据统一格式"""
    # 使用统一列名映射器标准化列名
    return ColumnMapper.to_english(df)


def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
    """获取股票基本信息-Akshare实现"""
    try:
        # 处理股票代码格式 - 使用专门的格式化函数
        stock_code = format_stock_code_for_source(symbol, "akshare")

        # 使用stock_individual_info_em接口获取股票基本信息
        # 参考文档: https://akshare.akfamily.xyz/data/stock/stock.html#id56
        df = ak.stock_individual_info_em(symbol=stock_code)

        if df is None or df.empty:
            logger.info("未能获取到股票 %s 的基本信息", stock_code)
            return {}

        # 转换为字典
        info_dict = {}
        for _, row in df.iterrows():
            info_dict[row["item"]] = row["value"]

        return info_dict
    except Exception as e:
        logger.error("Akshare获取股票基本信息失败: %s", e)
        return {}


def get_index_components(self, symbol: str) -> List[str]:
    """获取指数成分股-Akshare实现"""
    try:
        # 使用index_stock_cons接口获取指数成分股
        # 参考文档: https://akshare.akfamily.xyz/data/index/index.html#id4
        df = ak.index_stock_cons(symbol=symbol)

        if df is None or df.empty:
            logger.info("未能获取到指数 %s 的成分股", symbol)
            return []

        # 提取股票代码
        if "品种代码" in df.columns:
            return df["品种代码"].tolist()
        elif "成分券代码" in df.columns:
            return df["成分券代码"].tolist()
        else:
            logger.info("无法识别的成分股列名: %s", df.columns.tolist())
            return []
    except Exception as e:
        logger.error("Akshare获取指数成分股失败: %s", e)
        return []
