/**
 * Web Access Verification Script
 *
 * Implements the verification standard defined in docs/guides/WEB_ACCESS_VERIFICATION_STANDARD.md
 * 1. Parses Vue Router file to dynamically find all routes
 * 2. Checks backend health
 * 3. Runs Playwright tests for every route
 * 4. Generates a standard Markdown report
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const http = require('http');

// Configuration
const CONFIG = {
  frontendPort: 3020,
  backendPort: 8000,
  routerPath: 'web/frontend/src/router/index.ts',
  reportPath: 'docs/reports/WEB_ACCESS_VERIFICATION_REPORT.md',
  standardDoc: 'docs/guides/WEB_ACCESS_VERIFICATION_STANDARD.md'
};

// ANSI Colors
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  bold: '\x1b[1m'
};

function log(msg, type = 'info') {
  const color = {
    info: colors.blue,
    success: colors.green,
    warn: colors.yellow,
    error: colors.red,
    header: colors.bold
  }[type] || colors.reset;
  console.log(`${color}${msg}${colors.reset}`);
}

// 1. Dynamic Route Parser
function parseRoutes(filePath) {
  log(`Parsing routes from ${filePath}...`, 'info');
  const content = fs.readFileSync(filePath, 'utf-8');
  
  const routes = [];
  const parentStack = [];
  
  // Simplified line-by-line parser for the specific structure of index.ts
  const lines = content.split('
');
  let currentParent = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Detect start of children array
    if (line.includes('children: [')) {
      if (currentParent) parentStack.push(currentParent);
    }
    
    // Detect end of children array
    if (line === ']' || line === '},' || line === '}') {
        // Simple heuristic: if we see closing brackets and indentation decreases (not implemented here but implied)
        // For this specific file structure, we rely on context. 
        // Actually, regex extraction of full objects is safer.
    }
  }

  // Regex Approach (More robust for this specific file)
  // 1. Find all parent routes (path: '/...') that have children
  // 2. Find all simple routes
  
  // Let's use a more direct approach: Extract all 'path' strings and reconstructions
  // Since we cannot easily execute the TS file, we will infer paths.
  
  const rawRoutes = [];
  
  // Helper to extract path value
  const extractPath = (str) => {
    const match = str.match(/path:\s*['"]([^'"]+)['"]/);
    return match ? match[1] : null;
  };

  // State machine
  let parentPath = '';
  let inChildren = false;
  let bracketCount = 0;

  lines.forEach(line => {
    // Track nesting level
    bracketCount += (line.match(/\[/g) || []).length;
    bracketCount -= (line.match(/\]/g) || []).length;
    
    if (bracketCount === 0) {
        parentPath = '';
        inChildren = false;
    }

    const pathVal = extractPath(line);
    if (pathVal) {
      if (pathVal.startsWith('/')) {
        // Absolute path (Parent or standalone)
        parentPath = pathVal;
        if (!line.includes('children:')) {
             rawRoutes.push(pathVal);
        }
      } else {
        // Relative path (Child)
        // Handle empty path child (dashboard index)
        const fullPath = pathVal ? `${parentPath}/${pathVal}`.replace('//', '/') : parentPath;
        rawRoutes.push(fullPath);
      }
    }
  });

  // Filter out wildcards and parameters
  const validRoutes = rawRoutes
    .filter(r => !r.includes(':') && !r.includes('*'))
    .map(r => r.replace(/\/+$/, '')) // Remove trailing slash
    .filter((v, i, a) => a.indexOf(v) === i) // Unique
    .sort();

  log(`Found ${validRoutes.length} valid static routes.`, 'success');
  return validRoutes;
}

// 2. Backend Health Check
function checkBackend() {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${CONFIG.backendPort}/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200 || res.statusCode === 0) {
           try {
             const json = JSON.parse(data);
             log(`Backend Health: OK (${JSON.stringify(json)})`, 'success');
             resolve(true);
           } catch (e) {
             log(`Backend Health: Invalid JSON`, 'warn');
             resolve(false);
           }
        } else {
          log(`Backend Health: Failed (Status ${res.statusCode})`, 'error');
          resolve(false);
        }
      });
    });
    req.on('error', (e) => {
      log(`Backend Health: Connection Refused (${e.message})`, 'error');
      resolve(false);
    });
    req.end();
  });
}

// 3. Run Validation
async function runValidation() {
  log(`
Starting Web Access Verification...`, 'header');
  log(`Standard: ${CONFIG.standardDoc}
`, 'info');

  // A. Check Backend
  const backendOk = await checkBackend();
  
  // B. Parse Routes
  const routes = parseRoutes(CONFIG.routerPath);
  
  // C. Execute Test Script (reusing logic from test_all_pages.mjs but injecting routes)
  // We will create a temporary test runner
  const testRunnerPath = 'scripts/dev/temp_runner.mjs';
  const baseScript = fs.readFileSync('scripts/dev/test_all_pages.mjs', 'utf-8');
  
  // Replace ROUTES array in the script with our dynamic one
  const newScriptContent = baseScript.replace(
    /const ROUTES = \[[\s\S]*?\];/,
    `const ROUTES = ${JSON.stringify(routes)};`
  ).replace(
      // Ensure report path is also dynamic if needed, or keep default
      /page_test_results\.json/, 'verification_results.json'
  );
  
  fs.writeFileSync(testRunnerPath, newScriptContent);
  
  log(`Executing Playwright tests for ${routes.length} routes...`, 'info');
  
  try {
    execSync(`node ${testRunnerPath}`, { stdio: 'inherit' });
  } catch (e) {
    log('Test execution encountered errors (this is expected if pages failed)', 'warn');
  }

  // D. Process Results
  const resultPath = '/opt/claude/mystocks_spec/scripts/dev/verification_results.json';
  if (!fs.existsSync(resultPath)) {
      log('Fatal: Test results file not found!', 'error');
      process.exit(1);
  }
  
  const results = JSON.parse(fs.readFileSync(resultPath, 'utf-8'));
  const passed = results.pass.length;
  const failed = results.fail.length;
  const total = routes.length; // Use routes.length as total source of truth
  const rate = ((passed / total) * 100).toFixed(1);

  // E. Generate Report
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
  const statusIcon = failed === 0 ? '✅' : (passed > 0 ? '⚠️' : '❌');
  const statusText = failed === 0 ? '服务正常' : (passed > 0 ? '部分可用' : '服务异常');
  
  const report = `## Web 端访问验证报告

**验证时间**: ${timestamp}
**前端端口**: ${CONFIG.frontendPort}
**后端端口**: ${CONFIG.backendPort}
**标准文档**: [WEB_ACCESS_VERIFICATION_STANDARD.md](../../${CONFIG.standardDoc})

### 1. 服务状态
- **后端连接**: ${backendOk ? '✅ 正常' : '❌ 失败'}
- **路由覆盖**: ${total} 个页面
- **验证结论**: ${statusIcon} **${statusText}**

### 2. 页面测试详情
| 指标 | 结果 | 阈值 | 状态 |
|---|---|---|---|
| 通过率 | **${rate}%** (${passed}/${total}) | 100% | ${passed === total ? '✅' : '❌'} |
| 白屏/崩溃 | ${failed} 个 | 0 | ${failed === 0 ? '✅' : '❌'} |

### 3. 失败页面清单
${failed === 0 ? '_无失败页面_' : 
`| 页面 | 错误简述 |
|---|---|
${results.fail.map(url => `| `${url}` | ${formatError(results.errors[url])} |`).join('
')}
`}

### 4. 警告信息 (非阻塞)
- 控制台警告页面数: ${Object.values(results.errors).filter(e => e.severity === 'warning').length}

---
*Generated by scripts/verify_web_access.js*
`;

  // Ensure directory exists
  const reportDir = path.dirname(CONFIG.reportPath);
  if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
  }

  fs.writeFileSync(CONFIG.reportPath, report);
  log(`
Report generated at: ${CONFIG.reportPath}`, 'success');
  console.log(report); // Print to console

  // F. Cleanup
  fs.unlinkSync(testRunnerPath);
  fs.unlinkSync(resultPath);

  // G. Exit Code
  if (failed > 0 || !backendOk) {
      log('Verification FAILED.', 'error');
      process.exit(1);
  } else {
      log('Verification PASSED.', 'success');
      process.exit(0);
  }
}

function formatError(errorObj) {
    if (!errorObj) return 'Unknown';
    if (errorObj.issues && errorObj.issues.length) return errorObj.issues.join(', ');
    if (errorObj.error) return errorObj.error.substring(0, 50) + '...';
    return 'Unknown Error';
}

runValidation();
