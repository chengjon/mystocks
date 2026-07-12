#!/usr/bin/env python3
"""AI测试优化器使用反馈分析器
收集、分析和报告AI测试优化器的使用情况，为工具改进提供数据支持

功能:
1. 使用数据收集和分析
2. 用户反馈趋势分析
3. 工具效果评估
4. 改进建议生成
5. 使用模式识别

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import logging
import sqlite3
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class UsageFeedbackAnalyzerCoreMixin:
    """UsageFeedbackAnalyzer 方法集 Part 1"""

    def __init__(self):
        self.monitor = AIOptimizerMonitor() if AIOptimizerMonitor else None
        self.collector = FeedbackCollector() if FeedbackCollector else None
        self.analysis_dir = PROJECT_ROOT / "monitoring_data" / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)

    def collect_usage_patterns(self, days: int = 30) -> Dict:
        """收集使用模式数据"""
        logger.info(f"📊 收集最近{days}天的使用模式数据")

        if not self.monitor:
            logger.warning("监控系统不可用，使用模拟数据")
            return self._generate_mock_usage_patterns(days)

        # 从监控系统获取使用数据
        usage_stats = self.monitor.get_usage_stats(days)
        performance_stats = self.monitor.get_performance_stats(days)

        # 深度分析使用模式
        patterns = {
            "basic_stats": usage_stats,
            "performance_stats": performance_stats,
            "usage_trends": self._analyze_usage_trends(days),
            "peak_usage_times": self._find_peak_usage_times(days),
            "most_used_commands": self._analyze_command_frequency(days),
            "success_patterns": self._analyze_success_patterns(days),
            "user_behavior": self._analyze_user_behavior(days),
        }

        return patterns

    def _generate_mock_usage_patterns(self, days: int) -> Dict:
        """生成模拟使用模式数据（用于演示）"""
        logger.info("📝 生成模拟使用模式数据")

        # 生成模拟的日常使用数据
        patterns = {
            "basic_stats": {
                "total_usage": 150,
                "success_rate": 92.5,
                "avg_execution_time": 3.2,
                "daily_usage": self._generate_mock_daily_data(days),
            },
            "performance_stats": {
                "avg_cpu_usage": 25.3,
                "avg_memory_usage": 156.7,
                "avg_files_processed": 5.2,
            },
            "usage_trends": {
                "growth_rate": 15.2,  # 月增长率
                "adoption_rate": 85.0,  # 团队采用率
                "retention_rate": 95.0,  # 用户留存率
            },
            "peak_usage_times": [
                {"time": "09:00", "usage_count": 25},
                {"time": "14:00", "usage_count": 18},
                {"time": "16:00", "usage_count": 22},
            ],
            "most_used_commands": {
                "--batch": 45,
                "--generate-tests": 38,
                "--report": 28,
                "--help": 15,
            },
            "success_patterns": {
                "success_by_time_of_day": {
                    "morning": 95.2,
                    "afternoon": 91.8,
                    "evening": 89.3,
                },
                "success_by_module": {
                    "core": 93.5,
                    "adapters": 90.2,
                    "monitoring": 94.8,
                },
            },
            "user_behavior": {
                "avg_session_length": 12.5,
                "repeat_users": 85.0,
                "feature_adoption": 78.5,
            },
        }

        return patterns

    def _generate_mock_daily_data(self, days: int) -> Dict:
        """生成模拟每日数据"""
        daily_data = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            # 模拟工作日/周末差异
            weekday = (datetime.now() - timedelta(days=i)).weekday()
            if weekday < 5:  # 工作日
                usage_count = 20 + int(10 * (i % 3))  # 20-40
            else:  # 周末
                usage_count = 8 + int(5 * (i % 2))  # 8-18

            daily_data[date] = usage_count

        return daily_data

    def _analyze_usage_trends(self, days: int) -> Dict:
        """分析使用趋势"""
        if not self.monitor:
            return {"trend": "stable", "growth_rate": 15.0}

        # 获取详细的每日数据
        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 获取每日使用量
                daily_query = f"""
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """
                daily_data = conn.execute(daily_query).fetchall()

                if len(daily_data) < 2:
                    return {"trend": "insufficient_data", "growth_rate": 0}

                # 计算趋势
                counts = [row[1] for row in daily_data]
                first_half = counts[: len(counts) // 2]
                second_half = counts[len(counts) // 2 :]

                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)

                if first_avg == 0:
                    trend = "stable"
                    growth_rate = 0
                elif second_avg > first_avg * 1.2:
                    trend = "growing"
                    growth_rate = ((second_avg / first_avg) - 1) * 100
                elif second_avg < first_avg * 0.8:
                    trend = "declining"
                    growth_rate = ((second_avg / first_avg) - 1) * 100
                else:
                    trend = "stable"
                    growth_rate = ((second_avg / first_avg) - 1) * 100

                return {
                    "trend": trend,
                    "growth_rate": growth_rate,
                    "data_points": len(daily_data),
                    "daily_data": dict(daily_data),
                }

        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {"trend": "error", "growth_rate": 0}

    def _find_peak_usage_times(self, days: int) -> List[Dict]:
        """找出使用高峰时段"""
        if not self.monitor:
            return [
                {"time": "09:00-10:00", "usage_count": 25, "description": "早高峰"},
                {"time": "14:00-15:00", "usage_count": 20, "description": "下午高峰"},
                {"time": "16:00-17:00", "usage_count": 22, "description": "晚高峰"},
            ]

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 获取小时级别的使用数据
                hourly_query = f"""
                    SELECT
                        CASE
                            WHEN strftime('%H', timestamp) BETWEEN '09' AND '10' THEN '09:00-10:00'
                            WHEN strftime('%H', timestamp) BETWEEN '14' AND '15' THEN '14:00-15:00'
                            WHEN strftime('%H', timestamp) BETWEEN '16' AND '17' THEN '16:00-17:00'
                            ELSE strftime('%H:00-', timestamp)
                        END as time_slot,
                        COUNT(*) as count
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                    GROUP BY time_slot
                    ORDER BY count DESC
                    LIMIT 5
                """
                peak_data = conn.execute(hourly_query).fetchall()

                return [
                    {
                        "time": row[0],
                        "usage_count": row[1],
                        "description": self._get_time_description(row[0]),
                    }
                    for row in peak_data
                ]

        except Exception as e:
            logger.error(f"高峰时段分析失败: {e}")
            return []

    def _get_time_description(self, time_slot: str) -> str:
        """获取时间段描述"""
        descriptions = {
            "09:00-10:00": "早高峰",
            "14:00-15:00": "下午高峰",
            "16:00-17:00": "晚高峰",
            "10:00-11:00": "上午",
            "11:00-12:00": "中午",
            "13:00-14:00": "下午",
        }
        return descriptions.get(time_slot, "其他时段")

    def _analyze_command_frequency(self, days: int) -> Dict:
        """分析命令使用频率"""
        if not self.monitor:
            return {
                "--batch": 45,
                "--generate-tests": 38,
                "--report": 28,
                "--help": 15,
                "--config": 12,
                "--verbose": 10,
            }

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                command_query = f"""
                    SELECT
                        command,
                        COUNT(*) as usage_count,
                        AVG(execution_time) as avg_time
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                    GROUP BY command
                    ORDER BY usage_count DESC
                """
                command_data = conn.execute(command_query).fetchall()

                return {
                    "detailed": dict(
                        (row[0], {"count": row[1], "avg_time": row[2] if row[2] else 0}) for row in command_data
                    ),
                    "top_commands": dict((row[0], row[1]) for row in command_data[:5]),
                }

        except Exception as e:
            logger.error(f"命令频率分析失败: {e}")
            return {}

    def _analyze_success_patterns(self, days: int) -> Dict:
        """分析成功模式"""
        if not self.monitor:
            return {
                "overall_rate": 92.5,
                "by_time_of_day": {"morning": 95.2, "afternoon": 91.8, "evening": 89.3},
                "by_module": {"core": 93.5, "adapters": 90.2, "monitoring": 94.8},
            }

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 按时间段分析成功率
                time_query = f"""
                    SELECT
                        CASE
                            WHEN CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 6 AND 12 THEN 'morning'
                            WHEN CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 12 AND 18 THEN 'afternoon'
                            ELSE 'evening'
                        END as time_period,
                        COUNT(*) as total,
                        SUM(CASE WHEN exit_code = 0 THEN 1 ELSE 0 END) as success
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                    GROUP BY time_period
                """
                time_data = conn.execute(time_query).fetchall()

                success_by_time = {}
                for period, total, success in time_data:
                    success_by_time[period] = (success / total * 100) if total > 0 else 0

                # 计算总体成功率
                total_success = conn.execute(f"""
                    SELECT COUNT(*), SUM(CASE WHEN exit_code = 0 THEN 1 ELSE 0 END)
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                """).fetchone()

                overall_rate = (total_success[1] / total_success[0] * 100) if total_success[0] > 0 else 0

                return {"overall_rate": overall_rate, "by_time_of_day": success_by_time}

        except Exception as e:
            logger.error(f"成功模式分析失败: {e}")
            return {"overall_rate": 0}

    def _analyze_user_behavior(self, days: int) -> Dict:
        """分析用户行为"""
        if not self.monitor:
            return {
                "avg_session_length": 12.5,
                "repeat_users": 85.0,
                "feature_adoption": 78.5,
                "user_types": {
                    "power_users": 25.0,
                    "regular_users": 55.0,
                    "casual_users": 20.0,
                },
            }

        try:
            if self.monitor:
                db_path = self.monitor.db_path
            else:
                db_path = PROJECT_ROOT / "monitoring_data" / "ai_optimizer_monitor.db"

            with sqlite3.connect(db_path) as conn:
                # 分析用户会话长度（假设每次使用为一次会话）
                session_query = f"""
                    SELECT
                        user_id,
                        COUNT(*) as usage_count,
                        AVG(execution_time) as avg_time
                    FROM usage_logs
                    WHERE timestamp >= date('now', '-{days} days')
                    AND user_id IS NOT NULL
                    GROUP BY user_id
                """
                session_data = conn.execute(session_query).fetchall()

                if session_data:
                    avg_session_length = statistics.mean(
                        [row[2] for row in session_data],
                    )
                    repeat_users = len([row for row in session_data if row[1] > 1]) / len(session_data) * 100
                else:
                    avg_session_length = 0
                    repeat_users = 0

                return {
                    "avg_session_length": avg_session_length,
                    "repeat_users": repeat_users,
                    "user_diversity": len(session_data) if session_data else 0,
                }

        except Exception as e:
            logger.error(f"用户行为分析失败: {e}")
            return {}

    def analyze_feedback_patterns(self, days: int = 30) -> Dict:
        """分析反馈模式"""
        logger.info(f"📝 分析最近{days}天的用户反馈")

        if not self.monitor:
            logger.warning("监控系统不可用，使用模拟反馈数据")
            return self._generate_mock_feedback_patterns(days)

        # 获取反馈数据
        feedback_summary = self.monitor.get_feedback_summary(days)

        # 深度分析反馈模式
        patterns = {
            "basic_stats": feedback_summary,
            "feedback_trends": self._analyze_feedback_trends(days),
            "sentiment_analysis": self._analyze_sentiment(days),
            "issue_categories": self._categorize_issues(days),
            "improvement_areas": self._identify_improvement_areas(days),
            "user_satisfaction": self._calculate_satisfaction(days),
        }

        return patterns

    def _generate_mock_feedback_patterns(self, days: int) -> Dict:
        """生成模拟反馈模式数据"""
        logger.info("📝 生成模拟反馈模式数据")

        patterns = {
            "basic_stats": {
                "feedback_by_type": [
                    {
                        "type": "suggestion",
                        "category": "performance",
                        "count": 25,
                        "avg_rating": 4.2,
                    },
                    {
                        "type": "bug",
                        "category": "accuracy",
                        "count": 15,
                        "avg_rating": 3.8,
                    },
                    {
                        "type": "feature_request",
                        "category": "usability",
                        "count": 12,
                        "avg_rating": 4.5,
                    },
                    {
                        "type": "general",
                        "category": "documentation",
                        "count": 8,
                        "avg_rating": 4.0,
                    },
                ],
                "rating_distribution": {5: 35, 4: 42, 3: 15, 2: 5, 1: 3},
            },
            "feedback_trends": {
                "monthly_feedback_rate": 88.5,
                "positive_trend": True,
                "main_concerns": ["performance", "documentation"],
                "improving_areas": ["UI usability", "error messages"],
            },
            "sentiment_analysis": {
                "positive_sentiment": 75.5,
                "neutral_sentiment": 18.5,
                "negative_sentiment": 6.0,
                "sentiment_trend": "improving",
            },
            "issue_categories": {
                "performance_issues": 45,
                "usability_issues": 28,
                "documentation_issues": 20,
                "bug_reports": 15,
                "feature_requests": 12,
            },
            "improvement_areas": [
                {
                    "area": "Performance optimization",
                    "priority": "high",
                    "impact": "High",
                },
                {
                    "area": "Documentation enhancement",
                    "priority": "medium",
                    "impact": "Medium",
                },
                {"area": "UI/UX improvement", "priority": "medium", "impact": "Medium"},
            ],
            "user_satisfaction": {
                "overall_score": 4.2,
                "satisfaction_level": "Good",
                "satisfaction_trend": "Stable",
            },
        }

        return patterns

    def _analyze_feedback_trends(self, days: int) -> Dict:
        """分析反馈趋势"""
        # 这里可以实现更复杂的趋势分析
        return {
            "monthly_feedback_rate": 88.5,
            "positive_trend": True,
            "main_concerns": ["performance", "documentation"],
            "improving_areas": ["UI usability", "error messages"],
        }

    def _analyze_sentiment(self, days: int) -> Dict:
        """分析用户情绪"""
        if not self.monitor:
            return {
                "positive_sentiment": 75.5,
                "neutral_sentiment": 18.5,
                "negative_sentiment": 6.0,
                "sentiment_trend": "improving",
            }

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 获取评分数据
                rating_query = f"""
                    SELECT rating, COUNT(*) as count
                    FROM user_feedback
                    WHERE timestamp >= date('now', '-{days} days')
                    AND rating IS NOT NULL
                    GROUP BY rating
                """
                rating_data = conn.execute(rating_query).fetchall()

                if not rating_data:
                    return {
                        "positive_sentiment": 0,
                        "neutral_sentiment": 0,
                        "negative_sentiment": 0,
                        "sentiment_trend": "no_data",
                    }

                # 转换为字典格式
                rating_dict = dict(rating_data)
                total_feedbacks = sum(rating_dict.values())

                # 计算情绪分布
                positive_sentiment = sum(count for rating, count in rating_dict.items() if rating >= 4)
                neutral_sentiment = sum(count for rating, count in rating_dict.items() if rating == 3)
                negative_sentiment = sum(count for rating, count in rating_dict.items() if rating <= 2)

                return {
                    "positive_sentiment": (positive_sentiment / total_feedbacks) * 100,
                    "neutral_sentiment": (neutral_sentiment / total_feedbacks) * 100,
                    "negative_sentiment": (negative_sentiment / total_feedbacks) * 100,
                    "sentiment_distribution": dict(rating_data),
                }

        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return {
                "positive_sentiment": 0,
                "neutral_sentiment": 0,
                "negative_sentiment": 0,
                "sentiment_trend": "error",
            }

    def _categorize_issues(self, days: int) -> Dict:
        """分类问题类型"""
        if not self.monitor:
            return {
                "performance_issues": 45,
                "usability_issues": 28,
                "documentation_issues": 20,
                "bug_reports": 15,
                "feature_requests": 12,
            }

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 获取反馈分类统计
                category_query = f"""
                    SELECT category, COUNT(*) as count
                    FROM user_feedback
                    WHERE timestamp >= date('now', '-{days} days')
                    GROUP BY category
                """
                category_data = conn.execute(category_query).fetchall()

                issues = {}
                for category, count in category_data:
                    if category in [
                        "performance",
                        "usability",
                        "documentation",
                        "accuracy",
                    ]:
                        issues[f"{category}_issues"] = count

                return issues

        except Exception as e:
            logger.error(f"问题分类失败: {e}")
            return {}

    def _identify_improvement_areas(self, days: int) -> List[Dict]:
        """识别改进领域"""
        # 这里可以实现基于反馈的改进领域识别
        improvement_areas = [
            {"area": "Performance optimization", "priority": "high", "impact": "High"},
            {
                "area": "Documentation enhancement",
                "priority": "medium",
                "impact": "Medium",
            },
            {"area": "UI/UX improvement", "priority": "medium", "impact": "Medium"},
            {"area": "Error message clarity", "priority": "low", "impact": "Low"},
            {"area": "Feature expansion", "priority": "low", "impact": "Low"},
        ]

        return improvement_areas

    def _calculate_satisfaction(self, days: int) -> Dict:
        """计算用户满意度"""
        if not self.monitor:
            return {
                "overall_score": 4.2,
                "satisfaction_level": "Good",
                "satisfaction_trend": "Stable",
            }

        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                # 获取平均评分
                avg_rating_query = f"""
                    SELECT AVG(rating) as avg_rating
                    FROM user_feedback
                    WHERE timestamp >= date('now', '-{days} days')
                    AND rating IS NOT NULL
                """
                avg_rating_data = conn.execute(avg_rating_query).fetchone()

                if avg_rating_data and avg_rating_data[0]:
                    avg_score = avg_rating_data[0]

                    if avg_score >= 4.5:
                        level = "Excellent"
                        trend = "Very Positive"
                    elif avg_score >= 4.0:
                        level = "Good"
                        trend = "Positive"
                    elif avg_score >= 3.5:
                        level = "Fair"
                        trend = "Neutral"
                    else:
                        level = "Poor"
                        trend = "Negative"
                else:
                    avg_score = 0
                    level = "No Data"
                    trend = "Unknown"

                return {
                    "overall_score": avg_score,
                    "satisfaction_level": level,
                    "satisfaction_trend": trend,
                }

        except Exception as e:
            logger.error(f"满意度计算失败: {e}")
            return {
                "overall_score": 0,
                "satisfaction_level": "Error",
                "satisfaction_trend": "Error",
            }
