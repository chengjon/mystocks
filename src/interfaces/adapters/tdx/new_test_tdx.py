# pylint: disable=import-error,no-name-in-module
from tqcenter import tq

"""
    这里是tq的简单使用示例
    使用时请确保已经启动通达信客户端并登录
    取消对应注释即可运行对应功能
"""

"""
    参数设置
"""
codes = ["600519.SH"]  # 传入的股票代码格式必须是标准格式：6位数+市场后缀（.SH/.SZ/.JJ等）
startime = "20250620"  # 传入的时间格式必须是：YYYYMMDD 或 YYYYMMDDHHMMSS
endtime = "20250801"
period = "1d"  # K线周期：1d/1w/1m/5m/15m/30m/60m等
dividend_type = "none"  # 复权类型：none-不复权，front-前复权，back-后复权

# 初始化
tq.initialize(__file__)  # 所有策略连接通达信客户端都必须调用此函数进行初始化

"""
    刷新行情缓存 刷新后5分钟内取最新report和k线数据不会触发刷新
"""
refresh_cache = tq.refresh_cache()
print(refresh_cache)

"""
    缓存历史K线 目前仅支持1m 5m 1d三种类型数据 不建议一次更新太多，会堵塞策略和客户端
"""
refresh_kline = tq.refresh_kline(stock_list=["600519.SH"], period="1d")
print(refresh_kline)

"""
    获取K线数据  获取K线数据需要先在客户端中下载对应盘后数据，调用会触发客户端刷新数据，耗时过长请耐心等待
    field_list可以筛选返回字段，默认返回全部字段 比如 field_list=['Open','Close'] 就是只取开盘价和收盘价
    count可以设置每只股票取的数据量
    暂时不支持获取分笔数据
    开高低收单位为元，成交量单位为手，成交额单位为万元
"""
# df = tq.get_market_data(
#         # field_list=['Close'],
#         stock_list=codes,
#         start_time=startime,
#         end_time=endtime,
#         count=30,
#         # dividend_type=dividend_type,
#         period=period,
#         # fill_data=True
#     )
# print(df)

"""
    获取分红送配数据
"""
# divid_factors = tq.get_divid_factors(
#         stock_code=codes[0],
#         start_time='',
#         end_time=''
#     )
# print(divid_factors)

"""
    获取报表数据,调用会触发客户端刷新数据，耗时过长请耐心等待
    总成交额为万位，其他无特殊说明均为个位
"""
# report_data = tq.get_report_data(stock_code = codes[0])
# print(report_data)

"""
    获取基础财务数据 与专业财务数据有区别 不需要下载专业财务数据
    field_list可以筛选返回字段，默认返回全部字段 比如 field_list=['J_zgb','ActiveCapital'] 就是只取总股本和流通股本
    股本 资产 负债 利润 现金流量等数据均为万位
"""
# fdc = tq.get_instrument_detail(codes[0], field_list=[])
# print(fdc)

"""
    专业财务数据 需要先在客户端下载专业财务数据
    table_list可以筛选返回字段，默认返回固定字段 格式与field_list不同，是 表名.列名 例如 Capital.total_capital 就是 股本表中的总股本字段
    table_list=['Capital'] 就是返回股本表全部字段
    table_list = ['ALL'] #获取目前全部可取字段 读取时间较长 请耐心等待
    report_type 可选 'report_time' 按截止日期 'announce_time' 按公告日期 进行筛选
    如无特殊说明均为万位
"""
# fd = tq.get_financial_data(
#         stock_list=codes,
#         table_list=['Capital'],
#         start_time='20250101',
#         end_time='',
#         report_type='announce_time')
# print(fd)

"""
    下载10大股东数据或ETF申赎数据
    下载的文件保存在 .\\PYPlugins\\data 文件夹
    down_type=1时，下载10大股东数据，down_time只生效年份
    down_type=2时，下载ETF申赎清单，down_time生效到日期
"""
down_ptr_10 = tq.download_file(stock_code="688318.SH", down_time="20250101", down_type=1)
print(down_ptr_10)
# dowm_ptr_etf = tq.download_file(stock_code='159109.SH', down_time='20250101',down_type=2)
# print(dowm_ptr_etf)

"""
    获取交易日列表 需要现在客户端下载上证指数（999999）的盘后数据 目前仅支持A股
    count参数表示获取的交易日数量
"""
# trade_dates = tq.get_trading_dates(market = 'SH', start_time = '20220101', end_time = '', count = 10);
# print(trade_dates)

"""
    获取股票代码
    默认为全部A股
    0:自选股 1:持仓股
    5:所有A股 6:上证指数成份股 7:上证主板 8:深证主板 9:重点指数
    10:所有板块指数 11:缺省行业板块 12:概念板块 13:风格板块 14:地区板块 15:缺省行业分类+概念板块 16:研究行业一级 17:研究行业二级 18:研究行业三级
    21:含H股 22:含可转债 23:沪深300 24:中证500 25:中证1000 26:国证2000 27:中证2000 28:中证A500
    30:REITs 31:ETF基金 32:可转债 33:LOF基金 34:所有可交易基金 35:所有沪深基金 36:T+0基金
    49:金融类企业 50:沪深A股 51:创业板 52:科创板 53:北交所
    101:国内期货 102:港股 103:美股
"""
stock_list = tq.get_stock_list("0")
print(stock_list)
# print(len(stock_list))

"""
    获取A股全部板块指数
"""
# block_list = tq.get_sector_list()
# print(block_list)
# print(len(block_list))

"""
    获取板块成分股
    支持板块名称或板块代码两种方式传入
    block_type=0 表示传入板块代码或名称（默认）
    block_type=1 表示传入自定义板块简称 需要是客户端中预先定义好板块简称 不能是 自选股 或 临时条件股
"""
# block_stocks = tq.get_stock_list_in_sector('880081.SH')
# print(block_stocks)
# print(len(block_stocks))

# block_stocks = tq.get_stock_list_in_sector('钛金属')
# print(block_stocks)
# print(len(block_stocks))

# block_stocks = tq.get_stock_list_in_sector('CSBK', block_type = 1)
# print(block_stocks)
# print(len(block_stocks))

"""
    发送消息给通达信客户端的TQ策略界面
    消息使用 | 分行
"""
# msg_str = "这是第一行. | 这是第二行. "
# tq.send_message(msg_str)

"""
    创建自定义板块
    block_code为板块简称 block_name为板块名称
"""
block_name = "JOHN测试板块"
create_ptr = tq.create_sector(block_code="CSBK", block_name=block_name)
print(create_ptr)

"""
    删除自定义板块
"""
# delete_ptr = tq.delete_sector(block_code='CSBK', block_name='测试板块')
# print(delete_ptr)

"""
    重命名自定义板块
    重命名自定义板块仅能重命名板块名而不能改板块简称
"""
# rename_ptr = tq.rename_sector(block_code='CSBK', block_name='测试板块重命名')
# print(rename_ptr)

"""
    清空板块成份股
"""
# clear_ptr = tq.clear_sector(block_code='CSBK', block_name='测试板块重命名')
# print(clear_ptr)

"""
    添加自选股 到 通达信客户端的临时条件股列表 注意 会顶掉原有的临时条件股
    bk_name 客户端已有的自定义板块名，如果不存在则无效果，空则为添加到临时条件股
    bk_name存在，传入空列表则表示清空该板块所有股票，否则为新股票替换原有股票
"""
zxg_result = tq.send_user_block(
    bk_name=block_name, stocks=["600011.SH", "600000.SH", "600004.SH", "000001.SZ", "000002.SZ"]
)
# zxg_result = tq.send_user_block(bk_name='CSBK', stocks=[])
# zxg_result = tq.send_user_block(bk_name='', stocks=[])

"""
    发送文件路径给通达信客户端的TQ策略界面 可供客户端打开
    file_path 文件绝对路径字符串
"""
# file_path = "F:\\tdx\\new_tdx_600\\PYPlugins\\user\\test.py"
# tq.send_file(file_path)

"""
    发送预警信号给通达信客户端的TQ策略界面
    price_list close_list volum_list bs_flag_list warn_type_list 均要求为纯数字字符串List
    bs_flag_list 0买1卖2未知
    reason_list每个元素有效长度为25个汉字（50个英文）
"""
# warn_res = tq.send_warn(stock_list = codes,
#              time_list = ['20251215141115'],
#              price_list= ['123.45'],
#              close_list= ['122.50'],
#              volum_list= ['1000'],
#              bs_flag_list= ['0'],
#              warn_type_list= ['0'],
#              reason_list= ['价格突破预警线'],
#              count=1)
# print(warn_res)

"""
    发送回测结果给通达信客户端的TQ策略界面
    data_list为二维List，每个子元素对应time_list的一个元素时间点，且每个孙元素最多有16个有效纯数字字符串
"""
bt_data = tq.send_bt_data(
    stock_code=codes[0],
    time_list=["20251215141115", "20251216141115"],
    data_list=[["1", "2", "3"], ["11", "12", "13"]],
    count=2,
)
print(bt_data)

"""
    订阅股票更新 传入回调函数，订阅的股票有更新时，系统会调用回调函数，本例中回调函数功能为订阅股票有更新后获取最新的report数据
    一共最多定订阅100条
    回调定义形式为on_data(datas) 格式为 {"Code":"XXXXXX.XX","ErrorId":"0"}
"""
# def my_callback_func(data_str):
#     print("Callback received data:", data_str)
#     code_json = json.loads(data_str)
#     print(f"codes = {code_json.get('Code')}")
#     report_ptr = tq.get_report_data(code_json.get('Code'))
#     print(report_ptr)
#     return None

# sub_hq = tq.subscribe_hq(stock_list=['600519.SH'], callback=my_callback_func)
# print(sub_hq)

"""
    取消股票订阅更新
"""
# un_sub_ptr = tq.unsubscribe_hq(stock_list=['600519.SH'])
# print(un_sub_ptr)

"""
    获取当前订阅更新的股票列表
"""
# sub_list = tq.get_subscribe_hq_stock_list()
# print(sub_list)

"""
    断开连接 必须调用 在策略退出前或错误处理中调用 比如取到数据为空 中途退出策略 调用close 这样才能配合TQ策略管理器关闭策略
    未能正常close会导致策略管理器中该策略运行状态始终处于运行状态，无法二次启动
    如果遇到这种情况，在策略管理器中删除该策略即可

    断开连接示例：
    while True:
    df = tq.get_market_data(
        stock_list=['600519.SH'],
        start_time='',
        end_time='',
        count=1,
        period='1d',
    )
    if not df:
        tq.close()
        raise ValueError("未获得数据")
    else:
        print(df)
    策略管理器断开连接后，客户端将不会再返回数据，调用接口后判断数据是否为空，空则退出策略
    部分接口有自动错误抛出处理，即遇到未返回数据时会自己调用close，再提醒出现错误
    注意,close并不会直接停止程序，只会断开与客户端直接的通讯连接，程序依然会执行后续代码
"""
tq.close()
