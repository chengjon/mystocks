"""
Indicator Tasks
===============

Task functions for indicator calculation system.
"""

import logging
from typing import Dict, Any
from app.services.indicators.jobs.daily_calculation import run_daily_calculation

logger = logging.getLogger(__name__)

async def batch_calculate_indicators(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Batch calculate indicators for stocks.
    
    Wraps the daily calculation job.
    Args:
        params: Dict containing:
            - date: str (YYYY-MM-DD)
            - stocks: List[str] (optional)
            - indicators: List[Dict] (optional)
    """
    logger.info(f"Starting batch_calculate_indicators task with params: {params}")
    try:
        result = await run_daily_calculation(params)
        return result if result else {"status": "success"}
    except Exception as e:
        logger.error(f"Error in batch_calculate_indicators: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}
