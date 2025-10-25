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

try:
    from edgar import Company, set_identity
    EDGAR_AVAILABLE = True
except ImportError:
    EDGAR_AVAILABLE = False
    Company = None
    set_identity = None

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
            ImportError: If edgar library not installed
        """
        if not EDGAR_AVAILABLE:
            raise ImportError(
                "edgar library not available. Install with: pip install edgar\n"
                "Note: This is optional for the MVP demo. Risk metrics and notifications work without it."
            )

        email = email or os.getenv('SEC_EMAIL')
        if not email:
            raise ValueError(
                "SEC_EMAIL environment variable must be set. "
                "See: https://www.sec.gov/os/accessing-edgar-data"
            )

        if set_identity:
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
