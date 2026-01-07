    def _validate_data(self, endpoint_name: str, data: Any):
        """验证数据质量"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        quality_rules = source["config"].get("quality_rules", {})

        if not isinstance(data, pd.DataFrame):
            return  # 非DataFrame数据跳过验证

        # 检查最小记录数
        min_count = quality_rules.get("min_record_count", 0)
        if len(data) < min_count:
            raise ValueError(f"数据记录数不足: {len(data)} < {min_count}")

        # 检查必需列
        required_columns = quality_rules.get("required_columns", [])
        if required_columns:
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                raise ValueError(f"缺少必需列: {missing_columns}")


class LRUCache:
    """简单的LRU缓存实现"""

    def __init__(self, maxsize=100):
        from collections import OrderedDict

        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def __setitem__(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)


# 便捷的单例模式（可选）
_instance = None


def get_data_source_manager() -> DataSourceManagerV2:
    """获取数据源管理器单例"""
    global _instance
    if _instance is None:
        _instance = DataSourceManagerV2()
    return _instance
