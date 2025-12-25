/**
 * Mock K-Line Data
 *
 * Used for fallback when API fails
 */

// Generate mock K-line candles
function generateKlineCandles(count: number) {
  const candles = [];
  const basePrice = 10.0;
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - (count - i));

    const open = basePrice + Math.random() * 2 - 1;
    const close = open + Math.random() * 1 - 0.5;
    const high = Math.max(open, close) + Math.random() * 0.5;
    const low = Math.min(open, close) - Math.random() * 0.5;

    candles.push({
      datetime: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: Math.floor(Math.random() * 1000000 + 500000),
      amount: Math.floor(Math.random() * 10000000 + 5000000),
    });
  }

  return candles;
}

export default generateKlineCandles(100);
