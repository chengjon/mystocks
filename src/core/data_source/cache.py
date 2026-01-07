"""
LRU Cache类

简单的LRU缓存实现，用于缓存数据源调用结果。
"""

from collections import OrderedDict


class LRUCache:
    """简单的LRU缓存实现"""

    def __init__(self, maxsize=100):
        """初始化LRU缓存"""
        from collections import OrderedDict

        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key):
        """获取缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def __setitem__(self, key, value):
        """设置缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)
