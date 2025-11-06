"""
Redis队列工具模块
Redis Queue Utility Module
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisQueue:
    """Redis队列管理器"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client = None
        self.task_queues = {
            'backtest': 'gpu:backtest:queue',
            'realtime': 'gpu:realtime:queue',
            'ml': 'gpu:ml:queue',
            'optimization': 'gpu:optimization:queue',
            'risk_control': 'gpu:risk:queue',
            'high_freq': 'gpu:hft:queue'
        }
        self.result_queues = {
            'backtest': 'gpu:backtest:results',
            'realtime': 'gpu:realtime:results',
            'ml': 'gpu:ml:results',
            'optimization': 'gpu:optimization:results',
            'risk_control': 'gpu:risk:results',
            'high_freq': 'gpu:hft:results'
        }
        self.status_keys = {
            'backtest': 'gpu:backtest:status',
            'realtime': 'gpu:realtime:status',
            'ml': 'gpu:ml:status',
            'optimization': 'gpu:optimization:status',
            'risk_control': 'gpu:risk:status',
            'high_freq': 'gpu:hft:status'
        }

    def connect(self) -> bool:
        """连接到Redis服务器"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info(f"Redis连接成功: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            return False

    def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis连接已断开")

    def enqueue_task(self, queue_type: str, task_data: Dict[str, Any]) -> str:
        """添加任务到队列"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        queue_key = self.task_queues[queue_type]

        # 添加任务ID和时间戳
        task_id = f"{queue_type}_{int(time.time())}_{hash(task_data.get('task_name', ''))}"
        task_data['task_id'] = task_id
        task_data['created_at'] = datetime.now().isoformat()
        task_data['status'] = 'pending'
        task_data['retry_count'] = 0

        try:
            # 将任务添加到队列
            task_json = json.dumps(task_data, ensure_ascii=False)
            self.redis_client.lpush(queue_key, task_json)

            # 设置任务状态
            status_key = self.status_keys[queue_type]
            self.redis_client.hset(status_key, task_id, json.dumps({
                'task_id': task_id,
                'status': 'pending',
                'created_at': task_data['created_at'],
                'updated_at': task_data['created_at']
            }))

            logger.info(f"任务已添加到队列 {queue_type}: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            raise

    def dequeue_task(self, queue_type: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """从队列中获取任务"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        queue_key = self.task_queues[queue_type]

        try:
            # 使用BRPOP获取任务（阻塞式）
            result = self.redis_client.brpop(queue_key, timeout=timeout)
            if result:
                _, task_json = result
                task_data = json.loads(task_json)

                # 更新任务状态为处理中
                self.update_task_status(queue_type, task_data['task_id'], 'processing')

                logger.info(f"获取任务: {task_data['task_id']}")
                return task_data
            return None
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None

    def update_task_status(self, queue_type: str, task_id: str, status: str,
                           result_data: Optional[Dict] = None):
        """更新任务状态"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        status_key = self.status_keys[queue_type]

        try:
            status_data = {
                'task_id': task_id,
                'status': status,
                'updated_at': datetime.now().isoformat()
            }

            # 如果有结果数据，添加到状态中
            if result_data:
                status_data['result'] = result_data
                status_data['completed_at'] = status_data['updated_at']

            # 更新状态
            self.redis_client.hset(status_key, task_id, json.dumps(status_data))

            # 如果任务完成，添加到结果队列
            if status in ['completed', 'failed']:
                result_queue = self.result_queues[queue_type]
                self.redis_client.lpush(result_queue, json.dumps({
                    'task_id': task_id,
                    'status': status,
                    'result_data': result_data,
                    'completed_at': status_data['updated_at']
                }))

            logger.info(f"任务 {task_id} 状态更新为: {status}")
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")

    def get_task_status(self, queue_type: str, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        status_key = self.status_keys[queue_type]

        try:
            status_json = self.redis_client.hget(status_key, task_id)
            if status_json:
                return json.loads(status_json)
            return None
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return None

    def get_queue_length(self, queue_type: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """获取队列长度"""
        try:
            if queue_type:
                if queue_type not in self.task_queues:
                    raise ValueError(f"不支持的队列类型: {queue_type}")
                queue_key = self.task_queues[queue_type]
                return self.redis_client.llen(queue_key)
            else:
                # 获取所有队列长度
                lengths = {}
                for q_type, q_key in self.task_queues.items():
                    lengths[q_type] = self.redis_client.llen(q_key)
                return lengths
        except Exception as e:
            logger.error(f"获取队列长度失败: {e}")
            return {} if queue_type is None else 0

    def get_pending_tasks(self, queue_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待处理任务列表"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        status_key = self.status_keys[queue_type]

        try:
            # 获取状态为pending的任务
            all_statuses = self.redis_client.hgetall(status_key)
            pending_tasks = []

            for task_id, status_json in all_statuses.items():
                status_data = json.loads(status_json)
                if status_data.get('status') == 'pending':
                    pending_tasks.append(status_data)
                    if len(pending_tasks) >= limit:
                        break

            return pending_tasks
        except Exception as e:
            logger.error(f"获取待处理任务失败: {e}")
            return []

    def get_task_results(self, queue_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取任务结果"""
        if queue_type not in self.result_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        result_queue = self.result_queues[queue_type]

        try:
            # 获取最近的结果
            results = []
            for i in range(min(limit, self.redis_client.llen(result_queue))):
                result_json = self.redis_client.lindex(result_queue, i)
                if result_json:
                    results.append(json.loads(result_json))
            return results
        except Exception as e:
            logger.error(f"获取任务结果失败: {e}")
            return []

    def cleanup_old_tasks(self, queue_type: str, days: int = 7):
        """清理旧任务"""
        if queue_type not in self.task_queues:
            raise ValueError(f"不支持的队列类型: {queue_type}")

        status_key = self.status_keys[queue_type]
        cutoff_time = datetime.now() - timedelta(days=days)

        try:
            # 获取所有任务状态
            all_statuses = self.redis_client.hgetall(status_key)
            tasks_to_remove = []

            for task_id, status_json in all_statuses.items():
                status_data = json.loads(status_json)
                created_time = datetime.fromisoformat(status_data['created_at'])

                # 删除超过指定天数的已完成任务
                if created_time < cutoff_time and status_data.get('status') in ['completed', 'failed']:
                    tasks_to_remove.append(task_id)

            # 批量删除
            if tasks_to_remove:
                self.redis_client.hdel(status_key, *tasks_to_remove)
                logger.info(f"清理了 {len(tasks_to_remove)} 个旧任务")
        except Exception as e:
            logger.error(f"清理旧任务失败: {e}")

    def get_queue_statistics(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'queues': {},
                'total_pending': 0,
                'total_processing': 0,
                'total_completed': 0,
                'total_failed': 0
            }

            for queue_type in self.task_queues.keys():
                # 获取队列长度
                queue_length = self.get_queue_length(queue_type)

                # 获取状态统计
                status_key = self.status_keys[queue_type]
                all_statuses = self.redis_client.hgetall(status_key)

                pending = 0
                processing = 0
                completed = 0
                failed = 0

                for status_json in all_statuses.values():
                    status_data = json.loads(status_json)
                    status = status_data.get('status', 'unknown')

                    if status == 'pending':
                        pending += 1
                    elif status == 'processing':
                        processing += 1
                    elif status == 'completed':
                        completed += 1
                    elif status == 'failed':
                        failed += 1

                stats['queues'][queue_type] = {
                    'queue_length': queue_length,
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'failed': failed
                }

                stats['total_pending'] += pending
                stats['total_processing'] += processing
                stats['total_completed'] += completed
                stats['total_failed'] += failed

            return stats
        except Exception as e:
            logger.error(f"获取队列统计失败: {e}")
            return {}

    def monitor_queue_health(self) -> Dict[str, Any]:
        """监控队列健康状态"""
        try:
            health = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'issues': [],
                'queue_status': {}
            }

            for queue_type in self.task_queues.keys():
                queue_length = self.get_queue_length(queue_type)

                # 检查队列长度是否异常
                if queue_length > 1000:
                    health['issues'].append(f"{queue_type}队列积压严重: {queue_length}个任务")
                    health['overall_status'] = 'warning'

                # 检查处理中的任务数量
                processing_count = 0
                status_key = self.status_keys[queue_type]
                all_statuses = self.redis_client.hgetall(status_key)

                for status_json in all_statuses.values():
                    status_data = json.loads(status_json)
                    if status_data.get('status') == 'processing':
                        processing_count += 1

                # 检查是否有长时间运行的任务
                for status_json in all_statuses.values():
                    status_data = json.loads(status_json)
                    if status_data.get('status') == 'processing':
                        created_time = datetime.fromisoformat(status_data['created_at'])
                        if datetime.now() - created_time > timedelta(hours=1):
                            health['issues'].append(f"{queue_type}有长时间运行的任务")
                            health['overall_status'] = 'warning'
                            break

                health['queue_status'][queue_type] = {
                    'length': queue_length,
                    'processing': processing_count,
                    'healthy': queue_length <= 1000 and processing_count <= 10
                }

            return health
        except Exception as e:
            logger.error(f"监控队列健康失败: {e}")
            return {'overall_status': 'error', 'error': str(e)}