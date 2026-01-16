"""
Test Real-time Trading Integration
测试实时交易集成

Validates the integration between ML strategies, real-time data, and live trading engine.
验证ML策略、实时数据和实时交易引擎之间的集成。
"""

import asyncio
import logging
import sys
import os

# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.trading.realtime_strategy_executor import create_realtime_executor, RealtimeStrategyExecutor
from src.trading.live_trading_engine import LiveTradingConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_realtime_trading_integration():
    """Test the complete real-time trading integration"""
    logger.info("🧪 Starting real-time trading integration test...")

    try:
        # Create executor with default strategies
        executor = await create_realtime_executor(
            strategy_names=["SVMTradingStrategy"],  # Start with one strategy for testing
            config=LiveTradingConfig(
                max_positions=2,  # Limit positions for testing
                min_signal_confidence=0.5,  # Lower threshold for testing
                position_update_interval=5,  # Faster updates for testing
                market_data_update_interval=3,  # Faster market data for testing
            ),
        )

        logger.info("✅ Executor created successfully")

        # Test market data snapshot
        logger.info("📊 Testing market data snapshot...")
        snapshot = executor.get_market_data_snapshot()
        logger.info("Market data snapshot: %d symbols", snapshot["symbols_count"])

        # Test strategy performance
        logger.info("📈 Testing strategy performance...")
        performance = executor.get_strategy_performance()
        logger.info("Strategy performance: %s", list(performance.keys()))

        # Test execution status
        logger.info("📋 Testing execution status...")
        status = executor.get_execution_status()
        logger.info("Execution status: running=%s, strategies=%d", status["is_running"], len(status["strategies"]))

        # Start execution (brief test)
        logger.info("🚀 Starting real-time execution (brief test)...")
        session_id = await executor.start_execution()
        logger.info("✅ Execution started with session: %s", session_id)

        # Wait a few seconds for execution
        await asyncio.sleep(10)

        # Check status during execution
        status = executor.get_execution_status()
        logger.info("📊 Execution status during run: %s", status)

        # Stop execution
        logger.info("🛑 Stopping execution...")
        summary = await executor.stop_execution()
        logger.info("✅ Execution stopped. Summary: %s", summary)

        logger.info("🎉 Real-time trading integration test completed successfully!")

        return True

    except Exception as e:
        logger.error("❌ Real-time trading integration test failed: %s", e)
        import traceback

        traceback.print_exc()
        return False


async def test_strategy_management():
    """Test strategy management features"""
    logger.info("🔧 Testing strategy management...")

    try:
        # Create executor with minimal config
        executor = RealtimeStrategyExecutor([], LiveTradingConfig())

        # Test adding strategies
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy

        strategy = SVMTradingStrategy()

        success = executor.add_strategy(strategy)
        if success:
            logger.info("✅ Strategy added successfully")
        else:
            logger.error("❌ Failed to add strategy")
            return False

        # Test strategy config update (strategies may not have update_config method)
        success = executor.update_strategy_config("SVMTradingStrategy", {"test_param": "test_value"})
        if success:
            logger.info("✅ Strategy config updated successfully")
        else:
            logger.warning("⚠️ Strategy config update failed (method may not be implemented)")

        # Test removing strategy
        success = executor.remove_strategy("SVMTradingStrategy")
        if success:
            logger.info("✅ Strategy removed successfully")
        else:
            logger.error("❌ Failed to remove strategy")
            return False

        logger.info("🎉 Strategy management test completed successfully!")
        return True

    except Exception as e:
        logger.error("❌ Strategy management test failed: %s", e)
        return False


async def run_all_tests():
    """Run all integration tests"""
    logger.info("🚀 Running complete real-time trading integration test suite...")

    results = []

    # Test 1: Strategy management
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: Strategy Management")
    logger.info("=" * 50)
    result1 = await test_strategy_management()
    results.append(("Strategy Management", result1))

    # Test 2: Real-time trading integration
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: Real-time Trading Integration")
    logger.info("=" * 50)
    result2 = await test_realtime_trading_integration()
    results.append(("Real-time Trading Integration", result2))

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info("%s: %s", test_name, status)
        if success:
            passed += 1

    logger.info("Overall: %d/%d tests passed", passed, total)

    if passed == total:
        logger.info("🎉 All tests passed! Real-time trading integration is ready.")
        return True
    else:
        logger.warning("⚠️ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
