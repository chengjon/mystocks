/**
 * Trading Composable
 *
 * Vue 3 composable for trading operations with automatic error handling,
 * loading states, caching, and Mock data fallback.
 */

import { ref, readonly } from 'vue';
import { tradeApi } from '@/api/trade';
import type { AccountOverviewVM, OrderVM, PositionVM, TradeHistoryVM } from '@/utils/trade-adapters';

/**
 * Trading management composable
 *
 * Provides trading operations including:
 * - Account information
 * - Position management
 * - Order submission
 * - Trade history
 */
export function useTrading() {
  // State
  const accountInfo = ref<AccountOverviewVM | null>(null);
  const positions = ref<PositionVM[]>([]);
  const orders = ref<OrderVM[]>([]);
  const tradeHistory = ref<TradeHistoryVM[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch account information
   */
  const fetchAccountInfo = async () => {
    loading.value = true;
    error.value = null;

    try {
      accountInfo.value = await tradeApi.getAccountOverview();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取账户信息失败: ${errorMsg}`;
      console.error('[useTrading] fetchAccountInfo error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch positions
   */
  const fetchPositions = async () => {
    loading.value = true;
    error.value = null;

    try {
      positions.value = await tradeApi.getPositions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取持仓失败: ${errorMsg}`;
      console.error('[useTrading] fetchPositions error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch orders
   */
  const fetchOrders = async (params?: {
    symbol?: string;
    status?: string;
    side?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
    offset?: number;
  }) => {
    loading.value = true;
    error.value = null;

    try {
      orders.value = await tradeApi.getOrders(params);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取订单失败: ${errorMsg}`;
      console.error('[useTrading] fetchOrders error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Submit order
   */
  const submitOrder = async (order: {
    symbol: string;
    side: 'buy' | 'sell';
    type: 'market' | 'limit' | 'stop';
    quantity: number;
    price?: number;
  }): Promise<{ success: boolean; orderId?: string; message?: string }> => {
    loading.value = true;
    error.value = null;

    try {
      const orderResult = await tradeApi.createOrder(order);
      if (orderResult && orderResult.orderId) {
        await fetchPositions();
        return { success: true, orderId: orderResult.orderId };
      }
      return { success: false, message: '订单提交失败' };
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `订单提交失败: ${errorMsg}`;
      console.error('[useTrading] submitOrder error:', err);
      return { success: false, message: errorMsg };
    } finally {
      loading.value = false;
    }
  };

  /**
   * Cancel order
   */
  const cancelOrder = async (orderId: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      await tradeApi.cancelOrder(orderId);
      orders.value = orders.value.filter(o => o.orderId !== orderId);
      return true;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `取消订单失败: ${errorMsg}`;
      console.error('[useTrading] cancelOrder error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch trade history
   */
  const fetchTradeHistory = async (params?: {
    startDate?: string;
    endDate?: string;
    symbol?: string;
  }) => {
    loading.value = true;
    error.value = null;

    try {
      tradeHistory.value = await tradeApi.getTradeHistory(params);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取交易记录失败: ${errorMsg}`;
      console.error('[useTrading] fetchTradeHistory error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch all trading data
   */
  const fetchAll = async () => {
    await Promise.all([
      fetchAccountInfo(),
      fetchPositions(),
    ]);
  };

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null;
  };

  return {
    // State (readonly)
    accountInfo: readonly(accountInfo),
    positions: readonly(positions),
    orders: readonly(orders),
    tradeHistory: readonly(tradeHistory),
    loading: readonly(loading),
    error: readonly(error),

    // Methods
    fetchAccountInfo,
    fetchPositions,
    fetchOrders,
    submitOrder,
    cancelOrder,
    fetchTradeHistory,
    fetchAll,
    clearError,
  };
}

/**
 * Position management composable (dedicated to positions)
 */
export function usePositions() {
  const positions = ref<PositionVM[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchPositions = async () => {
    loading.value = true;
    error.value = null;

    try {
      positions.value = await tradeApi.getPositions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取持仓失败: ${errorMsg}`;
      console.error('[usePositions] fetchPositions error:', err);
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    positions: readonly(positions),
    loading: readonly(loading),
    error: readonly(error),
    fetchPositions,
    clearError,
  };
}

export default useTrading;
