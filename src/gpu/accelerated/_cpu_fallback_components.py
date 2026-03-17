"""
CPU fallback 组件选择器与 CLI 绑定。
"""

import logging
from typing import Dict, Optional


def create_component_selector_bindings(price_predictor_cls, data_processor_cls, feature_generator_cls):
    """构建 CPU/GPU 自动选择相关绑定。"""

    class ComponentSelector:
        """智能组件选择器 - 根据环境自动选择GPU或CPU版本"""

        def __init__(self):
            self.gpu_available = self._check_gpu_availability()
            self.logger = logging.getLogger(__name__)

        def _check_gpu_availability(self) -> bool:
            try:
                import cupy as cp

                cp.cuda.Device(0)
                return True
            except Exception:
                return False

        def get_price_predictor(self, gpu_enabled: Optional[bool] = None):
            if gpu_enabled is True:
                from .price_predictor_gpu import GPUPricePredictor

                return GPUPricePredictor(gpu_enabled=True)
            if gpu_enabled is False:
                return price_predictor_cls(gpu_enabled=False)
            if self.gpu_available:
                from .price_predictor_gpu import GPUPricePredictor

                return GPUPricePredictor(gpu_enabled=True)
            self.logger.info("GPU不可用，使用CPU版本")
            return price_predictor_cls(gpu_enabled=False)

        def get_data_processor(self, gpu_enabled: Optional[bool] = None):
            if gpu_enabled is True:
                from .data_processor_gpu import GPUDataProcessor

                return GPUDataProcessor(gpu_enabled=True)
            if gpu_enabled is False:
                return data_processor_cls(gpu_enabled=False)
            if self.gpu_available:
                from .data_processor_gpu import GPUDataProcessor

                return GPUDataProcessor(gpu_enabled=True)
            self.logger.info("GPU不可用，使用CPU版本")
            return data_processor_cls(gpu_enabled=False)

        def get_feature_generator(self, gpu_enabled: Optional[bool] = None):
            if gpu_enabled is True:
                from .feature_generator_gpu import GPUFeatureGenerator

                return GPUFeatureGenerator(gpu_enabled=True)
            if gpu_enabled is False:
                return feature_generator_cls(gpu_enabled=False)
            if self.gpu_available:
                from .feature_generator_gpu import GPUFeatureGenerator

                return GPUFeatureGenerator(gpu_enabled=True)
            self.logger.info("GPU不可用，使用CPU版本")
            return feature_generator_cls(gpu_enabled=False)

        def get_environment_info(self) -> Dict[str, object]:
            return {
                "gpu_available": self.gpu_available,
                "cpu_fallback_available": True,
                "selected_mode": "GPU" if self.gpu_available else "CPU",
            }

    component_selector = ComponentSelector()

    def get_component_selector() -> ComponentSelector:
        return component_selector

    def auto_select_component(component_type: str, gpu_enabled: Optional[bool] = None):
        selector = get_component_selector()
        if component_type == "price_predictor":
            return selector.get_price_predictor(gpu_enabled)
        if component_type == "data_processor":
            return selector.get_data_processor(gpu_enabled)
        if component_type == "feature_generator":
            return selector.get_feature_generator(gpu_enabled)
        raise ValueError(f"不支持的组件类型: {component_type}")

    def main():
        print("🔄 CPU回退版本测试")
        print("=" * 40)

        selector = ComponentSelector()
        print(f"GPU可用性: {selector.gpu_available}")

        print("\n1. 价格预测器测试:")
        predictor = auto_select_component("price_predictor")
        print(f"使用版本: {'GPU' if selector.gpu_available else 'CPU'}")

        import yfinance as yf

        test_data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

        print("训练模型...")
        predictor.train_models(test_data[:200])
        print(f"训练完成，最佳模型: {predictor.performance_stats['best_model'][0]}")

        print("进行预测...")
        prediction = predictor.predict_price(test_data)
        print(f"预测价格: {prediction.predicted_price:.2f}")
        print(f"置信度: {prediction.confidence_score:.2f}")

        print("\n2. 数据处理器测试:")
        processor = auto_select_component("data_processor")
        processed_data = processor.preprocess(test_data[:50])
        print(f"处理完成，数据形状: {processed_data.shape}")

        print("\n3. 特征生成器测试:")
        feature_generator = auto_select_component("feature_generator")
        features = feature_generator.generate_features(test_data[:50])
        print(f"特征生成完成，特征数量: {len(features.columns)}")

        print("\n4. 环境信息:")
        env_info = selector.get_environment_info()
        for key, value in env_info.items():
            print(f"  {key}: {value}")

        print("\n✅ CPU回退版本测试完成")

    return ComponentSelector, get_component_selector, auto_select_component, main
