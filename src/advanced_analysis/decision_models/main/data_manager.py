"""
数据管理器

负责加载和管理分析所需的数据
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path


class DataManager:
    """数据管理器"""

    def __init__(self, data_path: str = "data/"):
        self.data_path = Path(data_path)
        self.cache = {}
        self.last_update = None

    def load_stock_data(self, stock_code: str) -> Optional[Dict]:
        """加载股票数据"""
        cache_key = f"stock_{stock_code}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            file_path = self.data_path / f"{stock_code}.csv"
            if not file_path.exists():
                return None

            df = pd.read_csv(file_path)
            data = {
                "code": stock_code,
                "name": df.iloc[0]["name"] if "name" in df.columns else "",
                "price": df.iloc[0]["price"] if "price" in df.columns else 0,
                "pe": df.iloc[0]["pe"] if "pe" in df.columns else 0,
                "pb": df.iloc[0]["pb"] if "pb" in df.columns else 0,
                "roe": df.iloc[0]["roe"] if "roe" in df.columns else 0,
                "gross_margin": df.iloc[0]["gross_margin"] if "gross_margin" in df.columns else 0,
                "revenue_growth": df.iloc[0]["revenue_growth"] if "revenue_growth" in df.columns else 0,
                "profit_growth": df.iloc[0]["profit_growth"] if "profit_growth" in df.columns else 0,
                "ma_signal": df.iloc[0]["ma_signal"] if "ma_signal" in df.columns else "neutral",
                "macd_signal": df.iloc[0]["macd_signal"] if "macd_signal" in df.columns else "neutral",
                "rsi": df.iloc[0]["rsi"] if "rsi" in df.columns else 50,
                "bollinger_position": df.iloc[0]["bollinger_position"]
                if "bollinger_position" in df.columns
                else "neutral",
            }

            self.cache[cache_key] = data
            self.last_update = datetime.now()
            return data
        except Exception as e:
            print(f"Error loading stock data: {e}")
            return None

    def load_batch_stock_data(self, stock_codes: List[str]) -> List[Dict]:
        """批量加载股票数据"""
        results = []

        for stock_code in stock_codes:
            data = self.load_stock_data(stock_code)
            if data:
                results.append(data)

        return results

    def save_analysis_result(self, stock_code: str, model_name: str, result: Dict):
        """保存分析结果"""
        try:
            output_path = self.data_path / "analysis_results"
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stock_code}_{model_name}_{timestamp}.json"
            file_path = output_path / filename

            import json

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"Result saved to: {file_path}")
            return str(file_path)
        except Exception as e:
            print(f"Error saving result: {e}")
            return None

    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        self.last_update = None

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self.cache),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "cached_stocks": list(self.cache.keys()),
        }
