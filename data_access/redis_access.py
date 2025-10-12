"""
Redis数据访问层

封装Redis的所有操作。
专门处理实时热数据(实时持仓/实时账户/订单队列)。

创建日期: 2025-10-11
版本: 1.0.0
"""

import json
import pandas as pd
from typing import Optional, Dict, Any, List, Union
from datetime import timedelta

from db_manager.connection_manager import get_connection_manager


class RedisDataAccess:
    """
    Redis数据访问类

    提供实时热数据的存储和查询接口:
    - String操作 (简单键值对)
    - Hash操作 (实时持仓/账户)
    - List操作 (订单队列)
    - Set操作 (标的集合)
    - SortedSet操作 (排序队列)
    - TTL过期管理
    """

    def __init__(self):
        """初始化Redis连接"""
        self.conn_manager = get_connection_manager()
        self.redis = None

    def _get_connection(self):
        """获取Redis连接(懒加载)"""
        if self.redis is None:
            self.redis = self.conn_manager.get_redis_connection()
        return self.redis

    # ==================== String操作 ====================

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置键值对

        Args:
            key: 键
            value: 值 (自动JSON序列化)
            ttl: 过期时间(秒) (None表示不过期)

        Example:
            set('position:600000.SH', {'quantity': 1000, 'cost': 15.5}, ttl=300)
        """
        redis = self._get_connection()

        # 自动JSON序列化
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)

        if ttl:
            redis.setex(key, ttl, value)
        else:
            redis.set(key, value)

    def get(self, key: str) -> Optional[Any]:
        """
        获取键值

        Args:
            key: 键

        Returns:
            值 (自动JSON反序列化) 或 None

        Example:
            position = get('position:600000.SH')
        """
        redis = self._get_connection()
        value = redis.get(key)

        if value is None:
            return None

        # 尝试JSON反序列化
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def delete(self, *keys: str) -> int:
        """
        删除键

        Args:
            keys: 键列表

        Returns:
            删除的键数量

        Example:
            delete('position:600000.SH', 'position:000001.SZ')
        """
        redis = self._get_connection()
        return redis.delete(*keys)

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        redis = self._get_connection()
        return redis.exists(key) > 0

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 键
            ttl: 过期时间(秒)

        Returns:
            设置是否成功
        """
        redis = self._get_connection()
        return redis.expire(key, ttl)

    # ==================== Hash操作 ====================

    def hset(self, key: str, field: str, value: Any):
        """
        设置Hash字段

        Args:
            key: Hash键
            field: 字段名
            value: 字段值 (自动JSON序列化)

        Example:
            hset('account:user001', 'cash', 100000.0)
            hset('account:user001', 'positions', {'600000.SH': 1000})
        """
        redis = self._get_connection()

        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)

        redis.hset(key, field, value)

    def hget(self, key: str, field: str) -> Optional[Any]:
        """
        获取Hash字段值

        Args:
            key: Hash键
            field: 字段名

        Returns:
            字段值 或 None
        """
        redis = self._get_connection()
        value = redis.hget(key, field)

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def hgetall(self, key: str) -> Dict[str, Any]:
        """
        获取Hash所有字段

        Args:
            key: Hash键

        Returns:
            字段字典

        Example:
            account = hgetall('account:user001')
            # {'cash': 100000.0, 'positions': {...}}
        """
        redis = self._get_connection()
        data = redis.hgetall(key)

        # 反序列化所有值
        result = {}
        for field, value in data.items():
            try:
                result[field] = json.loads(value)
            except json.JSONDecodeError:
                result[field] = value

        return result

    def hmset(self, key: str, mapping: Dict[str, Any]):
        """
        批量设置Hash字段

        Args:
            key: Hash键
            mapping: 字段字典

        Example:
            hmset('account:user001', {
                'cash': 100000.0,
                'available_cash': 50000.0,
                'total_assets': 200000.0
            })
        """
        redis = self._get_connection()

        # 序列化所有值
        serialized = {}
        for field, value in mapping.items():
            if not isinstance(value, str):
                serialized[field] = json.dumps(value, ensure_ascii=False)
            else:
                serialized[field] = value

        redis.hset(key, mapping=serialized)

    def hdel(self, key: str, *fields: str) -> int:
        """删除Hash字段"""
        redis = self._get_connection()
        return redis.hdel(key, *fields)

    # ==================== List操作 ====================

    def lpush(self, key: str, *values: Any) -> int:
        """
        从左侧推入列表

        Args:
            key: 列表键
            values: 值列表 (自动JSON序列化)

        Returns:
            列表长度

        Example:
            lpush('order_queue', {'symbol': '600000.SH', 'quantity': 100})
        """
        redis = self._get_connection()

        # 序列化所有值
        serialized = []
        for value in values:
            if not isinstance(value, str):
                serialized.append(json.dumps(value, ensure_ascii=False))
            else:
                serialized.append(value)

        return redis.lpush(key, *serialized)

    def rpush(self, key: str, *values: Any) -> int:
        """从右侧推入列表"""
        redis = self._get_connection()

        serialized = []
        for value in values:
            if not isinstance(value, str):
                serialized.append(json.dumps(value, ensure_ascii=False))
            else:
                serialized.append(value)

        return redis.rpush(key, *serialized)

    def lpop(self, key: str) -> Optional[Any]:
        """从左侧弹出元素"""
        redis = self._get_connection()
        value = redis.lpop(key)

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def rpop(self, key: str) -> Optional[Any]:
        """从右侧弹出元素"""
        redis = self._get_connection()
        value = redis.rpop(key)

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表范围元素

        Args:
            key: 列表键
            start: 起始索引 (0表示第一个元素)
            end: 结束索引 (-1表示最后一个元素)

        Returns:
            元素列表

        Example:
            # 获取前10个订单
            orders = lrange('order_queue', 0, 9)
        """
        redis = self._get_connection()
        values = redis.lrange(key, start, end)

        # 反序列化所有值
        result = []
        for value in values:
            try:
                result.append(json.loads(value))
            except json.JSONDecodeError:
                result.append(value)

        return result

    def llen(self, key: str) -> int:
        """获取列表长度"""
        redis = self._get_connection()
        return redis.llen(key)

    # ==================== Set操作 ====================

    def sadd(self, key: str, *members: Any) -> int:
        """
        添加集合成员

        Args:
            key: 集合键
            members: 成员列表

        Returns:
            添加的成员数量

        Example:
            sadd('watchlist:user001', '600000.SH', '000001.SZ')
        """
        redis = self._get_connection()

        serialized = []
        for member in members:
            if not isinstance(member, str):
                serialized.append(json.dumps(member, ensure_ascii=False))
            else:
                serialized.append(member)

        return redis.sadd(key, *serialized)

    def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        redis = self._get_connection()
        members = redis.smembers(key)

        result = set()
        for member in members:
            try:
                result.add(json.loads(member))
            except (json.JSONDecodeError, TypeError):
                result.add(member)

        return result

    def srem(self, key: str, *members: Any) -> int:
        """删除集合成员"""
        redis = self._get_connection()

        serialized = []
        for member in members:
            if not isinstance(member, str):
                serialized.append(json.dumps(member, ensure_ascii=False))
            else:
                serialized.append(member)

        return redis.srem(key, *serialized)

    def sismember(self, key: str, member: Any) -> bool:
        """检查成员是否在集合中"""
        redis = self._get_connection()

        if not isinstance(member, str):
            member = json.dumps(member, ensure_ascii=False)

        return redis.sismember(key, member)

    # ==================== 批量操作 ====================

    def mget(self, *keys: str) -> List[Optional[Any]]:
        """批量获取键值"""
        redis = self._get_connection()
        values = redis.mget(*keys)

        result = []
        for value in values:
            if value is None:
                result.append(None)
            else:
                try:
                    result.append(json.loads(value))
                except json.JSONDecodeError:
                    result.append(value)

        return result

    def mset(self, mapping: Dict[str, Any]):
        """
        批量设置键值

        Args:
            mapping: 键值字典

        Example:
            mset({
                'position:600000.SH': {'quantity': 1000},
                'position:000001.SZ': {'quantity': 500}
            })
        """
        redis = self._get_connection()

        serialized = {}
        for key, value in mapping.items():
            if not isinstance(value, str):
                serialized[key] = json.dumps(value, ensure_ascii=False)
            else:
                serialized[key] = value

        redis.mset(serialized)

    # ==================== 工具方法 ====================

    def keys(self, pattern: str = '*') -> List[str]:
        """
        查找匹配模式的键

        Args:
            pattern: 匹配模式 (支持通配符 *)

        Returns:
            键列表

        Example:
            # 查找所有持仓键
            position_keys = keys('position:*')
        """
        redis = self._get_connection()
        return redis.keys(pattern)

    def flushdb(self):
        """清空当前数据库 (谨慎使用!)"""
        redis = self._get_connection()
        redis.flushdb()

    def info(self) -> Dict[str, Any]:
        """获取Redis服务器信息"""
        redis = self._get_connection()
        return redis.info()

    def close(self):
        """关闭连接"""
        if self.redis:
            self.redis.close()
            self.redis = None


if __name__ == "__main__":
    """测试Redis数据访问层"""
    print("\n正在测试Redis数据访问层...\n")

    access = RedisDataAccess()

    # 测试连接
    try:
        redis = access._get_connection()
        redis.ping()
        print("✅ Redis连接成功\n")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        exit(1)

    print("Redis数据访问层基础功能已实现")
    print("主要功能:")
    print("  - String操作 (get/set/delete)")
    print("  - Hash操作 (hget/hset/hgetall)")
    print("  - List操作 (lpush/rpush/lpop/rpop)")
    print("  - Set操作 (sadd/smembers/srem)")
    print("  - 批量操作 (mget/mset)")
    print("  - TTL过期管理")
    print("  - 自动JSON序列化/反序列化")

    access.close()
