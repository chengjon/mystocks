# 数据分析功能说明

## 功能概述

本项目的数据分析功能主要包括选股策略执行和回测分析两大部分。通过自定义策略函数，系统能够对处理后的股票数据进行分析，识别符合特定条件的股票，并对策略的历史表现进行回测验证。

## 核心组件

### 1. xuangu.py - 选股执行模块

#### 功能说明
- 执行用户定义的选股策略
- 支持盘中选股和盘后选股
- 多进程并行处理提高执行效率
- 剔除ST股、特定行业股票和科创板股票

#### 使用方法
```bash
# 正常执行选股
python xuangu.py

# 使用单进程执行
python xuangu.py single
```

#### 核心代码示例
```python
# 股票列表筛选函数
def make_stocklist():
    # 要进行策略的股票列表筛选
    stocklist = [i[:-4] for i in os.listdir(ucfg.tdx['csv_lday'])]  # 去文件名里的.csv，生成纯股票代码list
    print(f'生成股票列表, 共 {len(stocklist)} 只股票')
    print(f'剔除通达信概念股票: {要剔除的通达信概念}')
    tmplist = []
    df = func.get_TDX_blockfilecontent("block_gn.dat")
    # 获取df中blockname列的值是ST板块的行，对应code列的值，转换为list。用filter函数与stocklist过滤，得出不包括ST股票的对象，最后转为list
    for i in 要剔除的通达信概念:
        tmplist = tmplist + df.loc[df['blockname'] == i]['code'].tolist()
    stocklist = list(filter(lambda i: i not in tmplist, stocklist))
    print(f'剔除通达信行业股票: {要剔除的通达信行业}')
    tmplist = []
    df = pd.read_csv(ucfg.tdx['tdx_path'] + os.sep + 'T0002' + os.sep + 'hq_cache' + os.sep + "tdxhy.cfg",
                     sep='|', header=None, dtype='object')
    for i in 要剔除的通达信行业:
        tmplist = tmplist + df.loc[df[2] == i][1].tolist()
    stocklist = list(filter(lambda i: i not in tmplist, stocklist))
    print("剔除科创板股票")
    tmplist = []
    for stockcode in stocklist:
        if stockcode[:2] != '68':
            tmplist.append(stockcode)
    stocklist = tmplist
    return stocklist

# 策略执行函数
def run_celue1(stocklist, df_today, tqdm_position=None):
    if 'single' in sys.argv[1:]:
        tq = tqdm(stocklist[:])
    else:
        tq = tqdm(stocklist[:], leave=False, position=tqdm_position)
    for stockcode in tq:
        tq.set_description(stockcode)
        pklfile = csvdaypath + os.sep + stockcode + '.pkl'
        df_stock = pd.read_pickle(pklfile)
        if df_today is not None:  # 更新当前最新行情，否则用昨天的数据
            df_stock = func.update_stockquote(stockcode, df_stock, df_today)
        df_stock['date'] = pd.to_datetime(df_stock['date'], format='%Y-%m-%d')  # 转为时间格式
        df_stock.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并
        celue1 = CeLue.策略1(df_stock, start_date=start_date, end_date=end_date, mode='fast')
        if not celue1:
            stocklist.remove(stockcode)
    return stocklist
```

### 2. celue_save.py - 策略信号保存模块

#### 功能说明
- 为历史数据添加策略买卖信号
- 生成策略信号汇总文件用于回测
- 支持增量更新和全量重新生成

#### 使用方法
```bash
# 正常执行，只更新缺少策略信号的交易日
python celue_save.py

# 完全重新生成策略信号
python celue_save.py del

# 使用单进程执行
python celue_save.py single
```

#### 核心代码示例
```python
# 策略信号保存函数
def celue_save(file_list, HS300_信号, tqdm_position=None):
    def lambda_update0(x):
        if type(x) == float:
            x = np.nan
        elif x == '0.0':
            x = np.nan
        return x

    starttime_tick = time.time()
    df_celue = pd.DataFrame()
    if 'single' in sys.argv[1:]:
        tq = tqdm(file_list)
    else:
        tq = tqdm(file_list, leave=False, position=tqdm_position)
    for stockcode in tq:
        tq.set_description(stockcode)
        pklfile = ucfg.tdx['pickle'] + os.sep + stockcode + ".pkl"
        df = pd.read_pickle(pklfile)
        if 'del' in sys.argv[1:]:
            if 'celue_buy' in df.columns:
                del df['celue_buy']
            if 'celue_sell' in df.columns:
                del df['celue_sell']
        df.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并
        if not {'celue_buy', 'celue_buy'}.issubset(df.columns):
            df.insert(df.shape[1], 'celue_buy', np.nan)  # 插入celue_buy列，赋值NaN
            df.insert(df.shape[1], 'celue_sell', np.nan)  # 插入celue_sell列，赋值NaN
        else:
            # 由于make_fq时fillna将最新的空的celue单元格也填充为0，所以先恢复nan
            df['celue_buy'] = (df['celue_buy']
                               .apply(lambda x: lambda_update0(x))
                               .mask(df['celue_buy'] == 'False', False)
                               .mask(df['celue_buy'] == 'True', True)
                               )

            df['celue_sell'] = (df['celue_sell']
                                .apply(lambda x: lambda_update0(x))
                                .mask(df['celue_sell'] == 'False', False)
                                .mask(df['celue_sell'] == 'True', True)
                                )

        if True in df['celue_buy'].isna().to_list():
            start_date = df.index[np.where(df['celue_buy'].isna())[0][0]]
            end_date = df.index[-1]
            celue2 = CeLue.策略2(df, HS300_信号, start_date=start_date, end_date=end_date)
            celue_sell = CeLue.卖策略(df, celue2, start_date=start_date, end_date=end_date)
            df.loc[start_date:end_date, 'celue_buy'] = celue2
            df.loc[start_date:end_date, 'celue_sell'] = celue_sell
            df.reset_index(drop=True, inplace=True)
            df.to_csv(ucfg.tdx['csv_lday'] + os.sep + stockcode + '.csv', index=False, encoding='gbk')
            df.to_pickle(ucfg.tdx['pickle'] + os.sep + stockcode + ".pkl")
        lefttime_tick = int((time.time() - starttime_tick) / (file_list.index(stockcode) + 1)
                            * (len(file_list) - (file_list.index(stockcode) + 1)))

        # 提取celue是true的列，单独保存到一个df，返回这个df
        df_celue = df_celue.append(df.loc[df['celue_buy'] | df['celue_sell']])
    df_celue['date'] = pd.to_datetime(df_celue['date'], format='%Y-%m-%d')  # 转为时间格式
    df_celue.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并

    return df_celue
```

### 3. huice.py - 回测分析模块

#### 功能说明
- 基于RQAlpha框架进行策略回测
- 导入策略信号文件进行历史回测
- 生成详细的回测报告和收益曲线

#### 使用方法
```bash
# 执行回测
python huice.py
```

#### 核心代码示例
```python
# 初始化函数
def init(context):
    # 在context中保存全局变量
    context.percent = xiadan_percent  # 设定买入比例
    context.target_value = xiadan_target_value  # 设定具体股票总买入市值
    context.order_type = order_type  # 下单模式

    df_celue = pd.read_csv(ucfg.tdx['csv_gbbq'] + os.sep + 'celue汇总.csv',
                           index_col=0, encoding='gbk', dtype={'code': str})
    df_celue['code'] = df_celue['code'].apply(lambda x: update_stockcode(x))  # 升级股票代码，匹配rqalpha
    df_celue['date'] = pd.to_datetime(df_celue['date'], format='%Y-%m-%d')  # 转为时间格式
    df_celue.set_index('date', drop=False, inplace=True)  # 时间为索引
    context.df_celue = df_celue

# 交易处理函数
def handle_bar(context, bar_dict):
    if context.df_today is not None:
        for index, row in context.df_today.iterrows():
            # 检测是否停牌，停牌则交易单复制到下一个交易日
            if is_suspended(row['code']):
                # 处理停牌股票
                continue

            # 获取当前投资组合中具体股票的数据
            cur_quantity = get_position(row['code']).quantity  # 该股持仓量
            cur_pnl = get_position(row['code']).pnl  # 该股持仓的累积盈亏

            # 卖出股票
            if row['celue_sell'] and cur_quantity > 0:
                order_result_obj = order_target_value(row['code'], 0)
                # 处理卖出订单

            # 买入股票
            if row['celue_buy'] and cur_quantity == 0:
                if context.order_type == 'order_percent':
                    order_result_obj = order_percent(row['code'], context.percent)
                elif context.order_type == 'order_target_value':
                    order_result_obj = order_target_value(row['code'], context.target_value)
                # 处理买入订单
```

## 策略开发

### 策略模板 (CeLue模板.py)

用户需要根据策略模板编写自己的选股策略，保存为celue.py文件。

```python
def 策略1(df, start_date='', end_date='', mode=None):
    """
    :param DataFrame df:输入具体一个股票的DataFrame数据表。时间列为索引。
    :param mode :str 'fast'为快速模式，只处理当日数据，用于开盘快速筛选股票。和策略2结合使用时不能用fast模式
    :param date start_date:可选。留空从头开始。2020-10-10格式，策略指定从某日期开始
    :param date end_date:可选。留空到末尾。2020-10-10格式，策略指定到某日期结束
    :return : 布尔序列
    """
    # 策略实现逻辑
    # 返回布尔序列，表示是否符合选股条件
    pass

def 策略2(df, HS300_信号, start_date='', end_date=''):
    """
    :param DataFrame df:输入具体一个股票的DataFrame数据表。时间列为索引。
    :param date start_date:可选。留空从头开始。2020-10-10格式，策略指定从某日期开始
    :param date end_date:可选。留空到末尾。2020-10-10格式，策略指定到某日期结束
    :return bool: 截止日期这天，策略是否触发。true触发，false不触发
    """
    # 策略实现逻辑
    # 返回布尔值，表示是否触发买入信号
    pass
```

## 分析流程

1. **数据准备**：确保已完成数据抓取和处理
2. **策略编写**：根据模板编写选股策略
3. **选股执行**：运行xuangu.py执行选股
4. **信号保存**：运行celue_save.py保存历史策略信号
5. **回测分析**：运行huice.py进行策略回测
6. **结果评估**：分析回测报告，优化策略

## 注意事项

1. 策略文件必须保存为celue.py
2. 策略函数需遵循特定的输入输出格式
3. 回测需要安装RQAlpha框架和相应的数据源
4. 策略信号文件celue汇总.csv是回测的关键输入
