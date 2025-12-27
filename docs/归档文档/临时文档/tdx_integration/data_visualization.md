# 数据呈现功能说明

## 功能概述

本项目的数据呈现功能主要包括策略信号的可视化展示和回测结果的图形化呈现。通过图表和图形界面，用户可以直观地查看策略的买卖点、股票走势以及回测收益情况。

## 核心组件

### 1. plot.py - 策略信号可视化模块

#### 功能说明
- 绘制股票K线图
- 在K线图上标记策略买卖点
- 显示策略持仓区域（盈利为红色，亏损为绿色）
- 绘制趋势线辅助分析

#### 使用方法
```bash
# 绘制默认股票300496的K线图
python plot.py

# 绘制指定股票的K线图
python plot.py 000001
```

#### 核心代码示例
```python
# 生成买点卖点区域标示坐标点
def markareadata(df_stock):
    # 生成买点卖点区域标示坐标点
    df_celue = df_stock.loc[df_stock['celue_buy'] | df_stock['celue_sell']]  # 提取买卖点列
    yAxis_max = df_stock['high'].max()
    markareadata = []
    temp = []
    # k是range索引，对应图形第几个点,v是K行的内容，字典类型
    for k, v in df_celue.iterrows():
        temp.append(
            {
                "xAxis": k,
                # "yAxis": yAxis_max if v['celue_sell'] else 0,  # buy点是0，sell点是最大值 填了y坐标会导致图形放大后区域消失
            }
        )
        # 如果temp列表数量到达2，表示起点xy坐标、终点xy坐标生成完毕。添加到markareadata，清空temp重新开始
        if len(temp) == 2:
            # 给第2组xy坐标字典添加'itemStyle': {'color': '#14b143'}键值对。
            # df_celue.at[temp[1]['xAxis'], 'close']为读取对应索引的收盘价。
            # 第二组坐标收盘价和第一组坐标收盘价比较，大于则区域颜色是红色表示盈利，小于则绿色亏损
            temp[1]["itemStyle"] = {'color': "#ef232a" if df_celue.at[temp[1]['xAxis'], 'close'] > df_celue.at[
                temp[0]['xAxis'], 'close'] else "#14b143"}
            markareadata.append(temp)
            # rprint(markareadata)
            temp = []
    return markareadata

# 使用PyECharts绘制K线图
def draw_kline(stock_code, df_stock):
    kline = Kline(init_opts=opts.InitOpts(width="100%", height="600px", theme=ThemeType.ESSOS, page_title=stock_code, ))

    # 做横轴的处理
    datetime = df_stock['date'].astype(str).tolist()
    oclh = []
    for i in range(df_stock.shape[0]):
        oclh.append(df_stock.loc[i, ['open', 'close', 'low', 'high']].to_list())

    vol = df_stock['vol'].tolist()

    kline.add_xaxis(datetime)
    kline.add_yaxis(stock_code, oclh, itemstyle_opts=opts.ItemStyleOpts(
        color="#ef232a",
        color0="#14b143",
        border_color="#ef232a",
        border_color0="#14b143", ),
                    markline_opts=opts.MarkLineOpts(
                        label_opts=opts.LabelOpts(
                            position="middle", color="blue", font_size=15
                        ),
                        data=marklinedata(df_stock.copy()),
                        symbol=["none", "none"],
                        linestyle_opts=opts.LineStyleOpts(
                            width=2,
                            type_="solid",
                        ),
                    ),
                    )
    kline.set_series_opts(
        markarea_opts=opts.MarkAreaOpts(is_silent=True, data=markareadata(df_stock),
                                        itemstyle_opts=opts.ItemStyleOpts(opacity=0.5,
                                                                          )
                                        )
    )
    kline.set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
        datazoom_opts=[
            opts.DataZoomOpts(type_="inside", range_start=-100),
            opts.DataZoomOpts(pos_bottom="0%"),
        ],
    )

    grid_chart = Grid(init_opts=opts.InitOpts(width="100%", height="950px",
                                              theme=ThemeType.ESSOS,
                                              page_title=stock_code, ))
    grid_chart.add_js_funcs("var areaData={}".format(markareadata(df_stock)))
    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(
            pos_left="3%", pos_right="1%", height="85%"
        ),
    )
    grid_chart.render('plot.html')
    print(f'{stock_code} 绘图完成，打开plot.html文件查看结果，程序结束')
```

### 2. huice.py - 回测结果可视化模块

#### 功能说明
- 基于RQAlpha框架生成回测结果
- 输出收益曲线图
- 提供详细的投资回报率、最大回撤等统计数据

#### 核心代码示例
```python
# RQAlpha配置
__config__ = {
    "base": {
        # 回测起始日期
        "start_date": start_date,
        "end_date": end_date,
        # 数据源所存储的文件路径
        "data_bundle_path": "C:/Users/king/.rqalpha/bundle/",
        "strategy_file": "huice.py",
        # 目前支持 `1d` (日线回测) 和 `1m` (分钟线回测)
        "frequency": "1d",
        # 启用的回测引擎
        "matching_type": "current_bar",
        # 运行类型，`b` 为回测
        "run_type": "b",
        # 设置策略可交易品种
        "accounts": {
            "stock": stock_money,
        },
        # 设置初始仓位
        "init_positions": {}
    },
    "extra": {
        # 日志输出等级
        "log_level": "info",
    },
    "mod": {
        "sys_analyser": {
            "enabled": True,
            "benchmark": "000300.XSHG",
            # 保存收益曲线图
            'plot_save_file': rq_result_filename + ".png",
            # 保存回测结果
            "output_file": rq_result_filename + ".pkl",
        },
        # 策略运行过程中显示的进度条的控制
        "sys_progress": {
            "enabled": False,
            "show": True,
        },
    },
}

# 回测结果展示
def show_backtest_result(result_dict):
    rprint(result_dict["summary"])
    rprint(
        f"回测起点 {result_dict['summary']['start_date']}"
        f"\n回测终点 {result_dict['summary']['end_date']}"
        f"\n回测收益 {result_dict['summary']['total_returns']:>.2%}\t年化收益 {result_dict['summary']['annualized_returns']:>.2%}"
        f"\t基准收益 {result_dict['summary']['benchmark_total_returns']:>.2%}\t基准年化 {result_dict['summary']['benchmark_annualized_returns']:>.2%}"
        f"\t最大回撤 {result_dict['summary']['max_drawdown']:>.2%}"
        f"\n打开程序文件夹下的rq_result.png查看收益走势图")
```

## 可视化流程

1. **策略信号可视化**：
   - 运行plot.py生成指定股票的K线图
   - 图表中标记策略买卖点
   - 显示策略持仓区域和趋势线
   - 生成plot.html文件供查看

2. **回测结果可视化**：
   - 运行huice.py执行回测
   - 自动生成收益曲线图(rq_result.png)
   - 生成详细回测报告(rq_result.pkl)
   - 控制台输出关键指标

## 图表说明

### K线图元素
- **K线**：显示股票的开盘价、收盘价、最高价、最低价
- **颜色编码**：
  - 红色K线：收盘价高于开盘价（上涨）
  - 绿色K线：收盘价低于开盘价（下跌）
- **买卖点标记**：
  - 策略买入点：在K线下方标记
  - 策略卖出点：在K线上方标记
- **持仓区域**：
  - 红色区域：盈利持仓
  - 绿色区域：亏损持仓
- **趋势线**：
  - 红色线：上涨趋势线
  - 绿色线：下跌趋势线

### 回测结果图
- **收益曲线**：显示策略收益随时间的变化
- **基准曲线**：沪深300指数作为基准对比
- **关键指标**：
  - 总收益率
  - 年化收益率
  - 最大回撤
  - 基准收益对比

## 使用示例

### 查看策略信号
```bash
# 查看默认股票的策略信号
python plot.py

# 查看指定股票的策略信号
python plot.py 000001
```

执行后会生成plot.html文件，用浏览器打开即可查看K线图和策略信号。

### 查看回测结果
```bash
# 执行回测
python huice.py
```

执行后会生成以下文件：
- rq_result.png：收益曲线图
- rq_result.pkl：详细回测报告
- 控制台输出关键指标

## 注意事项

1. 需要安装PyECharts库支持K线图绘制
2. 需要安装RQAlpha框架支持回测可视化
3. 策略信号文件(celue汇总.csv)是可视化的重要输入
4. 生成的HTML文件可在浏览器中查看，支持交互操作
5. 回测需要相应的数据源支持
