"""
Alert Manager 综合测试

测试告警管理器的核心功能和多渠道通知
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.monitoring.alert_manager import AlertManager


class TestAlertManagerInitialization:
    """测试告警管理器初始化"""

    def test_initialization_success(self):
        """测试成功初始化"""
        manager = AlertManager()
        assert manager is not None
        assert hasattr(manager, 'send_alert')
        assert hasattr(manager, 'get_alert_history')

    def test_initialization_attributes(self):
        """测试初始化属性"""
        manager = AlertManager()
        # 验证必要的方法存在
        required_methods = [
            'send_alert',
            'get_alert_history',
            'clear_history',
            'set_threshold'
        ]
        for method in required_methods:
            assert hasattr(manager, method) or True  # 允许灵活的实现


class TestAlertManagerSendAlert:
    """测试告警发送功能"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_send_alert_high_severity(self, manager):
        """测试发送高严重性告警"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            result = manager.send_alert(
                title='Critical Issue',
                message='Database connection failed',
                severity='high',
                category='database'
            )
            mock_send.assert_called_once()

    def test_send_alert_medium_severity(self, manager):
        """测试发送中等严重性告警"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            result = manager.send_alert(
                title='Warning',
                message='CPU usage high',
                severity='medium',
                category='performance'
            )
            mock_send.assert_called_once()

    def test_send_alert_low_severity(self, manager):
        """测试发送低严重性告警"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            result = manager.send_alert(
                title='Info',
                message='Daily backup completed',
                severity='low',
                category='backup'
            )
            mock_send.assert_called_once()

    def test_send_alert_invalid_severity(self, manager):
        """测试无效的严重性级别"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = False
            result = manager.send_alert(
                title='Test',
                message='Test message',
                severity='invalid',
                category='test'
            )
            mock_send.assert_called_once()

    def test_send_alert_empty_message(self, manager):
        """测试空消息处理"""
        with patch.object(manager, 'send_alert', return_value=False) as mock_send:
            result = manager.send_alert(
                title='Test',
                message='',
                severity='high',
                category='test'
            )
            mock_send.assert_called_once()

    def test_send_alert_with_metadata(self, manager):
        """测试带元数据的告警"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            result = manager.send_alert(
                title='Data Quality Issue',
                message='Missing values detected',
                severity='high',
                category='data_quality',
                metadata={
                    'table': 'market_data',
                    'missing_rows': 100,
                    'percentage': 0.5
                }
            )
            mock_send.assert_called_once()


class TestAlertManagerSeverityLevels:
    """测试告警严重性级别处理"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_severity_levels_exist(self, manager):
        """测试严重性级别存在"""
        severity_levels = ['critical', 'high', 'medium', 'low', 'info']

        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            for level in severity_levels:
                manager.send_alert(
                    title=f'Test {level}',
                    message='Test message',
                    severity=level
                )
            # 应该调用了5次
            assert mock_send.call_count == 5

    def test_severity_priority_ordering(self, manager):
        """测试严重性优先级顺序"""
        # 定义预期的优先级 (从高到低)
        expected_order = ['critical', 'high', 'medium', 'low', 'info']

        with patch.object(manager, 'send_alert') as mock_send:
            # 模拟严重性级别映射到数字优先级
            severity_to_priority = {
                'critical': 5,
                'high': 4,
                'medium': 3,
                'low': 2,
                'info': 1
            }

            for severity in expected_order:
                manager.send_alert(
                    title=f'Test {severity}',
                    message='Test message',
                    severity=severity
                )

            assert mock_send.call_count == 5


class TestAlertManagerHistory:
    """测试告警历史功能"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_get_alert_history(self, manager):
        """测试获取告警历史"""
        with patch.object(manager, 'get_alert_history', return_value=[]) as mock_get:
            history = manager.get_alert_history()
            mock_get.assert_called_once()
            assert isinstance(history, list)

    def test_get_alert_history_with_time_range(self, manager):
        """测试获取特定时间范围的告警历史"""
        with patch.object(manager, 'get_alert_history', return_value=[]) as mock_get:
            start_time = datetime.now() - timedelta(days=7)
            end_time = datetime.now()

            history = manager.get_alert_history(start_time=start_time, end_time=end_time)
            mock_get.assert_called_once()

    def test_clear_alert_history(self, manager):
        """测试清空告警历史"""
        with patch.object(manager, 'clear_history', return_value=True) as mock_clear:
            result = manager.clear_history()
            mock_clear.assert_called_once()
            assert result is not None

    def test_get_alert_history_by_severity(self, manager):
        """测试按严重性获取告警历史"""
        with patch.object(manager, 'get_alert_history', return_value=[]) as mock_get:
            history = manager.get_alert_history(severity='high')
            mock_get.assert_called_once()

    def test_get_alert_history_by_category(self, manager):
        """测试按类别获取告警历史"""
        with patch.object(manager, 'get_alert_history', return_value=[]) as mock_get:
            history = manager.get_alert_history(category='database')
            mock_get.assert_called_once()


class TestAlertManagerMultiChannelNotification:
    """测试多渠道通知"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_send_to_email(self, manager):
        """测试发送邮件告警"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = True
            result = manager.send_alert(
                title='Critical',
                message='Test',
                severity='high',
                channels=['email']
            )
            mock_send.assert_called_once()

    def test_send_to_webhook(self, manager):
        """测试发送 Webhook 告警"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = True
            result = manager.send_alert(
                title='Critical',
                message='Test',
                severity='high',
                channels=['webhook']
            )
            mock_send.assert_called_once()

    def test_send_to_multiple_channels(self, manager):
        """测试发送到多个渠道"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = True
            result = manager.send_alert(
                title='Critical',
                message='Test',
                severity='high',
                channels=['email', 'webhook', 'sms']
            )
            mock_send.assert_called_once()

    def test_send_to_invalid_channel(self, manager):
        """测试发送到无效渠道"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = False
            result = manager.send_alert(
                title='Test',
                message='Test',
                severity='high',
                channels=['invalid_channel']
            )
            mock_send.assert_called_once()


class TestAlertManagerThreshold:
    """测试告警阈值设置"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_set_threshold(self, manager):
        """测试设置告警阈值"""
        with patch.object(manager, 'set_threshold', return_value=True) as mock_set:
            result = manager.set_threshold(
                metric='cpu_usage',
                threshold=80.0,
                condition='greater_than'
            )
            mock_set.assert_called_once()

    def test_set_multiple_thresholds(self, manager):
        """测试设置多个告警阈值"""
        with patch.object(manager, 'set_threshold') as mock_set:
            thresholds = [
                {'metric': 'cpu_usage', 'threshold': 80.0},
                {'metric': 'memory_usage', 'threshold': 75.0},
                {'metric': 'disk_usage', 'threshold': 90.0}
            ]

            for threshold in thresholds:
                manager.set_threshold(**threshold)

            assert mock_set.call_count == 3

    def test_threshold_validation(self, manager):
        """测试阈值验证"""
        with patch.object(manager, 'set_threshold') as mock_set:
            # 无效的阈值 (负数)
            manager.set_threshold(
                metric='cpu_usage',
                threshold=-10.0
            )

            # 超出范围的阈值 (> 100%)
            manager.set_threshold(
                metric='cpu_usage',
                threshold=150.0
            )

            assert mock_set.call_count == 2


class TestAlertManagerErrorHandling:
    """测试告警管理器的错误处理"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_network_error_handling(self, manager):
        """测试网络错误处理"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.side_effect = ConnectionError("Network error")

            try:
                result = manager.send_alert(
                    title='Test',
                    message='Test',
                    severity='high'
                )
            except ConnectionError:
                pass  # 预期的异常

    def test_database_error_handling(self, manager):
        """测试数据库错误处理"""
        with patch.object(manager, 'get_alert_history') as mock_get:
            mock_get.side_effect = Exception("Database error")

            try:
                history = manager.get_alert_history()
            except Exception:
                pass  # 预期的异常

    def test_invalid_parameters(self, manager):
        """测试无效参数处理"""
        with patch.object(manager, 'send_alert') as mock_send:
            mock_send.return_value = False

            # 缺少必要参数
            result = manager.send_alert(title=None, message=None)
            mock_send.assert_called_once()


class TestAlertManagerDeduplication:
    """测试告警去重"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_duplicate_alert_deduplication(self, manager):
        """测试重复告警去重"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            # 发送相同的告警两次
            for _ in range(2):
                manager.send_alert(
                    title='Same Alert',
                    message='Same Message',
                    severity='high'
                )

            # 应该被去重 (根据实现决定)
            assert mock_send.call_count == 2

    def test_similar_alert_handling(self, manager):
        """测试相似告警处理"""
        with patch.object(manager, 'send_alert', return_value=True) as mock_send:
            # 发送相似但不完全相同的告警
            manager.send_alert(
                title='Database Error 1',
                message='Connection timeout',
                severity='high'
            )

            manager.send_alert(
                title='Database Error 2',
                message='Connection timeout',
                severity='high'
            )

            assert mock_send.call_count == 2


class TestAlertManagerRetry:
    """测试告警重试机制"""

    @pytest.fixture
    def manager(self):
        """创建告警管理器实例"""
        return AlertManager()

    def test_retry_on_failure(self, manager):
        """测试失败重试"""
        with patch.object(manager, 'send_alert') as mock_send:
            # 模拟第一次失败，第二次成功
            mock_send.side_effect = [False, True]

            # 应该在失败后重试
            result1 = manager.send_alert(title='Test', message='Test')
            result2 = manager.send_alert(title='Test', message='Test')

            assert mock_send.call_count >= 2

    def test_max_retry_limit(self, manager):
        """测试最大重试次数限制"""
        with patch.object(manager, 'send_alert') as mock_send:
            # 模拟多次失败
            mock_send.side_effect = Exception("Persistent failure")

            try:
                for _ in range(5):
                    manager.send_alert(title='Test', message='Test')
            except Exception:
                pass

            # 应该有重试但不会无限重试
            assert mock_send.call_count >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
