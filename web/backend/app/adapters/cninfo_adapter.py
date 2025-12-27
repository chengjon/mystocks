"""
Cninfo (巨潮资讯) Adapter
Multi-data Source Support

巨潮资讯网是中国证监会指定的上市公司信息披露网站
提供官方、权威的公告数据，类似美国的SEC EDGAR系统

功能：
- 获取上市公司公告列表
- 获取公告详情和内容
- 公告分类和筛选
- 支持多种公告类型（年报、重大事项、业绩预告等）
"""

import time
import requests
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
import pandas as pd
import logging

from app.adapters.base import (
    BaseDataSourceAdapter,
    DataSourceType,
    DataSourceStatus,
    DataSourceConfig,
    DataCategory,
)

logger = logging.getLogger(__name__)


class CninfoAdapter(BaseDataSourceAdapter):
    """
    巨潮资讯适配器

    官方公告数据源，提供最权威的上市公司信息披露
    """

    # API配置
    BASE_URL = "http://www.cninfo.com.cn/new"
    ANNOUNCEMENT_API = f"{BASE_URL}/hisAnnouncement/query"
    FULLTEXT_API = f"{BASE_URL}/fulltextSearch/full"

    # 公告类型映射
    ANNOUNCEMENT_TYPES = {
        "all": ("", "全部公告"),
        "year_report": ("category_ndbg_szsh", "年度报告"),
        "semi_annual": ("category_bndbg_szsh", "半年度报告"),
        "quarterly": ("category_yjdbg_szsh", "季度报告"),
        "performance": ("category_yjygjxz_szsh", "业绩预告"),
        "major_event": ("category_dszqfx_szsh", "重大事项"),
        "dividend": ("category_fxsg_szsh", "分红送转"),
        "acquisition": ("category_gqbd_szsh", "股权变动"),
        "financing": ("category_pg_szsh", "配股"),
        "rights_issue": ("category_zf_szsh", "增发"),
        "risk_warning": ("category_tbcl_szsh", "退市风险警示"),
    }

    # 市场类型
    MARKET_TYPES = {
        "all": "",
        "sse": "shmb",  # 上海主板
        "sse_star": "shkpb",  # 上海科创板
        "szse_main": "szmb",  # 深圳主板
        "szse_sme": "szzx",  # 深圳中小板
        "szse_gem": "szcy",  # 深圳创业板
    }

    def __init__(self, config: Optional[DataSourceConfig] = None):
        """
        初始化巨潮资讯适配器

        Args:
            config: 数据源配置
        """
        if config is None:
            config = DataSourceConfig(
                source_type=DataSourceType.CNINFO,
                priority=2,
                enabled=True,
                timeout=30,
                retry_count=3,
            )

        super().__init__(config)

        # 创建HTTP会话
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        logger.info("CninfoAdapter initialized")

    def get_supported_categories(self) -> List[DataCategory]:
        """
        获取支持的数据类别

        Returns:
            List[DataCategory]: 支持的数据类别
        """
        return [DataCategory.ANNOUNCEMENT, DataCategory.FINANCIAL_REPORT]

    def fetch_announcements(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = "all",
        page: int = 1,
        page_size: int = 30,
    ) -> pd.DataFrame:
        """
        获取公告列表

        Args:
            symbol: 股票代码 (可选，不传则获取所有)
            start_date: 开始日期
            end_date: 结束日期
            category: 公告类型 (year_report, performance, major_event等)
            page: 页码
            page_size: 每页数量

        Returns:
            pd.DataFrame: 公告列表
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            # 设置日期范围（默认最近30天）
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=30)

            # 获取公告类型代码
            category_code, _ = self.ANNOUNCEMENT_TYPES.get(category, ("", ""))

            # 构建请求参数
            params = {
                "pageNum": page,
                "pageSize": page_size,
                "column": "szse_main",  # 默认深圳主板
                "tabName": "fulltext",
                "plate": "",
                "stock": (symbol.split(".")[0] if symbol and "." in symbol else symbol or ""),
                "searchkey": "",
                "secid": "",
                "category": category_code,
                "trade": "",
                "seDate": f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}",
                "sortName": "announcementTime",
                "sortType": "desc",
            }

            # 发送请求
            response = self.session.post(self.ANNOUNCEMENT_API, data=params, timeout=self.config.timeout)
            response.raise_for_status()

            # 解析响应
            result = response.json()

            if result.get("returncode") != 200:
                raise Exception(f"API returned error: {result.get('returnmsg', 'Unknown error')}")

            # 提取公告数据
            announcements = result.get("announcements", [])

            if not announcements:
                logger.info(f"No announcements found for {symbol or 'all'} " f"from {start_date} to {end_date}")
                success = True  # 空结果也算成功
                self.update_health_status(DataSourceStatus.AVAILABLE)
                return data

            # 转换为DataFrame
            data = pd.DataFrame(announcements)

            # 重命名和选择列
            column_mapping = {
                "secCode": "stock_code",
                "secName": "stock_name",
                "announcementTitle": "title",
                "announcementType": "type",
                "announcementTime": "publish_time",
                "adjunctUrl": "pdf_url",
                "announcementId": "announcement_id",
                "storageTime": "storage_time",
            }

            data = data.rename(columns=column_mapping)

            # 选择需要的列
            available_columns = [col for col in column_mapping.values() if col in data.columns]
            data = data[available_columns]

            # 转换日期格式
            if "publish_time" in data.columns:
                data["publish_time"] = pd.to_datetime(data["publish_time"], unit="ms", errors="coerce")
                data["publish_date"] = data["publish_time"].dt.date

            # 添加来源标识
            data["data_source"] = "cninfo"

            # 构建完整URL
            if "pdf_url" in data.columns:
                data["pdf_url"] = data["pdf_url"].apply(lambda x: f"http://static.cninfo.com.cn/{x}" if x else None)

            success = True
            self.update_health_status(DataSourceStatus.AVAILABLE)
            logger.info(f"Fetched {len(data)} announcements from Cninfo")

        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        except Exception as e:
            logger.error(f"Failed to fetch announcements from Cninfo: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def search_announcements(
        self,
        keywords: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 30,
    ) -> pd.DataFrame:
        """
        搜索公告（全文检索）

        Args:
            keywords: 关键词
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            page_size: 每页数量

        Returns:
            pd.DataFrame: 搜索结果
        """
        start_time = time.time()
        success = False
        data = pd.DataFrame()

        try:
            # 设置日期范围
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=365)  # 默认搜索一年内

            params = {
                "searchkey": keywords,
                "sdate": start_date.strftime("%Y-%m-%d"),
                "edate": end_date.strftime("%Y-%m-%d"),
                "isfulltext": "false",
                "sortName": "pubdate",
                "sortType": "desc",
                "pageNum": page,
                "pageSize": page_size,
            }

            response = self.session.post(self.FULLTEXT_API, data=params, timeout=self.config.timeout)
            response.raise_for_status()

            result = response.json()

            if result.get("returncode") != 200:
                raise Exception(f"Search API returned error: {result.get('returnmsg')}")

            # 提取结果
            announcements = result.get("announcements", [])

            if announcements:
                data = pd.DataFrame(announcements)
                data["data_source"] = "cninfo"
                data["search_keywords"] = keywords

                logger.info(f"Found {len(data)} announcements matching '{keywords}'")

            success = True
            self.update_health_status(DataSourceStatus.AVAILABLE)

        except Exception as e:
            logger.error(f"Failed to search announcements: {e}")
            self.update_health_status(DataSourceStatus.ERROR, str(e))

        finally:
            response_time = time.time() - start_time
            self.record_request(success, response_time)

        return data

    def fetch_announcement_detail(self, announcement_id: str) -> Dict[str, Any]:
        """
        获取公告详情（包括内容）

        Args:
            announcement_id: 公告ID

        Returns:
            Dict: 公告详情
        """
        # 注意：Cninfo的公告内容主要以PDF形式提供
        # 如需提取PDF文本内容，需要额外的PDF解析库
        logger.warning("PDF content extraction not yet implemented")

        return {
            "announcement_id": announcement_id,
            "detail_available": False,
            "note": "PDF content extraction requires additional implementation",
        }

    def get_announcement_types(self) -> Dict[str, tuple]:
        """
        获取支持的公告类型

        Returns:
            Dict: 公告类型映射
        """
        return self.ANNOUNCEMENT_TYPES.copy()

    def fetch_realtime_quote(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Cninfo不支持实时行情

        Returns:
            pd.DataFrame: 空DataFrame
        """
        logger.warning("Cninfo does not support realtime_quote")
        return pd.DataFrame()

    def fetch_historical_quote(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "daily",
    ) -> pd.DataFrame:
        """
        Cninfo不支持历史行情

        Returns:
            pd.DataFrame: 空DataFrame
        """
        logger.warning("Cninfo does not support historical_quote")
        return pd.DataFrame()


# 全局单例
_cninfo_adapter = None


def get_cninfo_adapter() -> CninfoAdapter:
    """获取巨潮资讯适配器单例"""
    global _cninfo_adapter
    if _cninfo_adapter is None:
        _cninfo_adapter = CninfoAdapter()
    return _cninfo_adapter
