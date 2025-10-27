#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks API Python 客户端 SDK

提供简单易用的Python接口访问MyStocks Web API

使用示例:
    from api_client_sdk import MyStocksClient

    # 创建客户端
    client = MyStocksClient(base_url="http://localhost:8000")

    # 登录
    client.login("admin", "admin123")

    # 获取股票基本信息
    stocks = client.get_stocks_basic(limit=10, market="SH")

    # 获取日线数据
    kline = client.get_daily_kline("600519.SH", start_date="2024-01-01")

    # 计算技术指标
    indicators = client.calculate_indicators(
        symbol="600519.SH",
        indicators=[
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ]
    )

创建日期: 2025-10-25
版本: 1.0.0
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """API异常基类"""
    pass


class AuthenticationError(APIException):
    """认证错误"""
    pass


class ValidationError(APIException):
    """验证错误"""
    pass


class ResourceNotFoundError(APIException):
    """资源不存在"""
    pass


class MyStocksClient:
    """
    MyStocks API Python客户端

    特性:
    - 自动Token管理
    - 自动Token刷新
    - 错误处理
    - 请求重试
    - 日志记录
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化API客户端

        Args:
            base_url: API服务器地址
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries

        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        logger.info(f"MyStocksClient initialized: {base_url}")

    # ==================== 认证相关 ====================

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录响应数据

        Raises:
            AuthenticationError: 认证失败
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                data={"username": username, "password": password},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=data.get('expires_in', 3600))

            logger.info(f"Login successful: {username}")
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("用户名或密码错误")
            raise AuthenticationError(f"登录失败: {str(e)}")

    def logout(self) -> None:
        """用户登出"""
        if not self.access_token:
            return

        try:
            self._post("/api/auth/logout")
            logger.info("Logout successful")
        finally:
            self.access_token = None
            self.token_expires_at = None

    def refresh_token(self) -> Dict[str, Any]:
        """
        刷新访问令牌

        Returns:
            新的Token数据
        """
        if not self.access_token:
            raise AuthenticationError("未登录")

        response = self._post("/api/auth/refresh")
        self.access_token = response['access_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=response.get('expires_in', 3600))

        logger.info("Token refreshed")
        return response

    def is_token_valid(self) -> bool:
        """检查Token是否有效"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

    def ensure_authenticated(self) -> None:
        """确保已认证，自动刷新Token"""
        if not self.is_token_valid():
            if self.access_token:
                try:
                    self.refresh_token()
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    raise AuthenticationError("Token过期，请重新登录")
            else:
                raise AuthenticationError("未登录，请先调用login()")

    # ==================== HTTP请求基础方法 ====================

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        require_auth: bool = True
    ) -> Any:
        """
        发送HTTP请求

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            params: 查询参数
            json_data: JSON请求体
            require_auth: 是否需要认证

        Returns:
            响应数据

        Raises:
            APIException: API错误
        """
        if require_auth:
            self.ensure_authenticated()

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    headers=headers,
                    timeout=self.timeout
                )

                # 处理HTTP错误
                if response.status_code == 401:
                    raise AuthenticationError("认证失败")
                elif response.status_code == 404:
                    raise ResourceNotFoundError("资源不存在")
                elif response.status_code == 422:
                    raise ValidationError(f"参数验证错误: {response.json()}")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request timeout, retrying ({attempt + 1}/{self.max_retries})...")
                    continue
                raise APIException("请求超时")

            except requests.exceptions.ConnectionError:
                raise APIException("连接失败，服务器可能未启动")

            except requests.exceptions.HTTPError as e:
                raise APIException(f"HTTP错误 {e.response.status_code}: {e.response.text}")

    def _get(self, endpoint: str, params: Optional[Dict] = None, require_auth: bool = True) -> Any:
        """GET请求"""
        return self._request("GET", endpoint, params=params, require_auth=require_auth)

    def _post(self, endpoint: str, json_data: Optional[Dict] = None, require_auth: bool = True) -> Any:
        """POST请求"""
        return self._request("POST", endpoint, json_data=json_data, require_auth=require_auth)

    def _put(self, endpoint: str, json_data: Optional[Dict] = None, require_auth: bool = True) -> Any:
        """PUT请求"""
        return self._request("PUT", endpoint, json_data=json_data, require_auth=require_auth)

    def _delete(self, endpoint: str, require_auth: bool = True) -> Any:
        """DELETE请求"""
        return self._request("DELETE", endpoint, require_auth=require_auth)

    # ==================== 数据查询API ====================

    def get_stocks_basic(
        self,
        limit: int = 100,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取股票基本信息列表

        Args:
            limit: 返回记录数限制 (1-1000)
            search: 股票代码或名称搜索关键词
            industry: 行业筛选
            market: 市场筛选 (SH/SZ)

        Returns:
            股票基本信息列表
        """
        params = {"limit": limit}
        if search:
            params["search"] = search
        if industry:
            params["industry"] = industry
        if market:
            params["market"] = market

        return self._get("/api/data/stocks/basic", params=params)

    def get_daily_kline(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码，如: 000001.SZ
            start_date: 开始日期，格式: YYYY-MM-DD
            end_date: 结束日期，格式: YYYY-MM-DD
            limit: 返回记录数限制 (1-5000)

        Returns:
            日线数据
        """
        params = {"symbol": symbol, "limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        return self._get("/api/data/stocks/daily", params=params)

    def search_stocks(self, keyword: str, limit: int = 20) -> Dict[str, Any]:
        """
        股票搜索

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制 (1-100)

        Returns:
            搜索结果
        """
        params = {"keyword": keyword, "limit": limit}
        return self._get("/api/data/stocks/search", params=params)

    def get_financial_data(
        self,
        symbol: str,
        report_type: str = "balance",
        period: str = "all",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取股票财务数据

        Args:
            symbol: 股票代码，如: 000001
            report_type: 报表类型 (balance/income/cashflow)
            period: 报告期 (quarterly/annual/all)
            limit: 返回记录数限制 (1-100)

        Returns:
            财务数据
        """
        params = {
            "symbol": symbol,
            "report_type": report_type,
            "period": period,
            "limit": limit
        }
        return self._get("/api/data/financial", params=params)

    # ==================== 市场数据API ====================

    def get_fund_flow(
        self,
        symbol: str,
        timeframe: str = "1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        查询资金流向

        Args:
            symbol: 股票代码
            timeframe: 时间维度 (1/3/5/10天)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            资金流向列表
        """
        params = {"symbol": symbol, "timeframe": timeframe}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        return self._get("/api/market/fund-flow", params=params, require_auth=False)

    def refresh_fund_flow(self, symbol: str, timeframe: str = "1") -> Dict[str, Any]:
        """
        刷新资金流向数据

        Args:
            symbol: 股票代码
            timeframe: 时间维度

        Returns:
            刷新结果
        """
        params = {"symbol": symbol, "timeframe": timeframe}
        return self._post("/api/market/fund-flow/refresh", json_data=params, require_auth=False)

    def get_etf_list(
        self,
        symbol: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        查询ETF列表

        Args:
            symbol: ETF代码
            keyword: 关键词搜索
            limit: 返回数量 (1-500)

        Returns:
            ETF数据列表
        """
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if keyword:
            params["keyword"] = keyword

        return self._get("/api/market/etf/list", params=params, require_auth=False)

    def get_market_quotes(self, symbols: Optional[str] = None) -> Dict[str, Any]:
        """
        查询实时行情

        Args:
            symbols: 股票代码列表，逗号分隔，如: 000001,600519

        Returns:
            实时行情数据
        """
        params = {}
        if symbols:
            params["symbols"] = symbols

        return self._get("/api/market/quotes", params=params, require_auth=False)

    # ==================== 技术指标API ====================

    def get_indicator_registry(self) -> Dict[str, Any]:
        """
        获取指标注册表

        Returns:
            所有可用的技术指标及其元数据
        """
        return self._get("/api/indicators/registry", require_auth=False)

    def get_indicators_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        获取指定分类的指标

        Args:
            category: 指标分类 (trend/momentum/volatility/volume/candlestick)

        Returns:
            指标列表
        """
        return self._get(f"/api/indicators/registry/{category}", require_auth=False)

    def calculate_indicators(
        self,
        symbol: str,
        indicators: List[Dict[str, Any]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        计算技术指标

        Args:
            symbol: 股票代码
            indicators: 指标列表，如: [{"abbreviation": "SMA", "parameters": {"timeperiod": 20}}]
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            指标计算结果
        """
        data = {
            "symbol": symbol,
            "indicators": indicators,
            "use_cache": use_cache
        }
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date

        return self._post("/api/indicators/calculate", json_data=data, require_auth=False)

    # ==================== 系统管理API ====================

    def get_system_health(self) -> Dict[str, Any]:
        """
        系统健康检查

        Returns:
            系统健康状态
        """
        return self._get("/api/system/health", require_auth=False)

    def get_database_health(self) -> Dict[str, Any]:
        """
        数据库健康检查

        Returns:
            数据库健康状态
        """
        return self._get("/api/system/database/health", require_auth=False)

    def get_database_stats(self) -> Dict[str, Any]:
        """
        数据库统计信息

        Returns:
            数据库统计
        """
        return self._get("/api/system/database/stats", require_auth=False)

    def get_adapters_health(self) -> Dict[str, Any]:
        """
        适配器健康检查

        Returns:
            适配器健康状态
        """
        return self._get("/api/system/adapters/health", require_auth=False)

    def get_system_logs(
        self,
        filter_errors: bool = False,
        limit: int = 100,
        offset: int = 0,
        level: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取系统日志

        Args:
            filter_errors: 是否只显示有问题的日志
            limit: 返回条数限制 (1-1000)
            offset: 偏移量
            level: 日志级别筛选 (INFO/WARNING/ERROR/CRITICAL)
            category: 日志分类筛选 (database/api/adapter/system)

        Returns:
            系统日志
        """
        params = {
            "filter_errors": filter_errors,
            "limit": limit,
            "offset": offset
        }
        if level:
            params["level"] = level
        if category:
            params["category"] = category

        return self._get("/api/system/logs", params=params, require_auth=False)


# ==================== 使用示例 ====================

def example_usage():
    """SDK使用示例"""

    # 1. 创建客户端
    client = MyStocksClient(base_url="http://localhost:8000")

    # 2. 登录（可选，部分API需要认证）
    try:
        client.login("admin", "admin123")
        print("✅ 登录成功")
    except AuthenticationError as e:
        print(f"❌ 登录失败: {e}")
        return

    # 3. 获取股票基本信息
    print("\n=== 获取股票基本信息 ===")
    stocks = client.get_stocks_basic(limit=5, market="SH")
    print(f"获取到 {len(stocks.get('data', []))} 只股票")

    # 4. 获取日线数据
    print("\n=== 获取日线数据 ===")
    kline = client.get_daily_kline("600519.SH", start_date="2024-01-01", limit=5)
    print(f"获取到 {len(kline.get('data', []))} 条K线数据")

    # 5. 搜索股票
    print("\n=== 搜索股票 ===")
    search_result = client.search_stocks("茅台", limit=3)
    print(f"搜索结果: {search_result}")

    # 6. 计算技术指标
    print("\n=== 计算技术指标 ===")
    indicators = client.calculate_indicators(
        symbol="600519.SH",
        indicators=[
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ],
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    print(f"计算了 {len(indicators.get('data', []))} 个数据点")

    # 7. 获取系统健康状态
    print("\n=== 系统健康检查 ===")
    health = client.get_system_health()
    print(f"系统状态: {health.get('status')}")

    # 8. 获取数据库健康状态
    print("\n=== 数据库健康检查 ===")
    db_health = client.get_database_health()
    print(f"数据库状态: {db_health.get('data', {}).get('summary', {})}")

    # 9. 登出
    client.logout()
    print("\n✅ 登出成功")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 运行示例
    example_usage()
