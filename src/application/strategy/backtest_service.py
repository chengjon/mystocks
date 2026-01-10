"""
Backtest Application Service
回测应用服务
"""
from typing import List
from src.domain.strategy.repository import IStrategyRepository
from src.domain.market_data.repository import IMarketDataRepository
from src.domain.strategy.service import SignalGenerationService
from src.application.dto.strategy_dto import BacktestRequest, BacktestResultDTO

class BacktestApplicationService:
    def __init__(self, 
                 strategy_repo: IStrategyRepository,
                 market_data_repo: IMarketDataRepository,
                 signal_service: SignalGenerationService):
        self.strategy_repo = strategy_repo
        self.market_data_repo = market_data_repo
        self.signal_service = signal_service

    def run_backtest(self, request: BacktestRequest) -> BacktestResultDTO:
        """
        用例：执行回测
        """
        # 1. 获取策略
        strategy = self.strategy_repo.get_by_id(request.strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")
            
        strategy.activate()
        
        total_signals = 0
        
        # 2. 遍历标地进行回测
        for symbol in request.symbols:
            # 获取历史数据 (调用 ACL)
            bars = self.market_data_repo.get_history_kline(
                symbol, request.start_date, request.end_date
            )
            
            # 简化：将 Bars 转换为策略执行所需的格式并逐个处理
            # 实际生产中应使用向量化计算优化
            for bar in bars:
                # 构造市场数据快照
                market_snapshot = {
                    'symbol': symbol,
                    'price': bar.close,
                    'indicators': {} # 此处应包含预计算指标
                }
                
                signals = strategy.execute(market_snapshot)
                total_signals += len(signals)
                
        # 3. 计算绩效 (此处简化逻辑)
        return BacktestResultDTO(
            total_returns=0.15, # Mock
            sharpe_ratio=1.2,   # Mock
            max_drawdown=0.05,  # Mock
            signal_count=total_signals,
            trade_count=total_signals # 假设全成交
        )