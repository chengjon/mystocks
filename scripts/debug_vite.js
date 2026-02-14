const http = require('http');

const PORT = 3003; // 根据上次运行结果调整，或手动指定
const TARGETS = [
    '/',
    '/index.html',
    '/src/main.js',
    '/src/main.ts',
    '/@vite/client'
];

async function check(urlPath) {
    return new Promise((resolve) => {
        const url = `http://localhost:${PORT}${urlPath}`;
        console.log(`Checking ${url}...`);
        
        http.get(url, (res) => {
            console.log(`  STATUS: ${res.statusCode}`);
            console.log(`  HEADERS: ${res.headers['content-type']}`);
            
            let data = '';
            res.on('data', chunk => { if (data.length < 500) data += chunk; });
            res.on('end', () => {
                // console.log(`  PREVIEW: ${data.substring(0, 100)}...`);
                resolve(res.statusCode);
            });
        }).on('error', (e) => {
            console.log(`  ERROR: ${e.message}`);
            resolve(500);
        });
    });
}

async function run() {
    console.log('--- Vite Service Debugger ---');
    for (const t of TARGETS) {
        await check(t);
    }
}

run();
