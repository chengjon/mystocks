const getAxios = require("./http-client");

const environmentMethods = {
  async checkEnvironment() {
    const axios = getAxios();
    console.log("🔍 检查测试环境...");

    try {
      // 检查前端服务
      const frontendResponse = await axios.get(`${this.config.baseUrl}`, { timeout: 5000 });
      this.testResults.environment.frontend = {
        status: frontendResponse.status,
        accessible: true,
      };
      console.log("✅ 前端服务正常");

      // 检查后端服务
      const backendResponse = await axios.get(`${this.config.apiUrl}/health`, { timeout: 5000 });
      this.testResults.environment.backend = {
        status: backendResponse.status,
        accessible: true,
      };
      console.log("✅ 后端服务正常");

      // 检查数据库连接
      await this.checkDatabaseConnection();

      console.log("✅ 环境检查完成");
    } catch (error) {
      console.error("❌ 环境检查失败:", error.message);
      throw new Error("测试环境不完整，请确保所有服务正常运行");
    }
  },

  async checkDatabaseConnection() {
    const axios = getAxios();
    try {
      const response = await axios.get(`${this.config.apiUrl}/api/system/health`, { timeout: 5000 });
      this.testResults.environment.database = {
        status: "connected",
        details: response.data,
      };
      console.log("✅ 数据库连接正常");
    } catch (error) {
      this.testResults.environment.database = {
        status: "disconnected",
        error: error.message,
      };
      throw error;
    }
  },
};

module.exports = environmentMethods;
