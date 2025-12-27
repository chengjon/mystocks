// Test BollingerBands API format
const { BollingerBands } = require('technicalindicators');

const testPrices = Array(100).fill(0).map((_, i) => 10 + Math.random());

console.log('Testing BollingerBands API formats...\n');

// Test 1: with stdDev
try {
  const result1 = BollingerBands.calculate({
    period: 20,
    values: testPrices,
    stdDev: 2
  });
  console.log('✓ Format 1 (stdDev) works:', result1.length, 'results');
} catch (e) {
  console.log('✗ Format 1 (stdDev) failed:', e.message);
}

// Test 2: with stdDevUp and stdDevDown
try {
  const result2 = BollingerBands.calculate({
    period: 20,
    values: testPrices,
    stdDevUp: 2,
    stdDevDown: 2
  });
  console.log('✓ Format 2 (stdDevUp/stdDevDown) works:', result2.length, 'results');
} catch (e) {
  console.log('✗ Format 2 (stdDevUp/stdDevDown) failed:', e.message);
}

// Test 3: with stdDev (numeric value only)
try {
  const result3 = BollingerBands.calculate({
    period: 20,
    stdDev: 2,
    values: testPrices
  });
  console.log('✓ Format 3 (stdDev first, values last) works:', result3.length, 'results');
} catch (e) {
  console.log('✗ Format 3 failed:', e.message);
}
