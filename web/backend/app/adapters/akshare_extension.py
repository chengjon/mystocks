"""
Akshare适配器扩展模块
添加4个新方法支持股票数据扩展功能

数据源: 东方财富网 (通过Akshare)
新增方法:
1. get_etf_spot() - ETF实时行情
2. get_stock_fund_flow() - 个股资金流向
3. get_stock_lhb_detail() - 龙虎榜详细数据
4. get_dividend_data() - 分红配送数据
"""
import akshare as ak
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AkshareExtension:
    """Akshare适配器扩展类"""

    @staticmethod
    def get_etf_spot() -> pd.DataFrame:
        """
        获取ETF基金实时行情数据 - 东方财富网

        Returns:
            pd.DataFrame: ETF实时数据
                columns: symbol, name, latest_price, change_percent, change_amount,
                        volume, amount, open_price, high_price, low_price, prev_close,
                        turnover_rate, total_market_cap, circulating_market_cap
        """
        try:
            df = ak.fund_etf_spot_em()
            if df is not None and not df.empty:
                # 标准化列名
                column_mapping = {
                    '代码': 'symbol',
                    '名称': 'name',
                    '最新价': 'latest_price',
                    '涨跌幅': 'change_percent',
                    '涨跌额': 'change_amount',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '开盘价': 'open_price',
                    '最高价': 'high_price',
                    '最低价': 'low_price',
                    '昨收': 'prev_close',
                    '换手率': 'turnover_rate',
                    '总市值': 'total_market_cap',
                    '流通市值': 'circulating_market_cap'
                }
                df = df.rename(columns=column_mapping)
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取ETF数据失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_fund_flow(symbol: str, timeframe: str = "1") -> Dict:
        """
        获取个股资金流向数据 - 东方财富网

        Args:
            symbol: 股票代码 (如: 600519.SH)
            timeframe: 时间维度 ("1"=今日, "3"=3日, "5"=5日, "10"=10日)

        Returns:
            Dict: 资金流向数据
                {
                    "main_net_inflow": 主力净流入额,
                    "main_net_inflow_rate": 主力净流入占比,
                    "super_large_net_inflow": 超大单净流入额,
                    "large_net_inflow": 大单净流入额,
                    "medium_net_inflow": 中单净流入额,
                    "small_net_inflow": 小单净流入额
                }
        """
        try:
            # 将数字转换为中文（akshare需要中文参数）
            timeframe_map = {
                "1": "今日",
                "3": "3日",
                "5": "5日",
                "10": "10日"
            }
            indicator = timeframe_map.get(timeframe, "今日")

            # 使用akshare的stock_individual_fund_flow_rank接口
            df = ak.stock_individual_fund_flow_rank(indicator=indicator)
            if df is None or df.empty:
                logger.warning(f"未获取到{indicator}资金流向数据")
                return {}

            # 处理股票代码格式 (移除.SH/.SZ后缀)
            stock_code = symbol.split('.')[0] if '.' in symbol else symbol

            # 筛选指定股票
            filtered_df = df[df['代码'] == stock_code]

            if filtered_df.empty:
                logger.warning(f"未找到股票代码 {symbol} 的资金流向数据")
                return {}

            # 转换为统一格式
            row = filtered_df.iloc[0]
            return {
                "symbol": symbol,
                "main_net_inflow": float(row.get('主力净流入-净额', 0)),
                "main_net_inflow_rate": float(row.get('主力净流入-净占比', 0)),
                "super_large_net_inflow": float(row.get('超大单净流入-净额', 0)),
                "large_net_inflow": float(row.get('大单净流入-净额', 0)),
                "medium_net_inflow": float(row.get('中单净流入-净额', 0)),
                "small_net_inflow": float(row.get('小单净流入-净额', 0))
            }
        except Exception as e:
            logger.error(f"获取资金流向数据失败: {e}")
            return {}

    @staticmethod
    def get_stock_lhb_detail(date: str) -> pd.DataFrame:
        """
        获取指定日期龙虎榜详细数据 - 东方财富网

        Args:
            date: 日期 (格式: YYYYMMDD 或 YYYY-MM-DD)

        Returns:
            pd.DataFrame: 龙虎榜数据
                columns: symbol, name, reason, buy_amount, sell_amount, net_amount,
                        turnover_rate, institution_buy, institution_sell
        """
        try:
            # 格式化日期(移除连字符)
            date_str = date.replace('-', '')

            # akshare API使用start_date和end_date参数
            df = ak.stock_lhb_detail_em(start_date=date_str, end_date=date_str)
            if df is not None and not df.empty:
                # 标准化列名
                column_mapping = {
                    '代码': 'symbol',
                    '名称': 'name',
                    '解读': 'reason',
                    '收盘价': 'close_price',
                    '涨跌幅': 'change_percent',
                    '龙虎榜净买额': 'net_amount',
                    '龙虎榜买入额': 'buy_amount',
                    '龙虎榜卖出额': 'sell_amount',
                    '龙虎榜成交额': 'turnover_amount',
                    '市场总成交额': 'market_total_amount',
                    '净买额占总成交比': 'net_amount_ratio',
                    '成交额占总成交比': 'turnover_ratio',
                    '换手率': 'turnover_rate',
                    '流通市值': 'circulating_market_cap'
                }
                df = df.rename(columns=column_mapping)

                # 提取机构买卖额(如果akshare提供的话)
                if '机构买入额' in df.columns:
                    df['institution_buy'] = df['机构买入额']
                if '机构卖出额' in df.columns:
                    df['institution_sell'] = df['机构卖出额']

                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取龙虎榜数据失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_dividend_data(symbol: str) -> pd.DataFrame:
        """
        获取股票分红配送数据 - 东方财富网

        Args:
            symbol: 股票代码 (如: 600519.SH)

        Returns:
            pd.DataFrame: 分红配送数据
                columns: symbol, announce_date, ex_dividend_date, record_date,
                        dividend_ratio, bonus_share_ratio, transfer_ratio,
                        allotment_ratio, allotment_price
        """
        try:
            # 处理股票代码格式
            stock_code = symbol.split('.')[0] if '.' in symbol else symbol

            # 使用akshare的stock_fhps_detail_em接口
            df = ak.stock_fhps_detail_em(symbol=stock_code)
            if df is not None and not df.empty:
                # 标准化列名
                column_mapping = {
                    '股票代码': 'symbol',
                    '公告日期': 'announce_date',
                    '除权除息日': 'ex_dividend_date',
                    '股权登记日': 'record_date',
                    '每股送转': 'bonus_share_ratio',
                    '每股派息': 'dividend_ratio',
                    '分红年度': 'dividend_year',
                    '方案进度': 'plan_progress'
                }
                df = df.rename(columns=column_mapping)

                # 添加symbol列(如果不存在)
                if 'symbol' not in df.columns:
                    df['symbol'] = symbol

                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取分红配送数据失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_sector_fund_flow(date: Optional[str] = None) -> pd.DataFrame:
        """
        获取行业/概念板块资金流向 - 东方财富网

        Args:
            date: 日期 (格式: YYYY-MM-DD), 默认为最新交易日

        Returns:
            pd.DataFrame: 板块资金流向数据
        """
        try:
            # 获取行业板块资金流向
            df = ak.stock_sector_fund_flow_rank(indicator="今日")
            if df is not None and not df.empty:
                column_mapping = {
                    '序号': 'rank',
                    '板块': 'sector_name',
                    '主力净流入-净额': 'main_net_inflow',
                    '主力净流入-净占比': 'main_net_inflow_rate',
                    '超大单净流入-净额': 'super_large_net_inflow',
                    '大单净流入-净额': 'large_net_inflow',
                    '中单净流入-净额': 'medium_net_inflow',
                    '小单净流入-净额': 'small_net_inflow',
                    '涨跌幅': 'change_percent',
                    '领涨股': 'leading_stock',
                    '领涨股-涨跌幅': 'leading_stock_change_percent'
                }
                df = df.rename(columns=column_mapping)
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取板块资金流向数据失败: {e}")
            return pd.DataFrame()


# 全局单例
_akshare_extension = None


def get_akshare_extension() -> AkshareExtension:
    """获取Akshare扩展单例"""
    global _akshare_extension
    if _akshare_extension is None:
        _akshare_extension = AkshareExtension()
    return _akshare_extension
