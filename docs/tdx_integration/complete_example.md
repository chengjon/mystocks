# 完整项目使用示例

以下是一个完整的使用示例，展示了如何从数据准备到策略回测的整个流程。

## 1. 环境配置

首先配置user_config.py文件：

```python
# user_config.py
debug = False

tdx = {
    'tdx_path': 'd:/stock/通达信',      # 指定通达信目录
    'csv_lday': 'd:/TDXdata/lday_qfq', # 指定csv格式日线数据保存目录
    'pickle': 'd:/TDXdata/pickle',     # 指定pickle格式日线数据保存目录
    'csv_index': 'd:/TDXdata/index',   # 指定指数保存目录
    'csv_cw': 'd:/TDXdata/cw',         # 指定专业财务保存目录
    'csv_gbbq': 'd:/TDXdata',          # 指定股本变迁保存目录
    'pytdx_ip': '218.6.170.55',        # 指定pytdx的通达信服务器IP
    'pytdx_port': 7709,                # 指定pytdx的通达信服务器端口。int类型
}

index_list = [  # 通达信需要转换的指数文件。通达信按998查看重要指数
    'sh999999.day',  # 上证指数
    'sh000300.day',  # 沪深300
    'sz399001.day',  # 深成指
]
```

## 2. 数据准备

### 下载通达信数据
1. 在通达信软件中下载日线数据：菜单-系统-盘后数据下载
2. 下载专业财务数据：菜单-系统-专业财务数据

### 处理日线数据
```bash
# 首次运行需要删除现有数据并重新生成
python readTDX_lday.py del

# 后续更新只需追加最新数据
python readTDX_lday.py
```

### 处理财务数据
```bash
# 更新财务和股本变迁数据
python readTDX_cw.py
```

## 3. 编写选股策略

创建celue.py文件（基于CeLue模板.py）：

```python
# celue.py
import numpy as np
import talib
import time
import func
from func_TDX import rolling_window, REF, MA, SMA, HHV, LLV, COUNT, EXIST, CROSS, BARSLAST
from rich import print

def 策略HS300(df_hs300, start_date='', end_date=''):
    """
    HS300信号的作用是，当信号是0时，当日不买股票，1时买入。
    """
    if start_date == '':
        start_date = df_hs300.index[0]  # 设置为df第一个日期
    if end_date == '':
        end_date = df_hs300.index[-1]  # 设置为df最后一个日期
    df_hs300 = df_hs300.loc[start_date:end_date]
    HS300_CLOSE = df_hs300['close']
    HS300_当日涨幅 = (HS300_CLOSE / REF(HS300_CLOSE, 1) - 1) * 100
    HS300_信号 = ~(HS300_当日涨幅 < -1.5) & ~(HS300_当日涨幅 > 1.5)
    return HS300_信号

def 策略1(df, start_date='', end_date='', mode=None):
    """
    基础选股策略
    """
    if start_date == '':
        start_date = df.index[0]  # 设置为df第一个日期
    if end_date == '':
        end_date = df.index[-1]  # 设置为df最后一个日期
    df = df.loc[start_date:end_date]

    O = df['open']
    H = df['high']
    L = df['low']
    C = df['close']
    if {'换手率'}.issubset(df.columns):  # 无换手率列的股票，只可能是近几个月的新股。
        换手率 = df['换手率']
    else:
        换手率 = 0

    if mode == 'fast':
        # 快速模式，只处理当日数据
        if C.shape[0] < 500 or C.iat[-1] < 9:
            return False

        金额万均 = MA(df['amount'] / 10000, 30)
        流通市值亿 = df['流通市值'] / 100000000
        MA5 = MA(C, 5)

        # TJ04 {排除当日涨停的股票}
        if df['code'][0][0:2] == "68" or df['code'][0][0:2] == "30":
            TJ04_1 = 1.2
        else:
            TJ04_1 = 1.1
        TJ04_2 = ~((C+0.01) >= np.ceil((np.floor(REF(C, 1)*1000*TJ04_1)-4)/10)/100)
        TJ04 = TJ04_2.iat[-1]

        result = TJ04
    else:
        金额万均 = SMA(df['amount'] / 10000, 30)
        流通市值亿 = df['流通市值'] / 100000000
        MA5 = SMA(C, 5)

        # TJ01
        TJ01 = (BARSLAST(C == 0) > 500) & (df['close'] > 9)

        # TJ04
        if df['code'][0][0:2] == "68" or df['code'][0][0:2] == "30":
            TJ04_1 = 1.2
        else:
            TJ04_1 = 1.1
        TJ04_2 = ~((C+0.01) >= np.ceil((np.floor(REF(C, 1)*1000*TJ04_1)-4)/10)/100)
        TJ04 = TJ04_2

        result = TJ01 & TJ04
    return result

def 策略2(df, HS300_信号, start_date='', end_date=''):
    """
    进阶选股策略
    """
    if start_date == '':
        start_date = df.index[0]  # 设置为df第一个日期
    if end_date == '':
        end_date = df.index[-1]  # 设置为df最后一个日期
    df = df.loc[start_date:end_date]

    if df.shape[0] < 251:  # 小于250日 直接返回flase序列
        return pd.Series(index=df.index, dtype=bool)

    # 根据df的索引重建HS300信号，为了与股票交易日期一致
    HS300_信号 = pd.Series(HS300_信号, index=df.index, dtype=bool).dropna()

    O = df['open']
    H = df['high']
    L = df['low']
    C = df['close']
    换手率 = df['换手率']

    # 变量定义
    MA5 = SMA(C, 5)
    MA10 = SMA(C, 10)
    MA20 = SMA(C, 20)
    MA60 = SMA(C, 60)
    MA120 = SMA(C, 120)
    MA250 = SMA(C, 250)

    流通市值亿 = df['流通市值'] / 100000000

    # 判断部分
    # TJ01
    TJ01 = (MA120 > -5) & (MA10 < 60) & (MA60 < 10) & (-7 < MA250) & (MA250 < 10)

    # TJ02
    TJ02 = (C > SMA(C, 60)) & (C < SMA(C, 60) * 1.1) & (C > O)

    # TJ06
    TJ06_1 = LLV(C, 200)
    TJ06_2 = LLV(C, 20)
    TJ06_MA60_DAY = BARSLAST((REF(C, 5) < MA60) & CROSS(C, MA60))
    TJ06_MA60 = pd.Series(index=TJ06_MA60_DAY.index, dtype=float)

    i = 0
    for k, v in TJ06_MA60_DAY.iteritems():
        if i - v > 0:
            TJ06_MA60.iat[i] = MA60.iat[i - v]
        i = i + 1

    df = pd.concat([df, TJ06_MA60_DAY.rename('TJ06_MA60_DAY')], axis=1)
    df.insert(df.shape[1], 'TJ06_MA60_LLV', np.NaN)
    for index_date in df.loc[df['TJ06_MA60_DAY'] == 0].index.to_list():
        index_int = df.index.get_loc(index_date)
        df.at[index_date, 'TJ06_MA60_LLV'] = df.iloc[index_int - 20:index_int]['close'].min()
    df = df.fillna(method='ffill')
    TJ06_MA60_LLV = df['TJ06_MA60_LLV']

    TJ06_3 = TJ06_MA60 / TJ06_MA60_LLV
    TJ06_4 = C / TJ06_MA60
    TJ06 = (TJ06_2 / TJ06_1 - 1 < 0.5) & (1 < TJ06_3 / TJ06_4) & (TJ06_3 / TJ06_4 < 1.5)

    # TJ11
    TJP1 = 策略1(df, start_date, end_date)
    TJ11_1 = HS300_信号 & TJP1 & TJ01 & TJ02 & TJ06
    TJ11_2 = COUNT(TJ11_1, 10)
    TJ11 = TJ11_1 & (REF(TJ11_2, 1) == 0)

    # TJ99
    TJ99 = TJ11

    # {输出部分}
    BUYSIGN = TJ99

    return BUYSIGN
```

## 4. 执行选股

```bash
# 执行选股（默认多进程）
python xuangu.py

# 单进程执行选股
python xuangu.py single
```

## 5. 保存策略信号

```bash
# 保存策略信号（只更新缺少策略信号的交易日）
python celue_save.py

# 完全重新生成策略信号
python celue_save.py del

# 单进程执行
python celue_save.py single
```

## 6. 策略可视化

```bash
# 查看默认股票的策略信号
python plot.py

# 查看指定股票的策略信号
python plot.py 000001
```

## 7. 策略回测

```bash
# 执行回测
python huice.py
```

## 8. 查看回测结果

回测执行完成后，会生成以下文件：
- rq_result.png：收益曲线图
- rq_result.pkl：详细回测报告

控制台会输出关键指标：
```
回测起点 2013-01-01
回测终点 2022-12-31
回测收益 156.28%    年化收益 9.98%    基准收益 45.89%    基准年化 3.90%    最大回撤 22.35%
打开程序文件夹下的rq_result.png查看收益走势图
```

## 9. 自动化流程脚本

可以创建一个批处理脚本来自动化整个流程：

```bash
#!/bin/bash
# daily_analysis.sh

echo "开始每日数据分析流程..."

# 更新数据
echo "1. 更新日线数据..."
python readTDX_lday.py

echo "2. 更新财务数据..."
python readTDX_cw.py

echo "3. 执行选股..."
python xuangu.py

echo "4. 保存策略信号..."
python celue_save.py

echo "5. 执行回测..."
python huice.py

echo "数据分析流程完成！"
```

## 10. 关键配置说明

### 多进程配置
项目中的多进程处理会根据CPU核心数自动调整进程数：
```python
# 进程数 读取CPU逻辑处理器个数
if os.cpu_count() > 8:
    t_num = int(os.cpu_count() / 1.5)
else:
    t_num = os.cpu_count() - 2
```

### 数据存储优化
项目使用pickle格式存储数据以提高读取速度：
```python
# 保存为pickle格式
df_qfq.to_pickle(ucfg.tdx['pickle'] + os.sep + filename[:-4] + '.pkl')

# 读取pickle格式
df_stock = pd.read_pickle(pklfile)
```

通过以上完整的示例，用户可以了解如何使用本项目进行股票数据分析、策略开发、选股执行和回测验证的全流程。