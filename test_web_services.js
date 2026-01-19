#!/usr/bin/env node

/**
 * Simple Web Service Verification Script
 * Tests if frontend and backend are accessible
 */

const http = require('http');

function testService(name, url, expectedStatus = 200) {
  return new Promise((resolve) => {
    console.log(`🔍 Testing ${name} at ${url}...`);

    const req = http.get(url, (res) => {
      const { statusCode } = res;

      if (statusCode === expectedStatus) {
        console.log(`✅ ${name}: ${statusCode} OK`);
        resolve(true);
      } else {
        console.log(`❌ ${name}: Expected ${expectedStatus}, got ${statusCode}`);
        resolve(false);
      }
    });

    req.on('error', (err) => {
      console.log(`❌ ${name}: Connection failed - ${err.message}`);
      resolve(false);
    });

    req.setTimeout(5000, () => {
      console.log(`❌ ${name}: Timeout after 5 seconds`);
      req.destroy();
      resolve(false);
    });
  });
}

async function main() {
  console.log('🚀 MyStocks Web Service Verification\n');

  const results = await Promise.all([
    testService('Frontend (port 3001)', 'http://localhost:3001'),
    testService('Backend API (port 8000)', 'http://localhost:8000/api/health'),
  ]);

  const allPassed = results.every(result => result);

  console.log('\n' + '='.repeat(50));

  if (allPassed) {
    console.log('🎉 ALL SERVICES ARE RUNNING SUCCESSFULLY!');
    console.log('\n📋 Access URLs:');
    console.log('   Frontend: http://localhost:3020');
    console.log('   Backend:  http://localhost:8000');
    console.log('\n🔧 PM2 Management:');
    console.log('   Status: pm2 list');
    console.log('   Logs:   pm2 logs');
    console.log('   Stop:   pm2 stop all && pm2 delete all');
  } else {
    console.log('❌ SOME SERVICES FAILED TO START');
    console.log('\n🔧 Check PM2 logs: pm2 logs');
  }

  console.log('='.repeat(50));
}

main().catch(console.error);