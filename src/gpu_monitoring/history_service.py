from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

Base = declarative_base()


class GPUMonitoringHistory(Base):
    __tablename__ = "gpu_monitoring_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    gpu_utilization = Column(Float, nullable=True)
    memory_used = Column(Integer, nullable=True)
    memory_total = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    power_usage = Column(Float, nullable=True)
    sm_clock = Column(Integer, nullable=True)
    memory_clock = Column(Integer, nullable=True)
    matrix_gflops = Column(Float, nullable=True)
    overall_speedup = Column(Float, nullable=True)
    cache_hit_rate = Column(Float, nullable=True)
    memory_bandwidth_gbs = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_gpu_monitoring_device_time", "device_id", "timestamp"),
        Index("idx_gpu_monitoring_timestamp", "timestamp"),
    )


class GPUPerformanceEvent(Base):
    __tablename__ = "gpu_performance_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True)
    message = Column(Text, nullable=True)
    event_metadata = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class HistoryDataService:
    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            db_url = self._get_db_url_from_env()

        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self._init_database()

    def _get_db_url_from_env(self) -> str:
        host = os.getenv("POSTGRESQL_HOST", "localhost")
        port = os.getenv("POSTGRESQL_PORT", "5432")
        user = os.getenv("POSTGRESQL_USER", "postgres")
        password = os.getenv("POSTGRESQL_PASSWORD", "")
        database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _init_database(self):
        try:
            Base.metadata.create_all(self.engine)
            logger.info("GPU monitoring database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")

    def save_metrics(self, gpu_metrics, perf_metrics):
        session = self.Session()
        try:
            record = GPUMonitoringHistory(
                device_id=gpu_metrics.device_id,
                timestamp=gpu_metrics.timestamp,
                gpu_utilization=gpu_metrics.gpu_utilization,
                memory_used=gpu_metrics.memory_used,
                memory_total=gpu_metrics.memory_total,
                temperature=gpu_metrics.temperature,
                power_usage=gpu_metrics.power_usage,
                sm_clock=gpu_metrics.sm_clock,
                memory_clock=gpu_metrics.memory_clock,
                matrix_gflops=perf_metrics.matrix_gflops,
                overall_speedup=perf_metrics.overall_speedup,
                cache_hit_rate=perf_metrics.cache_hit_rate,
                memory_bandwidth_gbs=perf_metrics.memory_bandwidth_gbs,
            )
            session.add(record)
            session.commit()
            logger.debug(f"Saved GPU metrics for device {gpu_metrics.device_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save metrics: {e}")
        finally:
            session.close()

    def query_history(self, device_id: int, start_time: datetime, end_time: datetime) -> List[GPUMonitoringHistory]:
        session = self.Session()
        try:
            results = (
                session.query(GPUMonitoringHistory)
                .filter(
                    GPUMonitoringHistory.device_id == device_id,
                    GPUMonitoringHistory.timestamp >= start_time,
                    GPUMonitoringHistory.timestamp <= end_time,
                )
                .order_by(GPUMonitoringHistory.timestamp.desc())
                .all()
            )

            return results
        except Exception as e:
            logger.error(f"Failed to query history: {e}")
            return []
        finally:
            session.close()

    def get_aggregated_stats(self, device_id: int, hours: int = 24) -> Dict:
        session = self.Session()
        try:
            from sqlalchemy import func

            start_time = datetime.now() - timedelta(hours=hours)

            stats = (
                session.query(
                    func.avg(GPUMonitoringHistory.gpu_utilization).label("avg_utilization"),
                    func.max(GPUMonitoringHistory.gpu_utilization).label("max_utilization"),
                    func.avg(GPUMonitoringHistory.temperature).label("avg_temperature"),
                    func.max(GPUMonitoringHistory.temperature).label("max_temperature"),
                    func.avg(GPUMonitoringHistory.matrix_gflops).label("avg_gflops"),
                    func.max(GPUMonitoringHistory.matrix_gflops).label("peak_gflops"),
                    func.avg(GPUMonitoringHistory.overall_speedup).label("avg_speedup"),
                    func.max(GPUMonitoringHistory.overall_speedup).label("peak_speedup"),
                )
                .filter(GPUMonitoringHistory.device_id == device_id, GPUMonitoringHistory.timestamp >= start_time)
                .first()
            )

            return {
                "avg_utilization": float(stats.avg_utilization or 0),
                "max_utilization": float(stats.max_utilization or 0),
                "avg_temperature": float(stats.avg_temperature or 0),
                "max_temperature": float(stats.max_temperature or 0),
                "avg_gflops": float(stats.avg_gflops or 0),
                "peak_gflops": float(stats.peak_gflops or 0),
                "avg_speedup": float(stats.avg_speedup or 0),
                "peak_speedup": float(stats.peak_speedup or 0),
            }
        except Exception as e:
            logger.error(f"Failed to get aggregated stats: {e}")
            return {
                "avg_utilization": 0.0,
                "max_utilization": 0.0,
                "avg_temperature": 0.0,
                "max_temperature": 0.0,
                "avg_gflops": 0.0,
                "peak_gflops": 0.0,
                "avg_speedup": 0.0,
                "peak_speedup": 0.0,
            }
        finally:
            session.close()

    def log_event(self, event):
        session = self.Session()
        try:
            if not isinstance(event, GPUPerformanceEvent):
                event = GPUPerformanceEvent(**event)
            session.add(event)
            session.commit()
            logger.debug(f"Logged GPU performance event: {event.event_type}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log event: {e}")
        finally:
            session.close()

    def get_recent_events(self, device_id: int, limit: int = 50) -> List[GPUPerformanceEvent]:
        session = self.Session()
        try:
            events = (
                session.query(GPUPerformanceEvent)
                .filter(GPUPerformanceEvent.device_id == device_id)
                .order_by(GPUPerformanceEvent.timestamp.desc())
                .limit(limit)
                .all()
            )

            return events
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            return []
        finally:
            session.close()
