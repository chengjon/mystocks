# Plan A0: Minimal Extraction - Implementation Guide

**Implementation Date**: Week 5, Day 1
**Estimated Duration**: 8 hours (1 working day)
**Target Code**: 200 lines across 3 modules
**Dependencies**: edgar (1 new), requests (existing)
**Maintenance**: <30 minutes/month

---

## 📋 Pre-Implementation Checklist

### 1. Environment Setup
```bash
# Install edgar library
pip install edgar-tool

# Set SEC identity (required by SEC.gov)
export SEC_EMAIL="your_email@example.com"

# Optional: Notification configuration
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
export WEBHOOK_URL="https://your-webhook-endpoint.com/notify"
```

### 2. Update .env File
```bash
# Add to .env
SEC_EMAIL=your_email@example.com

# Optional notification settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
WEBHOOK_URL=
```

### 3. Create Directory Structure
```bash
mkdir -p mystocks/data_sources
mkdir -p mystocks/utils
touch mystocks/data_sources/__init__.py
touch mystocks/data_sources/sec_fetcher.py
touch mystocks/analysis/risk_metrics.py
touch mystocks/utils/notifications.py
```

---

## 📦 Module 1: SEC Data Fetcher (2 hours)

### File: `mystocks/data_sources/sec_fetcher.py`

```python
"""
SEC Filing Data Fetcher

Provides direct access to SEC EDGAR filings for U.S. stocks.
Uses the edgar library for structured filing retrieval.

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
Dependencies: edgar-tool>=2.0.0

Usage:
    >>> from mystocks.data_sources import SECFetcher
    >>> fetcher = SECFetcher()
    >>> filing = fetcher.get_latest_filing('AAPL', '10-K')
    >>> print(filing['filing_date'])
"""

from edgar import Company, set_identity
from typing import Dict, List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class SECFetcher:
    """
    Minimalist SEC EDGAR data fetcher

    Provides clean access to SEC filings without LLM processing.
    Supports 10-K, 10-Q, 8-K, and 13F-HR forms.

    Example:
        >>> fetcher = SECFetcher()
        >>> filing = fetcher.get_latest_filing('TSLA', '10-K')
        >>> print(f"Filed on: {filing['filing_date']}")
    """

    def __init__(self, email: Optional[str] = None):
        """
        Initialize SEC fetcher

        Args:
            email: Email for SEC.gov identification (uses SEC_EMAIL env if None)

        Raises:
            ValueError: If email not provided and SEC_EMAIL not set
        """
        email = email or os.getenv('SEC_EMAIL')
        if not email:
            raise ValueError(
                "SEC_EMAIL environment variable must be set. "
                "See: https://www.sec.gov/os/accessing-edgar-data"
            )

        set_identity(email)
        logger.info(f"SEC fetcher initialized with identity: {email}")

    def get_latest_filing(
        self,
        ticker: str,
        form_type: str = "10-K"
    ) -> Optional[Dict]:
        """
        Get the latest SEC filing for a ticker

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            form_type: SEC form type (10-K, 10-Q, 8-K, 13F-HR)

        Returns:
            Dictionary with filing metadata and text, or None if not found

        Example:
            >>> fetcher = SECFetcher()
            >>> filing = fetcher.get_latest_filing('AAPL', '10-K')
            >>> if filing:
            >>>     print(f"Latest 10-K filed: {filing['filing_date']}")
        """
        try:
            company = Company(ticker)
            filings = company.get_filings(form=form_type)

            if not filings:
                logger.warning(f"No {form_type} filings found for {ticker}")
                return None

            filing = filings.latest()

            return {
                'ticker': ticker.upper(),
                'form_type': filing.form,
                'filing_date': str(filing.filing_date),
                'accession_number': filing.accession_number,
                'filing_url': filing.filing_url,
                'text_preview': filing.text()[:10000]  # First 10k characters
            }

        except Exception as e:
            logger.error(f"Error fetching {form_type} for {ticker}: {e}")
            return None

    def get_filing_history(
        self,
        ticker: str,
        form_type: str = "10-K",
        limit: int = 5
    ) -> List[Dict]:
        """
        Get multiple recent filings

        Args:
            ticker: Stock ticker symbol
            form_type: SEC form type
            limit: Maximum number of filings to retrieve

        Returns:
            List of filing metadata dictionaries

        Example:
            >>> fetcher = SECFetcher()
            >>> history = fetcher.get_filing_history('MSFT', '10-K', 3)
            >>> for filing in history:
            >>>     print(f"{filing['filing_date']}: {filing['form_type']}")
        """
        try:
            company = Company(ticker)
            filings = company.get_filings(form=form_type).head(limit)

            return [{
                'ticker': ticker.upper(),
                'form_type': f.form,
                'filing_date': str(f.filing_date),
                'accession_number': f.accession_number,
                'filing_url': f.filing_url
            } for f in filings]

        except Exception as e:
            logger.error(f"Error fetching filing history for {ticker}: {e}")
            return []

    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get basic company information

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with company metadata
        """
        try:
            company = Company(ticker)
            return {
                'ticker': ticker.upper(),
                'cik': company.cik,
                'name': company.name if hasattr(company, 'name') else None
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {e}")
            return None
```

### Test File: `tests/test_sec_fetcher.py`

```python
"""
Tests for SEC Data Fetcher

Run: pytest tests/test_sec_fetcher.py
"""

import pytest
import os
from mystocks.data_sources.sec_fetcher import SECFetcher


@pytest.fixture
def sec_fetcher():
    """Fixture to create SEC fetcher instance"""
    # Ensure SEC_EMAIL is set for tests
    if not os.getenv('SEC_EMAIL'):
        pytest.skip("SEC_EMAIL environment variable not set")
    return SECFetcher()


def test_sec_fetcher_initialization():
    """Test SEC fetcher can be initialized"""
    # Should raise error if no email
    original_email = os.getenv('SEC_EMAIL')
    os.environ.pop('SEC_EMAIL', None)

    with pytest.raises(ValueError):
        SECFetcher()

    # Restore original
    if original_email:
        os.environ['SEC_EMAIL'] = original_email


def test_get_latest_filing(sec_fetcher):
    """Test fetching latest 10-K filing"""
    filing = sec_fetcher.get_latest_filing('AAPL', '10-K')

    assert filing is not None
    assert filing['ticker'] == 'AAPL'
    assert filing['form_type'] == '10-K'
    assert 'filing_date' in filing
    assert 'accession_number' in filing
    assert 'text_preview' in filing
    assert len(filing['text_preview']) <= 10000


def test_get_filing_history(sec_fetcher):
    """Test fetching filing history"""
    history = sec_fetcher.get_filing_history('MSFT', '10-Q', 3)

    assert isinstance(history, list)
    assert len(history) <= 3

    if history:
        filing = history[0]
        assert filing['ticker'] == 'MSFT'
        assert 'filing_date' in filing


def test_invalid_ticker(sec_fetcher):
    """Test handling of invalid ticker"""
    filing = sec_fetcher.get_latest_filing('INVALID_TICKER_XYZ', '10-K')
    assert filing is None


def test_get_company_info(sec_fetcher):
    """Test company info retrieval"""
    info = sec_fetcher.get_company_info('TSLA')

    if info:  # May not be available for all tickers
        assert info['ticker'] == 'TSLA'
        assert 'cik' in info
```

---

## 📊 Module 2: Extended Risk Metrics (2 hours)

### File: `mystocks/analysis/risk_metrics.py`

```python
"""
Extended Risk Metrics

Provides VaR, CVaR, Beta, and other industry-standard risk measures.
Complements existing PerformanceMetrics with additional risk analysis.

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
Dependencies: numpy, pandas (existing)

Usage:
    >>> from mystocks.analysis import ExtendedRiskMetrics
    >>> var = ExtendedRiskMetrics.value_at_risk(returns)
    >>> print(f"95% VaR: {var:.2%}")
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ExtendedRiskMetrics:
    """
    Extended risk analysis metrics

    Provides Value at Risk (VaR), Conditional VaR, Beta, and correlation-adjusted
    position sizing algorithms.

    Example:
        >>> returns = pd.Series([0.01, -0.02, 0.015, ...])
        >>> metrics = ExtendedRiskMetrics.calculate_all(returns)
        >>> print(f"VaR (95%): {metrics['var_95_hist']:.2%}")
    """

    @staticmethod
    def value_at_risk(
        returns: pd.Series,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Value at Risk (VaR)

        VaR estimates the maximum loss over a given time period at a specific
        confidence level.

        Args:
            returns: Daily return series
            confidence_level: Confidence level (0.95 = 95%, 0.99 = 99%)
            method: 'historical' or 'parametric'
                - historical: Uses actual return distribution
                - parametric: Assumes normal distribution

        Returns:
            VaR value (negative indicates potential loss)

        Example:
            >>> returns = pd.Series([-0.02, 0.01, -0.01, 0.015])
            >>> var = ExtendedRiskMetrics.value_at_risk(returns, 0.95)
            >>> print(f"95% VaR: {var:.2%}")  # e.g., -3.2%
        """
        if len(returns) == 0:
            logger.warning("Empty returns series provided to VaR calculation")
            return 0.0

        if method == 'historical':
            # Use empirical percentile
            return float(np.percentile(returns, (1 - confidence_level) * 100))

        elif method == 'parametric':
            # Assume normal distribution
            mean = returns.mean()
            std = returns.std()

            # Z-scores for common confidence levels
            z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
            z_score = z_scores.get(confidence_level, 1.645)

            return float(mean - z_score * std)

        else:
            raise ValueError(
                f"Unknown method '{method}'. Use 'historical' or 'parametric'"
            )

    @staticmethod
    def conditional_var(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Conditional VaR (CVaR / Expected Shortfall)

        CVaR is the expected loss given that loss exceeds VaR.
        More conservative than VaR as it considers tail risk.

        Args:
            returns: Daily return series
            confidence_level: Confidence level (0.95 = 95%)

        Returns:
            CVaR value (average loss in worst (1-confidence)% scenarios)

        Example:
            >>> returns = pd.Series([...])
            >>> cvar = ExtendedRiskMetrics.conditional_var(returns, 0.95)
            >>> print(f"Expected loss in worst 5% cases: {cvar:.2%}")
        """
        if len(returns) == 0:
            return 0.0

        var = ExtendedRiskMetrics.value_at_risk(
            returns, confidence_level, 'historical'
        )
        worst_returns = returns[returns <= var]

        if len(worst_returns) == 0:
            return var

        return float(worst_returns.mean())

    @staticmethod
    def beta(
        asset_returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """
        Calculate Beta (market sensitivity)

        Beta measures how much an asset moves relative to the market.
        - Beta = 1: Moves with market
        - Beta > 1: More volatile than market
        - Beta < 1: Less volatile than market
        - Beta < 0: Moves opposite to market

        Args:
            asset_returns: Asset return series
            market_returns: Market return series (e.g., S&P 500)

        Returns:
            Beta coefficient

        Example:
            >>> stock_returns = pd.Series([...])
            >>> market_returns = pd.Series([...])
            >>> beta = ExtendedRiskMetrics.beta(stock_returns, market_returns)
            >>> print(f"Stock beta: {beta:.2f}")
        """
        if len(asset_returns) == 0 or len(market_returns) == 0:
            return 0.0

        # Align series
        aligned_data = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()

        if len(aligned_data) < 2:
            return 0.0

        covariance = np.cov(
            aligned_data['asset'],
            aligned_data['market']
        )[0][1]

        market_variance = np.var(aligned_data['market'])

        if market_variance == 0:
            return 0.0

        return float(covariance / market_variance)

    @staticmethod
    def calculate_all(
        returns: pd.Series,
        market_returns: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        Calculate all extended risk metrics

        Args:
            returns: Asset return series
            market_returns: Optional market return series for beta calculation

        Returns:
            Dictionary with all risk metrics

        Example:
            >>> returns = pd.Series([...])
            >>> market = pd.Series([...])
            >>> metrics = ExtendedRiskMetrics.calculate_all(returns, market)
            >>> print(f"VaR 95%: {metrics['var_95_hist']:.2%}")
            >>> print(f"CVaR 95%: {metrics['cvar_95']:.2%}")
            >>> print(f"Beta: {metrics['beta']:.2f}")
        """
        metrics = {
            'var_95_hist': ExtendedRiskMetrics.value_at_risk(
                returns, 0.95, 'historical'
            ),
            'var_95_param': ExtendedRiskMetrics.value_at_risk(
                returns, 0.95, 'parametric'
            ),
            'var_99_hist': ExtendedRiskMetrics.value_at_risk(
                returns, 0.99, 'historical'
            ),
            'cvar_95': ExtendedRiskMetrics.conditional_var(returns, 0.95),
            'cvar_99': ExtendedRiskMetrics.conditional_var(returns, 0.99)
        }

        if market_returns is not None and len(market_returns) > 0:
            metrics['beta'] = ExtendedRiskMetrics.beta(returns, market_returns)

        return metrics
```

### Test File: `tests/test_risk_metrics.py`

```python
"""
Tests for Extended Risk Metrics

Run: pytest tests/test_risk_metrics.py
"""

import pytest
import numpy as np
import pandas as pd
from mystocks.analysis.risk_metrics import ExtendedRiskMetrics


@pytest.fixture
def sample_returns():
    """Generate sample return series"""
    np.random.seed(42)
    return pd.Series(np.random.normal(0.001, 0.02, 252))


@pytest.fixture
def market_returns():
    """Generate sample market return series"""
    np.random.seed(43)
    return pd.Series(np.random.normal(0.0008, 0.015, 252))


def test_value_at_risk_historical(sample_returns):
    """Test historical VaR calculation"""
    var = ExtendedRiskMetrics.value_at_risk(sample_returns, 0.95, 'historical')

    assert isinstance(var, float)
    assert var < 0  # VaR should be negative (loss)
    assert -0.1 < var < 0  # Reasonable range


def test_value_at_risk_parametric(sample_returns):
    """Test parametric VaR calculation"""
    var = ExtendedRiskMetrics.value_at_risk(sample_returns, 0.95, 'parametric')

    assert isinstance(var, float)
    assert var < 0


def test_conditional_var(sample_returns):
    """Test CVaR calculation"""
    var = ExtendedRiskMetrics.value_at_risk(sample_returns, 0.95)
    cvar = ExtendedRiskMetrics.conditional_var(sample_returns, 0.95)

    assert isinstance(cvar, float)
    assert cvar <= var  # CVaR should be worse than VaR


def test_beta_calculation(sample_returns, market_returns):
    """Test beta calculation"""
    beta = ExtendedRiskMetrics.beta(sample_returns, market_returns)

    assert isinstance(beta, float)
    assert -2 < beta < 3  # Reasonable range


def test_calculate_all(sample_returns, market_returns):
    """Test comprehensive risk metrics"""
    metrics = ExtendedRiskMetrics.calculate_all(sample_returns, market_returns)

    required_keys = ['var_95_hist', 'var_95_param', 'var_99_hist',
                     'cvar_95', 'cvar_99', 'beta']

    for key in required_keys:
        assert key in metrics
        assert isinstance(metrics[key], float)


def test_empty_returns():
    """Test handling of empty return series"""
    empty = pd.Series([])
    var = ExtendedRiskMetrics.value_at_risk(empty, 0.95)
    assert var == 0.0
```

---

## 🔔 Module 3: Simple Notification System (2 hours)

### File: `mystocks/utils/notifications.py`

```python
"""
Simple Notification System

Provides email and webhook notifications for trading alerts.
Minimal design - no complex routing or retry logic.

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
Dependencies: smtplib (stdlib), requests

Usage:
    >>> from mystocks.utils import NotificationManager
    >>> notifier = NotificationManager()
    >>> notifier.notify("Portfolio exceeded 10% gain", email_to=['user@example.com'])
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Simple notification dispatcher

    Sends notifications via email and/or webhook. Configuration via environment
    variables. Handles failures gracefully without blocking execution.

    Example:
        >>> notifier = NotificationManager()
        >>> notifier.notify(
        ...     message="Stop loss triggered for 600000",
        ...     email_to=["trader@example.com"]
        ... )
    """

    def __init__(self):
        """
        Initialize notification manager

        Reads configuration from environment variables:
        - SMTP_HOST: SMTP server host (default: smtp.gmail.com)
        - SMTP_PORT: SMTP server port (default: 587)
        - SMTP_USERNAME: SMTP authentication username
        - SMTP_PASSWORD: SMTP authentication password
        - WEBHOOK_URL: Webhook endpoint URL
        """
        self.email_config = {
            'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD')
        }
        self.webhook_url = os.getenv('WEBHOOK_URL')

        # Check if email is configured
        self.email_enabled = bool(
            self.email_config['username'] and
            self.email_config['password']
        )

        # Check if webhook is configured
        self.webhook_enabled = bool(self.webhook_url)

        logger.info(
            f"NotificationManager initialized: "
            f"email={'enabled' if self.email_enabled else 'disabled'}, "
            f"webhook={'enabled' if self.webhook_enabled else 'disabled'}"
        )

    def send_email(
        self,
        to_addrs: List[str],
        subject: str,
        message: str
    ) -> bool:
        """
        Send email notification

        Args:
            to_addrs: List of recipient email addresses
            subject: Email subject line
            message: Email body content

        Returns:
            True if sent successfully, False otherwise

        Example:
            >>> notifier = NotificationManager()
            >>> success = notifier.send_email(
            ...     ['user@example.com'],
            ...     'Trading Alert',
            ...     'Position limit exceeded'
            ... )
        """
        if not self.email_enabled:
            logger.warning("Email not configured - skipping email notification")
            return False

        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(to_addrs)
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(
                self.email_config['host'],
                self.email_config['port']
            ) as server:
                server.starttls()
                server.login(
                    self.email_config['username'],
                    self.email_config['password']
                )
                server.send_message(msg)

            logger.info(f"Email sent to {to_addrs}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_webhook(
        self,
        message: str,
        **kwargs
    ) -> bool:
        """
        Send webhook notification

        Args:
            message: Notification message
            **kwargs: Additional data to include in webhook payload

        Returns:
            True if sent successfully, False otherwise

        Example:
            >>> notifier = NotificationManager()
            >>> success = notifier.send_webhook(
            ...     'Price alert triggered',
            ...     symbol='600000',
            ...     price=10.50
            ... )
        """
        if not self.webhook_enabled:
            logger.warning("Webhook not configured - skipping webhook notification")
            return False

        try:
            payload = {
                'message': message,
                'timestamp': pd.Timestamp.now().isoformat(),
                **kwargs
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"Webhook sent: {message}")
                return True
            else:
                logger.warning(
                    f"Webhook returned status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False

    def notify(
        self,
        message: str,
        subject: Optional[str] = None,
        email_to: Optional[List[str]] = None,
        use_webhook: bool = True,
        **webhook_data
    ) -> Dict[str, bool]:
        """
        Send notification through all configured channels

        Args:
            message: Notification message
            subject: Email subject (defaults to "MyStocks Notification")
            email_to: List of email recipients
            use_webhook: Whether to send webhook notification
            **webhook_data: Additional data for webhook

        Returns:
            Dictionary indicating success/failure for each channel

        Example:
            >>> notifier = NotificationManager()
            >>> results = notifier.notify(
            ...     message="Daily P&L Report: +5.2%",
            ...     subject="Daily Performance",
            ...     email_to=["trader@example.com"],
            ...     use_webhook=True,
            ...     pnl=0.052
            ... )
            >>> print(f"Email sent: {results['email']}")
        """
        results = {'email': False, 'webhook': False}

        # Send email if recipients provided
        if email_to:
            subject = subject or "MyStocks Notification"
            results['email'] = self.send_email(email_to, subject, message)

        # Send webhook if enabled
        if use_webhook:
            results['webhook'] = self.send_webhook(message, **webhook_data)

        return results


# Convenience function for quick notifications
def quick_notify(message: str, email_to: Optional[List[str]] = None):
    """
    Quick notification without creating NotificationManager instance

    Args:
        message: Notification message
        email_to: Optional list of email recipients

    Example:
        >>> from mystocks.utils.notifications import quick_notify
        >>> quick_notify("System started", email_to=['admin@example.com'])
    """
    manager = NotificationManager()
    return manager.notify(message, email_to=email_to)
```

### Test File: `tests/test_notifications.py`

```python
"""
Tests for Notification System

Run: pytest tests/test_notifications.py
"""

import pytest
from unittest.mock import patch, MagicMock
from mystocks.utils.notifications import NotificationManager, quick_notify


@pytest.fixture
def notifier():
    """Fixture to create notification manager"""
    return NotificationManager()


def test_notification_manager_init(notifier):
    """Test notification manager initialization"""
    assert isinstance(notifier, NotificationManager)
    assert hasattr(notifier, 'email_config')
    assert hasattr(notifier, 'webhook_url')


@patch('smtplib.SMTP')
def test_send_email_success(mock_smtp, notifier, monkeypatch):
    """Test successful email sending"""
    # Mock SMTP configuration
    monkeypatch.setenv('SMTP_USERNAME', 'test@example.com')
    monkeypatch.setenv('SMTP_PASSWORD', 'password')

    notifier = NotificationManager()
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    success = notifier.send_email(
        ['recipient@example.com'],
        'Test Subject',
        'Test Message'
    )

    assert success is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@patch('requests.post')
def test_send_webhook_success(mock_post, notifier, monkeypatch):
    """Test successful webhook sending"""
    monkeypatch.setenv('WEBHOOK_URL', 'https://example.com/webhook')
    notifier = NotificationManager()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    success = notifier.send_webhook('Test message', symbol='600000')

    assert success is True
    mock_post.assert_called_once()


def test_notify_no_configuration(notifier):
    """Test notification when nothing is configured"""
    results = notifier.notify('Test message')

    # Should not crash, just return False for all channels
    assert 'email' in results
    assert 'webhook' in results


@patch('mystocks.utils.notifications.NotificationManager.notify')
def test_quick_notify(mock_notify):
    """Test quick_notify convenience function"""
    mock_notify.return_value = {'email': True, 'webhook': False}

    result = quick_notify('Quick test', email_to=['test@example.com'])

    mock_notify.assert_called_once()
    assert 'email' in result
```

---

## 🔗 Integration Example (1 hour)

### File: `examples/week5_features_demo.py`

```python
"""
Week 5 Features Demonstration

Shows how to use SEC Fetcher, Extended Risk Metrics, and Notifications
in a practical trading workflow.

Usage: python examples/week5_features_demo.py
"""

import pandas as pd
import numpy as np
from mystocks.data_sources import SECFetcher
from mystocks.analysis import ExtendedRiskMetrics
from mystocks.utils import NotificationManager


def demo_sec_fetcher():
    """Demonstrate SEC filing retrieval"""
    print("\n=== SEC Filing Retrieval Demo ===")

    fetcher = SECFetcher()

    # Get latest 10-K for Apple
    print("\n1. Latest 10-K for AAPL:")
    filing = fetcher.get_latest_filing('AAPL', '10-K')

    if filing:
        print(f"  Form: {filing['form_type']}")
        print(f"  Date: {filing['filing_date']}")
        print(f"  URL: {filing['filing_url']}")
        print(f"  Preview: {filing['text_preview'][:200]}...")

    # Get filing history
    print("\n2. Recent 10-Q filings for TSLA:")
    history = fetcher.get_filing_history('TSLA', '10-Q', 3)

    for i, filing in enumerate(history, 1):
        print(f"  {i}. {filing['filing_date']}: {filing['form_type']}")


def demo_risk_metrics():
    """Demonstrate extended risk metrics"""
    print("\n=== Risk Metrics Demo ===")

    # Generate sample returns
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    market_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))

    # Calculate all metrics
    metrics = ExtendedRiskMetrics.calculate_all(returns, market_returns)

    print("\n1. Value at Risk:")
    print(f"  VaR (95%, Historical): {metrics['var_95_hist']:.2%}")
    print(f"  VaR (95%, Parametric): {metrics['var_95_param']:.2%}")
    print(f"  VaR (99%, Historical): {metrics['var_99_hist']:.2%}")

    print("\n2. Conditional VaR:")
    print(f"  CVaR (95%): {metrics['cvar_95']:.2%}")
    print(f"  CVaR (99%): {metrics['cvar_99']:.2%}")

    print("\n3. Market Sensitivity:")
    print(f"  Beta: {metrics['beta']:.2f}")


def demo_notifications():
    """Demonstrate notification system"""
    print("\n=== Notification System Demo ===")

    notifier = NotificationManager()

    # Send test notification
    print("\n1. Sending test notification...")
    results = notifier.notify(
        message="Daily portfolio performance: +3.2%",
        subject="Daily Report",
        email_to=None,  # Set to your email to test
        use_webhook=False,
        pnl=0.032,
        date="2025-10-24"
    )

    print(f"  Email sent: {results['email']}")
    print(f"  Webhook sent: {results['webhook']}")


def demo_integrated_workflow():
    """Demonstrate integrated usage in a trading workflow"""
    print("\n=== Integrated Workflow Demo ===")

    # 1. Check for SEC filing updates
    print("\n1. Checking SEC filings...")
    sec_fetcher = SECFetcher()
    filing = sec_fetcher.get_latest_filing('AAPL', '10-K')

    if filing:
        filing_info = f"Latest 10-K filed: {filing['filing_date']}"
        print(f"  {filing_info}")

    # 2. Calculate portfolio risk metrics
    print("\n2. Calculating risk metrics...")
    np.random.seed(42)
    portfolio_returns = pd.Series(np.random.normal(0.0015, 0.025, 252))

    risk_metrics = ExtendedRiskMetrics.calculate_all(portfolio_returns)

    print(f"  Portfolio VaR (95%): {risk_metrics['var_95_hist']:.2%}")
    print(f"  Portfolio CVaR (95%): {risk_metrics['cvar_95']:.2%}")

    # 3. Check for risk alerts
    print("\n3. Checking risk alerts...")
    if risk_metrics['var_95_hist'] < -0.05:
        alert_message = (
            f"Risk Alert: Portfolio VaR exceeds 5%\n"
            f"Current VaR: {risk_metrics['var_95_hist']:.2%}\n"
            f"CVaR: {risk_metrics['cvar_95']:.2%}"
        )

        print(f"  Alert triggered: {alert_message}")

        # 4. Send notification
        notifier = NotificationManager()
        notifier.notify(
            message=alert_message,
            subject="Portfolio Risk Alert",
            var=risk_metrics['var_95_hist'],
            cvar=risk_metrics['cvar_95']
        )


if __name__ == '__main__':
    print("MyStocks Week 5 Features Demonstration")
    print("=" * 50)

    try:
        demo_sec_fetcher()
    except Exception as e:
        print(f"\nSEC Fetcher Demo failed: {e}")
        print("(Set SEC_EMAIL environment variable to enable)")

    demo_risk_metrics()
    demo_notifications()
    demo_integrated_workflow()

    print("\n" + "=" * 50)
    print("Demo completed!")
```

---

## 📝 Documentation Updates (30 minutes)

### Update: `README.md`

Add to Week 5 section:
```markdown
### Week 5: Utility Enhancements ✅

**New Features**:
- **SEC Filing Access**: Direct integration with SEC EDGAR for U.S. stock filings
- **Extended Risk Metrics**: VaR, CVaR, and Beta calculations
- **Notification System**: Email and webhook alerts for trading events

**Code Stats**:
- Total: 200 lines across 3 modules
- Dependencies: +1 (edgar-tool)
- Maintenance: <30 minutes/month

**Usage Example**:
```python
# SEC filings
from mystocks.data_sources import SECFetcher
fetcher = SECFetcher()
filing = fetcher.get_latest_filing('AAPL', '10-K')

# Risk metrics
from mystocks.analysis import ExtendedRiskMetrics
metrics = ExtendedRiskMetrics.calculate_all(returns)
print(f"VaR (95%): {metrics['var_95_hist']:.2%}")

# Notifications
from mystocks.utils import NotificationManager
notifier = NotificationManager()
notifier.notify("Portfolio gained 5%", email_to=['you@example.com'])
```

---

## ✅ Implementation Timeline

| Time | Task | Deliverable |
|------|------|------------|
| **09:00 - 11:00** | SEC Fetcher | Module + tests |
| **11:00 - 13:00** | Risk Metrics | Module + tests |
| **13:00 - 14:00** | Lunch | |
| **14:00 - 16:00** | Notifications | Module + tests |
| **16:00 - 17:00** | Integration demo | Example code |
| **17:00 - 18:00** | Documentation | README + review |

---

## 🎯 Success Criteria

- [ ] All modules < 250 lines total
- [ ] Zero framework dependencies
- [ ] All tests passing (pytest)
- [ ] Integration example working
- [ ] Documentation complete
- [ ] Code review by project owner
- [ ] Maintenance estimate validated

---

## 📦 Dependencies Summary

**New**:
- `edgar-tool` (lightweight, SEC data access)

**Optional** (for notifications):
- `requests` (already in project for other features)

**Installation**:
```bash
pip install edgar-tool
```

---

## 🔍 Post-Implementation Review

After 1 week of usage, evaluate:

1. **Actual Maintenance Time**: Was <30 min/month accurate?
2. **Feature Usage**: Which features are actually used?
3. **Bug Reports**: Any issues discovered?
4. **Expansion Needs**: Should we add more SEC analysis? More risk metrics?

Document findings and decide whether to:
- ✅ Keep as-is (success)
- 🔧 Adjust features (minor changes)
- 🚀 Expand (add more capabilities)
- ❌ Remove (not valuable)

---

**Prepared by**: Claude (First-Principles Fullstack Architect)
**Target Completion**: Week 5, Day 1 (8 hours)
**Next Review**: Week 6, Day 1 (1-week post-implementation)
