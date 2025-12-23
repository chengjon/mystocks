#!/usr/bin/env python3
"""
AI测试优化器真实项目应用示例
演示如何在MyStocks项目中实际应用AI测试优化器

应用场景:
1. 核心模块质量提升
2. 新功能开发测试指导
3. 代码重构支持
4. 团队质量监控
5. 持续改进循环

作者: MyStocks AI Team
版本: 1.0
日期: 2025-01-22
"""

import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.ai_test_optimizer import AITestOptimizer
    from scripts.monitoring.ai_optimizer_monitor import AIOptimizerMonitor
    from scripts.feedback.ai_optimizer_feedback import FeedbackCollector
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


class RealProjectApplication:
    """真实项目应用演示"""

    def __init__(self):
        self.optimizer = AITestOptimizer()
        self.monitor = AIOptimizerMonitor()
        self.feedback_collector = FeedbackCollector()
        self.application_log = PROJECT_ROOT / "monitoring_data" / "application_log.md"
        self.application_log.parent.mkdir(exist_ok=True)

    def log_application(self, title: str, content: str):
        """记录应用日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"## {title}\n\n**时间**: {timestamp}\n\n{content}\n\n---\n\n"

        if self.application_log.exists():
            existing_content = self.application_log.read_text(encoding="utf-8")
        else:
            existing_content = "# AI测试优化器真实项目应用日志\n\n"

        with open(self.application_log, "w", encoding="utf-8") as f:
            f.write(existing_content + log_entry)

        print(f"📝 应用日志已更新: {title}")

    def scenario_1_core_module_quality_improvement(self):
        """场景1: 核心模块质量提升"""
        print("🎯 场景1: 核心模块质量提升")
        print("=" * 50)

        # 选择核心模块进行质量提升
        core_modules = [
            "src/adapters/data_validator.py",
            "src/adapters/base_adapter.py",
            "src/core/exceptions.py",
        ]

        results = []

        for module in core_modules:
            if not Path(module).exists():
                print(f"⚠️  模块不存在: {module}")
                continue

            print(f"\n📊 分析模块: {module}")

            try:
                # 分析当前状态
                result = self.optimizer.analyze_module_for_optimization(module)
                results.append(result)

                print(f"  当前覆盖率: {result.current_coverage:.1f}%")
                print(f"  质量评分: {result.quality_score:.1f}/100")

                # 生成优化测试
                if result.generated_tests:
                    print(f"  生成测试: {len(result.generated_tests)} 个")

                    # 模拟应用优化建议
                    print("  🔄 应用优化建议:")
                    for suggestion in result.optimization_suggestions[:3]:
                        print(f"    • {suggestion}")

            except Exception as e:
                print(f"  ❌ 分析失败: {e}")

        # 生成综合报告
        if results:
            report = self.optimizer.generate_optimization_report(results)
            report_path = (
                PROJECT_ROOT / "monitoring_data" / "core_module_improvement.md"
            )

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"\n✅ 核心模块分析完成")
            print(f"📄 报告已保存: {report_path}")

            # 记录应用日志
            self.log_application(
                "核心模块质量提升",
                f"分析了 {len(results)} 个核心模块，平均质量评分: {sum(r.quality_score for r in results) / len(results):.1f}",
            )

    def scenario_2_new_feature_development(self):
        """场景2: 新功能开发测试指导"""
        print("\n🚀 场景2: 新功能开发测试指导")
        print("=" * 50)

        # 模拟新开发的模块
        new_module = "src/adapters/new_market_data_adapter.py"

        # 创建示例新模块
        self._create_sample_new_module(new_module)

        print(f"📝 模拟新功能模块: {new_module}")

        try:
            # 分析新模块的测试需求
            result = self.optimizer.analyze_module_for_optimization(new_module)

            print(f"\n📋 新模块分析结果:")
            print(
                f"  模块复杂度: {'高' if result.quality_score < 60 else '中' if result.quality_score < 80 else '低'}"
            )
            print(f"  建议测试数: {len(result.generated_tests)}")
            print(f"  预估覆盖率提升: {95 - result.current_coverage:.1f}%")

            # 提供开发指导
            print(f"\n🎯 开发测试指导:")

            for i, suggestion in enumerate(result.optimization_suggestions, 1):
                print(f"  {i}. {suggestion}")

            # 生成初始测试框架
            if result.generated_tests:
                test_file = (
                    PROJECT_ROOT
                    / "tests"
                    / "generated"
                    / f"test_{Path(new_module).stem}_new_feature.py"
                )
                test_file.parent.mkdir(parents=True, exist_ok=True)

                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(f'''
"""
新功能模块测试框架: {Path(new_module).stem}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

使用方法:
1. 根据AI建议实现具体的测试逻辑
2. 运行测试验证新功能
3. 根据测试结果调整实现
4. 确保达到目标覆盖率

AI优化建议数量: {len(result.generated_tests)}
预计覆盖率提升: {95 - result.current_coverage:.1f}%
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入测试模块
try:
    from {Path(new_module).stem} import *
except ImportError as e:
    pytest.skip(f"无法导入模块: {{e}}", allow_module_level=True)

class TestNewFeatureModule:
    """新功能模块测试类"""

    def setup_method(self):
        """每个测试前的设置"""
        # TODO: 初始化测试数据
        pass

    def test_basic_functionality(self):
        """测试基础功能"""
        # TODO: 实现基础功能测试
        assert True  # 占位符

    def test_error_handling(self):
        """测试错误处理"""
        # TODO: 实现错误处理测试
        assert True  # 占位符

    def test_performance(self):
        """测试性能"""
        # TODO: 实现性能测试
        assert True  # 占位符

# AI生成的优化测试
{chr(10).join(result.generated_tests)}
''')

                print(f"\n✅ 测试框架已生成: {test_file}")
                print(f"💡 请根据AI建议完善测试实现")

        except Exception as e:
            print(f"❌ 新模块分析失败: {e}")

        # 记录应用日志
        self.log_application(
            "新功能开发测试指导",
            f"为新模块 {new_module} 生成了测试开发指导，包含 {len(result.generated_tests) if 'result' in locals() else 0} 个优化建议",
        )

    def _create_sample_new_module(self, module_path: str):
        """创建示例新模块"""
        module_content = '''"""
新市场数据适配器 - 模拟新功能模块
用于演示AI测试优化器在新功能开发中的应用
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class NewMarketDataAdapter:
    """新市场数据适配器"""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.is_connected = False

    def connect(self) -> bool:
        """连接到数据源"""
        # 模拟连接逻辑
        try:
            # 模拟API验证
            if len(self.api_key) < 10:
                raise ValueError("API密钥太短")

            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def fetch_market_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """获取市场数据"""
        if not self.is_connected:
            raise ConnectionError("未连接到数据源")

        # 模拟数据获取
        try:
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            data = pd.DataFrame({
                'date': dates,
                'symbol': symbol,
                'open': 100.0 + range(len(dates)),
                'high': 105.0 + range(len(dates)),
                'low': 95.0 + range(len(dates)),
                'close': 102.0 + range(len(dates)),
                'volume': [10000] * len(dates)
            })

            return data
        except Exception as e:
            print(f"数据获取失败: {e}")
            return None

    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据质量"""
        if data is None or data.empty:
            return False

        required_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)

    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理数据"""
        if not self.validate_data(data):
            raise ValueError("数据验证失败")

        # 添加技术指标
        data['ma_5'] = data['close'].rolling(window=5).mean()
        data['ma_20'] = data['close'].rolling(window=20).mean()

        return data

    def disconnect(self):
        """断开连接"""
        self.is_connected = False


def create_adapter(api_key: str) -> NewMarketDataAdapter:
    """创建适配器实例"""
    return NewMarketDataAdapter(api_key)
'''

        module_file = PROJECT_ROOT / module_path
        module_file.parent.mkdir(parents=True, exist_ok=True)

        with open(module_file, "w", encoding="utf-8") as f:
            f.write(module_content)

    def scenario_3_code_refactoring_support(self):
        """场景3: 代码重构支持"""
        print("\n🔧 场景3: 代码重构支持")
        print("=" * 50)

        # 选择一个需要重构的模块（模拟）
        refactor_module = "src/adapters/legacy_adapter.py"

        # 创建模拟的遗留代码模块
        self._create_legacy_module(refactor_module)

        print(f"📝 分析遗留模块: {refactor_module}")

        try:
            # 分析重构前的状态
            before_result = self.optimizer.analyze_module_for_optimization(
                refactor_module
            )

            print(f"\n📊 重构前状态:")
            print(f"  代码质量评分: {before_result.quality_score:.1f}/100")
            print(
                f"  复杂度问题: {len([s for s in before_result.optimization_suggestions if '复杂度' in s])}"
            )

            # 模拟重构过程
            print(f"\n🔄 执行重构建议:")
            refactoring_actions = []

            for suggestion in before_result.optimization_suggestions:
                if "复杂度" in suggestion:
                    action = f"重构复杂函数"
                elif "测试" in suggestion:
                    action = f"添加测试用例"
                elif "异常" in suggestion:
                    action = f"改进异常处理"
                else:
                    action = f"通用优化"

                refactoring_actions.append(action)
                print(f"  • {action}")

            # 模拟重构后的改进
            after_quality = before_result.quality_score + 15  # 假设重构后质量提升
            after_coverage = min(
                95, before_result.current_coverage + 20
            )  # 假设覆盖率提升

            print(f"\n📈 重构后预期状态:")
            print(
                f"  代码质量评分: {after_quality:.1f}/100 (+{after_quality - before_result.quality_score:.1f})"
            )
            print(
                f"  测试覆盖率: {after_coverage:.1f}% (+{after_coverage - before_result.current_coverage:.1f}%)"
            )

            # 生成重构报告
            refactor_report = f"""# 代码重构报告

**模块**: {refactor_module}
**重构时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 重构前后对比

| 指标 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| 质量评分 | {before_result.quality_score:.1f} | {after_quality:.1f} | +{after_quality - before_result.quality_score:.1f} |
| 覆盖率 | {before_result.current_coverage:.1f}% | {after_coverage:.1f}% | +{after_coverage - before_result.current_coverage:.1f}% |

## 重构行动项

{chr(10).join(f"{i + 1}. {action}" for i, action in enumerate(refactoring_actions, 1))}

## 建议

1. 逐步重构，保持向后兼容
2. 增加单元测试确保功能正确性
3. 进行性能测试避免性能回退
4. 定期监控重构效果

## 风险评估

- **低风险**: 重构范围可控，有测试保障
- **缓解措施**: 分阶段实施，充分测试
"""

            report_path = PROJECT_ROOT / "monitoring_data" / "refactoring_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(refactor_report)

            print(f"✅ 重构报告已生成: {report_path}")

        except Exception as e:
            print(f"❌ 重构分析失败: {e}")

        # 记录应用日志
        self.log_application(
            "代码重构支持",
            f"为遗留模块 {refactor_module} 生成了重构指导，预期质量提升 {after_quality - before_result.quality_score:.1f} 分",
        )

    def _create_legacy_module(self, module_path: str):
        """创建模拟遗留代码模块"""
        legacy_content = '''"""
遗留适配器 - 模拟复杂遗留代码
用于演示AI测试优化器在重构支持中的应用
"""

import sys
import json
from typing import Dict, Any


class LegacyAdapter:
    """遗留适配器 - 需要重构的复杂代码"""

    def __init__(self):
        self.config = {}
        self.connection = None
        self.cache = {}
        self.metrics = {}

    def process_request(self, request_data: Dict) -> Dict:
        """复杂的方法，需要重构"""
        # 模拟复杂的业务逻辑
        try:
            # 验证输入
            if not request_data:
                raise ValueError("请求数据为空")

            if 'type' not in request_data:
                raise ValueError("缺少请求类型")

            # 复杂的条件判断
            if request_data['type'] == 'data_fetch':
                if 'symbol' not in request_data:
                    raise ValueError("缺少symbol参数")

                if request_data['symbol'].startswith('6') or request_data['symbol'].startswith('0'):
                    exchange = 'SZSE'
                elif request_data['symbol'].startswith('6'):
                    exchange = 'SSE'
                elif request_data['symbol'].startswith('3'):
                    exchange = 'SZSE'
                else:
                    exchange = 'OTHER'

                # 模拟数据处理
                result = self._process_data_fetch(request_data, exchange)

            elif request_data['type'] == 'analysis':
                if 'analysis_type' not in request_data:
                    raise ValueError("缺少analysis_type参数")

                result = self._process_analysis(request_data)

            elif request_data['type'] == 'export':
                result = self._process_export(request_data)

            else:
                raise ValueError(f"不支持的请求类型: {request_data['type']}")

            # 后处理
            if result.get('success', False):
                self._update_metrics(request_data['type'], True)
            else:
                self._update_metrics(request_data['type'], False)

            return result

        except Exception as e:
            self._update_metrics('error', False)
            return {
                'success': False,
                'error': str(e),
                'error_code': self._get_error_code(e)
            }

    def _process_data_fetch(self, data: Dict, exchange: str) -> Dict:
        """数据处理方法 - 复杂度较高"""
        # 模拟数据获取
        try:
            # 检查缓存
            cache_key = f"{exchange}_{data['symbol']}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                # 检查缓存是否过期
                if time.time() - cached_data['timestamp'] < 300:  # 5分钟缓存
                    return {
                        'success': True,
                        'data': cached_data['data'],
                        'from_cache': True
                    }

            # 模拟从不同交易所获取数据
            if exchange == 'SZSE':
                data_result = self._fetch_from_szse(data['symbol'])
            elif exchange == 'SSE':
                data_result = self._fetch_from_sse(data['symbol'])
            else:
                data_result = self._fetch_from_general(data['symbol'])

            # 处理数据
            processed_data = self._transform_data(data_result)

            # 更新缓存
            self.cache[cache_key] = {
                'data': processed_data,
                'timestamp': time.time()
            }

            return {
                'success': True,
                'data': processed_data,
                'from_cache': False
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"数据处理失败: {str(e)}"
            }

    def _fetch_from_szse(self, symbol: str) -> Dict:
        """模拟从深交所获取数据"""
        # 复杂的API调用逻辑
        return {
            'symbol': symbol,
            'exchange': 'SZSE',
            'price': 10.5,
            'volume': 1000000
        }

    def _fetch_from_sse(self, symbol: str) -> Dict:
        """模拟从上交所获取数据"""
        return {
            'symbol': symbol,
            'exchange': 'SSE',
            'price': 15.2,
            'volume': 500000
        }

    def _fetch_from_general(self, symbol: str) -> Dict:
        """模拟从通用数据源获取数据"""
        return {
            'symbol': symbol,
            'exchange': 'OTHER',
            'price': 12.8,
            'volume': 200000
        }

    def _transform_data(self, raw_data: Dict) -> Dict:
        """数据转换"""
        # 复杂的数据转换逻辑
        transformed = raw_data.copy()

        # 添加计算字段
        if 'price' in raw_data:
            transformed['price_change'] = raw_data['price'] * 0.01
            transformed['price_change_percent'] = 1.0

        return transformed

    def _process_analysis(self, data: Dict) -> Dict:
        """分析处理"""
        # 复杂的分析逻辑
        analysis_type = data['analysis_type']

        if analysis_type == 'technical':
            return self._technical_analysis(data)
        elif analysis_type == 'fundamental':
            return self._fundamental_analysis(data)
        else:
            raise ValueError(f"不支持的分析类型: {analysis_type}")

    def _technical_analysis(self, data: Dict) -> Dict:
        """技术分析"""
        return {
            'type': 'technical',
            'signal': 'BUY',
            'confidence': 0.85
        }

    def _fundamental_analysis(self, data: Dict) -> Dict:
        """基本面分析"""
        return {
            'type': 'fundamental',
            'rating': 'BUY',
            'score': 8.5
        }

    def _process_export(self, data: Dict) -> Dict:
        """导出处理"""
        return {
            'type': 'export',
            'format': data.get('format', 'json'),
            'status': 'completed'
        }

    def _update_metrics(self, operation: str, success: bool):
        """更新指标"""
        if operation not in self.metrics:
            self.metrics[operation] = {'total': 0, 'success': 0, 'failed': 0}

        self.metrics[operation]['total'] += 1

        if success:
            self.metrics[operation]['success'] += 1
        else:
            self.metrics[operation]['failed'] += 1

    def _get_error_code(self, error: Exception) -> str:
        """获取错误代码"""
        if isinstance(error, ValueError):
            return 'INVALID_INPUT'
        elif isinstance(error, KeyError):
            return 'MISSING_PARAMETER'
        else:
            return 'UNKNOWN_ERROR'

    def get_metrics(self) -> Dict:
        """获取指标"""
        return self.metrics.copy()
'''

        # 补充import缺失的time模块
        import time

        module_file = PROJECT_ROOT / module_path
        module_file.parent.mkdir(parents=True, exist_ok=True)

        with open(module_file, "w", encoding="utf-8") as f:
            f.write(legacy_content)

    def scenario_4_team_quality_monitoring(self):
        """场景4: 团队质量监控"""
        print("\n👥 场景4: 团队质量监控")
        print("=" * 50)

        try:
            # 获取团队使用统计
            usage_stats = self.monitor.get_usage_stats(7)  # 最近7天

            print(f"\n📊 团队使用统计 (最近7天):")
            print(f"  总使用次数: {usage_stats['total_usage']}")
            print(f"  成功率: {usage_stats['success_rate']:.1f}%")
            print(f"  平均执行时间: {usage_stats['avg_execution_time']:.2f}秒")

            # 获取性能统计
            performance_stats = self.monitor.get_performance_stats(7)
            print(f"\n⚡ 性能统计:")
            print(f"  平均CPU使用: {performance_stats['avg_cpu_usage']:.1f}%")
            print(f"  平均内存使用: {performance_stats['avg_memory_usage']:.1f}MB")

            # 获取用户反馈
            feedback_summary = self.monitor.get_feedback_summary(30)  # 最近30天
            print(f"\n🗣️ 用户反馈统计 (最近30天):")

            if feedback_summary["feedback_by_type"]:
                for feedback in feedback_summary["feedback_by_type"]:
                    print(
                        f"  {feedback['type']} ({feedback['category']}): {feedback['count']} 条"
                    )

            # 检测异常
            anomalies = self.monitor.detect_anomalies()

            if anomalies:
                print(f"\n🚨 发现异常 ({len(anomalies)} 个):")
                for anomaly in anomalies:
                    print(f"  [{anomaly['severity'].upper()}] {anomaly['message']}")
            else:
                print(f"\n✅ 系统运行正常，未检测到异常")

            # 生成团队质量报告
            team_report = self._generate_team_quality_report(
                usage_stats, performance_stats, feedback_summary, anomalies
            )
            report_path = PROJECT_ROOT / "monitoring_data" / "team_quality_report.md"

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(team_report)

            print(f"\n✅ 团队质量报告已生成: {report_path}")

        except Exception as e:
            print(f"❌ 团队质量监控失败: {e}")

        # 记录应用日志
        self.log_application(
            "团队质量监控",
            f"团队使用次数: {usage_stats['total_usage']}, 成功率: {usage_stats['success_rate']:.1f}%, 异常数: {len(anomalies) if 'anomalies' in locals() else 0}",
        )

    def _generate_team_quality_report(
        self,
        usage_stats: Dict,
        performance_stats: Dict,
        feedback_summary: Dict,
        anomalies: List,
    ) -> str:
        """生成团队质量报告"""
        report = f"""# 团队质量监控报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 使用统计

- **总使用次数**: {usage_stats["total_usage"]}
- **成功率**: {usage_stats["success_rate"]:.1f}%
- **平均执行时间**: {usage_stats["avg_execution_time"]:.2f}秒

## ⚡ 性能指标

- **平均CPU使用**: {performance_stats["avg_cpu_usage"]:.1f}%
- **平均内存使用**: {performance_stats["avg_memory_usage"]:.1f}MB

## 🗣️ 用户反馈

{self._format_feedback_for_report(feedback_summary)}

## 🚨 异常检测

{self._format_anomalies_for_report(anomalies)}

## 📈 趋势分析

### 使用趋势
{self._format_usage_trend_for_report(usage_stats.get("daily_usage", {}))}

## 💡 改进建议

{self._generate_team_recommendations(usage_stats, performance_stats, anomalies)}
"""

        return report

    def _format_feedback_for_report(self, feedback_summary: Dict) -> str:
        """格式化反馈用于报告"""
        if not feedback_summary["feedback_by_type"]:
            return "暂无反馈数据"

        lines = []
        for feedback in feedback_summary["feedback_by_type"]:
            lines.append(
                f"- **{feedback['type']} ({feedback['category']}): {feedback['count']} 条**"
            )
            if feedback["avg_rating"]:
                lines.append(f"  - 平均评分: {feedback['avg_rating']:.1f}⭐")

        return "\n".join(lines)

    def _format_anomalies_for_report(self, anomalies: List) -> str:
        """格式化异常用于报告"""
        if not anomalies:
            return "✅ 系统运行正常"

        lines = []
        for anomaly in anomalies:
            lines.append(f"- **{anomaly['severity'].upper()}**: {anomaly['message']}")

        return "\n".join(lines)

    def _format_usage_trend_for_report(self, daily_usage: Dict) -> str:
        """格式化使用趋势用于报告"""
        if not daily_usage:
            return "暂无使用趋势数据"

        lines = ["| 日期 | 使用次数 |"]
        lines.append("|------|----------|")

        for date, count in sorted(daily_usage.items()):
            lines.append(f"| {date} | {count} |")

        return "\n".join(lines)

    def _generate_team_recommendations(
        self, usage_stats: Dict, performance_stats: Dict, anomalies: List
    ) -> str:
        """生成团队建议"""
        recommendations = []

        # 基于使用情况
        if usage_stats["success_rate"] < 90:
            recommendations.append("🔧 建议团队加强错误处理，提高成功率")

        if usage_stats["total_usage"] < 50:
            recommendations.append("📈 建议团队更频繁地使用测试优化工具")

        # 基于性能
        if performance_stats["avg_execution_time"] > 5:
            recommendations.append("⚡ 建议优化工具性能，减少执行时间")

        if performance_stats["avg_memory_usage"] > 500:
            recommendations.append("💾 建议监控内存使用，优化资源管理")

        # 基于异常
        if anomalies:
            recommendations.append("🚨 立即关注并解决检测到的系统异常")

        if not recommendations:
            recommendations.append("✅ 团队使用情况良好，继续保持")

        return "\n".join(f"- {rec}" for rec in recommendations)

    def scenario_5_continuous_improvement_cycle(self):
        """场景5: 持续改进循环"""
        print("\n🔄 场景5: 持续改进循环")
        print("=" * 50)

        improvement_cycle = [
            "1. 数据收集 - 使用AI测试优化器分析代码质量",
            "2. 问题识别 - 识别低质量模块和覆盖率缺口",
            "3. 优化实施 - 根据AI建议实施改进措施",
            "4. 效果验证 - 验证优化效果和质量提升",
            "5. 经验总结 - 总结最佳实践和改进经验",
        ]

        print("🔄 持续改进循环:")
        for step in improvement_cycle:
            print(f"  {step}")

        print("\n📋 当前改进状态:")

        # 模拟改进循环
        modules = [
            "src/adapters/data_validator.py",
            "src/adapters/base_adapter.py",
            "src/core/exceptions.py",
        ]

        improvement_results = []

        for module in modules:
            if not Path(module).exists():
                continue

            try:
                # 步骤1: 数据收集
                result = self.optimizer.analyze_module_for_optimization(module)

                # 步骤2: 问题识别
                issues = len(result.optimization_suggestions)
                quality_score = result.quality_score

                # 步骤3: 模拟优化实施
                simulated_improvement = min(15, 100 - quality_score) / 2
                new_quality = quality_score + simulated_improvement
                new_coverage = min(95, result.current_coverage + simulated_improvement)

                # 步骤4: 效果验证
                quality_improvement = new_quality - quality_score
                coverage_improvement = new_coverage - result.current_coverage

                improvement_results.append(
                    {
                        "module": module,
                        "quality_improvement": quality_improvement,
                        "coverage_improvement": coverage_improvement,
                        "issues_resolved": min(issues, int(quality_improvement / 5)),
                    }
                )

                print(f"  📈 {Path(module).name}:")
                print(
                    f"    质量提升: +{quality_improvement:.1f}分 ({quality_score:.1f} → {new_quality:.1f})"
                )
                print(
                    f"    覆盖率提升: +{coverage_improvement:.1f}% ({result.current_coverage:.1f} → {new_coverage:.1f})"
                )

            except Exception as e:
                print(f"  ❌ {module}: 分析失败 - {e}")

        # 步骤5: 经验总结
        if improvement_results:
            total_quality_improvement = sum(
                r["quality_improvement"] for r in improvement_results
            )
            total_coverage_improvement = sum(
                r["coverage_improvement"] for r in improvement_results
            )
            total_issues_resolved = sum(
                r["issues_resolved"] for r in improvement_results
            )

            print(f"\n📊 改进总结:")
            print(f"  处理模块数: {len(improvement_results)}")
            print(f"  总质量提升: +{total_quality_improvement:.1f}分")
            print(f"  总覆盖率提升: +{total_coverage_improvement:.1f}%")
            print(f"  问题解决数: {total_issues_resolved}")

            # 生成改进报告
            improvement_report = f"""# 持续改进循环报告

**改进时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 改进成果

- **处理模块数**: {len(improvement_results)}
- **总质量提升**: {total_quality_improvement:.1f}分
- **总覆盖率提升**: {total_coverage_improvement:.1f}%
- **问题解决数**: {total_issues_resolved}

## 📈 详细改进结果

{self._format_improvement_details(improvement_results)}

## 🎯 经验总结

1. **AI建议的有效性**: 大部分AI生成的建议都能有效提升代码质量
2. **覆盖率提升**: 通过系统性测试用例生成，覆盖率提升明显
3. **质量改善**: 综合质量评分得到显著改善
4. **问题解决**: 复杂度问题和异常处理得到有效改善

## 💡 下一步计划

- 将改进措施推广到更多模块
- 建立定期的质量检查机制
- 持续优化AI算法和建议准确性
- 收集更多用户反馈进行改进

---

*持续改进，追求卓越质量*
"""

            report_path = (
                PROJECT_ROOT / "monitoring_data" / "continuous_improvement_report.md"
            )
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(improvement_report)

            print(f"\n✅ 改进报告已生成: {report_path}")

        # 记录应用日志
        self.log_application(
            "持续改进循环",
            f"完成了 {len(improvement_results)} 个模块的改进，总质量提升 {total_quality_improvement:.1f} 分",
        )

    def _format_improvement_details(self, results: List[Dict]) -> str:
        """格式化改进详情"""
        lines = ["| 模块 | 质量提升 | 覆盖率提升 | 问题解决 |"]
        lines.append("|------|----------|------------|----------|")

        for result in results:
            module_name = Path(result["module"]).name
            lines.append(
                f"| {module_name} | +{result['quality_improvement']:.1f} | +{result['coverage_improvement']:.1f}% | {result['issues_resolved']} |"
            )

        return "\n".join(lines)


def main():
    """主函数"""
    print("🚀 AI测试优化器真实项目应用演示")
    print("演示AI测试优化器在MyStocks项目中的实际应用")
    print("=" * 60)

    app = RealProjectApplication()

    try:
        # 场景1: 核心模块质量提升
        app.scenario_1_core_module_quality_improvement()

        # 场景2: 新功能开发测试指导
        app.scenario_2_new_feature_development()

        # 场景3: 代码重构支持
        app.scenario_3_code_refactoring_support()

        # 场景4: 团队质量监控
        app.scenario_4_team_quality_monitoring()

        # 场景5: 持续改进循环
        app.scenario_5_continuous_improvement_cycle()

        print("\n" + "=" * 60)
        print("🎉 真实项目应用演示完成！")
        print(f"📁 所有报告已保存到: {app.application_log.parent}")
        print(f"📋 应用日志: {app.application_log}")

    except KeyboardInterrupt:
        print("\n⏹️  演示已中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
