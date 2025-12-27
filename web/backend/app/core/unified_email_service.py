"""
Unified Email Service - Consolidate email_service.py and email_notification_service.py
Task 1.4 Phase 2: Remove Duplicate Code - Service Consolidation

Consolidates 150+ LOC of duplicate email service implementations.

BEFORE (two separate services):
```python
# In services/email_service.py
class EmailService:
    def __init__(self, ...): ...
    def send_email(...): ...

# In services/email_notification_service.py
class EmailNotificationService:
    def __init__(self, ...): ...
    def send_email(...): ...
```

AFTER (single unified service):
```python
from app.core.unified_email_service import UnifiedEmailService

email = UnifiedEmailService()
result = email.send(to_addresses, subject, content)
```

Estimated Duplication Reduced: 150+ lines
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
import os
import structlog

logger = structlog.get_logger()


class EmailServiceError(Exception):
    """Email service error"""

    pass


class UnifiedEmailService:
    """
    Unified email service consolidating EmailService and EmailNotificationService.

    Supports both simple and advanced email sending with attachments,
    configurable templates, and comprehensive error handling.

    Usage:
        ```python
        from app.core.unified_email_service import UnifiedEmailService

        # Initialize from environment variables
        email_service = UnifiedEmailService()

        # Send simple email
        result = email_service.send(
            to_addresses=["user@example.com"],
            subject="Welcome",
            content="Hello, World!",
            content_type="plain"
        )

        # Send HTML email with attachments
        result = email_service.send_advanced(
            to_addresses=["user@example.com"],
            subject="Report",
            content="<h1>Report</h1>",
            content_type="html",
            attachments=["/path/to/file.pdf"]
        )
        ```
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        from_name: str = "MyStocks",
        timeout: int = 30,
    ):
        """
        Initialize email service

        Args:
            smtp_host: SMTP server host (default: environment variable)
            smtp_port: SMTP server port (default: environment variable)
            username: SMTP username/email (default: environment variable)
            password: SMTP password or app password (default: environment variable)
            use_tls: Whether to use TLS encryption (default: True)
            from_name: Sender name in email header (default: "MyStocks")
            timeout: Connection timeout in seconds (default: 30)
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USERNAME", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.use_tls = use_tls
        self.from_name = from_name
        self.timeout = timeout

        # Validate configuration
        self._is_configured = bool(self.username and self.password)
        if not self._is_configured:
            logger.warning(
                "⚠️  Email service not configured: " "Set SMTP_USERNAME and SMTP_PASSWORD environment variables"
            )

    def is_configured(self) -> bool:
        """
        Check if email service is properly configured

        Returns:
            True if SMTP credentials are available
        """
        return self._is_configured

    def send(
        self,
        to_addresses: Union[str, List[str]],
        subject: str,
        content: str,
        content_type: str = "plain",
        from_name: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send simple email

        Args:
            to_addresses: Recipient email address(es)
            subject: Email subject
            content: Email body content
            content_type: "plain" for text, "html" for HTML
            from_name: Override sender name (optional)
            cc_addresses: Carbon copy addresses (optional)
            bcc_addresses: Blind carbon copy addresses (optional)

        Returns:
            Dict with keys:
                - success (bool): Whether send was successful
                - message (str): Status message
                - error (str, optional): Error details if failed
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Email service not configured",
                "error": "SMTP_USERNAME and SMTP_PASSWORD not set",
            }

        # Normalize addresses
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]

        try:
            # Build email message
            msg = self._build_message(
                to_addresses=to_addresses,
                subject=subject,
                content=content,
                content_type=content_type,
                from_name=from_name,
                cc_addresses=cc_addresses,
                bcc_addresses=bcc_addresses,
            )

            # Send email
            self._send_smtp(msg, to_addresses, cc_addresses, bcc_addresses)

            logger.info("✅ Email sent successfully", to=to_addresses, subject=subject)

            return {
                "success": True,
                "message": f"Email sent to {len(to_addresses)} recipient(s)",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                "❌ Failed to send email",
                error=str(e),
                to=to_addresses,
                subject=subject,
            )
            return {
                "success": False,
                "message": "Failed to send email",
                "error": str(e),
            }

    def send_advanced(
        self,
        to_addresses: Union[str, List[str]],
        subject: str,
        content: str,
        content_type: str = "html",
        from_name: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send email with advanced features (attachments, CC, BCC)

        Args:
            to_addresses: Recipient email address(es)
            subject: Email subject
            content: Email body content
            content_type: "plain" for text, "html" for HTML
            from_name: Override sender name (optional)
            attachments: List of file paths to attach (optional)
            cc_addresses: Carbon copy addresses (optional)
            bcc_addresses: Blind carbon copy addresses (optional)

        Returns:
            Dict with send result
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Email service not configured",
                "error": "SMTP_USERNAME and SMTP_PASSWORD not set",
            }

        # Normalize addresses
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]

        try:
            # Build email with attachments
            msg = self._build_message(
                to_addresses=to_addresses,
                subject=subject,
                content=content,
                content_type=content_type,
                from_name=from_name,
                cc_addresses=cc_addresses,
                bcc_addresses=bcc_addresses,
            )

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)

            # Send email
            self._send_smtp(msg, to_addresses, cc_addresses, bcc_addresses)

            logger.info(
                "✅ Email sent with attachments",
                to=to_addresses,
                subject=subject,
                attachment_count=len(attachments) if attachments else 0,
            )

            return {
                "success": True,
                "message": f"Email sent to {len(to_addresses)} recipient(s)",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                "❌ Failed to send email with attachments",
                error=str(e),
                to=to_addresses,
                subject=subject,
            )
            return {
                "success": False,
                "message": "Failed to send email",
                "error": str(e),
            }

    def _build_message(
        self,
        to_addresses: List[str],
        subject: str,
        content: str,
        content_type: str = "plain",
        from_name: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
    ) -> MIMEMultipart:
        """Build MIME message object"""
        msg = MIMEMultipart()

        # Set headers
        sender_name = from_name or self.from_name
        msg["From"] = f"{sender_name} <{self.username}>"
        msg["To"] = ", ".join(to_addresses)

        if cc_addresses:
            msg["Cc"] = ", ".join(cc_addresses)

        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = Header(datetime.utcnow().isoformat(), "utf-8")

        # Add content
        content_mime = MIMEText(content, content_type, "utf-8")
        msg.attach(content_mime)

        return msg

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add file attachment to message"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)

            logger.info(f"✅ Added attachment: {filename}")

        except Exception as e:
            logger.error(f"❌ Failed to add attachment {file_path}: {str(e)}")
            raise

    def _send_smtp(
        self,
        msg: MIMEMultipart,
        to_addresses: List[str],
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
    ):
        """Send message via SMTP"""
        # Collect all recipients
        all_recipients = to_addresses.copy()
        if cc_addresses:
            all_recipients.extend(cc_addresses)
        if bcc_addresses:
            all_recipients.extend(bcc_addresses)

        # Connect and send
        if self.use_tls:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=self.timeout)

        try:
            server.login(self.username, self.password)
            server.sendmail(self.username, all_recipients, msg.as_string())
        finally:
            server.quit()

    def get_config(self) -> Dict[str, Any]:
        """Get current email service configuration (without credentials)"""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "username": self.username[:2] + "***" if self.username else "",
            "use_tls": self.use_tls,
            "from_name": self.from_name,
            "configured": self.is_configured(),
        }


"""
MIGRATION GUIDE:

From EmailService:
    ```python
    from app.services.email_service import EmailService
    service = EmailService()
    result = service.send_email(to_addresses, subject, content)
    ```

To UnifiedEmailService:
    ```python
    from app.core.unified_email_service import UnifiedEmailService
    service = UnifiedEmailService()
    result = service.send(to_addresses, subject, content)
    ```

From EmailNotificationService:
    ```python
    from app.services.email_notification_service import EmailNotificationService
    service = EmailNotificationService()
    result = service.send_email(to_addresses, subject, content)
    ```

To UnifiedEmailService:
    ```python
    from app.core.unified_email_service import UnifiedEmailService
    service = UnifiedEmailService()
    result = service.send(to_addresses, subject, content)
    ```
"""
