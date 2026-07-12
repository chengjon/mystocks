#!/usr/bin/env python3
"""AI测试优化器用户反馈收集工具
简化用户反馈提交流程，支持多种反馈类型和渠道

功能:
1. 交互式反馈收集
2. 反馈分类和标记
3. 自动环境信息收集
4. 批量反馈处理
5. 反馈分析和统计

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入监控系统
try:
    from scripts.monitoring.ai_optimizer_monitor import AIOptimizerMonitor, UserFeedback
except ImportError:
    logger.warning("无法导入监控系统，反馈将保存到文件")
    AIOptimizerMonitor = None


class FeedbackCollector:
    """用户反馈收集器"""

    def __init__(self):
        self.monitor = AIOptimizerMonitor() if AIOptimizerMonitor else None
        self.feedback_file = PROJECT_ROOT / "monitoring_data" / "feedback_queue.json"
        self.feedback_file.parent.mkdir(exist_ok=True)

    def collect_interactive_feedback(self) -> Dict:
        """交互式收集反馈"""
        print("🗣️ AI测试优化器用户反馈收集")
        print("=" * 50)

        feedback = {}

        # 用户标识
        user_id = self._get_user_input(
            "用户ID (可选):",
            default=os.environ.get("USER", "anonymous"),
            required=False,
        )
        if user_id:
            feedback["user_id"] = user_id

        # 反馈类型
        feedback_types = [
            "bug",
            "suggestion",
            "feature_request",
            "general",
            "performance",
            "usability",
        ]
        print(f"\n反馈类型: {', '.join(feedback_types)}")
        feedback_type = self._get_user_input(
            "反馈类型:", options=feedback_types, required=True,
        )
        feedback["feedback_type"] = feedback_type

        # 模块信息
        module = self._get_user_input(
            "相关模块 (如: src/adapters/data_validator.py):", required=False,
        )
        if module:
            feedback["module"] = module

        # 评分
        rating = self._get_user_input(
            "评分 (1-5星):", input_type="int", min_val=1, max_val=5, required=False,
        )
        if rating:
            feedback["rating"] = rating

        # 详细反馈
        print(f"\n请详细描述您的{feedback_type}:")
        comment = self._get_user_input("反馈内容:", required=True, multi_line=True)
        feedback["comment"] = comment

        # 分类
        categories = [
            "performance",
            "usability",
            "accuracy",
            "documentation",
            "integration",
            "other",
        ]
        print(f"\n分类: {', '.join(categories)}")
        category = self._get_user_input("选择分类:", options=categories, required=True)
        feedback["category"] = category

        # 收集环境信息
        feedback["environment"] = self._collect_environment_info()

        return feedback

    def _get_user_input(
        self,
        prompt: str,
        *,
        default: str = "",
        options: List[str] = None,
        input_type: str = "str",
        min_val: int = None,
        max_val: int = None,
        required: bool = False,
        multi_line: bool = False,
    ) -> Optional[str]:
        """获取用户输入"""
        while True:
            try:
                if multi_line:
                    print(f"{prompt} (输入空行结束)")
                    lines = []
                    while True:
                        line = input()
                        if line.strip() == "":
                            break
                        lines.append(line.strip())
                    user_input = "\n".join(lines)
                elif default:
                    user_input = input(f"{prompt} [{default}]: ").strip() or default
                else:
                    user_input = input(f"{prompt}: ").strip()

                if not user_input and not required:
                    return None

                if options and user_input not in options:
                    print(f"❌ 请从以下选项中选择: {', '.join(options)}")
                    continue

                if input_type == "int":
                    user_input = int(user_input)
                    if min_val is not None and user_input < min_val:
                        print(f"❌ 值不能小于 {min_val}")
                        continue
                    if max_val is not None and user_input > max_val:
                        print(f"❌ 值不能大于 {max_val}")
                        continue

                return user_input

            except ValueError as e:
                print(f"❌ 输入格式错误: {e}")
                continue
            except KeyboardInterrupt:
                print("\n⏹️  取消输入")
                return None

    def _collect_environment_info(self) -> Dict:
        """收集环境信息"""
        try:
            env_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "working_directory": os.getcwd(),
                "timestamp": datetime.now().isoformat(),
            }

            # 项目特定信息
            try:
                # Git信息
                git_hash = (
                    subprocess.check_output(
                        ["git", "rev-parse", "HEAD"],
                        stderr=subprocess.DEVNULL,
                        cwd=PROJECT_ROOT,
                    )
                    .decode()
                    .strip()
                )
                env_info["git_hash"] = git_hash

                git_branch = (
                    subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        stderr=subprocess.DEVNULL,
                        cwd=PROJECT_ROOT,
                    )
                    .decode()
                    .strip()
                )
                env_info["git_branch"] = git_branch

            except (subprocess.CalledProcessError, FileNotFoundError):
                env_info["git_info"] = "Not available"

            # 系统资源
            try:
                import psutil

                env_info["cpu_count"] = psutil.cpu_count()
                env_info["memory_total_gb"] = psutil.virtual_memory().total / (1024**3)
                env_info["disk_free_gb"] = psutil.disk_usage(".").free / (1024**3)
            except ImportError:
                env_info["system_resources"] = "psutil not available"

            return env_info

        except Exception as e:
            logger.warning(f"环境信息收集失败: {e}")
            return {"error": str(e)}

    def submit_feedback(self, feedback: Dict) -> bool:
        """提交反馈"""
        try:
            # 创建UserFeedback对象
            user_feedback = UserFeedback(
                timestamp=datetime.now(),
                user_id=feedback.get("user_id", "anonymous"),
                feedback_type=feedback["feedback_type"],
                category=feedback["category"],
                rating=feedback.get("rating"),
                comment=feedback["comment"],
                module=feedback.get("module"),
                environment=feedback.get("environment"),
            )

            # 如果监控系统可用，保存到数据库
            if self.monitor:
                self.monitor.record_feedback(user_feedback)
                logger.info("✅ 反馈已保存到监控系统")
            else:
                # 否则保存到文件队列
                self._save_to_queue(feedback)
                logger.info("✅ 反馈已保存到文件队列")

            return True

        except Exception as e:
            logger.error(f"❌ 反馈提交失败: {e}")
            return False

    def _save_to_queue(self, feedback: Dict):
        """保存到文件队列"""
        feedback["timestamp"] = datetime.now().isoformat()

        # 读取现有队列
        queue = []
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, encoding="utf-8") as f:
                    queue = json.load(f)
            except (OSError, json.JSONDecodeError):
                queue = []

        # 添加新反馈
        queue.append(feedback)

        # 保存队列
        with open(self.feedback_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

    def process_queue(self) -> int:
        """处理文件队列中的反馈"""
        if not self.monitor:
            logger.warning("监控系统不可用，无法处理队列")
            return 0

        if not self.feedback_file.exists():
            logger.info("反馈队列为空")
            return 0

        try:
            with open(self.feedback_file, encoding="utf-8") as f:
                queue = json.load(f)

            processed = 0
            for feedback_data in queue:
                try:
                    # 重新创建UserFeedback对象
                    user_feedback = UserFeedback(
                        timestamp=datetime.fromisoformat(feedback_data["timestamp"]),
                        user_id=feedback_data.get("user_id", "anonymous"),
                        feedback_type=feedback_data["feedback_type"],
                        category=feedback_data["category"],
                        rating=feedback_data.get("rating"),
                        comment=feedback_data["comment"],
                        module=feedback_data.get("module"),
                        environment=feedback_data.get("environment"),
                    )

                    # 保存到数据库
                    self.monitor.record_feedback(user_feedback)
                    processed += 1

                except Exception as e:
                    logger.error(f"❌ 处理反馈失败: {e}")

            # 清空队列
            self.feedback_file.unlink()
            logger.info(f"✅ 成功处理 {processed} 条反馈")

            return processed

        except Exception as e:
            logger.error(f"❌ 队列处理失败: {e}")
            return 0

    def batch_feedback_from_file(self, file_path: str) -> int:
        """从文件批量导入反馈"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 简单解析 - 假设每行一个反馈，格式为: 类型|分类|评分|评论
            feedbacks = []
            for line_num, line in enumerate(content.strip().split("\n"), 1):
                if not line.strip():
                    continue

                try:
                    parts = line.split("|", 3)
                    if len(parts) >= 3:
                        feedback = {
                            "feedback_type": parts[0].strip(),
                            "category": parts[1].strip(),
                            "rating": int(parts[2].strip())
                            if parts[2].strip().isdigit()
                            else None,
                            "comment": parts[3].strip()
                            if len(parts) > 3
                            else f"来自文件的第{line_num}行",
                            "user_id": "batch_import",
                            "environment": self._collect_environment_info(),
                        }
                        feedbacks.append(feedback)
                    else:
                        logger.warning(f"第{line_num}行格式不正确，跳过: {line}")

                except Exception as e:
                    logger.error(f"第{line_num}行解析失败: {e}")

            # 提交反馈
            success_count = 0
            for feedback in feedbacks:
                if self.submit_feedback(feedback):
                    success_count += 1

            logger.info(f"✅ 批量导入完成: {success_count}/{len(feedbacks)} 条反馈成功")
            return success_count

        except Exception as e:
            logger.error(f"❌ 批量导入失败: {e}")
            return 0

    def generate_feedback_report(self, days: int = 30) -> str:
        """生成反馈报告"""
        if not self.monitor:
            return "监控系统不可用，无法生成反馈报告"

        feedback_summary = self.monitor.get_feedback_summary(days)

        report = f"""# 用户反馈报告

**统计时间**: 最近{days}天
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 反馈统计

### 按类型和分类
"""

        if feedback_summary["feedback_by_type"]:
            for feedback in feedback_summary["feedback_by_type"]:
                report += f"- **{feedback['type']} ({feedback['category']}**: {feedback['count']} 条"
                if feedback["avg_rating"]:
                    report += f", 平均评分: {feedback['avg_rating']:.1f}⭐"
                report += "\n"

        report += "\n### 评分分布\n"
        if feedback_summary["rating_distribution"]:
            total_feedbacks = sum(feedback_summary["rating_distribution"].values())
            for rating in sorted(
                feedback_summary["rating_distribution"].keys(), reverse=True,
            ):
                count = feedback_summary["rating_distribution"][rating]
                percentage = (count / total_feedbacks) * 100
                report += f"- {rating}星: {count} 条 ({percentage:.1f}%)\n"
        else:
            report += "- 暂无评分数据\n"

        report += """
## 💡 建议行动

### 高优先级改进
1. 关注评分较低的反馈类型
2. 优先处理高频反馈类别
3. 收集更多用户评分以提高数据质量

### 持续改进
- 定期分析用户反馈趋势
- 建立反馈响应机制
- 将反馈转化为具体改进措施

---
*报告由AI测试优化器反馈系统自动生成*
"""

        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI测试优化器用户反馈收集工具")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="启动交互式反馈收集",
    )
    parser.add_argument("--batch", "-b", help="从文件批量导入反馈")
    parser.add_argument(
        "--process-queue", "-p", action="store_true", help="处理文件队列中的反馈",
    )
    parser.add_argument(
        "--report", "-r", type=int, default=30, help="生成最近N天的反馈报告",
    )
    parser.add_argument(
        "--quick", "-q", help="快速反馈模式 (格式: 类型|分类|评分|评论)",
    )

    args = parser.parse_args()

    try:
        collector = FeedbackCollector()

        if args.interactive:
            # 交互式反馈收集
            feedback = collector.collect_interactive_feedback()
            if feedback:
                success = collector.submit_feedback(feedback)
                if success:
                    print("✅ 感谢您的反馈！")
                else:
                    print("❌ 反馈提交失败")
            else:
                print("⏹️  反馈收集已取消")

        elif args.batch:
            # 批量导入
            if Path(args.batch).exists():
                count = collector.batch_feedback_from_file(args.batch)
                print(f"✅ 批量导入完成: {count} 条反馈")
            else:
                print(f"❌ 文件不存在: {args.batch}")

        elif args.process_queue:
            # 处理队列
            count = collector.process_queue()
            print(f"✅ 队列处理完成: {count} 条反馈")

        elif args.report:
            # 生成报告
            report = collector.generate_feedback_report(args.report)
            print(report)

            # 保存报告
            report_path = (
                PROJECT_ROOT
                / "monitoring_data"
                / f"feedback_report_{datetime.now().strftime('%Y%m%d')}.md"
            )
            report_path.parent.mkdir(exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n📄 报告已保存: {report_path}")

        elif args.quick:
            # 快速反馈模式
            try:
                parts = args.quick.split("|", 3)
                if len(parts) >= 3:
                    feedback = {
                        "feedback_type": parts[0].strip(),
                        "category": parts[1].strip(),
                        "rating": int(parts[2].strip())
                        if parts[2].strip().isdigit()
                        else None,
                        "comment": parts[3].strip() if len(parts) > 3 else "快速反馈",
                        "user_id": os.environ.get("USER", "quick_user"),
                        "environment": collector._collect_environment_info(),
                    }

                    success = collector.submit_feedback(feedback)
                    if success:
                        print("✅ 快速反馈提交成功！")
                    else:
                        print("❌ 快速反馈提交失败")
                else:
                    print("❌ 格式错误，应为: 类型|分类|评分|评论")
            except Exception as e:
                print(f"❌ 快速反馈处理失败: {e}")

        else:
            print("请使用 --help 查看可用选项")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  操作已取消")
        return 1
    except Exception as e:
        logger.error(f"💥 反馈系统发生异常: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
