"""
基础数据源适配器

提供所有数据源适配器的基类和接口定义
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor
from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource
)

logger = __import__("logging").getLogger(__name__)


class BaseAdapter(ABC):
    """数据源适配器基类"""
    
    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = source_type
        self.metrics = DataSourceMetrics()
        self.quality_monitor = get_data_quality_monitor()
        self.db_service = db_service
        
        logger.info(f"初始化{self.name}适配器")
    
    @abstractmethod
    def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
        
        Returns:
            Dict: 股票基本信息，失败返回None
        """
        pass
    
    @abstractmethod
    def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        获取股票日线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            List[Dict]: 日线数据列表，失败返回空列表
        """
        pass
    
    @abstractmethod
    def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """
        获取实时行情
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            List[Dict]: 实时行情数据列表，失败返回空列表
        """
        pass
    
    @abstractmethod
    def check_health(self) -> HealthStatus:
        """
        检查数据源健康状态
        
        Returns:
            HealthStatus: 健康状态
        """
        pass
    
    def _log_request_start(self, method_name: str, params: Dict):
        """记录请求开始"""
        self.metrics.record_request_start()
        logger.info(f"{self.name}.{method_name} 开始: {params}")
    
    def _log_request_success(self, method_name: str, result: Any):
        """记录请求成功"""
        self.metrics.record_request_success()
        logger.info(f"{self.name}.{method_name} 成功")
    
    def _log_request_error(self, method_name: str, error: Exception):
        """记录请求错误"""
        self.metrics.record_request_error(error)
        logger.error(f"{self.name}.{method_name} 失败: {error}")
    
    def _log_data_quality(self, data: Any, method_name: str):
        """记录数据质量"""
        quality_result = self.quality_monitor.check_data_quality(
            data, 
            f"{self.name}.{method_name}"
        )
        
        if quality_result['is_valid']:
            logger.info(f"{self.name}.{method_name} 数据质量良好")
        else:
            logger.warning(f"{self.name}.{method_name} 数据质量警告: {quality_result}")
    
    def get_metrics(self) -> Dict:
        """获取适配器指标"""
        return self.metrics.get_metrics_summary()
    
    async def get_stock_basic_with_metrics(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息并记录指标"""
        start_time = datetime.now()
        
        try:
            self._log_request_start('get_stock_basic', {'stock_code': stock_code})
            
            result = await self.get_stock_basic(stock_code)
            
            if result:
                self._log_request_success('get_stock_basic', result)
                self._log_data_quality(result, 'get_stock_basic')
            else:
                self._log_request_error('get_stock_basic', Exception('未返回数据'))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return result
        except Exception as e:
            self._log_request_error('get_stock_basic', e)
            logger.error(f"{self.name}.get_stock_basic 异常: {e}")
            return None
    
    async def get_stock_daily_with_metrics(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取日线数据并记录指标"""
        start_time = datetime.now()
        
        try:
            self._log_request_start('get_stock_daily', {
                'stock_code': stock_code,
                'start_date': start_date,
                'end_date': end_date
            })
            
            result = await self.get_stock_daily(stock_code, start_date, end_date)
            
            if result:
                self._log_request_success('get_stock_daily', result)
                self._log_data_quality(result, 'get_stock_daily')
            else:
                self._log_request_error('get_stock_daily', Exception('未返回数据'))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return result
        except Exception as e:
            self._log_request_error('get_stock_daily', e)
            logger.error(f"{self.name}.get_stock_daily 异常: {e}")
            return None
    
    async def get_realtime_quotes_with_metrics(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """获取实时行情并记录指标"""
        start_time = datetime.now()
        
        try:
            self._log_request_start('get_realtime_quotes', {'stock_codes': stock_codes})
            
            result = await self.get_realtime_quotes(stock_codes)
            
            if result:
                self._log_request_success('get_realtime_quotes', result)
                self._log_data_quality(result, 'get_realtime_quotes')
            else:
                self._log_request_error('get_realtime_quotes', Exception('未返回数据'))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return result
        except Exception as e:
            self._log_request_error('get_realtime_quotes', e)
            logger.error(f"{self.name}.get_realtime_quotes 异常: {e}")
            return None
    
    async def check_health_with_metrics(self) -> HealthStatus:
        """检查健康状态并记录指标"""
        start_time = datetime.now()
        
        try:
            self._log_request_start('check_health', {})
            
            result = await self.check_health()
            
            self._log_request_success('check_health', result)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return result
        except Exception as e:
            self._log_request_error('check_health', e)
            logger.error(f"{self.name}.check_health 异常: {e}")
            return HealthStatus(
                name=self.name,
                source_type=self.source_type,
                is_available=False,
                last_check=None,
                message=f"健康检查失败: {e}",
                metrics=self.get_metrics()
            )


class DataSourceMetrics:
    """数据源监控指标"""
    
    def __init__(self):
        self.availability: float = 0.0
        self.response_time: float = 0.0
        self.success_rate: float = 0.0
        self.error_count: int = 0
        self.last_error: str = None
        self.last_check = None
        self.total_requests: int = 0
        self.data_delay: float = 0.0
        
        logger.info("数据源监控指标初始化")
    
    def record_request_start(self):
        """记录请求开始"""
        self.total_requests += 1
        self.last_check = datetime.now()
    
    def record_request_success(self):
        """记录成功请求"""
        if self.total_requests == 1:
            self.success_rate = 100.0
        else:
            self.success_rate = (self.success_rate * (self.total_requests - 1) / self.total_requests) * 100.0
        
        self.last_error = None
    
    def record_request_error(self, error: Exception):
        """记录错误请求"""
        self.error_count += 1
        self.last_error = str(error)
        
        if self.total_requests == 1:
            self.success_rate = 0.0
        else:
            self.success_rate = (self.success_rate * (self.total_requests - 1) / self.total_requests) * 100.0
    
    def record_response_time(self, duration: float):
        """记录响应时间"""
        if self.response_time == 0.0:
            self.response_time = duration
        else:
            self.response_time = (self.response_time * (self.total_requests - 1) / self.total_requests + duration
    
    def get_metrics_summary(self) -> Dict:
        """获取指标摘要"""
        return {
            'availability': f"{self.availability:.1f}%",
            'response_time': f"{self.response_time:.0f}ms",
            'success_rate': f"{self.success_rate:.1f}%",
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'total_requests': self.total_requests,
            'data_delay': f"{self.data_delay:.0f}s" if self.data_delay else "N/A"
        }
