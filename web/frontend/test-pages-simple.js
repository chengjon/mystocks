const { chromium } = require('@playwright/test');

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

// 忽略的预期错误模式
const IGNORED_PATTERNS = [
    '/api/contracts/',       // 版本检测端点，可能不存在
    'Failed to load resource',
    'Download error',
    'deprecated',
    'message port closed',
    '503',
    'Not Found',
    'CORS',
    'Access to XMLHttpRequest'
];

function shouldIgnoreError(text) {
    return IGNORED_PATTERNS.some(function(pattern) {
        return text.includes(pattern);
    });
}

(async () => {
    const browser = await chromium.launch({ headless: true });
    
    console.log('Testing MyStocks Frontend Pages...\n');
    console.log('='.repeat(70));
    
    let passed = 0;
    let failed = 0;
    let errors = [];
    
    for (const p of pages) {
        const page = await browser.newPage();
        const pageErrors = [];
        
        page.on('console', msg => {
            if (msg.type() === 'error' && !shouldIgnoreError(msg.text())) {
                pageErrors.push('Console: ' + msg.text().substring(0, 100));
            }
        });
        
        page.on('pageerror', error => {
            if (!shouldIgnoreError(error.message)) {
                pageErrors.push('Page Error: ' + error.message.substring(0, 100));
            }
        });
        
        try {
            const response = await page.goto('http://localhost:3002' + p.path, { 
                waitUntil: 'domcontentloaded',
                timeout: 30000 
            });
            
            await page.waitForTimeout(2000);
            
            const status = response ? response.status() : 0;
            const namePad = p.name + '                    '.substring(0, 20);
            
            if (status >= 200 && status < 400) {
                if (pageErrors.length === 0) {
                    console.log('[PASS] ' + namePad + ' ' + p.path + ' HTTP:' + status);
                    passed++;
                } else {
                    console.log('[FAIL] ' + namePad + ' ' + p.path + ' HTTP:' + status + ' JS Errors:' + pageErrors.length);
                    pageErrors.forEach(function(e) { console.log('       -> ' + e); });
                    failed++;
                    errors = errors.concat(pageErrors);
                }
            } else {
                console.log('[FAIL] ' + namePad + ' ' + p.path + ' HTTP:' + status);
                failed++;
            }
        } catch (e) {
            console.log('[ERR]  ' + p.name + ' ' + p.path + ' - ' + e.message.substring(0, 50));
            failed++;
        }
        
        await page.close();
    }
    
    console.log('='.repeat(70));
    console.log('\nResults: ' + passed + ' passed, ' + failed + ' failed');
    console.log('Note: Ignored expected errors (version detection, CORS, deprecated warnings)\n');
    
    await browser.close();
    process.exit(failed > 0 ? 1 : 0);
})();
