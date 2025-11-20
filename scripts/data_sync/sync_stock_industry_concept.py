"""
个股行业概念关联数据同步脚本
从AkShare适配器获取个股行业概念关联数据并同步到数据库
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.factories.data_source_factory import get_data_source
from src.core.data_classification import DataClassification
from src.unified_manager import MyStocksUnifiedManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_sync/stock_industry_concept_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def sync_stock_industry_concept_data(stock_limit: int = None):
    """
    同步个股行业概念关联数据
    
    Args:
        stock_limit: int - 限制同步的股票数量（用于测试）
    """
    logger.info("开始同步个股行业概念关联数据")
    
    try:
        # 初始化数据源和统一管理器
        data_source = get_data_source()
        manager = MyStocksUnifiedManager()
        
        # 获取股票列表
        logger.info("正在获取股票列表...")
        # 使用统一管理器获取股票基础信息
        stock_df = manager.load_data_by_classification(
            DataClassification.SYMBOLS_INFO, 
            'symbols_info'
        )
        
        if stock_df is None or stock_df.empty:
            logger.warning("数据库中没有股票信息，无法同步个股行业概念关联数据")
            return
        
        symbols = stock_df['symbol'].tolist()
        if stock_limit:
            symbols = symbols[:stock_limit]
        
        logger.info(f"获取到 {len(symbols)} 只股票")
        
        # 存储所有股票的行业概念信息
        all_stock_info = []
        
        # 遍历每只股票获取行业概念信息
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"[{i+1}/{len(symbols)}] 正在获取股票 {symbol} 的行业概念信息...")
                
                # 提取纯股票代码（去除市场后缀）
                pure_symbol = symbol.split('.')[0] if '.' in symbol else symbol
                
                # 从AkShare适配器获取个股行业概念信息
                stock_info = data_source.get_stock_industry_concept(pure_symbol)
                
                if not stock_info or (not stock_info.get('industries') and not stock_info.get('concepts')):
                    logger.info(f"  股票 {symbol} 没有行业概念信息")
                    continue
                
                # 添加时间戳
                stock_info['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                all_stock_info.append(stock_info)
                logger.info(f"  成功获取股票 {symbol} 的行业概念信息")
                
            except Exception as e:
                logger.error(f"  获取股票 {symbol} 的行业概念信息失败: {e}")
                # 继续处理下一只股票
                continue
        
        if not all_stock_info:
            logger.warning("没有获取到任何股票的行业概念信息")
            return
        
        logger.info(f"共获取到 {len(all_stock_info)} 只股票的行业概念信息")
        
        # 转换为DataFrame
        # 展开行业和概念信息为多行
        expanded_data = []
        for stock_info in all_stock_info:
            symbol = stock_info['symbol']
            updated_at = stock_info['updated_at']
            
            # 处理行业信息
            for industry in stock_info.get('industries', []):
                expanded_data.append({
                    'symbol': symbol,
                    'category_type': 'industry',
                    'category_name': industry,
                    'updated_at': updated_at
                })
            
            # 处理概念信息
            for concept in stock_info.get('concepts', []):
                expanded_data.append({
                    'symbol': symbol,
                    'category_type': 'concept',
                    'category_name': concept,
                    'updated_at': updated_at
                })
        
        if not expanded_data:
            logger.warning("没有可保存的行业概念关联数据")
            return
            
        df = pd.DataFrame(expanded_data)
        logger.info(f"转换为 {len(df)} 条关联记录")
        
        # 确保数据类型正确
        if 'symbol' in df.columns:
            df['symbol'] = df['symbol'].astype(str)
        if 'category_type' in df.columns:
            df['category_type'] = df['category_type'].astype(str)
        if 'category_name' in df.columns:
            df['category_name'] = df['category_name'].astype(str)
        
        # 保存到数据库（REFERENCE_DATA分类，自动路由到PostgreSQL）
        table_name = "stock_industry_concept_relations"
        success = manager.save_data_by_classification(
            DataClassification.REFERENCE_DATA,
            df,
            table_name
        )
        
        if success:
            logger.info(f"成功保存 {len(df)} 条个股行业概念关联数据到 {table_name}")
        else:
            logger.error("保存个股行业概念关联数据失败")
            return
        
        # 统计信息
        stats = {
            "total_stocks": len(all_stock_info),
            "total_records": len(df),
            "sync_time": datetime.now().isoformat()
        }
        
        logger.info(f"个股行业概念关联数据同步完成: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"同步个股行业概念关联数据失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='个股行业概念关联数据同步脚本')
    parser.add_argument('--limit', type=int, help='限制同步的股票数量（用于测试）')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs('logs/data_sync', exist_ok=True)
    
    try:
        stats = sync_stock_industry_concept_data(args.limit)
        logger.info(f"个股行业概念关联数据同步完成: {stats}")
        print(f"个股行业概念关联数据同步完成: {stats}")
    except Exception as e:
        logger.error(f"个股行业概念关联数据同步失败: {e}")
        print(f"个股行业概念关联数据同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()