const reportHtmlMethods = {
  generateHTMLReport() {
    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks Web端可用性测试报告</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .content { padding: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: #f8fafc; border-radius: 8px; padding: 20px; text-align: center; border-left: 4px solid #667eea; }
        .metric h3 { margin: 0 0 10px 0; color: #2d3748; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric .value { font-size: 2em; font-weight: bold; color: #2d3748; }
        .metric .unit { font-size: 0.8em; color: #718096; }
        .pass { color: #48bb78; }
        .fail { color: #f56565; }
        .warning { color: #ed8936; }
        .section { margin: 30px 0; padding: 20px; background: #f8fafc; border-radius: 8px; }
        .section h2 { margin: 0 0 20px 0; color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #edf2f7; font-weight: 600; color: #4a5568; }
        .status { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; }
        .status.passed { background: #c6f6d5; color: #22543d; }
        .status.failed { background: #fed7d7; color: #742a2a; }
        .status.warning { background: #feebc8; color: #7c2d12; }
        .progress-bar { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #48bb78, #38a169); transition: width 0.3s ease; }
        .criteria-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .criteria-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .criteria-card h4 { margin: 0 0 15px 0; color: #2d3748; }
        .score-display { font-size: 2em; font-weight: bold; text-align: center; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; border-top: 1px solid #e2e8f0; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MyStocks Web端可用性测试报告</h1>
            <p>生成时间: ${this.testResults.timestamp}</p>
        </div>

        <div class="content">
            <div class="summary">
                <div class="metric">
                    <h3>总体通过率</h3>
                    <div class="value ${this.testResults.summary.passRate >= 95 ? "pass" : "fail"}">
                        ${this.testResults.summary.passRate}%
                    </div>
                    <div class="unit">${this.testResults.summary.passed}/${this.testResults.summary.totalTests}</div>
                </div>
                <div class="metric">
                    <h3>功能性测试</h3>
                    <div class="value ${this.calculateFunctionalPassRate() >= 95 ? "pass" : "fail"}">
                        ${this.calculateFunctionalPassRate()}%
                    </div>
                    <div class="unit">通过率</div>
                </div>
                <div class="metric">
                    <h3>性能评分</h3>
                    <div class="value ${this.calculatePerformanceScore() >= 95 ? "pass" : "fail"}">
                        ${this.calculatePerformanceScore()}
                    </div>
                    <div class="unit">Lighthouse分数</div>
                </div>
                <div class="metric">
                    <h3>安全评分</h3>
                    <div class="value ${this.calculateSecurityScore() >= 100 ? "pass" : "warning"}">
                        ${this.calculateSecurityScore()}%
                    </div>
                    <div class="unit">安全通过率</div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 通过标准评估</h2>
                <div class="criteria-grid">
                    <div class="criteria-card">
                        <h4>功能性标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.functional?.actual >= 95 ? "pass" : "fail"}">
                            ${this.testResults.summary.criteria?.functional?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.functional?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥95%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>性能标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.performance?.actual >= 95 ? "pass" : "fail"}">
                            ${this.testResults.summary.criteria?.performance?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.performance?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥95%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>安全性标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.security?.actual >= 100 ? "pass" : "warning"}">
                            ${this.testResults.summary.criteria?.security?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.security?.actual || 0}%"></div>
                        </div>
                        <p>要求: 100%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>用户体验标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.usability?.actual >= 90 ? "pass" : "fail"}">
                            ${this.testResults.summary.criteria?.usability?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.usability?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥90%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>数据质量标准</h4>
                        <div class="score-display ${this.testResults.summary.criteria?.dataQuality?.actual >= 99 ? "pass" : "fail"}">
                            ${this.testResults.summary.criteria?.dataQuality?.actual || 0}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.criteria?.dataQuality?.actual || 0}%"></div>
                        </div>
                        <p>要求: ≥99%</p>
                    </div>
                    <div class="criteria-card">
                        <h4>总体评估</h4>
                        <div class="score-display ${this.testResults.summary.meetsStandard ? "pass" : "fail"}">
                            ${this.testResults.summary.overallScore}%
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.testResults.summary.overallScore}%"></div>
                        </div>
                        <p>${this.testResults.summary.meetsStandard ? '✅ 达到"完全可用"标准' : '❌ 未达到"完全可用"标准'}</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🧪 功能性测试结果</h2>
                ${this.renderFunctionalResults()}
            </div>

            <div class="section">
                <h2>⚡ 性能测试结果</h2>
                ${this.renderPerformanceResults()}
            </div>

            <div class="section">
                <h2>🔒 安全性测试结果</h2>
                ${this.renderSecurityResults()}
            </div>

            <div class="section">
                <h2>👤 用户体验测试结果</h2>
                ${this.renderUsabilityResults()}
            </div>

            <div class="section">
                <h2>📊 数据质量测试结果</h2>
                ${this.renderDataQualityResults()}
            </div>
        </div>

        <div class="footer">
            <p>📋 本报告由MyStocks Web端可用性测试工具自动生成</p>
            <p>🔄 建议定期执行测试以监控系统质量</p>
        </div>
    </div>
</body>
</html>`;
  },

  renderFunctionalResults() {
    const functional = this.testResults.functional;
    let html = "<table><tr><th>功能模块</th><th>测试用例</th><th>通过</th><th>失败</th><th>通过率</th><th>状态</th></tr>";

    Object.entries(functional).forEach(([module, results]) => {
      if (results.total) {
        const passRate = Math.round((results.passed / results.total) * 100);
        const status = passRate >= 95 ? "passed" : "failed";
        html += `
                    <tr>
                        <td>${module}</td>
                        <td>${results.total}</td>
                        <td>${results.passed}</td>
                        <td>${results.failed}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${status}">${passRate >= 95 ? "✅" : "❌"}</span></td>
                    </tr>
                `;
      }
    });

    html += "</table>";
    return html;
  },

  renderPerformanceResults() {
    const performance = this.testResults.performance;
    let html = "<table><tr><th>性能指标</th><th>目标值</th><th>实际值</th><th>状态</th></tr>";

    if (performance.lighthouse) {
      html += `
                <tr>
                    <td>Lighthouse性能评分</td>
                    <td>≥90</td>
                    <td>${performance.lighthouse.performance}</td>
                    <td><span class="status ${performance.lighthouse.performance >= 90 ? "passed" : "failed"}">${
                      performance.lighthouse.performance >= 90 ? "✅" : "❌"
                    }</span></td>
                </tr>
            `;
    }

    if (performance.api && performance.api.length > 0) {
      const avgResponseTime = Math.round(performance.api.reduce((sum, item) => sum + item.average, 0) / performance.api.length);
      html += `
                <tr>
                    <td>平均API响应时间</td>
                    <td>≤200ms</td>
                    <td>${avgResponseTime}ms</td>
                    <td><span class="status ${avgResponseTime <= 200 ? "passed" : "failed"}">${
                      avgResponseTime <= 200 ? "✅" : "❌"
                    }</span></td>
                </tr>
            `;
    }

    html += "</table>";
    return html;
  },

  renderSecurityResults() {
    const security = this.testResults.security;
    let html = "<table><tr><th>安全检查</th><th>项目数量</th><th>通过率</th><th>状态</th></tr>";

    Object.entries(security).forEach(([category, results]) => {
      if (Array.isArray(results)) {
        const passed = results.filter(item => item.status === "passed" || item.safe).length;
        const total = results.length;
        const passRate = Math.round((passed / total) * 100);
        html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${passRate === 100 ? "passed" : "warning"}">${
                          passRate === 100 ? "✅" : "⚠️"
                        }</span></td>
                    </tr>
                `;
      }
    });

    html += "</table>";
    return html;
  },

  renderUsabilityResults() {
    const usability = this.testResults.usability;
    let html = "<table><tr><th>用户体验检查</th><th>测试项目</th><th>通过数</th><th>状态</th></tr>";

    Object.entries(usability).forEach(([category, results]) => {
      if (Array.isArray(results)) {
        const passed = results.filter(item => item.success || item.found).length;
        const total = results.length;
        html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passed}</td>
                        <td><span class="status ${passed === total ? "passed" : "failed"}">${
                          passed === total ? "✅" : "❌"
                        }</span></td>
                    </tr>
                `;
      }
    });

    html += "</table>";
    return html;
  },

  renderDataQualityResults() {
    const dataQuality = this.testResults.dataQuality;
    let html = "<table><tr><th>数据质量检查</th><th>测试项目</th><th>通过数</th><th>通过率</th><th>状态</th></tr>";

    Object.entries(dataQuality).forEach(([category, results]) => {
      if (Array.isArray(results)) {
        const passed = results.filter(item => item.accurate || item.realTime || item.integrity).length;
        const total = results.length;
        const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
        html += `
                    <tr>
                        <td>${category}</td>
                        <td>${total}</td>
                        <td>${passed}</td>
                        <td>${passRate}%</td>
                        <td><span class="status ${passRate >= 99 ? "passed" : "failed"}">${
                          passRate >= 99 ? "✅" : "❌"
                        }</span></td>
                    </tr>
                `;
      }
    });

    html += "</table>";
    return html;
  },
};

module.exports = reportHtmlMethods;
