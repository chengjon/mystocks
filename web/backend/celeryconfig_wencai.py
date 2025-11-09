#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财功能Celery配置示例

将以下配置添加到现有的celeryconfig.py文件中

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

from celery.schedules import crontab

# ============================================================================
# 问财定时任务配置
# ============================================================================

# 添加到beat_schedule字典中
WENCAI_BEAT_SCHEDULE = {
    # 每日9:00自动刷新所有查询
    "wencai-refresh-all-daily": {
        "task": "wencai.scheduled_refresh_all",
        "schedule": crontab(hour=9, minute=0),  # 每天 09:00
        "args": (1,),  # pages=1
        "kwargs": {"active_only": True},
        "options": {
            "expires": 3600,  # 任务1小时后过期
        },
    },
    # 每日凌晨2:00清理30天前的旧数据
    "wencai-cleanup-old-data-daily": {
        "task": "wencai.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),  # 每天 02:00
        "args": (30,),  # days=30
        "kwargs": {"dry_run": False},
        "options": {
            "expires": 7200,  # 任务2小时后过期
        },
    },
    # 每小时获取统计信息（可选，用于监控）
    "wencai-stats-hourly": {
        "task": "wencai.stats",
        "schedule": crontab(minute=0),  # 每小时的0分
        "options": {
            "expires": 3600,
        },
    },
    # 每周一早上9:30刷新所有查询（多页数据）
    "wencai-refresh-all-weekly-full": {
        "task": "wencai.scheduled_refresh_all",
        "schedule": crontab(day_of_week=1, hour=9, minute=30),  # 周一
        "args": (3,),  # pages=3，获取更多数据
        "kwargs": {"active_only": True},
        "options": {
            "expires": 7200,
        },
    },
}


# ============================================================================
# 使用说明
# ============================================================================
"""
将上述配置添加到现有的celeryconfig.py中：

1. 找到beat_schedule配置：
   beat_schedule = {
       # ... 现有任务
   }

2. 添加问财任务：
   beat_schedule.update(WENCAI_BEAT_SCHEDULE)

或者直接合并到beat_schedule字典中。

3. 重启Celery服务：
   systemctl restart celery-beat
   systemctl restart celery-worker
"""


# ============================================================================
# 完整示例
# ============================================================================
"""
from celery import Celery
from celery.schedules import crontab

app = Celery('mystocks')
app.config_from_object('celeryconfig')

# Beat调度配置
beat_schedule = {
    # ... 现有任务

    # 问财定时任务
    'wencai-refresh-all-daily': {
        'task': 'wencai.scheduled_refresh_all',
        'schedule': crontab(hour=9, minute=0),
        'args': (1,),
        'kwargs': {'active_only': True},
    },

    'wencai-cleanup-old-data-daily': {
        'task': 'wencai.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
        'args': (30,),
        'kwargs': {'dry_run': False},
    },
}

app.conf.beat_schedule = beat_schedule
"""


# ============================================================================
# 任务队列配置（可选）
# ============================================================================
"""
如果需要将问财任务分配到专用队列：

from kombu import Queue

task_routes = {
    'wencai.*': {
        'queue': 'wencai',
        'routing_key': 'wencai',
    },
}

task_queues = (
    Queue('wencai', routing_key='wencai'),
)

启动专用worker：
celery -A app.celery_app worker -Q wencai -l info
"""


# ============================================================================
# 任务配置（可选）
# ============================================================================
"""
针对问财任务的特定配置：

task_annotations = {
    'wencai.refresh_query': {
        'rate_limit': '10/m',  # 每分钟最多10次
        'time_limit': 300,     # 5分钟超时
        'soft_time_limit': 240,  # 4分钟软超时
    },
    'wencai.scheduled_refresh_all': {
        'time_limit': 1800,    # 30分钟超时
        'soft_time_limit': 1500,  # 25分钟软超时
    },
}
"""
