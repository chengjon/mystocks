"""
投资组合追踪模块

提供投资组合创建、更新、查询、删除、性能追踪、统计分析等功能
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class PortfolioStatus(Enum):
    """投资组合状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class PerformanceMetric(Enum):
    """性能指标类型"""
    TOTAL_RETURN = "total_return"
    ANNUALIZED_RETURN = "annualized_return"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    VOLATILITY = "volatility"
    ALPHA = "alpha"
    BETA = "beta"
    INFORMATION_RATIO = "information_ratio"


@dataclass
class PortfolioInfo:
    """投资组合信息数据类"""
    portfolio_id: str = ""
    name: str = ""
    user_id: str = ""
    status: PortfolioStatus = PortfolioStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    initial_capital: float = 0.0
    current_capital: float = 0.0
    number_of_positions: int = 0
    total_assets: float = 0.0
    risk_profile_id: Optional[str] = None
    description: str = ""
    tags: List[str] = None
    is_favorite: bool = False
    is_public: bool = False

    def to_dict(self) -> Dict:
        return {
            'portfolio_id': self.portfolio_id,
            'name': self.name,
            'user_id': self.user_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'number_of_positions': self.number_of_positions,
            'total_assets': self.total_assets,
            'risk_profile_id': self.risk_profile_id,
            'description': self.description,
            'tags': self.tags,
            'is_favorite': self.is_favorite,
            'is_public': self.is_public
        }


@dataclass
class PerformanceMetricsData:
    """性能指标数据类"""
    portfolio_id: str = ""
    metric_type: PerformanceMetric = PerformanceMetric.TOTAL_RETURN
    period: str = "daily"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    value: float = 0.0
    benchmark: Optional[float] = None
    rank: Optional[int] = None
    percentile: Optional[float] = None
    calculated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            'portfolio_id': self.portfolio_id,
            'metric_type': self.metric_type.value,
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'value': f"{self.value:.2f}%",
            'benchmark': f"{self.benchmark:.2f}%" if self.benchmark else None,
            'rank': self.rank if self.rank else None,
            'percentile': f"{self.percentile:.2f}%" if self.percentile else None,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


class PortfolioTracker:
    """投资组合追踪器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.portfolios = {}  # portfolio_id -> PortfolioInfo
        self.performance_metrics = {}  # portfolio_id -> List[PerformanceMetricsData]
        self.benchmark_metrics = {
            'avg_return': 0.08,
            'avg_sharpe': 1.2,
            'avg_max_drawdown': 0.15
        }

        logger.info("投资组合追踪模块初始化")

    async def create_portfolio(self, user_id: str, name: str, initial_capital: float = 100000.0, risk_profile_id: Optional[str] = None, description: str = "", tags: List[str] = None) -> str:
        """
        创建投资组合
        
        Args:
            user_id: 用户ID
            name: 投资组合名称
            initial_capital: 初始资金
            risk_profile_id: 风险配置文件ID
            description: 描述
            tags: 标签列表
        
        Returns:
            str: 投资组合ID，失败返回空字符串
        """
        try:
            import uuid
            portfolio_id = f"portfolio_{uuid.uuid4()}"

            portfolio_info = PortfolioInfo(
                portfolio_id=portfolio_id,
                user_id=user_id,
                name=name,
                status=PortfolioStatus.DRAFT,
                created_at=datetime.now(),
                initial_capital=initial_capital,
                current_capital=initial_capital,
                number_of_positions=0,
                total_assets=initial_capital,
                risk_profile_id=risk_profile_id,
                description=description,
                tags=tags,
                is_favorite=False,
                is_public=False
            )

            self.portfolios[portfolio_id] = portfolio_info

            self.logger.info(f"创建投资组合: {name} (ID: {portfolio_id})")
            return portfolio_id

        except Exception as e:
            self.logger.error(f"创建投资组合失败: {e}")
            raise

    async def update_portfolio(self, portfolio_id: str, name: Optional[str] = None, status: Optional[PortfolioStatus] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """
        更新投资组合
        
        Args:
            portfolio_id: 投资组合ID
            name: 名称
            status: 状态
            description: 描述
            tags: 标签列表
        
        Returns:
            bool: 是否更新成功
        """
        try:
            if portfolio_id not in self.portfolios:
                self.logger.warning(f"投资组合不存在: {portfolio_id}")
                return False

            portfolio_info = self.portfolios[portfolio_id]

            if name:
                portfolio_info.name = name

            if status:
                portfolio_info.status = status
                portfolio_info.updated_at = datetime.now()

            if description:
                portfolio_info.description = description

            if tags:
                portfolio_info.tags = tags

            self.logger.info(f"更新投资组合: {portfolio_id} (名称: {name})")
            return True

        except Exception as e:
            self.logger.error(f"更新投资组合失败: {e}")
            return False

    async def delete_portfolio(self, portfolio_id: str) -> bool:
        """
        删除投资组合
        
        Args:
            portfolio_id: 投资组合ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            if portfolio_id not in self.portfolios:
                self.logger.warning(f"投资组合不存在: {portfolio_id}")
                return False

            # 从性能指标中删除该组合
            if portfolio_id in self.performance_metrics:
                del self.performance_metrics[portfolio_id]

            del self.portfolios[portfolio_id]

            self.logger.info(f"删除投资组合: {portfolio_id}")
            return True

        except Exception as e:
            self.logger.error(f"删除投资组合失败: {e}")
            return False

    async def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """
        获取投资组合信息
        
        Args:
            portfolio_id: 投资组合ID
        
        Returns:
            Dict: 投资组合信息，失败返回None
        """
        try:
            if portfolio_id not in self.portfolios:
                self.logger.warning(f"投资组合不存在: {portfolio_id}")
                return None

            portfolio_info = self.portfolios[portfolio_id]

            # 获取性能指标
            metrics = self.performance_metrics.get(portfolio_id, [])

            # 计算当前资产
            if metrics:
                total_return = sum(m.value for m in metrics if m.metric_type == PerformanceMetric.TOTAL_RETURN) / len(metrics)
                drawdown_metrics = [m for m in metrics if m.metric_type == PerformanceMetric.MAX_DRAWDOWN]
                max_drawdown = max(abs(m.value) for m in drawdown_metrics) if drawdown_metrics else 0
                portfolio_info.total_assets = portfolio_info.initial_capital * (1 + total_return)
                portfolio_info.current_capital = portfolio_info.total_assets

            return portfolio_info.to_dict()

        except Exception as e:
            self.logger.error(f"获取投资组合失败: {e}")
            return None

    async def list_portfolios(self, user_id: str, status: Optional[PortfolioStatus] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取投资组合列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            List[Dict]: 投资组合列表
        """
        try:
            user_portfolios = [
                p for p in self.portfolios.values()
                if p.user_id == user_id
            ]

            if status:
                user_portfolios = [
                    p for p in user_portfolios
                    if p.status == status
                ]

            if limit:
                user_portfolios = user_portfolios[offset:offset + limit]
            else:
                user_portfolios = user_portfolios[offset:]

            return [p.to_dict() for p in user_portfolios]

        except Exception as e:
            self.logger.error(f"获取投资组合列表失败: {e}")
            return []

    async def calculate_performance_metrics(self, portfolio_id: str, metric_type: PerformanceMetric, period: str = "daily", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        计算性能指标
        
        Args:
            portfolio_id: 投资组合ID
            metric_type: 指标类型
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict: 性能指标结果
        """
        try:
            import uuid
            metric_id = f"metric_{uuid.uuid4()}"

            if not end_date:
                end_date = datetime.now()

            if not start_date:
                start_date = end_date - timedelta(days=30)

            period_days = (end_date - start_date).days

            # 根据投资组合ID获取价格历史
            from app.core.database import db_service

            sql = f"""
            SELECT 
                trade_date,
                close_price
            FROM stock_daily
            WHERE code IN (
                SELECT symbol
                FROM portfolio_positions
                WHERE portfolio_id = '{portfolio_id}'
                AND status = 'active'
            )
            AND trade_date >= '{start_date.date()}'
            AND trade_date <= '{end_date.date()}'
            ORDER BY trade_date ASC
            """

            results = await db_service.fetch_many(sql)

            if not results:
                self.logger.warning(f"未找到{portfolio_id}的价格历史数据")
                return {}

            # 计算收益率
            returns = []
            previous_price = None

            for result in results:
                if previous_price:
                    daily_return = (result['close_price'] - previous_price) / previous_price
                    returns.append(daily_return)

                previous_price = result['close_price']

            # 计算性能指标
            if not returns:
                return {}

            if metric_type == PerformanceMetric.TOTAL_RETURN:
                value = sum(returns) / len(returns)
            elif metric_type == PerformanceMetric.ANNUALIZED_RETURN:
                value = (1 + sum(returns) / len(returns)) ** (365 / period_days) - 1
            elif metric_type == PerformanceMetric.SHARPE_RATIO:
                mean_return = sum(returns) / len(returns)
                volatility = sum((r - mean_return) ** 2 for r in returns) / len(returns)

                if volatility == 0:
                    sharpe = 0
                else:
                    risk_free_rate = 0.03 / 252
                    sharpe = (mean_return - risk_free_rate) / volatility
                    value = sharpe
            elif metric_type == PerformanceMetric.MAX_DRAWDOWN:
                max_drawdown = 0
                peak_price = 0

                for i in range(len(returns) - 1):
                    peak_price = max(peak_price, returns[i])
                    drawdown = (peak_price - returns[i]) / peak_price

                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

                value = abs(max_drawdown)
            elif metric_type == PerformanceMetric.VOLATILITY:
                mean_return = sum(returns) / len(returns)
                volatility = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                value = volatility * (252 ** 0.5)
            elif metric_type == PerformanceMetric.BETA:
                benchmark_returns = self.benchmark_metrics.get('benchmark_returns', [])

                if not benchmark_returns:
                    value = 1.0
                else:
                    covariance = sum(returns[i] * benchmark_returns[i] for i in range(min(len(returns), len(benchmark_returns)))) / len(returns)
                    benchmark_variance = sum((br - sum(benchmark_returns) / len(benchmark_returns)) ** 2 for br in benchmark_returns) / len(benchmark_returns)

                    if benchmark_variance == 0:
                        value = 0
                    else:
                        value = covariance / benchmark_variance
            elif metric_type == PerformanceMetric.INFORMATION_RATIO:
                mean_return = sum(returns) / len(returns)
                volatility = sum((r - mean_return) ** 2 for r in returns) / len(returns)

                if volatility == 0:
                    value = 0
                else:
                    value = mean_return / volatility
            else:
                value = 0.0

            metric_data = PerformanceMetricsData(
                portfolio_id=portfolio_id,
                metric_type=metric_type,
                period=period,
                start_date=start_date,
                end_date=end_date,
                value=value,
                benchmark=None,
                rank=None,
                percentile=None,
                calculated_at=datetime.now()
            )

            # 保存性能指标
            if portfolio_id not in self.performance_metrics:
                self.performance_metrics[portfolio_id] = []

            self.performance_metrics[portfolio_id].append(metric_data)

            self.logger.info(f"计算性能指标: {metric_type.value} - {portfolio_id}")
            return metric_data.to_dict()

        except Exception as e:
            self.logger.error(f"计算性能指标失败: {e}")
            return {}

    async def get_performance_summary(self, portfolio_id: str) -> Dict:
        """
        获取性能摘要
        
        Args:
            portfolio_id: 投资组合ID
        
        Returns:
            Dict: 性能摘要
        """
        try:
            if portfolio_id not in self.performance_metrics:
                return {
                    'portfolio_id': portfolio_id,
                    'metrics': [],
                    'summary': {
                        'total_return': 0.0,
                        'sharpe_ratio': 0.0,
                        'max_drawdown': 0.0,
                        'volatility': 0.0,
                        'beta': 0.0,
                        'information_ratio': 0.0
                    },
                    'benchmarks': {
                        'avg_return': self.benchmark_metrics.get('avg_return', 0.08),
                        'avg_sharpe': self.benchmark_metrics.get('avg_sharpe', 1.2),
                        'avg_max_drawdown': self.benchmark_metrics.get('avg_max_drawdown', 0.15)
                    }
                }

            metrics = self.performance_metrics[portfolio_id]

            if not metrics:
                return {
                    'portfolio_id': portfolio_id,
                    'metrics': [],
                    'summary': {
                        'total_return': 0.0,
                        'sharpe_ratio': 0.0,
                        'max_drawdown': 0.0,
                        'volatility': 0.0,
                        'beta': 0.0,
                        'information_ratio': 0.0
                    },
                    'benchmarks': self.benchmark_metrics
                }

            # 计算汇总指标
            drawdown_metrics = [m for m in metrics if m.metric_type == PerformanceMetric.MAX_DRAWDOWN]
            summary = {
                'total_return': sum(m.value for m in metrics if m.metric_type == PerformanceMetric.TOTAL_RETURN) / len(metrics),
                'sharpe_ratio': sum(m.value for m in metrics if m.metric_type == PerformanceMetric.SHARPE_RATIO) / len(metrics),
                'max_drawdown': max(abs(m.value) for m in drawdown_metrics) if drawdown_metrics else 0,
                'volatility': sum(m.value for m in metrics if m.metric_type == PerformanceMetric.VOLATILITY) / len(metrics),
                'beta': sum(m.value for m in metrics if m.metric_type == PerformanceMetric.BETA) / len(metrics),
                'information_ratio': sum(m.value for m in metrics if m.metric_type == PerformanceMetric.INFORMATION_RATIO) / len(metrics)
            }

            return {
                'portfolio_id': portfolio_id,
                'metrics': [m.to_dict() for m in metrics],
                'summary': summary,
                'benchmarks': self.benchmark_metrics,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"获取性能摘要失败: {e}")
            return {}

    async def get_all_portfolios_summary(self, user_id: str) -> Dict:
        """
        获取所有投资组合摘要
        
        Args:
            user_id: 用户ID
        
        Returns:
            Dict: 投资组合摘要
        """
        try:
            portfolios = await self.list_portfolios(user_id)

            total_portfolio_value = sum(p.get('current_capital', 0) for p in portfolios)
            total_assets = sum(p.get('total_assets', 0) for p in portfolios)

            summary = {
                'user_id': user_id,
                'total_portfolios': len(portfolios),
                'total_value': f"{total_portfolio_value:.2f}",
                'total_assets': f"{total_assets:.2f}",
                'active_portfolios': len([p for p in portfolios if p.get('status') == PortfolioStatus.ACTIVE]),
                'draft_portfolios': len([p for p in portfolios if p.get('status') == PortfolioStatus.DRAFT]),
                'favorite_portfolios': len([p for p in portfolios if p.get('is_favorite', False)]),
                'generated_at': datetime.now().isoformat()
            }

            self.logger.info(f"获取投资组合摘要: {user_id}")
            return summary

        except Exception as e:
            self.logger.error(f"获取投资组合摘要失败: {e}")
            return {}

    async def export_portfolio_data(self, portfolio_id: str, format: str = 'json') -> str:
        """
        导出投资组合数据
        
        Args:
            portfolio_id: 投资组合ID
            format: 格式（json/csv）
        
        Returns:
            str: 导出内容
        """
        try:
            portfolio = await self.get_portfolio(portfolio_id)

            if not portfolio:
                self.logger.warning(f"投资组合不存在: {portfolio_id}")
                return ""

            if format == 'json':
                import json
                return json.dumps(portfolio, indent=2)

            elif format == 'csv':
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=['portfolio_id', 'name', 'status', 'initial_capital', 'current_capital', 'created_at', 'updated_at'])

                writer.writerow({
                    'portfolio_id': portfolio['portfolio_id'],
                    'name': portfolio['name'],
                    'status': portfolio['status'],
                    'initial_capital': portfolio['initial_capital'],
                    'current_capital': portfolio['current_capital'],
                    'created_at': portfolio['created_at'],
                    'updated_at': portfolio['updated_at']
                })

                output.seek(0)
                return output.getvalue()

            else:
                self.logger.warning(f"不支持的导出格式: {format}")
                return ""

        except Exception as e:
            self.logger.error(f"导出投资组合数据失败: {e}")
            return ""

    async def update_benchmark_metrics(self, new_benchmarks: Dict[str, float]) -> bool:
        """
        更新基准指标
        
        Args:
            new_benchmarks: 新的基准指标
        
        Returns:
            bool: 是否更新成功
        """
        try:
            self.benchmark_metrics.update(new_benchmarks)

            self.logger.info(f"基准指标已更新: {len(new_benchmarks)}个指标")
            return True

        except Exception as e:
            self.logger.error(f"更新基准指标失败: {e}")
            return False
