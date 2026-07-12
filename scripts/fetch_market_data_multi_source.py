#!/usr/bin/env python3
"""多源数据获取脚本
使用 efinance, baostock, easyquotation 获取股票板块和全市场行情数据

数据源:
- efinance: 东方财富网数据
- baostock: 证券数据
- easyquotation: 新浪/腾讯实时行情

文档参考: /opt/mydoc/mymd/Astock_data_source.md
"""

import time
from datetime import datetime

import pandas as pd


def fetch_stock_belong_board_efinance(stock_code: str = "300377"):
    """使用 efinance 获取股票所属板块

    对应文档: Line 62-74
    接口: efinance.stock.get_belong_board(stock_code)

    Args:
        stock_code: 股票代码（不带前缀）

    Returns:
        pd.DataFrame: 板块数据
        - 股票名称
        - 股票代码
        - 板块代码
        - 板块名称
        - 板块涨幅

    """
    print("=" * 80)
    print(f"📊 [efinance] 获取股票 {stock_code} 所属板块...")

    try:
        import efinance as ef

        df = ef.stock.get_belong_board(stock_code)

        if df is not None and not df.empty:
            print(f"✅ 成功获取 {len(df)} 个板块信息")
            print(f"   列: {list(df.columns)}")
            print("\n   前3条数据:")
            print(df.head(3).to_string())
            return df
        print("⚠️  未找到板块信息")
        return pd.DataFrame()

    except ImportError:
        print("❌ efinance 未安装，请运行: pip install efinance")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取板块失败: {e}")
        return pd.DataFrame()


def fetch_stock_industry_baostock(stock_code: str = "300377"):
    """使用 baostock 查询股票行业

    对应文档: Line 75-82
    接口: bao.query_stock_industry(stock_code)

    Args:
        stock_code: 股票代码

    Returns:
        pd.DataFrame: 行业数据
        - updateDate: 更新日期
        - code: 股票代码
        - code_name: 股票名称
        - industry: 行业
        - industryClassification: 行业分类

    """
    print("=" * 80)
    print(f"📊 [baostock] 查询股票 {stock_code} 的行业信息...")

    try:
        import baostock as bs

        # 登陆系统
        lg = bs.login()
        if lg.error_code != "0":
            print(f"❌ 登录失败: {lg.error_msg}")
            return pd.DataFrame()

        # 查询行业
        rs = bs.query_stock_industry(code=stock_code)

        # 打印结果
        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        bs.logout()

        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            print("✅ 成功获取行业信息")
            print(f"   列: {list(df.columns)}")
            print("\n   数据:")
            print(df.to_string())
            return df
        print("⚠️  未找到行业信息")
        return pd.DataFrame()

    except ImportError:
        print("❌ baostock 未安装，请运行: pip install baostock")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 查询行业失败: {e}")
        return pd.DataFrame()


def fetch_market_realtime_efinance(market: str = "沪深A股"):
    """使用 efinance 获取全市场实时行情

    对应文档: Line 458-466
    接口: ef.stock.get_realtime_quotes(fs)

    Args:
        market: 市场类型
            - None: 沪深京A股市场
            - '沪深A股': 沪深A股市场
            - '沪A': 沪市A股
            - '深A': 深市A股
            - '创业板': 创业板
            - '科创板': 科创板
            - '行业板块': 行业板块
            - '概念板块': 概念板块
            - 等等...

    Returns:
        pd.DataFrame: 全市场行情数据
        - 股票代码、股票名称、涨跌幅、最新价、最高、最低、今开
        - 涨跌额、换手率、量比、动态市盈率、成交量、成交额
        - 昨日收盘、总市值、流通市值、行情ID、市场类型
        - 更新时间、最新交易日

    """
    print("=" * 80)
    print(f"📊 [efinance] 获取 {market} 全市场实时行情...")

    try:
        import efinance as ef

        # 获取实时行情
        df = ef.stock.get_realtime_quotes(fs=[market] if market else None)

        if df is not None and not df.empty:
            print(f"✅ 成功获取 {len(df)} 只股票的实时行情")
            print(f"   列: {list(df.columns)}")
            print("\n   前5条数据:")
            print(df.head(5).to_string())
            return df
        print("⚠️  未获取到行情数据")
        return pd.DataFrame()

    except ImportError:
        print("❌ efinance 未安装，请运行: pip install efinance")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取行情失败: {e}")
        return pd.DataFrame()


def fetch_market_snapshot_easyquotation(source: str = "tencent", prefix: bool = True):
    """使用 EasyQuotation 获取全市场快照

    对应文档: Line 479-502
    接口: quotation.market_snapshot(prefix=True)

    Args:
        source: 数据源
            - 'tencent' 或 'qq': 腾讯财经
            - 'sina': 新浪财经
        prefix: 是否带市场前缀 (sz/sh/bj)

    Returns:
        pd.DataFrame: 全市场行情数据
        - name: 股票名称
        - code: 股票代码
        - 各项实时行情数据

    """
    print("=" * 80)
    print(f"📊 [easyquotation] 获取全市场快照 (数据源: {source})...")

    try:
        import easyquotation as eq

        # 选择行情源
        quotation = eq.use(source)

        # 获取所有股票行情
        market_data = quotation.market_snapshot(prefix=prefix)

        # 转换为 DataFrame
        df = pd.DataFrame.from_dict(market_data, orient="index")

        if not df.empty:
            print(f"✅ 成功获取 {len(df)} 只股票的快照数据")
            print(f"   列: {list(df.columns)}")
            print("\n   前5条数据:")
            print(df.head(5).to_string())
            return df
        print("⚠️  未获取到快照数据")
        return pd.DataFrame()

    except ImportError:
        print("❌ easyquotation 未安装，请运行: pip install easyquotation")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取快照失败: {e}")
        return pd.DataFrame()


def fetch_all_stock_codes_easyquotation():
    """使用 EasyQuotation 获取所有 A 股股票代码

    对应文档: Line 914-932
    接口: eq.update_stock_codes()

    Returns:
        list: 股票代码列表

    """
    print("=" * 80)
    print("📊 [easyquotation] 获取所有 A 股股票代码...")

    try:
        import easyquotation as eq

        # 更新并获取股票代码列表
        codes = eq.update_stock_codes()

        if codes:
            print(f"✅ 成功获取 {len(codes)} 个股票代码")
            print(f"   示例代码 (前10个): {codes[:10]}")

            # 转换为 DataFrame
            df_codes = pd.DataFrame({"code": codes})
            print("\n   数据预览:")
            print(df_codes.head(10).to_string())

            return codes
        print("⚠️  未获取到股票代码")
        return []

    except ImportError:
        print("❌ easyquotation 未安装，请运行: pip install easyquotation")
        return []
    except Exception as e:
        print(f"❌ 获取股票代码失败: {e}")
        return []


def fetch_all_stock_codes_mairui(api_key: str = None):
    """使用麦蕊数据接口获取所有 A 股股票代码

    对应文档: Line 935-949
    接口: https://api.mairui.club/hslt/list/{api_key}

    Args:
        api_key: 麦蕊 API 密钥 (需要注册获取)

    Returns:
        pd.DataFrame: 股票列表数据

    """
    print("=" * 80)
    print("📊 [麦蕊数据] 获取所有 A 股股票代码...")

    if not api_key:
        print("⚠️  需要提供麦蕊 API 密钥")
        print("   注册地址: https://www.mairui.club/")
        print("   使用方法: fetch_all_stock_codes_mairui('your_api_key')")
        return pd.DataFrame()

    try:
        import requests

        url = f"https://api.mairui.club/hslt/list/{api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            print(f"✅ 成功获取 {len(df)} 只股票信息")
            print(f"   列: {list(df.columns)}")
            print("\n   前5条数据:")
            print(df.head(5).to_string())

            return df
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return pd.DataFrame()

    except ImportError:
        print("❌ requests 未安装，请运行: pip install requests")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取股票代码失败: {e}")
        return pd.DataFrame()


def compare_market_data(stock_code: str = "000001"):
    """对比不同数据源的股票行情数据

    Args:
        stock_code: 股票代码

    """
    print("\n" + "=" * 80)
    print(f"🔍 对比不同数据源的股票 {stock_code} 行情数据")
    print("=" * 80)

    results = {}

    # 1. efinance 实时行情
    try:
        import efinance as ef

        df_ef = ef.stock.get_realtime_quotes()
        if not df_ef.empty:
            stock_data = df_ef[df_ef["股票代码"] == stock_code]
            if not stock_data.empty:
                results["efinance"] = stock_data.iloc[0]
                print("\n✅ [efinance] 获取成功")
                print(f"   股票名称: {stock_data.iloc[0]['股票名称']}")
                print(f"   最新价: {stock_data.iloc[0]['最新价']}")
                print(f"   涨跌幅: {stock_data.iloc[0]['涨跌幅']}")
    except Exception as e:
        print(f"\n❌ [efinance] 获取失败: {e}")

    # 2. easyquotation 快照
    try:
        import easyquotation as eq

        quotation = eq.use("tencent")
        market_data = quotation.market_snapshot(prefix=True)

        # 查找指定股票
        code_sh = f"sh{stock_code}" if stock_code.startswith("6") else f"sz{stock_code}"
        if code_sh in market_data:
            results["easyquotation"] = market_data[code_sh]
            print("\n✅ [easyquotation] 获取成功")
            print(f"   股票名称: {market_data[code_sh].get('name', 'N/A')}")
            print(f"   最新价: {market_data[code_sh].get('now', 'N/A')}")
            print(f"   涨跌: {market_data[code_sh].get('涨跌', 'N/A')}")
    except Exception as e:
        print(f"\n❌ [easyquotation] 获取失败: {e}")

    return results


def save_to_csv(df: pd.DataFrame, filename: str):
    """保存数据到 CSV"""
    if not df.empty:
        filepath = f"/tmp/{filename}"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"💾 数据已保存到: {filepath}")


# ============================================================================
# 主函数
# ============================================================================


def main():
    """主函数 - 演示所有接口"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "=" * 80)
    print("🚀 多源股票数据获取工具")
    print("=" * 80)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # =========================================================================
    # 1. 获取股票所属板块 (efinance)
    # =========================================================================
    print("\n【任务 1/4】获取股票所属板块 (efinance)")
    print("-" * 80)

    belong_board_df = fetch_stock_belong_board_efinance("300377")
    if not belong_board_df.empty:
        save_to_csv(belong_board_df, f"stock_belong_board_300377_{timestamp}.csv")
    time.sleep(1)

    # =========================================================================
    # 2. 查询股票行业 (baostock)
    # =========================================================================
    print("\n【任务 2/4】查询股票行业信息 (baostock)")
    print("-" * 80)

    industry_df = fetch_stock_industry_baostock("300377")
    if not industry_df.empty:
        save_to_csv(industry_df, f"stock_industry_300377_{timestamp}.csv")
    time.sleep(1)

    # =========================================================================
    # 3. 获取全市场行情 (efinance)
    # =========================================================================
    print("\n【任务 3/4】获取全市场实时行情 (efinance)")
    print("-" * 80)

    # 获取创业板数据（示例）
    market_df = fetch_market_realtime_efinance("创业板")
    if not market_df.empty:
        save_to_csv(market_df, f"market_realtime_cyb_{timestamp}.csv")
    time.sleep(1)

    # =========================================================================
    # 4. 获取全市场快照 (easyquotation)
    # =========================================================================
    print("\n【任务 4/6】获取全市场快照 (easyquotation)")
    print("-" * 80)

    snapshot_df = fetch_market_snapshot_easyquotation("tencent", prefix=True)
    if not snapshot_df.empty:
        # 保存前100条数据作为示例
        save_to_csv(snapshot_df.head(100), f"market_snapshot_tencent_{timestamp}.csv")
    time.sleep(1)

    # =========================================================================
    # 5. 获取所有股票代码 (easyquotation)
    # =========================================================================
    print("\n【任务 5/6】获取所有 A 股股票代码 (easyquotation)")
    print("-" * 80)

    stock_codes_list = fetch_all_stock_codes_easyquotation()
    if stock_codes_list:
        # 保存股票代码列表
        df_codes = pd.DataFrame({"code": stock_codes_list})
        save_to_csv(df_codes, f"stock_codes_all_easyquotation_{timestamp}.csv")
    time.sleep(1)

    # =========================================================================
    # 6. 获取所有股票代码 (麦蕊数据 - 需要API密钥)
    # =========================================================================
    print("\n【任务 6/6】获取所有 A 股股票代码 (麦蕊数据)")
    print("-" * 80)
    print("   ⚠️  此功能需要麦蕊 API 密钥")
    print("   如有密钥，取消下面代码的注释即可使用")
    # mairui_df = fetch_all_stock_codes_mairui("your_api_key_here")
    # if not mairui_df.empty:
    #     save_to_csv(mairui_df, f"stock_codes_all_mairui_{timestamp}.csv")

    # =========================================================================
    # 额外功能: 数据对比
    # =========================================================================
    print("\n【额外功能】对比不同数据源")
    print("-" * 80)

    comparison = compare_market_data("000001")

    # =========================================================================
    # 总结
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ 数据获取完成!")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 返回统计信息
    return {
        "belong_board": len(belong_board_df) if not belong_board_df.empty else 0,
        "industry_info": len(industry_df) if not industry_df.empty else 0,
        "market_realtime": len(market_df) if not market_df.empty else 0,
        "market_snapshot": len(snapshot_df) if not snapshot_df.empty else 0,
        "stock_codes_eq": len(stock_codes_list) if stock_codes_list else 0,
        "comparison_sources": len(comparison),
    }


if __name__ == "__main__":
    print("\n💡 提示:")
    print("   - 本脚本使用多个数据源获取股票数据")
    print("   - 请确保已安装依赖: pip install efinance baostock easyquotation pandas requests")
    print("   - 所有数据文件保存在 /tmp 目录")
    print("   - 建议在网络良好环境下运行")
    print("   - 麦蕊数据 API 需要注册获取密钥: https://www.mairui.club/\n")

    results = main()

    print("\n📊 数据统计:")
    for key, value in results.items():
        print(f"   - {key}: {value} 条记录")

    print("\n🔗 接口说明:")
    print("   - efinance: 东方财富网数据，更新快，数据丰富")
    print("   - baostock: 历史数据完整，适合回测")
    print("   - easyquotation: 轻量级实时行情，速度快")
    print("   - 麦蕊数据: 需要API密钥，提供更详细的股票信息")
    print("\n📝 新增功能:")
    print("   ✅ 获取所有A股股票代码 (easyquotation)")
    print("   ✅ 获取所有A股股票代码 (麦蕊数据API)")
