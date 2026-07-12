"""Mock 数据子模块"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict


logger = logging.getLogger(__name__)


class MockTechnicalDataMixin:
    """Mock 技术指标与资金流向数据"""

    def _generate_mock_fund_flow(self, symbol: str = "600519", timeframe: str = "1", **kwargs) -> Dict[str, Any]:
        """生成模拟资金流向数据

        Args:
            symbol: 股票代码，默认600519（贵州茅台）
            timeframe: 时间维度，1=今日，3=3日，5=5日，10=10日
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD

        Returns:
            资金流向数据

        """
        # 解析时间维度
        timeframe_days = {"1": 1, "3": 3, "5": 5, "10": 10}.get(timeframe, 1)

        # 解析日期范围参数
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        # 生成日期列表
        dates = []

        if start_date and end_date:
            # 如果提供了日期范围，使用指定范围
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")

                # 确保开始日期不晚于结束日期
                if start_dt > end_dt:
                    start_dt, end_dt = end_dt, start_dt

                # 生成日期范围内的所有日期
                current_dt = start_dt
                while current_dt <= end_dt:
                    dates.append(current_dt.strftime("%Y-%m-%d"))
                    current_dt += timedelta(days=1)

                logger.info("使用指定日期范围: %(start_date)s 到 %(end_date)s, 共 {len(dates)} 天")

            except ValueError:
                logger.warning("日期格式错误，使用默认时间维度: %(e)s")
                # 回退到默认时间维度逻辑
                for i in range(timeframe_days):
                    date = datetime.now() - timedelta(days=i)
                    dates.append(date.strftime("%Y-%m-%d"))
        else:
            # 没有提供日期范围，使用timeframe逻辑
            for i in range(timeframe_days):
                date = datetime.now() - timedelta(days=i)
                dates.append(date.strftime("%Y-%m-%d"))

            logger.info("使用时间维度 %(timeframe)s, 共 {len(dates)} 天")

        # 生成资金流向数据
        fund_flow_data = []
        total_main_inflow = 0
        total_main_outflow = 0
        total_retain_inflow = 0
        total_retain_outflow = 0

        for i, date in enumerate(dates):
            # 主力资金（万元）
            main_inflow = random.uniform(5000, 50000) if i == 0 else random.uniform(-10000, 30000)
            main_outflow = random.uniform(3000, 40000) if i == 0 else random.uniform(-5000, 25000)

            # 散户资金（万元）
            retain_inflow = random.uniform(2000, 20000) if i == 0 else random.uniform(-5000, 15000)
            retain_outflow = random.uniform(1500, 18000) if i == 0 else random.uniform(-3000, 12000)

            # 计算净流入
            main_net = main_inflow - main_outflow
            retain_net = retain_inflow - retain_outflow
            total_net = main_net + retain_net

            fund_flow_data.append(
                {
                    "date": date,
                    "main_inflow": round(main_inflow, 2),
                    "main_outflow": round(main_outflow, 2),
                    "main_net": round(main_net, 2),
                    "retain_inflow": round(retain_inflow, 2),
                    "retain_outflow": round(retain_outflow, 2),
                    "retain_net": round(retain_net, 2),
                    "total_net": round(total_net, 2),
                },
            )

            total_main_inflow += main_inflow
            total_main_outflow += main_outflow
            total_retain_inflow += retain_inflow
            total_retain_outflow += retain_outflow

        # 计算总计
        total_main_net = total_main_inflow - total_main_outflow
        total_retain_net = total_retain_inflow - total_retain_outflow
        total_net_flow = total_main_net + total_retain_net

        # 获取股票基本信息
        stock_name = "贵州茅台" if symbol == "600519" else f"股票{symbol}"
        current_price = random.uniform(1500, 1800) if symbol == "600519" else random.uniform(10, 200)

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "stock_name": stock_name,
                "current_price": round(current_price, 2),
                "timeframe": timeframe,
                "timeframe_desc": f"{timeframe_days}日" if timeframe_days > 1 else "今日",
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total_main_inflow": round(total_main_inflow, 2),
                    "total_main_outflow": round(total_main_outflow, 2),
                    "total_main_net": round(total_main_net, 2),
                    "total_retain_inflow": round(total_retain_inflow, 2),
                    "total_retain_outflow": round(total_retain_outflow, 2),
                    "total_retain_net": round(total_retain_net, 2),
                    "total_net_flow": round(total_net_flow, 2),
                },
                "details": fund_flow_data,
                # 添加一些统计信息
                "stats": {
                    "avg_main_net": round(total_main_net / timeframe_days, 2),
                    "avg_retain_net": round(total_retain_net / timeframe_days, 2),
                    "avg_total_net": round(total_net_flow / timeframe_days, 2),
                    "max_main_net": max([d["main_net"] for d in fund_flow_data]),
                    "min_main_net": min([d["main_net"] for d in fund_flow_data]),
                    "max_total_net": max([d["total_net"] for d in fund_flow_data]),
                    "min_total_net": min([d["total_net"] for d in fund_flow_data]),
                },
            },
            "timestamp": datetime.now().isoformat(),
            "source": "mock",
        }


# 创建全局Mock数据管理器实例
# ⚠️ 临时注释：解决循环导入问题，应通过 get_mock_data_manager() 获取
# mock_data_manager = UnifiedMockDataManager()
