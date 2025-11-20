"""
MyStocks AI实时监控器

AI驱动的实时监控系统，负责系统性能、GPU状态、AI策略性能和交易指标的实时监控。
集成智能阈值算法和自适应监控间隔优化。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0 (完整AI版本)
依赖: 详见requirements.txt或文件导入部分
注意事项: 本文件是MyStocks v3.0核心组件，遵循5-tier数据分类架构
版权: MyStocks Project © 2025
"""

import asyncio
import time
import logging
import psutil
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("⚠️ GPUtil not available, GPU monitoring disabled")

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    SystemMetrics,
    get_ai_alert_manager,
)

from src.monitoring.monitoring_database import (
    MonitoringDatabase,
    get_monitoring_database,
)

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """监控配置"""
    monitoring_interval: float = 5.0  # 监控间隔(秒)
    max_history_size: int = 1000      # 最大历史记录数
    enable_gpu_monitoring: bool = True
    enable_performance_monitoring: bool = True
    enable_ai_strategy_monitoring: bool = True
    adaptive_intervals: bool = True   # 自适应间隔
    alert_check_frequency: int = 1    # 每N次监控检查告警

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class PerformanceThresholds:
    """性能阈值配置"""
    cpu_warning: float = 80.0
    cpu_critical: float = 95.0
    memory_warning: float = 85.0
    memory_critical: float = 95.0
    gpu_memory_warning: float = 85.0
    gpu_memory_critical: float = 95.0
    gpu_utilization_warning: float = 90.0
    disk_warning: float = 80.0
    disk_critical: float = 90.0
    ai_strategy_win_rate_critical: float = 0.3
    data_quality_critical: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class IMetricsCollector(ABC):
    """指标收集器接口"""
    
    @abstractmethod
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集指标"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass


class SystemMetricsCollector(IMetricsCollector):
    """系统指标收集器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.previous_network_io = None
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU和内存使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # 网络IO
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # 计算网络速度
            network_speed = {}
            if self.previous_network_io:
                time_diff = 1.0  # 假设间隔1秒
                network_speed = {
                    'bytes_sent_per_sec': (network.bytes_sent - self.previous_network_io.bytes_sent) / time_diff,
                    'bytes_recv_per_sec': (network.bytes_recv - self.previous_network_io.bytes_recv) / time_diff,
                }
            
            self.previous_network_io = network
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'network_io': network_io,
                'network_speed': network_speed,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 系统指标收集失败: {e}")
            return {}
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class GPUMetricsCollector(IMetricsCollector):
    """GPU指标收集器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.gpu_available = GPU_AVAILABLE
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集GPU指标"""
        if not self.config.enable_gpu_monitoring or not self.gpu_available:
            return {}
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {}
            
            gpu = gpus[0]  # 使用第一个GPU
            return {
                'gpu_memory_used': gpu.memoryUsed,
                'gpu_memory_total': gpu.memoryTotal,
                'gpu_utilization': gpu.load * 100,
                'gpu_temperature': gpu.temperature,
                'gpu_name': gpu.name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"⚠️ GPU指标收集失败: {e}")
            return {}
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.gpu_available and self.config.enable_gpu_monitoring


class AIStrategyMetricsCollector(IMetricsCollector):
    """AI策略指标收集器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集AI策略指标"""
        if not self.config.enable_ai_strategy_monitoring:
            return {}
        
        try:
            # 模拟AI策略指标收集
            # 实际实现中应该从策略分析器获取真实数据
            return {
                'active_strategies': 3,
                'total_signals_today': 156,
                'avg_confidence': 0.73,
                'winning_trades': 89,
                'total_trades': 156,
                'win_rate': 0.57,
                'best_strategy': 'ML-Based Strategy',
                'strategy_performance': {
                    'ML-Based': {'return': 1.78, 'sharpe': 0.79, 'drawdown': 2.42},
                    'Momentum': {'return': 1.14, 'sharpe': 0.60, 'drawdown': 1.73},
                    'Mean_Reversion': {'return': 0.42, 'sharpe': 0.50, 'drawdown': 1.40}
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI策略指标收集失败: {e}")
            return {}
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.config.enable_ai_strategy_monitoring


class TradingMetricsCollector(IMetricsCollector):
    """交易指标收集器"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集交易指标"""
        try:
            # 模拟交易指标收集
            # 实际实现中应该从交易系统获取真实数据
            return {
                'total_positions': 12,
                'daily_pnl': 1250.75,
                'portfolio_value': 102567.83,
                'daily_return': 0.0123,
                'max_drawdown': 2.42,
                'sharpe_ratio': 0.79,
                'last_trade_time': datetime.now().isoformat(),
                'active_alerts': 0,
                'data_quality_score': 0.95,
                'last_query_time': 125.0,  # 用于慢查询检测
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 交易指标收集失败: {e}")
            return {}
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class AdaptiveIntervalManager:
    """自适应间隔管理器"""
    
    def __init__(self, base_interval: float = 5.0, min_interval: float = 2.0, max_interval: float = 60.0):
        self.base_interval = base_interval
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.current_interval = base_interval
        self.load_history = []
        self.max_history = 50
        
    def calculate_next_interval(self, system_metrics: Dict[str, Any]) -> float:
        """根据系统负载计算下一个监控间隔"""
        try:
            cpu_usage = system_metrics.get('cpu_usage', 0)
            memory_usage = system_metrics.get('memory_usage', 0)
            
            # 计算综合负载
            load_score = (cpu_usage + memory_usage) / 2
            
            # 记录负载历史
            self.load_history.append(load_score)
            if len(self.load_history) > self.max_history:
                self.load_history = self.load_history[-self.max_history:]
            
            # 自适应调整间隔
            if load_score > 80:  # 高负载，增加间隔
                self.current_interval = min(self.current_interval * 1.2, self.max_interval)
            elif load_score < 30:  # 低负载，减少间隔
                self.current_interval = max(self.current_interval * 0.8, self.min_interval)
            else:  # 正常负载，回归基准
                self.current_interval = self.base_interval
            
            # 添加小量随机性避免同步
            import random
            jitter = random.uniform(0.9, 1.1)
            self.current_interval *= jitter
            
            return max(self.min_interval, min(self.current_interval, self.max_interval))
            
        except Exception as e:
            logger.error(f"❌ 自适应间隔计算失败: {e}")
            return self.base_interval
    
    def get_interval(self) -> float:
        """获取当前间隔"""
        return self.current_interval


class AIRealtimeMonitor:
    """AI实时监控器"""
    
    def __init__(self, alert_manager: Optional[AIAlertManager] = None, config: Optional[MonitoringConfig] = None):
        """初始化AI实时监控器"""
        self.alert_manager = alert_manager or get_ai_alert_manager()
        self.config = config or MonitoringConfig()
        self.thresholds = PerformanceThresholds()
        
        # 监控状态
        self.running = False
        self.monitoring_task = None
        
        # 指标历史
        self.metrics_history = []
        self.current_metrics = None
        self.max_history_size = self.config.max_history_size
        
        # 指标收集器
        self.system_collector = SystemMetricsCollector(self.config)
        self.gpu_collector = GPUMetricsCollector(self.config)
        self.ai_strategy_collector = AIStrategyMetricsCollector(self.config)
        self.trading_collector = TradingMetricsCollector(self.config)
        
        # 自适应间隔管理器
        self.adaptive_manager = AdaptiveIntervalManager(self.config.monitoring_interval)
        
        # 统计信息
        self.stats = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'avg_cycle_time': 0.0,
            'last_metrics_time': None,
            'monitoring_start_time': None
        }
        
        logger.info(f"✅ AIRealtimeMonitor initialized (interval: {self.config.monitoring_interval}s)")
    
    async def start_monitoring(self, duration_seconds: int = 120):
        """启动实时监控"""
        if self.running:
            logger.warning("⚠️ 监控已在运行中")
            return
        
        self.running = True
        self.stats['monitoring_start_time'] = datetime.now()
        
        print(f"🔍 开始AI实时监控，时长: {duration_seconds}秒")
        logger.info(f"🔍 开始AI实时监控，时长: {duration_seconds}秒")
        
        try:
            monitoring_start = time.time()
            cycle_count = 0
            
            while self.running and (time.time() - monitoring_start) < duration_seconds:
                cycle_start_time = time.time()
                cycle_count += 1
                
                try:
                    # 收集系统指标
                    metrics = await self._collect_all_metrics()
                    
                    if metrics:
                        # 保存指标
                        self.current_metrics = metrics
                        self._save_metrics_history(metrics)
                        
                        # 检查告警条件 (每N次检查一次)
                        if cycle_count % self.config.alert_check_frequency == 0:
                            await self._check_alert_conditions()
                        
                        # 更新统计
                        self.stats['successful_cycles'] += 1
                        cycle_time = time.time() - cycle_start_time
                        self._update_cycle_stats(cycle_time)
                        
                        # 打印状态 (每10次循环打印一次)
                        if cycle_count % 10 == 0:
                            self._print_monitoring_status()
                    else:
                        self.stats['failed_cycles'] += 1
                        logger.warning("⚠️ 指标收集失败")
                    
                    # 等待下一个监控周期 (自适应间隔)
                    if self.running:
                        interval = self.adaptive_manager.get_interval()
                        
                        # 如果启用了自适应间隔，根据系统负载调整
                        if self.config.adaptive_intervals and self.current_metrics:
                            system_metrics = self.current_metrics.get('system', {})
                            interval = self.adaptive_manager.calculate_next_interval(system_metrics)
                        
                        await asyncio.sleep(interval)
                
                except Exception as e:
                    logger.error(f"❌ 监控循环异常: {e}")
                    self.stats['failed_cycles'] += 1
                    await asyncio.sleep(5)  # 错误后短暂等待
                
                self.stats['total_cycles'] += 1
            
        except Exception as e:
            logger.error(f"❌ 监控异常: {e}")
        finally:
            self.running = False
            self._print_final_stats()
            print("🛑 AI实时监控已停止")
            logger.info("🛑 AI实时监控已停止")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("🛑 正在停止监控...")
    
    async def _collect_all_metrics(self) -> Optional[SystemMetrics]:
        """收集所有指标"""
        try:
            # 并行收集各类指标
            tasks = []
            
            # 系统指标
            if self.system_collector.is_available():
                tasks.append(self.system_collector.collect_metrics())
            
            # GPU指标
            if self.gpu_collector.is_available():
                tasks.append(self.gpu_collector.collect_metrics())
            
            # AI策略指标
            if self.ai_strategy_collector.is_available():
                tasks.append(self.ai_strategy_collector.collect_metrics())
            
            # 交易指标
            if self.trading_collector.is_available():
                tasks.append(self.trading_collector.collect_metrics())
            
            # 等待所有收集任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 解析结果
            system_metrics = {}
            gpu_metrics = {}
            ai_strategy_metrics = {}
            trading_metrics = {}
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ 指标收集异常: {result}")
                    continue
                
                if i == 0 and self.system_collector.is_available():
                    system_metrics = result
                elif i == 1 and self.gpu_collector.is_available():
                    gpu_metrics = result
                elif i == 2 and self.ai_strategy_collector.is_available():
                    ai_strategy_metrics = result
                elif i == 3 and self.trading_collector.is_available():
                    trading_metrics = result
            
            # 组合系统指标
            if not system_metrics:
                return None
            
            combined_metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=system_metrics.get('cpu_usage', 0.0),
                memory_usage=system_metrics.get('memory_usage', 0.0),
                gpu_memory_used=gpu_metrics.get('gpu_memory_used', 0.0),
                gpu_memory_total=gpu_metrics.get('gpu_memory_total', 0.0),
                gpu_utilization=gpu_metrics.get('gpu_utilization', 0.0),
                disk_usage=system_metrics.get('disk_usage', 0.0),
                network_io=system_metrics.get('network_io', {}),
                ai_strategy_metrics=ai_strategy_metrics,
                trading_metrics=trading_metrics
            )
            
            self.stats['last_metrics_time'] = datetime.now()
            return combined_metrics
            
        except Exception as e:
            logger.error(f"❌ 指标收集失败: {e}")
            return None
    
    def _save_metrics_history(self, metrics: SystemMetrics):
        """保存指标历史"""
        self.metrics_history.append(metrics)
        
        # 保持历史大小限制
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    async def _check_alert_conditions(self):
        """检查告警条件"""
        try:
            if self.current_metrics:
                await self.alert_manager.check_alert_conditions(self.current_metrics)
        except Exception as e:
            logger.error(f"❌ 告警检查失败: {e}")
    
    def _update_cycle_stats(self, cycle_time: float):
        """更新循环统计"""
        # 更新平均执行时间
        total_cycles = self.stats['total_cycles']
        if total_cycles <= 1:
            self.stats['avg_cycle_time'] = cycle_time
        else:
            # 移动平均
            current_avg = self.stats['avg_cycle_time']
            self.stats['avg_cycle_time'] = (current_avg * (total_cycles - 1) + cycle_time) / total_cycles
    
    def _print_monitoring_status(self):
        """打印监控状态"""
        if not self.current_metrics:
            return
        
        metrics = self.current_metrics
        status_msg = (
            f"📊 监控状态 | CPU: {metrics.cpu_usage:.1f}% | "
            f"GPU: {metrics.gpu_utilization:.1f}% | "
            f"内存: {metrics.memory_usage:.1f}% | "
            f"循环: {self.stats['successful_cycles']}/{self.stats['total_cycles']}"
        )
        
        print(status_msg)
        logger.info(status_msg)
    
    def _print_final_stats(self):
        """打印最终统计"""
        stats = self.stats
        duration = (datetime.now() - stats['monitoring_start_time']).total_seconds() if stats['monitoring_start_time'] else 0
        
        final_msg = (
            f"📊 监控完成 | 总循环: {stats['total_cycles']} | "
            f"成功: {stats['successful_cycles']} | "
            f"失败: {stats['failed_cycles']} | "
            f"成功率: {stats['successful_cycles']/max(stats['total_cycles'], 1)*100:.1f}% | "
            f"平均时间: {stats['avg_cycle_time']:.2f}s"
        )
        
        print(f"\n{final_msg}")
        logger.info(final_msg)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.current_metrics:
            return {}
        
        metrics = self.current_metrics
        
        summary = {
            'monitoring_status': 'running' if self.running else 'stopped',
            'current_metrics': {
                'cpu_usage': f"{metrics.cpu_usage:.1f}%",
                'memory_usage': f"{metrics.memory_usage:.1f}%",
                'gpu_utilization': f"{metrics.gpu_utilization:.1f}%",
                'gpu_memory_usage': f"{metrics.gpu_memory_used:.0f}/{metrics.gpu_memory_total:.0f}MB" if metrics.gpu_memory_total > 0 else "N/A",
                'disk_usage': f"{metrics.disk_usage:.1f}%",
                'active_strategies': len(metrics.ai_strategy_metrics.get('strategy_performance', {})),
                'win_rate': f"{metrics.ai_strategy_metrics.get('win_rate', 0)*100:.1f}%" if metrics.ai_strategy_metrics.get('win_rate') else "N/A",
                'daily_return': f"{metrics.trading_metrics.get('daily_return', 0)*100:.2f}%" if metrics.trading_metrics.get('daily_return') else "N/A"
            },
            'statistics': {
                'total_cycles': self.stats['total_cycles'],
                'successful_cycles': self.stats['successful_cycles'],
                'failed_cycles': self.stats['failed_cycles'],
                'success_rate': f"{self.stats['successful_cycles']/max(self.stats['total_cycles'], 1)*100:.1f}%",
                'avg_cycle_time': f"{self.stats['avg_cycle_time']:.3f}s",
                'history_size': len(self.metrics_history),
                'monitoring_duration': f"{(datetime.now() - self.stats['monitoring_start_time']).total_seconds():.0f}s" if self.stats['monitoring_start_time'] else "0s"
            },
            'configuration': {
                'monitoring_interval': f"{self.adaptive_manager.get_interval():.1f}s",
                'adaptive_intervals': self.config.adaptive_intervals,
                'gpu_monitoring': self.config.enable_gpu_monitoring,
                'ai_strategy_monitoring': self.config.enable_ai_strategy_monitoring
            }
        }
        
        return summary
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        return [alert.to_dict() for alert in self.alert_manager.get_active_alerts()]
    
    def update_config(self, config_updates: Dict[str, Any]):
        """更新配置"""
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        logger.info(f"✅ 更新监控配置: {config_updates}")
    
    def set_performance_thresholds(self, thresholds: Dict[str, float]):
        """设置性能阈值"""
        for key, value in thresholds.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
        
        logger.info(f"✅ 更新性能阈值: {thresholds}")
    
    async def run_health_check(self) -> Dict[str, Any]:
        """运行健康检查"""
        health_status = {
            'overall_status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 检查监控状态
            health_status['checks']['monitoring_status'] = {
                'status': 'running' if self.running else 'stopped',
                'message': '监控正常运行' if self.running else '监控未运行'
            }
            
            # 检查指标收集器
            collectors = {
                'system': self.system_collector,
                'gpu': self.gpu_collector,
                'ai_strategy': self.ai_strategy_collector,
                'trading': self.trading_collector
            }
            
            for name, collector in collectors.items():
                available = collector.is_available()
                health_status['checks'][f'{name}_collector'] = {
                    'status': 'available' if available else 'unavailable',
                    'message': f'{name}指标收集器可用' if available else f'{name}指标收集器不可用'
                }
            
            # 检查告警系统
            alert_summary = self.alert_manager.get_alert_summary()
            active_alerts = alert_summary['active_alerts_count']
            health_status['checks']['alert_system'] = {
                'status': 'healthy' if active_alerts == 0 else 'warning',
                'message': f'活跃告警数: {active_alerts}' if active_alerts > 0 else '无活跃告警'
            }
            
            # 检查GPU状态
            if self.config.enable_gpu_monitoring:
                gpu_available = self.gpu_collector.is_available()
                health_status['checks']['gpu_status'] = {
                    'status': 'available' if gpu_available else 'unavailable',
                    'message': 'GPU监控可用' if gpu_available else 'GPU监控不可用'
                }
            
            # 计算整体状态
            error_checks = [check for check in health_status['checks'].values() if check['status'] in ['error', 'unavailable']]
            if error_checks:
                health_status['overall_status'] = 'degraded' if active_alerts == 0 else 'warning'
            elif active_alerts > 0:
                health_status['overall_status'] = 'warning'
            
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
        
        return health_status


# 全局AI实时监控器实例 (单例模式)
_ai_realtime_monitor: Optional[AIRealtimeMonitor] = None


def get_ai_realtime_monitor(alert_manager: Optional[AIAlertManager] = None) -> AIRealtimeMonitor:
    """获取全局AI实时监控器实例 (单例模式)"""
    global _ai_realtime_monitor
    if _ai_realtime_monitor is None:
        _ai_realtime_monitor = AIRealtimeMonitor(alert_manager)
    return _ai_realtime_monitor


if __name__ == "__main__":
    """测试AI实时监控器"""
    import sys

    sys.path.insert(0, ".")

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n测试AIRealtimeMonitor...\n")

    # 创建AI实时监控器
    monitor = AIRealtimeMonitor()

    # 测试1: 健康检查
    print("1. 运行健康检查...")
    health_check = asyncio.run(monitor.run_health_check())
    print(f"   健康状态: {health_check['overall_status']}")
    for check_name, check_result in health_check['checks'].items():
        print(f"   {check_name}: {check_result['status']} - {check_result['message']}")
    print()

    # 测试2: 短时间监控测试
    print("2. 启动30秒监控测试...")
    asyncio.run(monitor.start_monitoring(duration_seconds=30))
    print("   监控测试完成\n")

    # 测试3: 获取监控摘要
    print("3. 获取监控摘要...")
    summary = monitor.get_metrics_summary()
    print(f"   监控状态: {summary.get('monitoring_status', 'unknown')}")
    if summary.get('current_metrics'):
        for key, value in summary['current_metrics'].items():
            print(f"   {key}: {value}")
    print()

    # 测试4: 测试配置更新
    print("4. 测试配置更新...")
    monitor.update_config({
        'monitoring_interval': 3.0,
        'enable_gpu_monitoring': True,
        'adaptive_intervals': True
    })
    print("   配置更新完成\n")

    # 测试5: 测试阈值设置
    print("5. 测试阈值设置...")
    monitor.set_performance_thresholds({
        'cpu_warning': 75.0,
        'gpu_memory_warning': 80.0
    })
    print("   阈值设置完成\n")

    print("✅ AIRealtimeMonitor 所有测试完成!")
