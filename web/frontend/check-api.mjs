import axios from 'axios';

const apis = [
  'GET /health',
  'GET /api/v1/market/list',
  'GET /api/v1/market/quote/600519',
  'GET /api/v1/auth/status',
  'GET /api/system/info'
];

console.log('🔍 测试后端API\n');

for (const api of apis) {
  const [method, path] = api.split(' ');
  const url = `http://localhost:8000${path}`;

  try {
    const response = await axios.get(url, { timeout: 5000 });
    console.log(`✅ ${api}`);
    console.log(`   状态: ${response.status}`);
    console.log(`   数据: ${JSON.stringify(response.data).substring(0, 100)}...\n`);
  } catch (error) {
    console.log(`❌ ${api}`);
    console.log(`   错误: ${error.message}\n`);
  }
}
