# AI监控和告警系统实施指南

## 📋 概述

本文档详细说明MyStocks系统中AI监控和告警系统的实施、配置和优化方法，为mystocks_nice分支提供完整的监控系统参考。

**目标读者**: 运维工程师、SRE、监控专家、AI系统管理员  
**实施难度**: 中等  
**前置要求**: Python基础、系统管理知识、AI系统理解

---

## 🏗️ 监控系统架构

### 核心组件

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import asyncio
import logging
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class AlertType(Enum):
    """告警类型"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    GPU_MEMORY_HIGH = "gpu_memory_high"
    AI_MODEL_ERROR = "ai_model_error"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYSTEM_RESOURCE_HIGH = "system_resource_high"
    STRATEGY_ANOMALY = "strategy_anomaly"
    TRADING_SIGNAL_ABNORMAL = "trading_signal_abnormal"

class AlertSeverity(Enum):
    """告警严重性"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    threshold: float
    duration_seconds: int
    enabled: bool
    description: str

@dataclass
class Alert:
    """告警实例"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class IAlertHandler(ABC):
    """告警处理器接口"""
    
    @abstractmethod
    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    gpu_memory_used: float
    gpu_memory_total: float
    gpu_utilization: float
    disk_usage: float
    network_io: Dict[str, float]
    ai_strategy_metrics: Dict[str, Any]
    trading_metrics: Dict[str, Any]

class AIRealtimeMonitor:
    """AI实时监控器"""
    
    def __init__(self, alert_manager: 'AIAlertManager'):
        self.alert_manager = alert_manager
        self.running = False
        self.monitoring_interval = 5  # 5秒监控间隔
        self.metrics_history = []
        self.max_history_size = 1000
    
    async def start_monitoring(self, duration_seconds: int = 120):
        """启动实时监控"""
        self.running = True
        start_time = datetime.now()
        
        print(f"🔍 开始AI实时监控，时长: {duration_seconds}秒")
        
        try:
            while self.running and (datetime.now() - start_time).seconds < duration_seconds:
                # 收集系统指标
                metrics = await self._collect_system_metrics()
                
                # 检查告警条件
                await self.alert_manager.check_alert_conditions(metrics)
                
                # 保存指标历史
                self._save_metrics_history(metrics)
                
                # 短暂休息
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            print(f"❌ 监控异常: {e}")
            logging.error(f"监控异常: {e}")
        finally:
            self.running = False
            print("🛑 AI实时监控已停止")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        import psutil
        import GPUtil
        
        # CPU和内存使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # GPU指标
        gpu_metrics = self._get_gpu_metrics()
        
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
        
        # AI策略指标
        ai_strategy_metrics = await self._collect_ai_strategy_metrics()
        
        # 交易指标
        trading_metrics = await self._collect_trading_metrics()
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_memory_used=gpu_metrics['memory_used'],
            gpu_memory_total=gpu_metrics['memory_total'],
            gpu_utilization=gpu_metrics['utilization'],
            disk_usage=disk_usage,
            network_io=network_io,
            ai_strategy_metrics=ai_strategy_metrics,
            trading_metrics=trading_metrics
        )
    
    def _get_gpu_metrics(self) -> Dict[str, float]:
        """获取GPU指标"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'utilization': gpu.load * 100
                }
        except Exception as e:
            logging.warning(f"GPU指标获取失败: {e}")
        
        return {
            'memory_used': 0.0,
            'memory_total': 0.0,
            'utilization': 0.0
        }
    
    async def _collect_ai_strategy_metrics(self) -> Dict[str, Any]:
        """收集AI策略指标"""
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
                }
            }
        except Exception as e:
            logging.error(f"AI策略指标收集失败: {e}")
            return {}
    
    async def _collect_trading_metrics(self) -> Dict[str, Any]:
        """收集交易指标"""
        try:
            # 模拟交易指标收集
            return {
                'total_positions': 12,
                'daily_pnl': 1250.75,
                'portfolio_value': 102567.83,
                'daily_return': 0.0123,
                'max_drawdown': 2.42,
                'sharpe_ratio': 0.79,
                'last_trade_time': datetime.now().isoformat(),
                'active_alerts': 0,
                'data_quality_score': 0.95
            }
        except Exception as e:
            logging.error(f"交易指标收集失败: {e}")
            return {}
    
    def _save_metrics_history(self, metrics: SystemMetrics):
        """保存指标历史"""
        self.metrics_history.append(metrics)
        
        # 保持历史大小限制
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        
        return {
            'current_metrics': {
                'cpu_usage': latest.cpu_usage,
                'memory_usage': latest.memory_usage,
                'gpu_utilization': latest.gpu_utilization,
                'gpu_memory_usage': f"{latest.gpu_memory_used}/{latest.gpu_memory_total}MB",
                'disk_usage': latest.disk_usage,
                'ai_strategies': latest.ai_strategy_metrics.get('active_strategies', 0),
                'win_rate': latest.ai_strategy_metrics.get('win_rate', 0),
                'daily_return': latest.trading_metrics.get('daily_return', 0)
            },
            'history_size': len(self.metrics_history),
            'monitoring_duration': f"{(self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).seconds if len(self.metrics_history) > 1 else 0}秒"
        }
```

---

## 🚨 AI告警管理器

```python
class AIAlertManager:
    """AI告警管理器"""
    
    def __init__(self):
        self.alert_rules = self._load_default_alert_rules()
        self.active_alerts = {}
        self.alert_handlers = []
        self.alert_history = []
        self.max_history_size = 10000
    
    def _load_default_alert_rules(self) -> List[AlertRule]:
        """加载默认告警规则"""
        return [
            AlertRule(
                name="CPU使用率过高",
                alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
                severity=AlertSeverity.WARNING,
                threshold=80.0,
                duration_seconds=60,
                enabled=True,
                description="CPU使用率持续超过80%"
            ),
            AlertRule(
                name="GPU内存使用率过高",
                alert_type=AlertType.GPU_MEMORY_HIGH,
                severity=AlertSeverity.WARNING,
                threshold=85.0,
                duration_seconds=30,
                enabled=True,
                description="GPU内存使用率持续超过85%"
            ),
            AlertRule(
                name="AI策略胜率异常",
                alert_type=AlertType.STRATEGY_ANOMALY,
                severity=AlertSeverity.CRITICAL,
                threshold=0.3,
                duration_seconds=300,
                enabled=True,
                description="AI策略胜率持续低于30%"
            ),
            AlertRule(
                name="AI策略回撤过大",
                alert_type=AlertType.STRATEGY_ANOMALY,
                severity=AlertSeverity.CRITICAL,
                threshold=5.0,
                duration_seconds=180,
                enabled=True,
                description="AI策略最大回撤持续超过5%"
            ),
            AlertRule(
                name="数据质量异常",
                alert_type=AlertType.DATA_QUALITY_ISSUE,
                severity=AlertSeverity.WARNING,
                threshold=0.8,
                duration_seconds=120,
                enabled=True,
                description="数据质量评分持续低于80%"
            )
        ]
    
    def add_alert_handler(self, handler: IAlertHandler):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def add_alert_rule(self, rule: AlertRule):
        """添加自定义告警规则"""
        self.alert_rules.append(rule)
    
    def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
    
    async def check_alert_conditions(self, metrics: SystemMetrics):
        """检查告警条件"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            try:
                # 获取指标值
                metric_value = self._get_metric_value(metrics, rule.alert_type)
                
                if metric_value is None:
                    continue
                
                # 检查是否触发告警
                triggered = self._check_threshold(metric_value, rule)
                
                if triggered:
                    await self._trigger_alert(rule, metrics, metric_value)
                else:
                    await self._resolve_alert(rule)
                    
            except Exception as e:
                logging.error(f"告警规则 {rule.name} 检查失败: {e}")
    
    def _get_metric_value(self, metrics: SystemMetrics, alert_type: AlertType) -> Optional[float]:
        """获取指标值"""
        if alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return metrics.cpu_usage
        elif alert_type == AlertType.GPU_MEMORY_HIGH:
            return (metrics.gpu_memory_used / metrics.gpu_memory_total * 100) if metrics.gpu_memory_total > 0 else 0
        elif alert_type == AlertType.STRATEGY_ANOMALY:
            return metrics.ai_strategy_metrics.get('win_rate', 0)
        elif alert_type == AlertType.DATA_QUALITY_ISSUE:
            return metrics.trading_metrics.get('data_quality_score', 0)
        elif alert_type == AlertType.PERFORMANCE_DEGRADATION:
            return metrics.trading_metrics.get('sharpe_ratio', 0)
        
        return None
    
    def _check_threshold(self, metric_value: float, rule: AlertRule) -> bool:
        """检查阈值"""
        if rule.alert_type == AlertType.GPU_MEMORY_HIGH:
            return metric_value > rule.threshold
        elif rule.alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return metric_value > rule.threshold
        elif rule.alert_type == AlertType.STRATEGY_ANOMALY:
            return metric_value < rule.threshold
        elif rule.alert_type == AlertType.DATA_QUALITY_ISSUE:
            return metric_value < rule.threshold
        elif rule.alert_type == AlertType.PERFORMANCE_DEGRADATION:
            return metric_value < rule.threshold
        
        return False
    
    async def _trigger_alert(self, rule: AlertRule, metrics: SystemMetrics, metric_value: float):
        """触发告警"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 检查是否已有未解决的同类告警
        if rule.name in self.active_alerts:
            return
        
        # 创建告警
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            message=self._generate_alert_message(rule, metric_value),
            timestamp=datetime.now(),
            metrics={
                'current_value': metric_value,
                'threshold': rule.threshold,
                'duration_seconds': rule.duration_seconds,
                'system_metrics': self._serialize_metrics(metrics)
            }
        )
        
        # 保存告警
        self.active_alerts[rule.name] = alert
        self._save_alert_history(alert)
        
        # 处理告警
        await self._handle_alert(alert)
        
        print(f"🚨 告警触发: {alert.message}")
    
    async def _resolve_alert(self, rule: AlertRule):
        """解决告警"""
        if rule.name in self.active_alerts:
            alert = self.active_alerts[rule.name]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[rule.name]
            self._save_alert_history(alert)
            
            print(f"✅ 告警解决: {rule.name}")
    
    def _generate_alert_message(self, rule: AlertRule, metric_value: float) -> str:
        """生成告警消息"""
        if rule.alert_type == AlertType.GPU_MEMORY_HIGH:
            return f"GPU内存使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return f"CPU使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.STRATEGY_ANOMALY:
            return f"AI策略胜率异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.DATA_QUALITY_ISSUE:
            return f"数据质量异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
        else:
            return f"{rule.name}: {metric_value:.2f} (阈值: {rule.threshold})"
    
    def _serialize_metrics(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """序列化指标"""
        return {
            'timestamp': metrics.timestamp.isoformat(),
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage,
            'gpu_utilization': metrics.gpu_utilization,
            'ai_strategies_count': len(metrics.ai_strategy_metrics),
            'trading_metrics': metrics.trading_metrics
        }
    
    def _save_alert_history(self, alert: Alert):
        """保存告警历史"""
        self.alert_history.append(alert)
        
        # 保持历史大小限制
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
    
    async def _handle_alert(self, alert: Alert):
        """处理告警"""
        # 通知所有处理器
        for handler in self.alert_handlers:
            try:
                success = await handler.handle_alert(alert)
                if not success:
                    logging.error(f"告警处理器 {handler.__class__.__name__} 处理失败")
            except Exception as e:
                logging.error(f"告警处理器异常: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """获取告警摘要"""
        total_alerts = len(self.alert_history)
        critical_alerts = len([a for a in self.alert_history if a.severity == AlertSeverity.CRITICAL])
        warning_alerts = len([a for a in self.alert_history if a.severity == AlertSeverity.WARNING])
        active_alerts = len(self.active_alerts)
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'info_alerts': total_alerts - critical_alerts - warning_alerts,
            'alert_rules_count': len(self.alert_rules),
            'enabled_rules_count': len([r for r in self.alert_rules if r.enabled])
        }
```

---

## 📧 告警处理器实现

### 1. 邮件告警处理器

```python
class EmailAlertHandler(IAlertHandler):
    """邮件告警处理器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
    
    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] MyStocks AI告警: {alert.rule_name}"
            
            # 邮件正文
            body = f"""
            <html>
            <body>
                <h2>MyStocks AI系统告警</h2>
                <p><strong>告警ID:</strong> {alert.id}</p>
                <p><strong>规则名称:</strong> {alert.rule_name}</p>
                <p><strong>严重性:</strong> {alert.severity.value}</p>
                <p><strong>告警类型:</strong> {alert.alert_type.value}</p>
                <p><strong>发生时间:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>告警消息:</strong> {alert.message}</p>
                
                <h3>详细指标:</h3>
                <pre>{json.dumps(alert.metrics, indent=2, ensure_ascii=False)}</pre>
                
                <p>请及时处理此告警。</p>
                <p><small>此邮件由MyStocks AI监控系统自动发送</small></p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(body, 'html', 'utf-8'))
            
            # 发送邮件
            await self._send_email(msg)
            
            return True
            
        except Exception as e:
            logging.error(f"邮件告警发送失败: {e}")
            return False
    
    async def _send_email(self, msg: MimeMultipart):
        """发送邮件"""
        def _send():
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            def _test():
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    return True
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _test)
            
        except Exception as e:
            logging.error(f"邮件连接测试失败: {e}")
            return False
```

### 2. Webhook告警处理器

```python
class WebhookAlertHandler(IAlertHandler):
    """Webhook告警处理器"""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {'Content-Type': 'application/json'}
    
    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            import aiohttp
            
            payload = {
                'alert_id': alert.id,
                'rule_name': alert.rule_name,
                'severity': alert.severity.value,
                'alert_type': alert.alert_type.value,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'metrics': alert.metrics
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logging.error(f"Webhook告警发送失败: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            import aiohttp
            
            test_payload = {
                'test': True,
                'message': 'MyStocks AI监控连接测试',
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=test_payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logging.error(f"Webhook连接测试失败: {e}")
            return False
```

### 3. 本地日志处理器

```python
class LogAlertHandler(IAlertHandler):
    """本地日志告警处理器"""
    
    def __init__(self, log_file: str = "alerts.log"):
        self.log_file = log_file
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AIAlertHandler')
    
    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            log_message = f"""
            ========================================
            AI系统告警通知
            ========================================
            告警ID: {alert.id}
            规则名称: {alert.rule_name}
            严重性: {alert.severity.value.upper()}
            告警类型: {alert.alert_type.value}
            发生时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            告警消息: {alert.message}
            
            详细指标:
            {json.dumps(alert.metrics, indent=2, ensure_ascii=False)}
            ========================================
            """
            
            if alert.severity == AlertSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif alert.severity == AlertSeverity.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return True
            
        except Exception as e:
            print(f"日志告警处理失败: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            self.logger.info("MyStocks AI监控日志处理器连接测试")
            return True
        except Exception as e:
            print(f"日志处理器测试失败: {e}")
            return False
```

---

## 🚀 监控面板实现

### NiceGUI监控面板

```python
from nicegui import ui, app
import asyncio
import json
from datetime import datetime, timedelta

class MonitoringDashboard:
    """监控面板"""
    
    def __init__(self, alert_manager: AIAlertManager, monitor: AIRealtimeMonitor):
        self.alert_manager = alert_manager
        self.monitor = monitor
        self.dashboard_refresh_interval = 5  # 5秒刷新
    
    def create_monitoring_page(self):
        """创建监控页面"""
        
        # 页面标题
        ui.header().style('background-color: #1976d2').classes('text-white')
        with ui.row().classes('w-full q-pa-md items-center justify-between'):
            ui.label('🔍 MyStocks AI实时监控系统').classes('text-h4 text-white')
            with ui.row().classes('items-center'):
                ui.badge('在线', color='green').bind_text_from(lambda: '在线' if self.monitor.running else '离线')
        
        # 主要指标卡片
        self._create_metrics_cards()
        
        # 告警状态
        self._create_alert_status()
        
        # 实时图表
        self._create_realtime_charts()
        
        # 告警历史
        self._create_alert_history()
        
        # 控制按钮
        self._create_control_buttons()
        
        # 启动自动刷新
        self._start_auto_refresh()
    
    def _create_metrics_cards(self):
        """创建指标卡片"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📊 系统指标概览').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.row().classes('q-gutter-md'):
                # CPU使用率
                with ui.card().classes('col-3 q-pa-md text-center'):
                    ui.label('CPU使用率').classes('text-subtitle2')
                    self.cpu_label = ui.label('0%').classes('text-h5 text-primary')
                    ui.progress(value=0, size='lg', color='primary').bind_value_from(self.cpu_label, lambda x: float(x.replace('%', '')) if x.replace('%', '').replace('.', '').isdigit() else 0)
                
                # GPU使用率
                with ui.card().classes('col-3 q-pa-md text-center'):
                    ui.label('GPU使用率').classes('text-subtitle2')
                    self.gpu_label = ui.label('0%').classes('text-h5 text-secondary')
                    ui.progress(value=0, size='lg', color='secondary').bind_value_from(self.gpu_label, lambda x: float(x.replace('%', '')) if x.replace('%', '').replace('.', '').isdigit() else 0)
                
                # 内存使用率
                with ui.card().classes('col-3 q-pa-md text-center'):
                    ui.label('内存使用率').classes('text-subtitle2')
                    self.memory_label = ui.label('0%').classes('text-h5 text-accent')
                    ui.progress(value=0, size='lg', color='accent').bind_value_from(self.memory_label, lambda x: float(x.replace('%', '')) if x.replace('%', '').replace('.', '').isdigit() else 0)
                
                # 活跃告警数
                with ui.card().classes('col-3 q-pa-md text-center'):
                    ui.label('活跃告警').classes('text-subtitle2')
                    self.alerts_label = ui.label('0').classes('text-h5 text-negative')
    
    def _create_alert_status(self):
        """创建告警状态"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('🚨 告警状态').classes('text-h6 text-weight-bold q-mb-md')
            
            # 活跃告警列表
            with ui.row().classes('q-gutter-sm'):
                self.critical_alert_badge = ui.badge('0', color='red')
                self.warning_alert_badge = ui.badge('0', color='orange')
                self.info_alert_badge = ui.badge('0', color='blue')
            
            # 活跃告警详情
            with ui.column().classes('q-mt-md'):
                ui.label('当前活跃告警:').classes('text-subtitle1')
                self.active_alerts_list = ui.column()
    
    def _create_realtime_charts(self):
        """创建实时图表"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📈 实时指标图表').classes('text-h6 text-weight-bold q-mb-md')
            
            # 使用简单的文本图表代替复杂图表
            with ui.column().classes('q-gutter-sm'):
                ui.label('CPU使用率趋势:').classes('text-subtitle2')
                self.cpu_chart = ui.textarea(readonly=True).classes('w-full')
                
                ui.label('GPU使用率趋势:').classes('text-subtitle2')
                self.gpu_chart = ui.textarea(readonly=True).classes('w-full')
    
    def _create_alert_history(self):
        """创建告警历史"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('📋 告警历史').classes('text-h6 text-weight-bold q-mb-md')
            
            # 历史告警表格
            self.alert_history_table = ui.table({
                'columns': [
                    {'name': 'time', 'label': '时间', 'field': 'time'},
                    {'name': 'rule', 'label': '规则', 'field': 'rule'},
                    {'name': 'severity', 'label': '严重性', 'field': 'severity'},
                    {'name': 'message', 'label': '消息', 'field': 'message'},
                    {'name': 'status', 'label': '状态', 'field': 'status'}
                ],
                'rows': []
            }).classes('w-full')
    
    def _create_control_buttons(self):
        """创建控制按钮"""
        with ui.card().classes('w-full q-pa-md q-mb-md'):
            ui.label('🎮 控制面板').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.row().classes('q-gutter-md'):
                self.start_button = ui.button('开始监控', on_click=self.start_monitoring).classes('primary')
                self.stop_button = ui.button('停止监控', on_click=self.stop_monitoring).classes('secondary')
                self.test_alert_button = ui.button('测试告警', on_click=self.test_alert).classes('warning')
    
    def _start_auto_refresh(self):
        """启动自动刷新"""
        async def refresh_dashboard():
            while True:
                await asyncio.sleep(self.dashboard_refresh_interval)
                self._update_dashboard()
                ui.update()
        
        ui.timer(self.dashboard_refresh_interval, refresh_dashboard)
    
    async def start_monitoring(self):
        """开始监控"""
        await self.monitor.start_monitoring(duration_seconds=3600)  # 1小时
        ui.notify('监控已启动', type='positive')
    
    async def stop_monitoring(self):
        """停止监控"""
        self.monitor.stop_monitoring()
        ui.notify('监控已停止', type='warning')
    
    async def test_alert(self):
        """测试告警"""
        # 创建一个测试告警
        test_alert = Alert(
            id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            rule_name="测试告警",
            alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
            severity=AlertSeverity.WARNING,
            message="这是一个测试告警",
            timestamp=datetime.now(),
            metrics={'test': True}
        )
        
        await self.alert_manager._handle_alert(test_alert)
        ui.notify('测试告警已发送', type='info')
    
    def _update_dashboard(self):
        """更新仪表盘"""
        # 更新指标
        metrics_summary = self.monitor.get_metrics_summary()
        if metrics_summary:
            current_metrics = metrics_summary.get('current_metrics', {})
            
            self.cpu_label.text = f"{current_metrics.get('cpu_usage', 0):.1f}%"
            self.gpu_label.text = f"{current_metrics.get('gpu_utilization', 0):.1f}%"
            self.memory_label.text = f"{current_metrics.get('memory_usage', 0):.1f}%"
        
        # 更新告警状态
        alert_summary = self.alert_manager.get_alert_summary()
        active_alerts = self.alert_manager.get_active_alerts()
        
        self.alerts_label.text = str(alert_summary.get('active_alerts', 0))
        
        # 更新告警徽章
        critical_count = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        warning_count = len([a for a in active_alerts if a.severity == AlertSeverity.WARNING])
        info_count = len([a for a in active_alerts if a.severity == AlertSeverity.INFO])
        
        self.critical_alert_badge.text = str(critical_count)
        self.warning_alert_badge.text = str(warning_count)
        self.info_alert_badge.text = str(info_count)
        
        # 更新活跃告警列表
        self.active_alerts_list.clear()
        for alert in active_alerts[-10:]:  # 只显示最近10个
            with self.active_alerts_list:
                color = 'red' if alert.severity == AlertSeverity.CRITICAL else 'orange' if alert.severity == AlertSeverity.WARNING else 'blue'
                ui.badge(f"{alert.severity.value}: {alert.rule_name}", color=color).classes('q-mr-sm q-mb-sm')
        
        # 更新告警历史
        recent_alerts = self.alert_manager.alert_history[-50:]  # 最近50个告警
        rows = []
        for alert in reversed(recent_alerts[-20:]):  # 显示最近20个
            status = "已解决" if alert.resolved else "活跃"
            rows.append({
                'time': alert.timestamp.strftime('%H:%M:%S'),
                'rule': alert.rule_name,
                'severity': alert.severity.value,
                'message': alert.message[:50] + "..." if len(alert.message) > 50 else alert.message,
                'status': status
            })
        
        self.alert_history_table.rows = rows
```

---

## 📊 使用示例

```python
async def main():
    """完整监控示例"""
    
    # 1. 创建告警管理器
    alert_manager = AIAlertManager()
    
    # 2. 创建实时监控器
    monitor = AIRealtimeMonitor(alert_manager)
    
    # 3. 添加告警处理器
    email_handler = EmailAlertHandler(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your-email@gmail.com",
        password="your-password",
        recipients=["admin@example.com", "ops@example.com"]
    )
    
    webhook_handler = WebhookAlertHandler(
        webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    )
    
    log_handler = LogAlertHandler("ai_monitoring.log")
    
    alert_manager.add_alert_handler(email_handler)
    alert_manager.add_alert_handler(webhook_handler)
    alert_manager.add_alert_handler(log_handler)
    
    # 4. 添加自定义告警规则
    custom_rule = AlertRule(
        name="AI策略延迟过高",
        alert_type=AlertType.PERFORMANCE_DEGRADATION,
        severity=AlertSeverity.WARNING,
        threshold=0.5,  # 延迟超过0.5秒
        duration_seconds=60,
        enabled=True,
        description="AI策略计算延迟持续超过0.5秒"
    )
    
    alert_manager.add_alert_rule(custom_rule)
    
    # 5. 测试告警处理器连接
    print("🔍 测试告警处理器连接...")
    for i, handler in enumerate(alert_manager.alert_handlers):
        try:
            success = await handler.test_connection()
            print(f"  处理器 {i+1} ({handler.__class__.__name__}): {'✅ 成功' if success else '❌ 失败'}")
        except Exception as e:
            print(f"  处理器 {i+1} ({handler.__class__.__name__}): ❌ 异常 - {e}")
    
    # 6. 启动监控
    print("🚀 启动AI实时监控系统...")
    await monitor.start_monitoring(duration_seconds=300)  # 5分钟
    
    # 7. 输出监控报告
    print("\n📊 监控报告:")
    metrics_summary = monitor.get_metrics_summary()
    alert_summary = alert_manager.get_alert_summary()
    
    print("系统指标:")
    for key, value in metrics_summary.get('current_metrics', {}).items():
        print(f"  • {key}: {value}")
    
    print("\n告警统计:")
    for key, value in alert_summary.items():
        print(f"  • {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎯 Mystocks_nice集成

### 完整的NiceGUI监控页面

```python
from nicegui import app, ui
import asyncio

# 创建全局实例
alert_manager = AIAlertManager()
monitor = AIRealtimeMonitor(alert_manager)

# 添加处理器
alert_manager.add_alert_handler(LogAlertHandler("nicegui_alerts.log"))

@ui.page('/monitoring')
def monitoring_page():
    """监控页面路由"""
    dashboard = MonitoringDashboard(alert_manager, monitor)
    dashboard.create_monitoring_page()

@ui.page('/')
def main_page():
    """主页"""
    with ui.column().classes('w-full q-pa-lg items-center'):
        ui.label('🏠 MyStocks AI系统').classes('text-h3 text-primary q-mb-lg')
        
        with ui.row().classes('q-gutter-lg items-center justify-center'):
            ui.button('🔍 监控系统', on_click=lambda: ui.navigate.to('/monitoring')).classes('primary text-h6 q-pa-lg')
            ui.button('📊 策略分析', on_click=lambda: ui.navigate.to('/strategy')).classes('secondary text-h6 q-pa-lg')
            ui.button('⚡ GPU状态', on_click=lambda: ui.navigate.to('/gpu')).classes('accent text-h6 q-pa-lg')

# 启动应用
if __name__ == "__main__":
    ui.run(host='0.0.0.0', port=8080, title="MyStocks AI监控系统")
```

---

## 📚 最佳实践

### 1. 告警规则配置

```python
# 推荐的告警规则配置
RECOMMENDED_ALERT_RULES = [
    AlertRule(
        name="CPU使用率过高",
        alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
        severity=AlertSeverity.WARNING,
        threshold=80.0,
        duration_seconds=60,
        enabled=True,
        description="CPU使用率持续超过80%"
    ),
    AlertRule(
        name="GPU内存不足",
        alert_type=AlertType.GPU_MEMORY_HIGH,
        severity=AlertSeverity.CRITICAL,
        threshold=90.0,
        duration_seconds=30,
        enabled=True,
        description="GPU内存使用率超过90%"
    ),
    AlertRule(
        name="AI策略表现异常",
        alert_type=AlertType.STRATEGY_ANOMALY,
        severity=AlertSeverity.CRITICAL,
        threshold=0.4,
        duration_seconds=300,
        enabled=True,
        description="策略胜率持续低于40%"
    ),
    AlertRule(
        name="数据质量下降",
        alert_type=AlertType.DATA_QUALITY_ISSUE,
        severity=AlertSeverity.WARNING,
        threshold=0.85,
        duration_seconds=180,
        enabled=True,
        description="数据质量评分持续低于85%"
    )
]
```

### 2. 监控频率优化

```python
# 监控频率建议
MONITORING_CONFIG = {
    'high_frequency_metrics': {
        'interval': 1,  # 1秒
        'metrics': ['cpu_usage', 'gpu_utilization', 'memory_usage']
    },
    'medium_frequency_metrics': {
        'interval': 5,  # 5秒
        'metrics': ['ai_strategy_performance', 'trading_metrics']
    },
    'low_frequency_metrics': {
        'interval': 60,  # 1分钟
        'metrics': ['data_quality', 'system_health']
    }
}
```

### 3. 告警处理策略

```python
# 告警聚合和抑制
class AlertAggregationManager:
    """告警聚合管理器"""
    
    def __init__(self, aggregation_window: int = 300):  # 5分钟窗口
        self.aggregation_window = aggregation_window
        self.alert_groups = {}
    
    def should_suppress_alert(self, alert: Alert) -> bool:
        """判断是否应该抑制告警"""
        group_key = f"{alert.alert_type.value}_{alert.rule_name}"
        
        if group_key not in self.alert_groups:
            self.alert_groups[group_key] = []
        
        # 清理过期告警
        cutoff_time = datetime.now() - timedelta(seconds=self.aggregation_window)
        self.alert_groups[group_key] = [
            a for a in self.alert_groups[group_key] 
            if a.timestamp > cutoff_time
        ]
        
        # 检查是否已有活跃告警
        recent_alerts = self.alert_groups[group_key]
        if recent_alerts:
            return True  # 抑制重复告警
        
        # 记录新告警
        recent_alerts.append(alert)
        return False
```

---

**文档版本**: v1.0  
**更新时间**: 2025-11-16  
**维护者**: MyStocks开发团队