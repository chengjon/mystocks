#!/usr/bin/env python3
"""AI测试优化器监控和反馈收集系统
实时监控工具使用情况、收集用户反馈、分析性能指标

功能:
1. 使用情况监控
2. 性能指标收集
3. 用户反馈管理
4. 趋势分析报告
5. 异常检测和告警

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
MONITORING_DIR = PROJECT_ROOT / "monitoring_data"
MONITORING_DIR.mkdir(exist_ok=True)

# 数据库路径
DB_PATH = MONITORING_DIR / "ai_optimizer_monitor.db"


@dataclass
class UsageRecord:
    """使用记录"""

    timestamp: datetime
    command: str
    files_count: int
    execution_time: float
    exit_code: int
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    parameters: Optional[Dict] = None


@dataclass
class PerformanceMetrics:
    """性能指标"""

    timestamp: datetime
    cpu_usage: float
    memory_usage_mb: float
    disk_io_mb: float
    network_io_kb: float
    files_processed: int
    avg_file_size_kb: float


@dataclass
class UserFeedback:
    """用户反馈"""

    timestamp: datetime
    user_id: str
    feedback_type: str  # bug, suggestion, feature_request, general
    category: str  # performance, usability, accuracy, other
    rating: Optional[int]  # 1-5星评分
    comment: str
    module: Optional[str] = None
    environment: Optional[Dict] = None


class AIOptimizerMonitor:
    """AI测试优化器监控系统"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    command TEXT NOT NULL,
                    files_count INTEGER,
                    execution_time REAL,
                    exit_code INTEGER,
                    user_id TEXT,
                    session_id TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_usage REAL,
                    memory_usage_mb REAL,
                    disk_io_mb REAL,
                    network_io_kb REAL,
                    files_processed INTEGER,
                    avg_file_size_kb REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rating INTEGER,
                    comment TEXT NOT NULL,
                    module TEXT,
                    environment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_logs(timestamp)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON user_feedback(timestamp)",
            )

    def record_usage(self, usage: UsageRecord):
        """记录使用情况"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO usage_logs
                (timestamp, command, files_count, execution_time, exit_code, user_id, session_id, parameters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    usage.timestamp.isoformat(),
                    usage.command,
                    usage.files_count,
                    usage.execution_time,
                    usage.exit_code,
                    usage.user_id,
                    usage.session_id,
                    json.dumps(usage.parameters) if usage.parameters else None,
                ),
            )

    def record_performance(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO performance_metrics
                (timestamp, cpu_usage, memory_usage_mb, disk_io_mb, network_io_kb, files_processed, avg_file_size_kb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.timestamp.isoformat(),
                    metrics.cpu_usage,
                    metrics.memory_usage_mb,
                    metrics.disk_io_mb,
                    metrics.network_io_kb,
                    metrics.files_processed,
                    metrics.avg_file_size_kb,
                ),
            )

    def record_feedback(self, feedback: UserFeedback):
        """记录用户反馈"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO user_feedback
                (timestamp, user_id, feedback_type, category, rating, comment, module, environment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feedback.timestamp.isoformat(),
                    feedback.user_id,
                    feedback.feedback_type,
                    feedback.category,
                    feedback.rating,
                    feedback.comment,
                    feedback.module,
                    json.dumps(feedback.environment) if feedback.environment else None,
                ),
            )

    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict] = None,
    ):
        """创建告警"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO system_alerts
                (timestamp, alert_type, severity, message, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    alert_type,
                    severity,
                    message,
                    json.dumps(metadata) if metadata else None,
                ),
            )

    def get_usage_stats(self, days: int = 7) -> Dict:
        """获取使用统计"""
        with sqlite3.connect(self.db_path) as conn:
            # 基础统计
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            # 总使用次数
            total_usage = conn.execute(
                "SELECT COUNT(*) FROM usage_logs WHERE timestamp >= ?",
                (start_date,),
            ).fetchone()[0]

            # 成功率
            success_rate = (
                conn.execute(
                    "SELECT AVG(CASE WHEN exit_code = 0 THEN 1.0 ELSE 0.0 END) FROM usage_logs WHERE timestamp >= ?",
                    (start_date,),
                ).fetchone()[0]
                or 0
            )

            # 平均执行时间
            avg_execution_time = (
                conn.execute(
                    "SELECT AVG(execution_time) FROM usage_logs WHERE timestamp >= ?",
                    (start_date,),
                ).fetchone()[0]
                or 0
            )

            # 每日使用趋势
            daily_usage = conn.execute(
                """
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM usage_logs
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """,
                (start_date,),
            ).fetchall()

            # 热门命令
            popular_commands = conn.execute(
                """
                SELECT command, COUNT(*) as count
                FROM usage_logs
                WHERE timestamp >= ?
                GROUP BY command
                ORDER BY count DESC
                LIMIT 5
            """,
                (start_date,),
            ).fetchall()

            return {
                "total_usage": total_usage,
                "success_rate": success_rate * 100,
                "avg_execution_time": avg_execution_time,
                "daily_usage": dict(daily_usage),
                "popular_commands": dict(popular_commands),
            }

    def get_performance_stats(self, days: int = 7) -> Dict:
        """获取性能统计"""
        with sqlite3.connect(self.db_path) as conn:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            # 平均性能指标
            avg_metrics = conn.execute(
                """
                SELECT
                    AVG(cpu_usage) as avg_cpu,
                    AVG(memory_usage_mb) as avg_memory,
                    AVG(disk_io_mb) as avg_disk_io,
                    AVG(files_processed) as avg_files
                FROM performance_metrics
                WHERE timestamp >= ?
            """,
                (start_date,),
            ).fetchone()

            # 性能趋势
            performance_trend = conn.execute(
                """
                SELECT DATE(timestamp) as date,
                       AVG(cpu_usage) as avg_cpu,
                       AVG(memory_usage_mb) as avg_memory
                FROM performance_metrics
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """,
                (start_date,),
            ).fetchall()

            return {
                "avg_cpu_usage": avg_metrics[0] or 0,
                "avg_memory_usage": avg_metrics[1] or 0,
                "avg_disk_io": avg_metrics[2] or 0,
                "avg_files_processed": avg_metrics[3] or 0,
                "performance_trend": [
                    {"date": row[0], "avg_cpu": row[1], "avg_memory": row[2]} for row in performance_trend
                ],
            }

    def get_feedback_summary(self, days: int = 30) -> Dict:
        """获取反馈摘要"""
        with sqlite3.connect(self.db_path) as conn:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            # 反馈统计
            feedback_stats = conn.execute(
                """
                SELECT
                    feedback_type,
                    category,
                    COUNT(*) as count,
                    AVG(rating) as avg_rating
                FROM user_feedback
                WHERE timestamp >= ?
                GROUP BY feedback_type, category
            """,
                (start_date,),
            ).fetchall()

            # 评分分布
            rating_distribution = conn.execute(
                """
                SELECT rating, COUNT(*) as count
                FROM user_feedback
                WHERE timestamp >= ? AND rating IS NOT NULL
                GROUP BY rating
            """,
                (start_date,),
            ).fetchall()

            return {
                "feedback_by_type": [
                    {
                        "type": row[0],
                        "category": row[1],
                        "count": row[2],
                        "avg_rating": row[3],
                    }
                    for row in feedback_stats
                ],
                "rating_distribution": dict(rating_distribution),
            }

    def detect_anomalies(self) -> List[Dict]:
        """检测异常"""
        anomalies = []

        # 检测最近的失败率异常
        recent_failures = self._check_failure_rate_anomaly()
        if recent_failures:
            anomalies.extend(recent_failures)

        # 检测性能异常
        performance_anomalies = self._check_performance_anomalies()
        if performance_anomalies:
            anomalies.extend(performance_anomalies)

        # 检测使用量异常
        usage_anomalies = self._check_usage_anomalies()
        if usage_anomalies:
            anomalies.extend(usage_anomalies)

        return anomalies

    def _check_failure_rate_anomaly(self) -> List[Dict]:
        """检查失败率异常"""
        anomalies = []

        with sqlite3.connect(self.db_path) as conn:
            # 最近24小时的失败率
            recent_start = (datetime.now() - timedelta(hours=24)).isoformat()
            recent_stats = conn.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN exit_code != 0 THEN 1 ELSE 0 END) as failures "
                "FROM usage_logs WHERE timestamp >= ?",
                (recent_start,),
            ).fetchone()

            # 前24小时的失败率
            previous_start = (datetime.now() - timedelta(hours=48)).isoformat()
            previous_end = (datetime.now() - timedelta(hours=24)).isoformat()
            previous_stats = conn.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN exit_code != 0 THEN 1 ELSE 0 END) as failures "
                "FROM usage_logs WHERE timestamp BETWEEN ? AND ?",
                (previous_start, previous_end),
            ).fetchone()

            if recent_stats[0] > 0:
                recent_failure_rate = recent_stats[1] / recent_stats[0]
            else:
                recent_failure_rate = 0

            if previous_stats[0] > 0:
                previous_failure_rate = previous_stats[1] / previous_stats[0]
            else:
                previous_failure_rate = 0

            # 失败率增加超过50%则告警
            if recent_failure_rate > 0.1 and recent_failure_rate > previous_failure_rate * 1.5:
                anomalies.append(
                    {
                        "type": "failure_rate_spike",
                        "severity": "high",
                        "message": f"失败率异常上升: {recent_failure_rate * 100:.1f}% (前24小时) vs {previous_failure_rate * 100:.1f}% (之前24小时)",
                        "data": {
                            "recent_failure_rate": recent_failure_rate,
                            "previous_failure_rate": previous_failure_rate,
                            "recent_total": recent_stats[0],
                            "recent_failures": recent_stats[1],
                        },
                    },
                )

        return anomalies

    def _check_performance_anomalies(self) -> List[Dict]:
        """检查性能异常"""
        anomalies = []

        with sqlite3.connect(self.db_path) as conn:
            # 最近24小时的性能
            recent_start = (datetime.now() - timedelta(hours=24)).isoformat()
            recent_perf = conn.execute(
                "SELECT AVG(execution_time) as avg_time, MAX(execution_time) as max_time "
                "FROM usage_logs WHERE timestamp >= ?",
                (recent_start,),
            ).fetchone()

            # 检测执行时间异常
            if recent_perf[0] and recent_perf[0] > 30:  # 平均执行时间超过30秒
                anomalies.append(
                    {
                        "type": "slow_execution",
                        "severity": "medium",
                        "message": f"平均执行时间过长: {recent_perf[0]:.1f}秒",
                        "data": {
                            "avg_execution_time": recent_perf[0],
                            "max_execution_time": recent_perf[1],
                        },
                    },
                )

            # 检测内存使用异常
            recent_memory = conn.execute(
                "SELECT AVG(memory_usage_mb) FROM performance_metrics WHERE timestamp >= ?",
                (recent_start,),
            ).fetchone()

            if recent_memory[0] and recent_memory[0] > 1000:  # 内存使用超过1GB
                anomalies.append(
                    {
                        "type": "high_memory_usage",
                        "severity": "high",
                        "message": f"内存使用过高: {recent_memory[0]:.1f}MB",
                        "data": {"avg_memory_usage": recent_memory[0]},
                    },
                )

        return anomalies

    def _check_usage_anomalies(self) -> List[Dict]:
        """检查使用量异常"""
        anomalies = []

        with sqlite3.connect(self.db_path) as conn:
            # 最近7天的使用量
            recent_start = (datetime.now() - timedelta(days=7)).isoformat()
            recent_usage = conn.execute(
                "SELECT COUNT(*) FROM usage_logs WHERE timestamp >= ?",
                (recent_start,),
            ).fetchone()[0]

            # 前7天的使用量
            previous_start = (datetime.now() - timedelta(days=14)).isoformat()
            previous_end = recent_start
            previous_usage = conn.execute(
                "SELECT COUNT(*) FROM usage_logs WHERE timestamp BETWEEN ? AND ?",
                (previous_start, previous_end),
            ).fetchone()[0]

            # 使用量突然下降超过50%
            if previous_usage > 10 and recent_usage < previous_usage * 0.5:
                anomalies.append(
                    {
                        "type": "usage_drop",
                        "severity": "medium",
                        "message": f"使用量异常下降: 最近7天 {recent_usage} 次 vs 之前7天 {previous_usage} 次",
                        "data": {
                            "recent_usage": recent_usage,
                            "previous_usage": previous_usage,
                            "drop_percentage": (1 - recent_usage / previous_usage) * 100,
                        },
                    },
                )

        return anomalies

    def generate_daily_report(self) -> str:
        """生成每日报告"""
        today = datetime.now().strftime("%Y-%m-%d")

        usage_stats = self.get_usage_stats(1)
        performance_stats = self.get_performance_stats(1)
        feedback_summary = self.get_feedback_summary(7)  # 最近7天的反馈
        anomalies = self.detect_anomalies()

        report = f"""# AI测试优化器每日监控报告

**日期**: {today}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 今日使用统计

- **总使用次数**: {usage_stats["total_usage"]}
- **成功率**: {usage_stats["success_rate"]:.1f}%
- **平均执行时间**: {usage_stats["avg_execution_time"]:.2f}秒

## ⚡ 性能指标

- **平均CPU使用**: {performance_stats["avg_cpu_usage"]:.1f}%
- **平均内存使用**: {performance_stats["avg_memory_usage"]:.1f}MB
- **平均处理文件数**: {performance_stats["avg_files_processed"]:.1f}

## 🗣️ 用户反馈

最近7天反馈统计:
{self._format_feedback_summary(feedback_summary)}

## 🚨 异常检测

"""

        if anomalies:
            for anomaly in anomalies:
                report += f"### {anomaly['severity'].upper()}: {anomaly['type']}\n"
                report += f"{anomaly['message']}\n\n"
        else:
            report += "✅ 未检测到异常\n"

        report += f"""
## 📈 趋势分析

### 使用趋势
{self._format_usage_trend(usage_stats.get("daily_usage", {}))}

### 性能趋势
{self._format_performance_trend(performance_stats.get("performance_trend", []))}

## 🎯 建议行动

{self._generate_recommendations(usage_stats, performance_stats, anomalies)}

---
*报告由AI测试优化器监控系统自动生成*
"""

        return report

    def _format_feedback_summary(self, feedback_summary: Dict) -> str:
        """格式化反馈摘要"""
        if not feedback_summary["feedback_by_type"]:
            return "暂无反馈数据"

        summary = ""
        for feedback in feedback_summary["feedback_by_type"]:
            summary += f"- {feedback['type']} ({feedback['category']}): {feedback['count']} 条"
            if feedback["avg_rating"]:
                summary += f", 平均评分: {feedback['avg_rating']:.1f}⭐"
            summary += "\n"

        return summary

    def _format_usage_trend(self, daily_usage: Dict) -> str:
        """格式化使用趋势"""
        if not daily_usage:
            return "暂无使用数据"

        trend = "| 日期 | 使用次数 |\n"
        trend += "|------|----------|\n"

        for date, count in sorted(daily_usage.items()):
            trend += f"| {date} | {count} |\n"

        return trend

    def _format_performance_trend(self, performance_trend: List) -> str:
        """格式化性能趋势"""
        if not performance_trend:
            return "暂无性能数据"

        trend = "| 日期 | 平均CPU | 平均内存 |\n"
        trend += "|------|---------|----------|\n"

        for day_data in performance_trend:
            trend += f"| {day_data['date']} | {day_data['avg_cpu']:.1f}% | {day_data['avg_memory']:.1f}MB |\n"

        return trend

    def _generate_recommendations(
        self,
        usage_stats: Dict,
        performance_stats: Dict,
        anomalies: List,
    ) -> str:
        """生成建议"""
        recommendations = []

        # 基于使用情况的建议
        if usage_stats["success_rate"] < 90:
            recommendations.append("🔧 成功率偏低，建议检查常见失败原因并优化错误处理")

        if usage_stats["avg_execution_time"] > 10:
            recommendations.append("⚡ 执行时间较长，建议优化算法性能或增加缓存机制")

        # 基于性能的建议
        if performance_stats["avg_memory_usage"] > 500:
            recommendations.append("💾 内存使用较高，建议优化内存管理或增加内存限制")

        # 基于异常的建议
        if anomalies:
            recommendations.append("🚨 检测到系统异常，建议立即关注并采取相应措施")

        if not recommendations:
            recommendations.append("✅ 系统运行正常，继续保持当前配置")

        return "\n".join(f"- {rec}" for rec in recommendations)

    def save_daily_report(self, report: str) -> Path:
        """保存每日报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = MONITORING_DIR / f"daily_report_{today}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return report_path


def run_monitoring_daemon():
    """运行监控守护进程"""
    monitor = AIOptimizerMonitor()

    logger.info("🤖 AI测试优化器监控守护进程启动")
    logger.info(f"数据库路径: {monitor.db_path}")
    logger.info(f"监控数据目录: {MONITORING_DIR}")

    try:
        while True:
            try:
                # 检测异常
                anomalies = monitor.detect_anomalies()

                if anomalies:
                    logger.warning(f"🚨 检测到 {len(anomalies)} 个异常")
                    for anomaly in anomalies:
                        logger.warning(
                            f"  - {anomaly['severity']}: {anomaly['message']}",
                        )

                        # 创建告警记录
                        monitor.create_alert(
                            anomaly["type"],
                            anomaly["severity"],
                            anomaly["message"],
                            anomaly.get("data"),
                        )

                # 生成每日报告（每天早上9点）
                now = datetime.now()
                if now.hour == 9 and now.minute == 0:
                    logger.info("📊 生成每日监控报告")
                    report = monitor.generate_daily_report()
                    report_path = monitor.save_daily_report(report)
                    logger.info(f"📄 每日报告已保存: {report_path}")

                # 等待1分钟后继续监控
                time.sleep(60)

            except Exception as e:
                logger.error(f"❌ 监控过程中发生错误: {e}")
                time.sleep(60)  # 出错时等待1分钟后继续

    except KeyboardInterrupt:
        logger.info("⏹️  监控守护进程已停止")
