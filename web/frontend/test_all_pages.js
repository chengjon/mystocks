// Chrome DevTools Test for MyStocks All Pages
const puppeteer = require('puppeteer');

const pages = [
    { name: 'Home', path: '/' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Market', path: '/market' },
    { name: 'Stocks', path: '/stocks' },
    { name: 'Analysis', path: '/analysis' },
    { name: 'Risk', path: '/risk' },
    { name: 'Trading', path: '/trading' },
    { name: 'Strategy', path: '/strategy' },
    { name: 'System', path: '/system' },
    { name: 'ArtDeco Dashboard', path: '/artdeco/dashboard' },
    { name: 'ArtDeco Risk', path: '/artdeco/risk' },
    { name: 'ArtDeco Trading', path: '/artdeco/trading' },
    { name: 'ArtDeco Backtest', path: '/artdeco/backtest' },
    { name: 'ArtDeco Monitor', path: '/artdeco/monitor' },
    { name: 'ArtDeco Strategy', path: '/artdeco/strategy' },
    { name: 'ArtDeco Settings', path: '/artdeco/settings' },
    { name: 'ArtDeco Community', path: '/artdeco/community' },
    { name: 'ArtDeco Help', path: '/artdeco/help' }
];

async function testPage(page, browser) {
    const errors = [];
    const pageObj = await browser.newPage();
    
    pageObj.on('console', msg => {
        if (msg.type() === 'error') {
            const text = msg.text();
            // 忽略一些已知的警告
            if (!text.includes('Failed to load resource') && 
                !text.includes('Download error') &&
                !text.includes('deprecated') &&
                !text.includes('message port closed') &&
                !text.includes('503')) {
                errors.push('Console: ' + text.substring(0, 100));
            }
        }
    });
    
    pageObj.on('pageerror', error => {
        errors.push('Page Error: ' + error.message.substring(0, 100));
    });
    
    try {
        const response = await pageObj.goto('http://localhost:3002' + page.path, { 
            waitUntil: 'domcontentloaded', 
            timeout: 30000 
        });
        
        await pageObj.waitForTimeout(3000);
        
        if (errors.length > 0) {
            return { name: page.name, path: page.path, status: 'FAILED', errors, httpStatus: response ? response.status() : null };
        } else {
            return { name: page.name, path: page.path, status: 'PASSED', errors: [], httpStatus: response ? response.status() : null };
        }
    } catch (e) {
        return { name: page.name, path: page.path, status: 'ERROR', errors: [e.message], httpStatus: null };
    }
}

(async () => {
    console.log('Testing MyStocks Frontend Pages...\n');
    console.log('='.repeat(70));
    
    const browser = await puppeteer.launch({ 
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    
    const results = [];
    for (const p of pages) {
        const result = await testPage(p, browser);
        results.push(result);
        const icon = result.status === 'PASSED' ? '[PASS]' : result.status === 'FAILED' ? '[FAIL]' : '[ERR]';
        var namePad = result.name + '               '.substring(0, 20 - result.name.length);
        console.log(icon + ' ' + namePad + ' ' + result.path + ' HTTP:' + (result.httpStatus || 'N/A'));
        if (result.errors.length > 0) {
            result.errors.forEach(function(e) { console.log('   -> ' + e); });
        }
    }
    
    console.log('='.repeat(70));
    const passed = results.filter(function(r) { return r.status === 'PASSED'; }).length;
    const failed = results.filter(function(r) { return r.status !== 'PASSED'; }).length;
    console.log('\nResults: ' + passed + ' passed, ' + failed + ' failed\n');
    
    await browser.close();
    process.exit(failed > 0 ? 1 : 0);
})();
