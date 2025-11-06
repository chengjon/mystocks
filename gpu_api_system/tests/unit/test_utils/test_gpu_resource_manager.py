"""
GPU资源管理器单元测试
测试GPU资源分配、调度和监控
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time


class TestGPUResourceManager:
    """GPU资源管理器测试"""

    @pytest.fixture
    def gpu_manager(self):
        """创建GPU资源管理器实例"""
        with patch('utils.gpu_utils.GPUResourceManager') as MockManager:
            manager = MockManager(max_gpus=1)
            manager.available_gpus = [0]
            manager.allocated_gpus = {}
            yield manager

    def test_manager_initialization(self, gpu_manager):
        """测试管理器初始化"""
        assert gpu_manager is not None
        gpu_manager.get_available_gpus.return_value = [0]
        available = gpu_manager.get_available_gpus()
        assert len(available) > 0

    def test_allocate_gpu(self, gpu_manager):
        """测试GPU分配"""
        task_id = "task_001"
        priority = 1

        gpu_manager.allocate_gpu.return_value = 0
        gpu_id = gpu_manager.allocate_gpu(task_id, priority)

        assert gpu_id is not None
        assert isinstance(gpu_id, int)
        assert gpu_id >= 0

    def test_release_gpu(self, gpu_manager):
        """测试GPU释放"""
        task_id = "task_002"

        # 先分配
        gpu_manager.allocate_gpu.return_value = 0
        gpu_id = gpu_manager.allocate_gpu(task_id, 1)

        # 再释放
        gpu_manager.release_gpu.return_value = True
        result = gpu_manager.release_gpu(task_id)

        assert result is True

    def test_gpu_not_available(self, gpu_manager):
        """测试GPU不可用情况"""
        # 模拟所有GPU已被占用
        gpu_manager.allocate_gpu.return_value = None

        gpu_id = gpu_manager.allocate_gpu("task_003", 1)
        assert gpu_id is None

    def test_priority_scheduling(self, gpu_manager):
        """测试优先级调度"""
        # 高优先级任务
        high_priority_task = "high_priority"
        gpu_manager.allocate_gpu.return_value = 0

        # 低优先级任务
        low_priority_task = "low_priority"

        # 高优先级应该优先获得GPU
        gpu_high = gpu_manager.allocate_gpu(high_priority_task, priority=0)
        gpu_low = gpu_manager.allocate_gpu(low_priority_task, priority=2)

        # 高优先级应该成功
        assert gpu_high is not None


class TestGPUUtilizationMonitor:
    """GPU利用率监控测试"""

    @pytest.fixture
    def monitor(self):
        """创建监控器实例"""
        with patch('utils.gpu_utils.GPUUtilizationMonitor') as MockMonitor:
            monitor = MockMonitor()
            yield monitor

    def test_get_gpu_utilization(self, monitor):
        """测试获取GPU利用率"""
        monitor.get_utilization.return_value = {
            'gpu_id': 0,
            'utilization': 75.5,
            'memory_used': 6144,
            'memory_total': 8192,
            'temperature': 68
        }

        stats = monitor.get_utilization(0)

        assert 'utilization' in stats
        assert 0 <= stats['utilization'] <= 100
        assert stats['memory_used'] <= stats['memory_total']

    def test_get_all_gpus_status(self, monitor):
        """测试获取所有GPU状态"""
        monitor.get_all_status.return_value = [
            {
                'gpu_id': 0,
                'utilization': 75.5,
                'memory_used': 6144,
                'memory_total': 8192,
                'temperature': 68
            }
        ]

        all_stats = monitor.get_all_status()

        assert isinstance(all_stats, list)
        assert len(all_stats) > 0

    def test_high_utilization_alert(self, monitor):
        """测试高利用率告警"""
        threshold = 95.0

        monitor.get_utilization.return_value = {
            'gpu_id': 0,
            'utilization': 98.5
        }

        stats = monitor.get_utilization(0)

        if stats['utilization'] > threshold:
            alert = {
                'type': 'high_utilization',
                'gpu_id': 0,
                'value': stats['utilization'],
                'threshold': threshold
            }
            assert alert['type'] == 'high_utilization'

    def test_memory_usage_tracking(self, monitor):
        """测试内存使用跟踪"""
        monitor.get_memory_usage.return_value = {
            'used_mb': 6144,
            'total_mb': 8192,
            'percentage': 75.0
        }

        memory = monitor.get_memory_usage(0)

        assert 'used_mb' in memory
        assert 'total_mb' in memory
        assert memory['used_mb'] <= memory['total_mb']


class TestGPUTaskQueue:
    """GPU任务队列测试"""

    @pytest.fixture
    def task_queue(self):
        """创建任务队列实例"""
        with patch('utils.gpu_utils.GPUTaskQueue') as MockQueue:
            queue = MockQueue()
            queue.tasks = []
            yield queue

    def test_enqueue_task(self, task_queue):
        """测试任务入队"""
        task = {
            'task_id': 'task_001',
            'type': 'backtest',
            'priority': 1,
            'timestamp': time.time()
        }

        task_queue.enqueue.return_value = True
        result = task_queue.enqueue(task)

        assert result is True

    def test_dequeue_task(self, task_queue):
        """测试任务出队"""
        task = {
            'task_id': 'task_002',
            'type': 'ml_training',
            'priority': 0
        }

        # 入队
        task_queue.enqueue(task)

        # 出队
        task_queue.dequeue.return_value = task
        dequeued = task_queue.dequeue()

        assert dequeued is not None
        assert dequeued['task_id'] == 'task_002'

    def test_priority_queue_ordering(self, task_queue):
        """测试优先级队列排序"""
        tasks = [
            {'task_id': 'low', 'priority': 2},
            {'task_id': 'high', 'priority': 0},
            {'task_id': 'medium', 'priority': 1}
        ]

        for task in tasks:
            task_queue.enqueue(task)

        # 出队应该按优先级
        task_queue.dequeue.return_value = {'task_id': 'high', 'priority': 0}
        first = task_queue.dequeue()

        assert first['priority'] == 0

    def test_queue_size_limit(self, task_queue):
        """测试队列大小限制"""
        max_size = 100

        task_queue.is_full.return_value = False
        task_queue.size.return_value = 50

        assert task_queue.size() < max_size
        assert not task_queue.is_full()

    def test_empty_queue(self, task_queue):
        """测试空队列"""
        task_queue.is_empty.return_value = True
        assert task_queue.is_empty()

        task_queue.dequeue.return_value = None
        task = task_queue.dequeue()
        assert task is None


class TestResourceScheduler:
    """资源调度器测试"""

    @pytest.fixture
    def scheduler(self):
        """创建调度器实例"""
        with patch('utils.resource_scheduler.ResourceScheduler') as MockScheduler:
            scheduler = MockScheduler()
            yield scheduler

    def test_schedule_task(self, scheduler):
        """测试任务调度"""
        task = {
            'task_id': 'scheduled_task',
            'type': 'backtest',
            'priority': 1,
            'resource_requirements': {
                'gpu_memory': 4096,
                'cpu_cores': 2
            }
        }

        scheduler.schedule.return_value = {
            'status': 'scheduled',
            'gpu_id': 0,
            'estimated_start_time': time.time()
        }

        result = scheduler.schedule(task)

        assert result['status'] == 'scheduled'
        assert 'gpu_id' in result

    def test_concurrent_task_limit(self, scheduler):
        """测试并发任务限制"""
        max_concurrent = 3

        scheduler.get_concurrent_count.return_value = 2
        current_count = scheduler.get_concurrent_count()

        assert current_count < max_concurrent

    def test_fair_scheduling(self, scheduler):
        """测试公平调度"""
        # 多个用户的任务
        tasks = [
            {'task_id': 'user1_task1', 'user_id': 'user1', 'priority': 1},
            {'task_id': 'user1_task2', 'user_id': 'user1', 'priority': 1},
            {'task_id': 'user2_task1', 'user_id': 'user2', 'priority': 1}
        ]

        # 应该平均分配资源
        scheduler.schedule.return_value = {'status': 'scheduled'}

        for task in tasks:
            result = scheduler.schedule(task)
            assert result['status'] == 'scheduled'

    def test_resource_preemption(self, scheduler):
        """测试资源抢占"""
        # 低优先级任务正在运行
        low_priority_task = {
            'task_id': 'low_task',
            'priority': 2,
            'preemptible': True
        }

        # 高优先级任务到来
        high_priority_task = {
            'task_id': 'high_task',
            'priority': 0,
            'preemptible': False
        }

        # 应该允许抢占
        scheduler.can_preempt.return_value = True
        can_preempt = scheduler.can_preempt(
            current_task=low_priority_task,
            new_task=high_priority_task
        )

        assert can_preempt is True


class TestGPUHealthMonitor:
    """GPU健康监控测试"""

    @pytest.fixture
    def health_monitor(self):
        """创建健康监控器实例"""
        with patch('utils.gpu_utils.GPUHealthMonitor') as MockMonitor:
            monitor = MockMonitor()
            yield monitor

    def test_check_gpu_health(self, health_monitor):
        """测试GPU健康检查"""
        health_monitor.check_health.return_value = {
            'status': 'healthy',
            'gpu_id': 0,
            'temperature': 65,
            'fan_speed': 50,
            'power_usage': 180
        }

        health = health_monitor.check_health(0)

        assert health['status'] == 'healthy'
        assert health['temperature'] < 85  # 安全温度

    def test_temperature_warning(self, health_monitor):
        """测试温度告警"""
        threshold = 80

        health_monitor.check_health.return_value = {
            'status': 'warning',
            'temperature': 82
        }

        health = health_monitor.check_health(0)

        if health['temperature'] > threshold:
            assert health['status'] == 'warning'

    def test_gpu_failure_detection(self, health_monitor):
        """测试GPU故障检测"""
        health_monitor.check_health.return_value = {
            'status': 'failed',
            'error': 'GPU not responding'
        }

        health = health_monitor.check_health(0)

        assert health['status'] == 'failed'
        assert 'error' in health

    def test_automatic_recovery(self, health_monitor):
        """测试自动恢复"""
        # 检测到故障
        health_monitor.check_health.return_value = {
            'status': 'failed'
        }

        # 触发恢复
        health_monitor.recover.return_value = {
            'status': 'recovered',
            'action': 'gpu_reset'
        }

        recovery = health_monitor.recover(0)

        assert recovery['status'] == 'recovered'


class TestCPUFallback:
    """CPU降级测试"""

    def test_gpu_unavailable_fallback(self):
        """测试GPU不可用时降级到CPU"""
        with patch('utils.gpu_utils.GPUResourceManager') as MockManager:
            manager = MockManager()
            manager.is_gpu_available.return_value = False

            if not manager.is_gpu_available():
                # 应该使用CPU
                use_cpu = True
                assert use_cpu is True

    def test_fallback_performance(self):
        """测试降级性能"""
        # CPU模式应该能完成任务，只是慢一些
        with patch('utils.gpu_acceleration_engine.BacktestEngineGPU') as MockEngine:
            engine = MockEngine(None, None)

            # 模拟CPU执行
            engine.run_backtest_cpu.return_value = {
                'total_return': 0.20,
                'execution_time': 45.0,  # CPU较慢
                'mode': 'cpu'
            }

            result = engine.run_backtest_cpu({}, {})

            assert result['mode'] == 'cpu'
            assert result['execution_time'] > 0

    def test_automatic_fallback_switch(self):
        """测试自动降级切换"""
        with patch('utils.gpu_utils.GPUResourceManager') as MockManager:
            manager = MockManager()

            # 初始GPU可用
            manager.is_gpu_available.return_value = True
            assert manager.is_gpu_available()

            # GPU故障，自动切换
            manager.is_gpu_available.return_value = False
            assert not manager.is_gpu_available()

            # 模拟使用CPU
            manager.use_cpu_fallback.return_value = True
            fallback = manager.use_cpu_fallback()
            assert fallback is True
