"""
User, Watchlist and Notification Schemas for Frontend Compatibility
These models match the expectations of the frontend adapters.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """User preferences schema"""

    theme: str = "auto"
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"
    dateFormat: str = "YYYY-MM-DD"
    timeFormat: str = "24h"
    defaultDashboard: str = "overview"
    watchlistLayout: str = "grid"
    chartSettings: Dict[str, Any] = Field(
        default_factory=lambda: {"defaultPeriod": "1D", "showVolume": True, "showMA": True, "indicators": []}
    )
    notifications: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": True,
            "push": True,
            "sms": False,
            "priceAlerts": True,
            "orderStatus": True,
            "systemUpdates": True,
            "marketNews": True,
            "strategySignals": True,
        }
    )
    privacy: Dict[str, Any] = Field(
        default_factory=lambda: {
            "profileVisibility": "private",
            "showRealName": False,
            "showEmail": False,
            "showTradingStats": True,
            "allowDirectMessages": True,
            "dataSharing": False,
        }
    )


class UserPermissions(BaseModel):
    """User permissions schema"""

    canTrade: bool = True
    canWithdraw: bool = True
    canUseStrategies: bool = True
    canAccessAdvancedFeatures: bool = False
    canViewMarketData: bool = True
    canExportData: bool = True
    canManageUsers: bool = False
    canViewAnalytics: bool = True
    maxStrategies: int = 5
    maxWatchlists: int = 10
    maxApiCalls: int = 1000


class SubscriptionInfo(BaseModel):
    """Subscription info schema"""

    plan: str = "free"
    status: str = "active"
    startDate: str
    endDate: str
    trialEndDate: Optional[str] = None
    autoRenew: bool = True
    features: List[str] = []
    limits: Dict[str, int] = Field(
        default_factory=lambda: {
            "maxStrategies": 5,
            "maxWatchlists": 10,
            "maxApiCallsPerDay": 1000,
            "maxDataRetention": 30,
        }
    )
    nextBillingAmount: Optional[float] = None
    nextBillingDate: Optional[str] = None


class UserStatistics(BaseModel):
    """User statistics schema"""

    totalTrades: int = 0
    winningTrades: int = 0
    losingTrades: int = 0
    winRate: float = 0.0
    totalPnL: float = 0.0
    totalPnLPercent: float = 0.0
    averageReturn: float = 0.0
    sharpeRatio: float = 0.0
    maxDrawdown: float = 0.0
    totalCommission: float = 0.0
    joinDate: str
    activeStrategies: int = 0
    activeWatchlists: int = 0
    followers: int = 0
    following: int = 0


class UserProfileResponse(BaseModel):
    """User profile response schema"""

    userId: str
    username: str
    email: str
    displayName: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"
    status: str = "active"
    preferences: UserPreferences
    permissions: UserPermissions
    subscription: SubscriptionInfo
    statistics: UserStatistics
    createdAt: datetime
    lastLoginAt: datetime
    lastUpdateAt: datetime


class WatchlistStockResponse(BaseModel):
    """Stock item within a watchlist"""

    symbol: str
    name: str
    market: str = "A"
    currentPrice: float = 0.0
    changeAmount: float = 0.0
    changePercent: float = 0.0
    volume: int = 0
    marketCap: float = 0.0
    pe: Optional[float] = None
    pb: Optional[float] = None
    addedAt: datetime
    notes: Optional[str] = None
    alerts: List[Dict[str, Any]] = []
    customFields: Optional[Dict[str, Any]] = None


class WatchlistResponse(BaseModel):
    """Watchlist response schema"""

    id: str
    name: str
    description: Optional[str] = None
    isDefault: bool = False
    isPublic: bool = False
    owner: Dict[str, str]
    stocks: List[WatchlistStockResponse] = []
    statistics: Dict[str, Any] = {}
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime
    lastViewedAt: Optional[datetime] = None
    sortOrder: int = 0


class NotificationResponse(BaseModel):
    """Notification response schema"""

    id: str
    type: str = "system"
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    isRead: bool = False
    createdAt: datetime
    expiresAt: Optional[datetime] = None
    actionUrl: Optional[str] = None
    actionText: Optional[str] = None
    icon: Optional[str] = None
    category: str = "general"
