"""
Daily Indicator Calculation Job
===============================

Fetches OHLCV data for all stocks and calculates indicators.
Saves results to the database.
Publishes events to Redis Pub/Sub for real-time monitoring.

Version: 2.0.0 - Phase 3: Event-Driven Real-Time Monitoring
Author: MyStocks Project
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from app.core.database import db_service
from app.repositories.indicator_repo import IndicatorRepository
from app.services.indicators import CalculationMode, OHLCVData, create_scheduler
from app.services.indicators.defaults import load_default_indicators

# Phase 3: Event publishing
try:
    from app.models.event_models import (
        EventChannels,
        TaskStatus,
        create_stock_indicators_completed_event,
        create_task_completed_event,
        create_task_progress_event,
    )
    from app.services.redis import redis_pubsub

    REDIS_PUBSUB_AVAILABLE = True
    logger.info("Redis Pub/Sub enabled for daily_calculation")
except ImportError:
    REDIS_PUBSUB_AVAILABLE = False
    logger.warning("Redis Pub/Sub not available, daily_calculation running without event publishing")

logger = logging.getLogger(__name__)


# ========== Event Publishing Helpers (Phase 3) ==========


async def _publish_task_progress(
    job_id: str,
    task_type: str,
    status: TaskStatus,
    progress: float,
    message: str = "",
    processed: int = 0,
    total: int = 0,
    failed: int = 0,
):
    """Publish task progress event"""
    if not REDIS_PUBSUB_AVAILABLE:
        return

    try:
        event = create_task_progress_event(
            task_id=job_id,
            task_type=task_type,
            status=status,
            progress=progress,
            message=message,
            processed=processed,
            total=total,
            failed=failed,
        )

        # Publish to both global tasks channel and specific task channel
        await redis_pubsub.async_publish(EventChannels.TASKS_ALL, event.model_dump())
        await redis_pubsub.async_publish(EventChannels.task_channel(job_id), event.model_dump())

    except Exception as e:
        logger.error("Failed to publish task progress event: %(e)s"")


async def _publish_stock_completed(
    stock_code: str,
    indicators: List[str],
    success_count: int,
    failed_count: int = 0,
    calculation_time_ms: float = 0,
    from_cache_count: int = 0,
):
    """Publish stock indicators completed event (Batching optimization)"""
    if not REDIS_PUBSUB_AVAILABLE:
        return

    try:
        event = create_stock_indicators_completed_event(
            stock_code=stock_code,
            indicators=indicators,
            success_count=success_count,
            failed_count=failed_count,
            calculation_time_ms=calculation_time_ms,
            from_cache_count=from_cache_count,
        )

        # Publish to indicators channel
        await redis_pubsub.async_publish(EventChannels.INDICATORS_ALL, event.model_dump())

    except Exception as e:
        logger.error("Failed to publish stock completed event: %(e)s"")


async def _publish_task_completed(job_id: str, task_type: str, status: TaskStatus, duration_seconds: float, **result):
    """Publish task completed event"""
    if not REDIS_PUBSUB_AVAILABLE:
        return

    try:
        event = create_task_completed_event(
            task_id=job_id, task_type=task_type, status=status, duration_seconds=duration_seconds, **result
        )

        # Publish to both channels
        await redis_pubsub.async_publish(EventChannels.TASKS_ALL, event.model_dump())
        await redis_pubsub.async_publish(EventChannels.task_channel(job_id), event.model_dump())

    except Exception as e:
        logger.error("Failed to publish task completed event: %(e)s"")


# ========== Main Calculation Function ==========


async def run_daily_calculation(params: Dict[str, Any] = None):
    """
    Run daily indicator calculation for all stocks.

    Phase 3 Enhancements:
    - Publishes task progress events to Redis Pub/Sub
    - Publishes stock completion events (batching optimization)
    - Throttled progress updates (every 1% or 50 stocks)

    Params:
        date (str, optional): Target date (YYYY-MM-DD). Default is today.
        stocks (List[str], optional): List of stock codes. Default is all.
        indicators (List[Dict], optional): List of indicators to calculate. Default is SMA, MACD, RSI.
        job_id (str, optional): Unique job identifier.
    """
    params = params or {}
    job_id = params.get("job_id", f"calc_{int(time.time())}")
    target_date = params.get("date", datetime.now().strftime("%Y-%m-%d"))

    # Start timing
    job_start_time = time.time()

    logger.info("Starting daily calculation job %(job_id)s for %(target_date)s"")

    # Phase 3: Publish task started event
    await _publish_task_progress(
        job_id=job_id,
        task_type="batch_daily",
        status=TaskStatus.RUNNING,
        progress=0.0,
        message=f"Starting daily calculation for {target_date}",
        processed=0,
        total=0,
    )

    # 1. Initialize Registry
    load_default_indicators()

    # 2. Initialize Scheduler & Repo
    scheduler = create_scheduler(max_workers=10, mode=CalculationMode.ASYNC_PARALLEL)
    scheduler.set_calculation_function(lambda abbr, data, p: from_factory(abbr).calculate(data, p))

    from app.services.indicators import IndicatorPluginFactory

    def from_factory(abbr):
        instance = IndicatorPluginFactory.create_instance(abbr)
        if not instance:
            raise ValueError(f"No plugin found for {abbr}")
        return instance

    repo = IndicatorRepository()

    # 3. Determine Indicators to Calculate
    target_indicators = params.get(
        "indicators",
        [
            {"abbreviation": "SMA", "params": {"timeperiod": 5}},
            {"abbreviation": "SMA", "params": {"timeperiod": 10}},
            {"abbreviation": "SMA", "params": {"timeperiod": 20}},
            {"abbreviation": "SMA", "params": {"timeperiod": 60}},
            {"abbreviation": "MACD", "params": {}},
            {"abbreviation": "RSI", "params": {"timeperiod": 14}},
            {"abbreviation": "BBANDS", "params": {}},
            {"abbreviation": "ATR", "params": {}},
            {"abbreviation": "KDJ", "params": {}},
        ],
    )

    # 4. Get Stocks
    stock_codes = params.get("stocks")
    if not stock_codes:
        try:
            df_stocks = db_service.query_stocks_basic(limit=5000)
            if df_stocks.empty:
                logger.warning("No stocks found in database")
                await _publish_task_progress(
                    job_id=job_id,
                    task_type="batch_daily",
                    status=TaskStatus.FAILED,
                    progress=0.0,
                    message="No stocks found in database",
                )
                return
            stock_codes = df_stocks["symbol"].tolist()
        except Exception as e:
            logger.error("Failed to fetch stock list: %(e)s"")
            await _publish_task_progress(
                job_id=job_id,
                task_type="batch_daily",
                status=TaskStatus.FAILED,
                progress=0.0,
                message=f"Failed to fetch stock list: {e}",
            )
            return

    total_stocks = len(stock_codes)
    logger.info("Processing %(total_stocks)s stocks..."")

    # Create task record
    try:
        repo.create_task(job_id, "batch_daily", params)
        repo.update_task(job_id, "running", 0.0)
    except Exception as e:
        logger.error("Failed to create task record: %(e)s"")

    # 5. Process Batch with event publishing
    success_count = 0
    fail_count = 0
    last_progress_percent = 0

    for idx, code in enumerate(stock_codes):
        stock_start_time = time.time()
        try:
            # Fetch Data
            end_date = target_date
            start_date = (pd.to_datetime(target_date) - pd.Timedelta(days=365)).strftime("%Y-%m-%d")

            df_kline = db_service.query_daily_kline(code, start_date, end_date)

            if df_kline.empty or len(df_kline) < 50:
                # Skip if not enough data
                continue

            # Convert to OHLCVData
            try:
                ohlcv = OHLCVData(
                    open=df_kline["open"].values.astype(float),
                    high=df_kline["high"].values.astype(float),
                    low=df_kline["low"].values.astype(float),
                    close=df_kline["close"].values.astype(float),
                    volume=df_kline["volume"].values.astype(float),
                    timestamps=pd.to_datetime(df_kline["date"]).to_pydatetime(),
                )
            except Exception as e:
                logger.warning("Data conversion failed for %(code)s: %(e)s"")
                continue

            # Calculate indicators
            schedule_results = scheduler.calculate(target_indicators, ohlcv)

            # Extract results and stats
            indicator_results = []
            calculated_indicators = []
            failed_indicators = 0
            from_cache_count = 0

            for res in schedule_results:
                if res.success and res.result:
                    indicator_results.append(res.result)
                    calculated_indicators.append(res.abbreviation)
                    if res.from_cache:
                        from_cache_count += 1
                else:
                    failed_indicators += 1

            # Save to DB
            if indicator_results:
                repo.save_results(code, ohlcv.timestamps, indicator_results)
                success_count += 1
            else:
                fail_count += 1

            # Phase 3: Publish stock completion event (Batching optimization)
            stock_calc_time = (time.time() - stock_start_time) * 1000  # Convert to ms
            await _publish_stock_completed(
                stock_code=code,
                indicators=calculated_indicators,
                success_count=len(calculated_indicators),
                failed_count=failed_indicators,
                calculation_time_ms=stock_calc_time,
                from_cache_count=from_cache_count,
            )

        except Exception as e:
            logger.error("Failed to process %(code)s: %(e)s"")
            fail_count += 1

        # Phase 3: Throttled progress updates (every 1% or 50 stocks)
        current_progress = (idx + 1) / total_stocks * 100
        if current_progress - last_progress_percent >= 1.0 or (idx + 1) % 50 == 0:  # Every 1%  # Or every 50 stocks

            last_progress_percent = current_progress

            # Update DB
            try:
                repo.update_task(job_id, "running", current_progress)
            except:
                pass

            # Publish progress event
            await _publish_task_progress(
                job_id=job_id,
                task_type="batch_daily",
                status=TaskStatus.RUNNING,
                progress=current_progress,
                message=f"Processing {code} ({idx + 1}/{total_stocks})",
                processed=idx + 1,
                total=total_stocks,
                failed=fail_count,
            )

    # 6. Finalize
    job_duration = time.time() - job_start_time

    try:
        repo.update_task(job_id, "success", 100.0, {"success": success_count, "failed": fail_count})
    except:
        pass

    # Phase 3: Publish task completed event
    final_status = (
        TaskStatus.COMPLETED if fail_count == 0 else TaskStatus.COMPLETED
    )  # Still completed even with some failures
    await _publish_task_completed(
        job_id=job_id,
        task_type="batch_daily",
        status=final_status,
        duration_seconds=job_duration,
        success=success_count,
        failed=fail_count,
    )

    logger.info(
        f"Job {job_id} completed. Success: {success_count}, Failed: {fail_count}, Duration: {job_duration:.2f}s"
    )
    return {"success": success_count, "failed": fail_count}
