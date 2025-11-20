"""
行业分类数据同步脚本
从AkShare适配器获取行业分类数据并同步到数据库
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
        logging.FileHandler('logs/data_sync/industry_classify_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def sync_industry_classify_data():
    """
    同步行业分类数据
    """
    logger.info("开始同步行业分类数据")
    
    try:
        # 初始化数据源和统一管理器
        data_source = get_data_source()
        manager = MyStocksUnifiedManager()
        
        # 从AkShare适配器获取行业分类数据
        logger.info("正在获取行业分类数据...")
        industry_df = data_source.get_industry_classify()
        
        if industry_df is None or industry_df.empty:
            logger.warning("未能获取到行业分类数据")
            return
        
        logger.info(f"获取到 {len(industry_df)} 条行业分类数据")
        
        # 添加时间戳
        industry_df['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 确保数据类型正确
        if 'index' in industry_df.columns:
            industry_df['index'] = industry_df['index'].astype(str)
        if 'name' in industry_df.columns:
            industry_df['name'] = industry_df['name'].astype(str)
        
        # 保存到数据库（REFERENCE_DATA分类，自动路由到PostgreSQL）
        table_name = "industry_classifications"
        success = manager.save_data_by_classification(
            DataClassification.REFERENCE_DATA,
            industry_df,
            table_name
        )
        
        if success:
            logger.info(f"成功保存 {len(industry_df)} 条行业分类数据到 {table_name}")
        else:
            logger.error("保存行业分类数据失败")
            return
        
        # 统计信息
        stats = {
            "total_records": len(industry_df),
            "sync_time": datetime.now().isoformat()
        }
        
        logger.info(f"行业分类数据同步完成: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"同步行业分类数据失败: {e}")
        raise e


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='行业分类数据同步脚本')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs('logs/data_sync', exist_ok=True)
    
    try:
        stats = sync_industry_classify_data()
        logger.info(f"行业分类数据同步完成: {stats}")
        print(f"行业分类数据同步完成: {stats}")
    except Exception as e:
        logger.error(f"行业分类数据同步失败: {e}")
        print(f"行业分类数据同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()