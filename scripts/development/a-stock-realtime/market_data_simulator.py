"""
A股市场数据模拟器
模拟实时推送A股指数、股票行情数据
"""
import random
import time
from datetime import datetime
from typing import Dict, Any


class MarketDataSimulator:
    """A股市场数据模拟器"""

    def __init__(self):
        # 初始化指数数据
        self.indices = {
            '000001': {'name': '上证指数', 'value': 3245.67, 'change': 1.23},
            '399001': {'name': '深证成指', 'value': 10234.89, 'change': 0.87},
            '399006': {'name': '创业板指', 'value': 2145.32, 'change': -0.34},
            '000688': {'name': '科创50', 'value': 987.45, 'change': 1.56},
        }

        # 初始化股票数据
        self.stocks = {
            '600519': {'name': '贵州茅台', 'price': 1856.00, 'change': 2.35},
            '300750': {'name': '宁德时代', 'price': 245.67, 'change': -1.23},
            '601318': {'name': '中国平安', 'price': 52.34, 'change': 0.89},
            '000858': {'name': '五粮液', 'price': 178.45, 'change': 1.56},
            '002594': {'name': '比亚迪', 'price': 267.89, 'change': 3.12},
        }

        # 市场统计数据
        self.market_stats = {
            'limitUp': 45,
            'limitDown': 12,
            'northBound': 52.3,
            'totalVolume': 8563,
            'riseCount': 2845,
            'fallCount': 1892,
        }

        # 热门板块
        self.hotSectors = [
            {'name': '新能源汽车', 'change': 3.45, 'leader': '比亚迪', 'leaders': 3},
            {'name': '半导体', 'change': 2.87, 'leader': '中芯国际', 'leaders': 5},
            {'name': '人工智能', 'change': 2.34, 'leader': '科大讯飞', 'leaders': 4},
            {'name': '国防军工', 'change': -0.89, 'leader': '中航沈飞', 'leaders': 2},
        ]

    def _random_fluctuation(self, base_value: float, volatility: float = 0.002) -> float:
        """生成随机波动"""
        return base_value * (1 + random.uniform(-volatility, volatility))

    def update_index(self, code: str) -> Dict[str, Any]:
        """更新单个指数数据"""
        if code not in self.indices:
            return None

        index = self.indices[code]
        old_value = index['value']
        new_value = self._random_fluctuation(old_value, 0.001)
        change_percent = ((new_value - old_value) / old_value) * 100

        self.indices[code] = {
            **index,
            'value': new_value,
            'change': change_percent,
            'changeAmount': new_value - old_value,
            'volume': f'{random.randint(2000, 5000)}亿',
            'timestamp': datetime.now().isoformat()
        }

        return {
            'code': code,
            **self.indices[code]
        }

    def update_stock(self, code: str) -> Dict[str, Any]:
        """更新单个股票数据"""
        if code not in self.stocks:
            return None

        stock = self.stocks[code]
        old_price = stock['price']
        new_price = self._random_fluctuation(old_price, 0.003)
        change_percent = ((new_price - old_price) / old_price) * 100

        self.stocks[code] = {
            **stock,
            'price': new_price,
            'change': change_percent,
            'volume': f'{random.randint(1, 50)}万手',
            'timestamp': datetime.now().isoformat()
        }

        return {
            'code': code,
            **self.stocks[code]
        }

    def update_market_stats(self) -> Dict[str, Any]:
        """更新市场统计数据"""
        # 随机波动
        self.market_stats['limitUp'] += random.randint(-2, 3)
        self.market_stats['limitDown'] += random.randint(-1, 2)
        self.market_stats['northBound'] += random.uniform(-1, 1)
        self.market_stats['riseCount'] += random.randint(-50, 50)
        self.market_stats['fallCount'] += random.randint(-30, 30)

        return {
            **self.market_stats,
            'timestamp': datetime.now().isoformat()
        }

    def get_full_snapshot(self) -> Dict[str, Any]:
        """获取完整市场快照"""
        return {
            'type': 'snapshot',
            'timestamp': datetime.now().isoformat(),
            'indices': [
                {'code': code, **self.indices[code]}
                for code in self.indices.keys()
            ],
            'stocks': [
                {'code': code, **self.stocks[code]}
                for code in self.stocks.keys()
            ],
            'marketStats': self.market_stats,
            'hotSectors': self.hotSectors
        }

    def get_incremental_update(self) -> Dict[str, Any]:
        """获取增量更新（随机选择2-3个股票/指数更新）"""
        updates = []

        # 随机更新指数
        num_indices = random.randint(1, 2)
        index_codes = random.sample(list(self.indices.keys()), num_indices)
        for code in index_codes:
            updates.append({
                'type': 'index',
                'data': self.update_index(code)
            })

        # 随机更新股票
        num_stocks = random.randint(2, 3)
        stock_codes = random.sample(list(self.stocks.keys()), num_stocks)
        for code in stock_codes:
            updates.append({
                'type': 'stock',
                'data': self.update_stock(code)
            })

        # 偶尔更新市场统计
        if random.random() < 0.3:
            updates.append({
                'type': 'market_stats',
                'data': self.update_market_stats()
            })

        return {
            'type': 'incremental',
            'timestamp': datetime.now().isoformat(),
            'updates': updates
        }


# 测试代码
if __name__ == '__main__':
    simulator = MarketDataSimulator()

    print("=== 初始市场快照 ===")
    snapshot = simulator.get_full_snapshot()
    print(f"指数数量: {len(snapshot['indices'])}")
    print(f"股票数量: {len(snapshot['stocks'])}")
    print(f"\n上证指数: {snapshot['indices'][0]}")
    print(f"\n贵州茅台: {snapshot['stocks'][0]}")

    print("\n=== 模拟实时更新 ===")
    for i in range(5):
        update = simulator.get_incremental_update()
        print(f"\n[{i+1}] 更新时间: {update['timestamp']}")
        for u in update['updates']:
            print(f"  {u['type']}: {u['data']['code']} - {u['data'].get('value', u['data'].get('price'))}")
        time.sleep(1)
