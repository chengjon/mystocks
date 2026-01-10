"""
Indicator Repository
====================

Data access layer for Indicator System.
Handles persistence of calculation results and task status.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import get_postgresql_session
from app.models.indicator_data import IndicatorData, IndicatorTaskModel
from app.services.indicators.indicator_interface import IndicatorResult, CalculationStatus

class IndicatorRepository:
    """
    指标数据仓库
    
    负责指标数据和任务状态的持久化。
    """
    
    def __init__(self, session: Optional[Session] = None):
        self._session = session

    def get_session(self) -> Session:
        """获取数据库会话"""
        if self._session:
            return self._session
        return get_postgresql_session()

    def save_results(self, stock_code: str, timestamps: Union[List[datetime], np.ndarray], results: List[IndicatorResult]):
        """
        批量保存指标计算结果
        
        Args:
            stock_code: 股票代码
            timestamps: 时间戳列表 (必须与结果数据的长度一致)
            results: 指标计算结果列表
        """
        if not results:
            return

        session = self.get_session()
        data_to_insert = []
        
        # 转换时间戳为标准Python datetime
        if isinstance(timestamps, np.ndarray):
            ts_list = pd.to_datetime(timestamps).to_pydatetime().tolist()
        else:
            ts_list = timestamps
            
        count = len(ts_list)
        
        for result in results:
            if not result.success:
                continue
                
            # 提取主值 (通常取第一个输出作为 value, 其他作为 complex_value)
            # 例如 MACD: value=macd, complex_value={signal, hist}
            # 例如 SMA: value=sma, complex_value=None
            
            output_names = list(result.values.keys())
            if not output_names:
                continue
                
            main_output = output_names[0]
            
            for i in range(min(count, result.data_points)):
                # 对应的时间戳
                # 注意：如果指标计算导致前N个点是NaN，result.values通常包含NaN
                # 这里假设 results.values 的长度与 timestamps 严格对齐 (padding with NaN)
                
                ts = ts_list[i]
                
                # 构建存储对象
                record = {
                    "timestamp": ts,
                    "stock_code": stock_code,
                    "indicator_code": result.abbreviation,
                    "value": None,
                    "complex_value": None
                }
                
                # 提取值
                try:
                    main_val = result.values[main_output][i]
                    if np.isnan(main_val):
                        continue # 跳过NaN值，节省空间
                        
                    record["value"] = float(main_val)
                    
                    if len(output_names) > 1:
                        complex_val = {}
                        for name in output_names:
                            val = result.values[name][i]
                            if not np.isnan(val):
                                complex_val[name] = float(val)
                        if complex_val:
                            record["complex_value"] = complex_val
                            
                except IndexError:
                    continue
                    
                data_to_insert.append(record)
        
        if not data_to_insert:
            return

        # 执行批量插入 (Upsert)
        try:
            # 分批插入以避免SQL过大
            batch_size = 1000
            for i in range(0, len(data_to_insert), batch_size):
                batch = data_to_insert[i:i+batch_size]
                stmt = pg_insert(IndicatorData).values(batch)
                
                # On Conflict Update
                stmt = stmt.on_conflict_do_update(
                    index_elements=['timestamp', 'stock_code', 'indicator_code'],
                    set_={
                        "value": stmt.excluded.value,
                        "complex_value": stmt.excluded.complex_value,
                        "created_at": func.now() # 更新时间
                    }
                )
                session.execute(stmt)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if not self._session: # 如果是自己创建的session，需要关闭
                session.close()

    def create_task(self, task_id: str, task_type: str, params: Dict) -> IndicatorTaskModel:
        """创建新任务"""
        session = self.get_session()
        try:
            task = IndicatorTaskModel(
                task_id=task_id,
                task_type=task_type,
                status="pending",
                params=params
            )
            session.add(task)
            session.commit()
            return task
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if not self._session:
                session.close()

    def update_task(self, task_id: str, status: str, progress: float = None, result: Dict = None, error: str = None):
        """更新任务状态"""
        session = self.get_session()
        try:
            stmt = select(IndicatorTaskModel).where(IndicatorTaskModel.task_id == task_id)
            task = session.execute(stmt).scalar_one_or_none()
            
            if task:
                task.status = status
                if progress is not None:
                    task.progress = progress
                if result:
                    task.result_summary = result
                if error:
                    task.error_message = error
                if status in ["success", "failed"]:
                    task.completed_at = func.now()
                    
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if not self._session:
                session.close()

    def get_latest_data(self, stock_code: str, indicator_code: str) -> Optional[IndicatorData]:
        """获取最新的指标数据"""
        session = self.get_session()
        try:
            stmt = select(IndicatorData).where(
                and_(
                    IndicatorData.stock_code == stock_code,
                    IndicatorData.indicator_code == indicator_code
                )
            ).order_by(desc(IndicatorData.timestamp)).limit(1)
            
            return session.execute(stmt).scalar_one_or_none()
        finally:
            if not self._session:
                session.close()

from sqlalchemy.sql import func
