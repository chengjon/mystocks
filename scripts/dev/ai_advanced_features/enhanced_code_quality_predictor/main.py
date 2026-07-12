#!/usr/bin/env python3
"""增强代码质量预测器
集成机器学习和深度学习技术的高级代码质量分析系统
"""

import ast
import json
import logging
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import numpy as np


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """主入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增强代码质量预测器")
    parser.add_argument("files", nargs="+", help="要分析的Python文件")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = EnhancedCodeAnalyzer()
    predictor = QualityPredictor()
    feature_extractor = FeatureExtractor()

    results = []

    print("🚀 启动增强代码质量预测器")
    print("=" * 50)

    for file_path in args.files:
        if not Path(file_path).exists():
            print(f"⚠️ 文件不存在: {file_path}")
            continue

        print(f"\n🔍 分析文件: {file_path}")

        try:
            # 执行高级分析
            advanced_metrics = analyzer.analyze_file_advanced(file_path)

            # 计算基础指标
            with open(file_path, encoding="utf-8") as f:
                source_code = f.read()

            # 简化的基础指标计算
            lines_of_code = len(
                [line for line in source_code.split("\n") if line.strip()],
            )
            cyclomatic_complexity = analyzer.deep_analyzer.complexity_analysis(
                ast.parse(source_code),
            )["cognitive_complexity"]

            code_metrics = CodeMetrics(
                file_path=file_path,
                lines_of_code=lines_of_code,
                cyclomatic_complexity=cyclomatic_complexity,
                cognitive_complexity=cyclomatic_complexity,
                maintainability_index=70.0,  # 简化
                technical_debt=0.0,
                bug_risk_score=0.0,
                security_vulnerabilities=0,
                test_coverage_gap=0.0,
                duplication_ratio=0.0,
                code_churn=0.0,
                developer_experience=1.0,
                change_frequency=0.0,
            )

            # 特征提取
            features = feature_extractor.extract_features(
                code_metrics,
                advanced_metrics,
            )

            # 质量预测
            prediction = predictor.predict_quality(features)
            prediction.file_path = file_path

            results.append(
                {
                    "metrics": asdict(advanced_metrics),
                    "prediction": asdict(prediction),
                    "features": features.tolist(),
                },
            )

            print(
                f"✅ 分析完成: {prediction.overall_score:.1f}分 ({prediction.risk_level})",
            )

        except Exception as e:
            print(f"❌ 分析失败: {e}")
            continue

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 结果已保存到: {args.output}")

    # 打印摘要
    print("\n📊 分析摘要:")
    print(f"   分析文件数: {len(results)}")
    if results:
        avg_score = np.mean([r["prediction"]["overall_score"] for r in results])
        risk_distribution = Counter([r["prediction"]["risk_level"] for r in results])

        print(f"   平均质量分: {avg_score:.1f}")
        print(f"   风险分布: {dict(risk_distribution)}")
