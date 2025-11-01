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
from typing import List, Optional, Dict
import os
import logging
import pandas as pd

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
