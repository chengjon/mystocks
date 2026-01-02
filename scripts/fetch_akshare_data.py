#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare 数据获取脚本
获取 A 股市场行业、概念、股票基本信息等数据

数据来源: 东方财富网 - AkShare
文档参考: /opt/mydoc/mymd/Astock_data_source.md
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time


def fetch_industry_data():
    """
    获取行业板块数据

    数据接口: ak.stock_board_industry_name_em()
    对应文档: 行业板块名称列表

    Returns:
        pd.DataFrame: 行业板块数据
        - 排名
        - 板块名称
        - 板块代码
        - 最新价
        - 涨跌额
        - 涨跌幅
        - 总市值
        - 换手率
        - 上涨家数
        - 下跌家数
        - 领涨股票
        - 领涨股票-涨跌幅
    """
    print("=" * 80)
    print("📋 获取行业板块名称列表...")

    try:
        df = ak.stock_board_industry_name_em()
        print(f"✅ 成功获取 {len(df)} 个行业板块")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取行业板块失败: {e}")
        return pd.DataFrame()


def fetch_industry_cons(symbol: str = "黑色金属"):
    """
    获取指定行业的成分股

    Args:
        symbol: 行业板块名称或代码

    Returns:
        pd.DataFrame: 成分股数据
    """
    print("=" * 80)
    print(f"📋 获取行业 '{symbol}' 的成分股...")

    try:
        df = ak.stock_board_industry_cons_em(symbol=symbol)
        print(f"✅ 成功获取 {len(df)} 只成分股")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取成分股失败: {e}")
        return pd.DataFrame()


def fetch_concept_data():
    """
    获取概念板块数据

    数据接口: ak.stock_board_concept_name_em()
    对应文档: 概念板块名称列表

    Returns:
        pd.DataFrame: 概念板块数据
        - 排名
        - 板块名称
        - 板块代码
        - 最新价
        - 涨跌额
        - 涨跌幅
        - 总市值
        - 换手率
        - 上涨家数
        - 下跌家数
        - 领涨股票
        - 领涨股票-涨跌幅
    """
    print("=" * 80)
    print("📋 获取概念板块名称列表...")

    try:
        df = ak.stock_board_concept_name_em()
        print(f"✅ 成功获取 {len(df)} 个概念板块")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取概念板块失败: {e}")
        return pd.DataFrame()


def fetch_concept_cons(symbol: str = "可燃冰"):
    """
    获取指定概念的成分股

    Args:
        symbol: 概念板块名称或代码

    Returns:
        pd.DataFrame: 成分股数据
        - 序号
        - 代码
        - 名称
        - 最新价
        - 涨跌幅
        - 涨跌额
        - 成交量
        - 成交额
        - 振幅
        - 最高
        - 最低
        - 今开
        - 昨收
        - 换手率
        - 市盈率-动态
        - 市净率
    """
    print("=" * 80)
    print(f"📋 获取概念板块 '{symbol}' 的成分股...")

    try:
        df = ak.stock_board_concept_cons_em(symbol=symbol)
        print(f"✅ 成功获取 {len(df)} 只成分股")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取概念成分股失败: {e}")
        return pd.DataFrame()


def fetch_stock_list():
    """
    获取 A 股所有股票基本信息

    数据接口: ak.stock_info_a_code_name()
    对应文档: 股票代码和名称

    Returns:
        pd.DataFrame: 股票列表
        - code: 股票代码
        - name: 股票名称
    """
    print("=" * 80)
    print("📋 获取 A 股所有股票代码和名称...")

    try:
        # 获取 A 股股票列表
        df_sh = ak.stock_info_sh_name_code(indicator="主板A股")
        df_sz = ak.stock_info_sz_name_code(indicator="A股列表")

        # 合并沪深数据
        df_sh['market'] = 'SH'
        df_sz['market'] = 'SZ'

        df = pd.concat([df_sh, df_sz], ignore_index=True)

        print(f"✅ 成功获取 {len(df)} 只 A 股股票")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return pd.DataFrame()


def fetch_stock_info(symbol: str = "000001"):
    """
    获取单只股票的详细信息

    Args:
        symbol: 股票代码（不带前缀）

    Returns:
        pd.DataFrame: 股票详细信息
    """
    print("=" * 80)
    print(f"📋 获取股票 {symbol} 的详细信息...")

    try:
        # 获取个股信息
        df = ak.stock_individual_info_em(symbol=symbol)
        print(f"✅ 成功获取股票 {symbol} 的信息")
        print(f"   列: {list(df['item'].values)}")
        return df
    except Exception as e:
        print(f"❌ 获取股票信息失败: {e}")
        return pd.DataFrame()


def fetch_stock_history(symbol: str = "000001",
                        start_date: str = "20240101",
                        end_date: str = "20241231",
                        adjust: str = "hfq"):
    """
    获取单只股票的历史行情数据

    Args:
        symbol: 股票代码
        start_date: 开始日期 (YYYYMMDD)
        end_date: 结束日期 (YYYYMMDD)
        adjust: 复权类型
            - "": 不复权
            - "qfq": 前复权
            - "hfq": 后复权

    Returns:
        pd.DataFrame: 历史行情数据
        - 日期
        - 股票代码
        - 开盘
        - 收盘
        - 最高
        - 最低
        - 成交量
        - 成交额
        - 振幅
        - 涨跌幅
        - 涨跌额
        - 换手率
    """
    print("=" * 80)
    print(f"📋 获取股票 {symbol} 的历史行情 ({start_date} ~ {end_date})...")

    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        print(f"✅ 成功获取 {len(df)} 条历史数据")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取历史行情失败: {e}")
        return pd.DataFrame()


def fetch_concept_history(symbol: str = "绿色电力",
                          start_date: str = "20240101",
                          end_date: str = "20241231"):
    """
    获取概念板块的历史走势

    Args:
        symbol: 概念板块名称
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        pd.DataFrame: 概念板块历史数据
    """
    print("=" * 80)
    print(f"📋 获取概念板块 '{symbol}' 的历史走势...")

    try:
        df = ak.stock_board_concept_hist_em(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        print(f"✅ 成功获取 {len(df)} 条历史数据")
        print(f"   列: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 获取概念历史失败: {e}")
        return pd.DataFrame()


def save_to_csv(df: pd.DataFrame, filename: str):
    """
    保存数据到 CSV 文件

    Args:
        df: 数据框
        filename: 文件名（自动保存在 /tmp 目录）
    """
    if not df.empty:
        filepath = f"/tmp/{filename}"
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"💾 数据已保存到: {filepath}")
    else:
        print("⚠️  数据为空，不保存文件")


# ============================================================================
# 主函数 - 批量获取所有数据
# ============================================================================

def main():
    """主函数 - 批量获取所有数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "=" * 80)
    print("🚀 AkShare 数据获取工具")
    print("=" * 80)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 获取行业板块列表
    print("\n【1/6】行业板块数据")
    industry_df = fetch_industry_data()
    if not industry_df.empty:
        save_to_csv(industry_df, f"industry_list_{timestamp}.csv")
        time.sleep(1)  # 避免请求过快

    # 2. 获取行业成分股示例
    print("\n【2/6】行业成分股数据（示例：黑色金属）")
    industry_cons_df = fetch_industry_cons("黑色金属")
    if not industry_cons_df.empty:
        save_to_csv(industry_cons_df, f"industry_cons_example_{timestamp}.csv")
        time.sleep(1)

    # 3. 获取概念板块列表
    print("\n【3/6】概念板块数据")
    concept_df = fetch_concept_data()
    if not concept_df.empty:
        save_to_csv(concept_df, f"concept_list_{timestamp}.csv")
        time.sleep(1)

    # 4. 获取概念成分股示例
    print("\n【4/6】概念成分股数据（示例：可燃冰）")
    concept_cons_df = fetch_concept_cons("可燃冰")
    if not concept_cons_df.empty:
        save_to_csv(concept_cons_df, f"concept_cons_example_{timestamp}.csv")
        time.sleep(1)

    # 5. 获取股票列表
    print("\n【5/6】股票代码列表")
    stock_list_df = fetch_stock_list()
    if not stock_list_df.empty:
        save_to_csv(stock_list_df, f"stock_list_{timestamp}.csv")
        time.sleep(1)

    # 6. 获取单只股票详细信息（示例）
    print("\n【6/6】股票详细信息（示例：000001 平安银行）")
    stock_info_df = fetch_stock_info("000001")
    if not stock_info_df.empty:
        save_to_csv(stock_info_df, f"stock_info_example_{timestamp}.csv")

    # 获取单只股票历史行情（示例）
    print("\n【额外】股票历史行情（示例：000001）")
    stock_history_df = fetch_stock_history(
        symbol="000001",
        start_date="20240101",
        end_date="20241231",
        adjust="hfq"
    )
    if not stock_history_df.empty:
        save_to_csv(stock_history_df, f"stock_history_example_{timestamp}.csv")

    print("\n" + "=" * 80)
    print("✅ 数据获取完成!")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 返回汇总信息
    return {
        "industry_list": len(industry_df) if not industry_df.empty else 0,
        "industry_cons": len(industry_cons_df) if not industry_cons_df.empty else 0,
        "concept_list": len(concept_df) if not concept_df.empty else 0,
        "concept_cons": len(concept_cons_df) if not concept_cons_df.empty else 0,
        "stock_list": len(stock_list_df) if not stock_list_df.empty else 0,
        "stock_info": len(stock_info_df) if not stock_info_df.empty else 0,
        "stock_history": len(stock_history_df) if not stock_history_df.empty else 0,
    }


if __name__ == "__main__":
    results = main()

    print("\n📊 数据统计:")
    for key, value in results.items():
        print(f"   - {key}: {value} 条记录")

    print("\n💡 提示:")
    print("   - 所有数据已保存到 /tmp 目录")
    print("   - 可以使用 pandas.read_csv() 读取这些文件")
    print("   - 如需获取其他股票/板块数据，修改参数即可")
