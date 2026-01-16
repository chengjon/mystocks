import http from 'k6/http';
import { check, sleep } from 'k6';

// K6 Performance Test Configuration for MyStocks Web Application

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10, name: 'Warm up' },   // Warm up phase
    { duration: '5m', target: 50, name: 'Normal load' },  // Normal load
    { duration: '3m', target: 100, name: 'Peak load' },  // Peak load
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Less than 1% failure rate
    checks: ['rate>0.9'],              // More than 90% check pass rate
  },
};

// Base URL for testing
const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

/**
 * MyStocks Performance Test Suite
 */

export default function () {
  // Test 1: Homepage Load Test
  const homepageRes = http.get(`${BASE_URL}/`);

  check(homepageRes, {
    'Homepage Response Time': (r) => r.timings.duration < 500,
    'Homepage Status 200': (r) => r.status === 200,
    'Homepage has content': (r) => r.body.includes('MyStocks'),
  });

  sleep(1);

  // Test 2: Market Data API Load
  const marketDataRes = http.get(`${BASE_URL}/api/market/realtime`);

  check(marketDataRes, {
    'Market Data Response Time': (r) => r.timings.duration < 300,
    'Market Data Status 200': (r) => r.status === 200,
    'Market Data Valid JSON': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.success === true;
      } catch {
        return false;
      }
    },
  });

  sleep(1);

  // Test 3: Technical Indicators Load
  const indicatorsRes = http.get(`${BASE_URL}/api/technical/indicators/600000`);

  check(indicatorsRes, {
    'Indicators Response Time': (r) => r.timings.duration < 400,
    'Indicators Status 200': (r) => r.status === 200,
  });

  sleep(1);

  // Test 4: Login Page Load
  const loginRes = http.get(`${BASE_URL}/login`);

  check(loginRes, {
    'Login Page Response Time': (r) => r.timings.duration < 300,
    'Login Page Status 200': (r) => r.status === 200,
  });

  sleep(1);

  // Test 5: Dashboard Load (after simulated login)
  const dashboardRes = http.get(`${BASE_URL}/dashboard`);

  check(dashboardRes, {
    'Dashboard Response Time': (r) => r.timings.duration < 500,
    'Dashboard Status 200': (r) => r.status === 200,
  });
}

/**
 * Run K6 test with command line arguments
 */
export function runPerformanceTest(baseUrl?: string) {
  if (baseUrl) {
    __ENV.BASE_URL = baseUrl;
  }

  // Execute the test
  return defaultFunction();
}
