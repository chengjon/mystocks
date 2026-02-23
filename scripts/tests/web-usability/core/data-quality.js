const getAxios = require("./http-client");

const dataQualityMethods = {
  async runDataQualityTests() {
    console.log("  📊 执行数据准确性测试...");
    const accuracyResults = await this.runDataAccuracyTests();
    this.testResults.dataQuality.accuracy = accuracyResults;

    console.log("  ⏰ 执行数据实时性测试...");
    const realtimeResults = await this.runDataRealtimeTests();
    this.testResults.dataQuality.realtime = realtimeResults;

    console.log("  🔍 执行数据完整性测试...");
    const integrityResults = await this.runDataIntegrityTests();
    this.testResults.dataQuality.integrity = integrityResults;
  },

  async runDataAccuracyTests() {
    const axios = getAxios();
    const stocks = ["000001", "000002", "600000"];
    const results = [];

    for (const symbol of stocks) {
      try {
        const response = await axios.get(`${this.config.apiUrl}/api/data/realtime/${symbol}`, { timeout: 5000 });
        const data = response.data;

        if (data && typeof data === "object") {
          const hasRequiredFields = ["price", "volume", "change"].every(field => Object.prototype.hasOwnProperty.call(data, field));
          const priceValid = typeof data.price === "number" && data.price > 0;
          const volumeValid = typeof data.volume === "number" && data.volume >= 0;

          results.push({
            symbol,
            accurate: hasRequiredFields && priceValid && volumeValid,
            hasRequiredFields,
            priceValid,
            volumeValid,
          });
        } else {
          results.push({ symbol, accurate: false, error: "Invalid data format" });
        }
      } catch (error) {
        results.push({ symbol, accurate: false, error: error.message });
      }
    }

    return results;
  },

  async runDataRealtimeTests() {
    const axios = getAxios();
    const symbol = "000001";
    const samples = 5;
    const times = [];

    for (let i = 0; i < samples; i += 1) {
      try {
        const start = Date.now();
        await axios.get(`${this.config.apiUrl}/api/data/realtime/${symbol}`, { timeout: 2000 });
        const responseTime = Date.now() - start;
        times.push(responseTime);

        // 等待一段时间避免请求过快
        await new Promise(resolve => {
          setTimeout(resolve, 200);
        });
      } catch (error) {
        console.warn("实时数据请求失败:", error.message);
      }
    }

    if (times.length > 0) {
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const max = Math.max(...times);

      return {
        samples: times.length,
        averageResponseTime: Math.round(average),
        maxResponseTime: max,
        meetsStandard: average <= 500, // 500ms标准
        realTime: true,
      };
    }

    return { realTime: false, error: "无法获取实时数据" };
  },

  async runDataIntegrityTests() {
    const axios = getAxios();
    try {
      // 检查历史数据完整性
      const symbol = "000001";
      const response = await axios.get(`${this.config.apiUrl}/api/data/history/${symbol}?period=1d&count=30`, {
        timeout: 10000,
      });

      if (response.data && Array.isArray(response.data)) {
        const data = response.data;
        const hasValidStructure = data.every(
          item =>
            Object.prototype.hasOwnProperty.call(item, "date") &&
            Object.prototype.hasOwnProperty.call(item, "price") &&
            Object.prototype.hasOwnProperty.call(item, "volume")
        );

        const hasValidData = data.every(
          item => typeof item.price === "number" && item.price > 0 && typeof item.volume === "number" && item.volume >= 0
        );

        return {
          symbol,
          recordCount: data.length,
          hasValidStructure,
          hasValidData,
          integrity: hasValidStructure && hasValidData,
        };
      }

      return { symbol, integrity: false, error: "Invalid response format" };
    } catch (error) {
      return { integrity: false, error: error.message };
    }
  },
};

module.exports = dataQualityMethods;
