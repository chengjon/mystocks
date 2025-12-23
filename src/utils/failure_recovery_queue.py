"""
故障恢复队列

基于SQLite的Outbox持久化队列,用于数据库故障时的数据缓冲和重试。

创建日期: 2025-10-11
版本: 1.0.0
"""

import sqlite3
import json
from typing import Dict, Any


class FailureRecoveryQueue:
    """
    故障恢复队列

    当目标数据库不可用时,将数据持久化到本地SQLite队列,
    待数据库恢复后自动重试。
    """

    def __init__(self, db_path: str = "/tmp/mystocks_recovery_queue.db"):
        """
        初始化队列

        Args:
            db_path: SQLite数据库文件路径
        """
        import os

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化SQLite数据库表"""
        conn = sqlite3.connect(self.db_path, timeout=10.0, isolation_level="IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS outbox_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                classification TEXT NOT NULL,
                target_database TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending'
            )
        """
        )

        conn.commit()
        conn.close()

    def enqueue(self, classification: str, target_database: str, data: Dict[str, Any]):
        """
        将失败的数据操作加入队列

        Args:
            classification: 数据分类
            target_database: 目标数据库
            data: 数据内容 (将转为JSON)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO outbox_queue (classification, target_database, data_json)
            VALUES (?, ?, ?)
        """,
            (classification, target_database, json.dumps(data)),
        )

        conn.commit()
        conn.close()

    def get_pending_items(self, limit: int = 100):
        """
        获取待重试的队列项

        Args:
            limit: 最大返回数量

        Returns:
            待处理的队列项列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, classification, target_database, data_json
            FROM outbox_queue
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT ?
        """,
            (limit,),
        )

        items = cursor.fetchall()
        conn.close()

        return items
