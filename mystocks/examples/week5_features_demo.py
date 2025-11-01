"""
Week 5 Features Demonstration

Shows how to use SEC Fetcher, Extended Risk Metrics, and Notifications
in a practical trading workflow.

Usage: python examples/week5_features_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from data_sources import SECFetcher
from analysis import ExtendedRiskMetrics
from utils import NotificationManager


def demo_sec_fetcher():
    """Demonstrate SEC filing retrieval"""
    print("\n=== SEC Filing Retrieval Demo ===")

    try:
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

    except ValueError as e:
        print(f"  ⚠️  {e}")
        print("  Set SEC_EMAIL environment variable to enable this feature")


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
    print("  (Configure SMTP_USERNAME and WEBHOOK_URL to enable)")


def demo_integrated_workflow():
    """Demonstrate integrated usage in a trading workflow"""
    print("\n=== Integrated Workflow Demo ===")

    # 1. Check for SEC filing updates
    print("\n1. Checking SEC filings...")
    try:
        sec_fetcher = SECFetcher()
        filing = sec_fetcher.get_latest_filing('AAPL', '10-K')

        if filing:
            filing_info = f"Latest 10-K filed: {filing['filing_date']}"
            print(f"  {filing_info}")
    except (ValueError, ImportError) as e:
        print(f"  SEC filing check skipped ({str(e).split('.')[0]})")

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
    else:
        print("  No risk alerts - portfolio within acceptable limits")


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
    print("✅ Demo completed!")
