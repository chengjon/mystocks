#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财数据源适配器

功能:
  1. 调用问财(iwencai.com) Web API获取股票筛选数据
  2. 数据解析和清理
  3. 错误处理和重试机制
  4. 实现IDataSource接口（如果需要）

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import re
import time
import logging
from typing import Optional, Dict

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logger = logging.getLogger(__name__)


class WencaiDataSource:
    """
    问财数据源适配器

    负责与问财API交互，获取股票筛选数据
    """

    # 问财API配置
    WENCAI_API_URL = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_PAGES = 1

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, retry_count: int = DEFAULT_RETRY_COUNT):
        """
        初始化问财数据源

        Args:
            timeout: API请求超时时间（秒）
            retry_count: 失败重试次数
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = self._create_session()

        logger.info(f"WencaiDataSource initialized: timeout={timeout}s, " f"retry_count={retry_count}")

    def _create_session(self) -> requests.Session:
        """
        创建带重试机制的HTTP会话

        Returns:
            配置好的requests.Session对象
        """
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.retry_count,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def fetch_data(self, query: str, pages: int = DEFAULT_PAGES) -> pd.DataFrame:
        """
        从问财获取数据

        Args:
            query: 查询语句（自然语言）
            pages: 获取页数

        Returns:
            包含股票数据的DataFrame

        Raises:
            requests.RequestException: 请求失败
            ValueError: 数据解析失败
        """
        logger.info(f"Fetching Wencai data: query='{query}', pages={pages}")

        all_data = pd.DataFrame()

        for page in range(1, pages + 1):
            try:
                page_data = self._fetch_single_page(query, page)

                if page_data.empty:
                    logger.warning(f"Page {page} returned empty data")
                    continue

                all_data = pd.concat([all_data, page_data], ignore_index=True)
                logger.debug(f"Page {page}: fetched {len(page_data)} records")

                # 避免请求过快
                if page < pages:
                    time.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed to fetch page {page}: {str(e)}")
                # 继续处理其他页
                continue

        if all_data.empty:
            logger.warning("No data fetched from Wencai API")
        else:
            logger.info(f"Total fetched: {len(all_data)} records")

        all_data.reset_index(drop=True, inplace=True)
        return all_data

    def _fetch_single_page(self, query: str, page: int) -> pd.DataFrame:
        """
        获取单页数据

        Args:
            query: 查询语句
            page: 页码

        Returns:
            单页数据DataFrame

        Raises:
            requests.RequestException: 请求失败
            ValueError: 响应数据格式错误
        """
        params = {
            "query": query,
            "urp_sort_way": "desc",
            "urp_sort_index": "",
            "page": str(page),
            "perpage": "100",
            "addheaderindexes": "",
            "condition": "",
            "codelist": "",
            "indexnamelimit": "",
            "ret": "json_all",
            "source": "Ths_iwencai_Xuangu",
            "urp_use_sort": "1",
            "uuids[0]": "24087",
            "query_type": "stock",
            "comp_id": "6836372",
            "business_cat": "soniu",
            "uuid": "24087",
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/111.0.0.0 Safari/537.36"
            )
        }

        try:
            response = self.session.get(
                self.WENCAI_API_URL,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            # 解析JSON响应
            data_json = response.json()

            # 提取数据
            if not data_json.get("answer"):
                raise ValueError("Response missing 'answer' field")

            components = data_json["answer"].get("components", [])
            if not components:
                logger.warning("No components in response")
                return pd.DataFrame()

            datas = components[0].get("data", {}).get("datas", [])
            if not datas:
                logger.warning("No datas in first component")
                return pd.DataFrame()

            df = pd.DataFrame(datas)
            return df

        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise ValueError(f"Invalid response format: {str(e)}")

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清理数据：处理列名和数据格式

        Args:
            data: 原始数据DataFrame

        Returns:
            清理后的DataFrame
        """
        if data.empty:
            return data

        logger.info(f"Cleaning data: {len(data)} rows, {len(data.columns)} columns")

        cleaned_data = data.copy()
        fetch_interval = None

        # 处理列名中的[内容]
        for col in cleaned_data.columns:
            match = re.search(r"\[(.*?)\]", col)
            if match:
                bracket_content = match.group(1)
                new_col = re.sub(r"\[.*?\]", "", col).strip()

                # 提取取数区间（从包含"涨停次数"的列）
                if "涨停次数" in col:
                    fetch_interval = bracket_content

                # 修改列名
                if new_col != col:
                    cleaned_data.rename(columns={col: new_col}, inplace=True)

        # 处理重复列名
        cleaned_data = self._handle_duplicate_columns(cleaned_data)

        # 添加取数区间列
        if fetch_interval:
            cleaned_data["取数区间"] = fetch_interval

        # 添加数据获取时间戳
        cleaned_data["fetch_time"] = pd.Timestamp.now()

        # 再次处理可能的重复列名
        cleaned_data = self._handle_duplicate_columns(cleaned_data)

        logger.info(f"Data cleaned: {len(cleaned_data)} rows, {len(cleaned_data.columns)} columns")

        return cleaned_data

    @staticmethod
    def _handle_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理重复的列名

        Args:
            df: 输入DataFrame

        Returns:
            列名唯一化后的DataFrame
        """
        from collections import defaultdict

        col_counts = defaultdict(int)
        new_columns = []

        for col in df.columns:
            col_counts[col] += 1
            count = col_counts[col]
            new_col = f"{col}_{count}" if count > 1 else col
            new_columns.append(new_col)

        df.columns = new_columns
        return df

    def validate_query(self, query: str) -> bool:
        """
        验证查询语句是否有效

        Args:
            query: 查询语句

        Returns:
            是否有效
        """
        if not query or not isinstance(query, str):
            return False

        query = query.strip()

        # 基本验证：长度检查
        if len(query) < 5 or len(query) > 500:
            logger.warning(f"Query length invalid: {len(query)}")
            return False

        return True

    def close(self):
        """关闭HTTP会话"""
        if hasattr(self, "session"):
            self.session.close()
            logger.info("WencaiDataSource session closed")


# 预定义的查询语句库
WENCAI_QUERIES = {
    "qs_1": "请列举出20天内出现过涨停，量比大于1.5倍以上，换手率大于3%，振幅小于5%，流通市值小于200亿的股票",
    "qs_2": "请列出近2周内资金流入持续5天为正，且涨幅不超过5%的股票",
    "qs_3": "请列出近3个月内出现过5日平均换手率大于30%的股票",
    "qs_4": "20日涨跌幅小于10%，换手率小于10%，市值小于100亿元，周成交量环比增长率大于100%前20名，当日涨幅＜4%，排除ST",
    "qs_5": "请列出2024年1月1日以来上市满10个月的股票里，平均换手率大于40%或者换手率标准差大于15%的股票",
    "qs_6": "请列出现近1周内板块资金流入持续为正的板块名称",
    "qs_7": "请列出现价小于30元、平均换手率大于20%、交易天数不少于250天的股票",
    "qs_8": "今日热度前300",
    "qs_9": "请列出均线多头排列，10天内有过涨停板，非ST，日线MACD金叉且日线KDJ金叉的股票",
}


def get_query_text(query_name: str) -> Optional[str]:
    """
    根据查询名称获取查询文本

    Args:
        query_name: 查询名称（如'qs_1'）

    Returns:
        查询文本，如果不存在返回None
    """
    return WENCAI_QUERIES.get(query_name)


def get_all_queries() -> Dict[str, str]:
    """
    获取所有预定义查询

    Returns:
        查询名称到查询文本的映射
    """
    return WENCAI_QUERIES.copy()
