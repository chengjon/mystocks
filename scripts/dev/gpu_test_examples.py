
# MyStocks GPU加速测试代码示例
import cudf
import cupy as cp
import cuml
import numpy as np

# 1. 大规模历史数据回测
def backtest_strategies_gpu(stock_data, strategies):
    """GPU加速的策略回测"""
    df_gpu = cudf.DataFrame(stock_data)

    results = []
    for strategy in strategies:
        # GPU并行计算策略信号
        signals = strategy.calculate_signals(df_gpu)

        # GPU计算收益
        returns = df_gpu['close'].pct_change()
        strategy_returns = returns * signals

        # GPU计算性能指标
        sharpe = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)
        max_drawdown = (strategy_returns.cumsum().cummax() - strategy_returns.cumsum()).max()

        results.append({
            'strategy': strategy.name,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        })

    return results

# 2. 实时特征计算
def calculate_features_gpu(real_time_data):
    """GPU加速的实时特征计算"""
    df_gpu = cudf.DataFrame(real_time_data)

    # 技术指标计算 (GPU加速)
    df_gpu['sma_20'] = df_gpu['price'].rolling(20).mean()
    df_gpu['sma_50'] = df_gpu['price'].rolling(50).mean()
    df_gpu['rsi'] = calculate_rsi_gpu(df_gpu['price'])
    df_gpu['macd'], df_gpu['macd_signal'] = calculate_macd_gpu(df_gpu['price'])

    return df_gpu

# 3. 多因子模型
def multi_factor_model_gpu(factors_data):
    """GPU加速的多因子模型"""
    df_gpu = cudf.DataFrame(factors_data)

    # 因子标准化 (GPU)
    for factor in ['pe', 'pb', 'roe', 'momentum']:
        df_gpu[f'{factor}_normalized'] = (df_gpu[factor] - df_gpu[factor].mean()) / df_gpu[factor].std()

    # 因子权重计算 (GPU矩阵运算)
    weights = cp.array([0.25, 0.25, 0.3, 0.2])  # 因子权重
    factor_columns = ['pe_normalized', 'pb_normalized', 'roe_normalized', 'momentum_normalized']

    df_gpu['composite_score'] = (df_gpu[factor_columns] * weights).sum(axis=1)
    df_gpu['rank'] = df_gpu['composite_score'].rank(method='dense', ascending=False)

    return df_gpu

# 4. 风险计算
def risk_calculation_gpu(portfolio_data):
    """GPU加速的风险计算"""
    df_gpu = cudf.DataFrame(portfolio_data)

    # 协方差矩阵 (GPU)
    returns = df_gpu[['stock1_return', 'stock2_return']].pct_change().dropna()
    cov_matrix = returns.cov().to_numpy()  # 转换为CPU用于计算

    # VaR计算
    portfolio_returns = returns.mean(axis=1)
    var_95 = cp.percentile(cp.array(portfolio_returns), 5)

    return {
        'covariance_matrix': cov_matrix,
        'var_95': var_95,
        'volatility': portfolio_returns.std()
    }
