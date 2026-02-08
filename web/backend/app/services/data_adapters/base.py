"""
数据源适配器基类和指标
"""
from datetime import datetime
from typing import Optional

class DataSourceMetrics:
    """数据源监控指标"""

    def __init__(self):
        self.availability: float = 0.0  # 可用性百分比 (0-100)
        self.response_time: float = 0.0  # 平均响应时间 (ms)
        self.success_rate: float = 0.0  # 成功率百分比 (0-100)
        self.error_count: int = 0  # 错误次数
        self.last_error = None  # 最后错误信息
        self.last_check = None  # 最后检查时间
        self.total_requests: int = 0  # 总请求数
        self.data_delay = None  # 数据延迟 (秒)

    def record_request(self, success: bool = True, error_msg: Optional[str] = None):
        """记录请求结果，更新指标"""
        self.total_requests += 1
        if success:
            # 计算成功率 (移动平均)
            if self.total_requests == 1:
                self.success_rate = 100.0
            else:
                # 使用指数移动平均
                alpha = 0.1  # 平滑因子
                self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate
        else:
            self.error_count += 1
            if error_msg:
                self.last_error = error_msg

            # 更新成功率
            if self.total_requests == 1:
                self.success_rate = 0.0
            else:
                failed_rate = (self.error_count / self.total_requests) * 100
                self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_success(self, response_time: float = 0.0):
        """记录成功请求，更新指标"""
        self.total_requests += 1
        self.response_time = response_time

        # 计算成功率 (移动平均)
        if self.total_requests == 1:
            self.success_rate = 100.0
        else:
            # 使用指数移动平均
            alpha = 0.1  # 平滑因子
            self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_error(self, response_time: float = 0.0, error_msg: str = ""):
        """记录错误，更新指标"""
        self.total_requests += 1
        self.error_count += 1
        if error_msg:
            self.last_error = error_msg

        # 更新成功率
        if self.total_requests == 1:
            self.success_rate = 0.0
        else:
            failed_rate = (self.error_count / self.total_requests) * 100
            self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()
