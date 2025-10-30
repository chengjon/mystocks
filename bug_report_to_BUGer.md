 以下是B项目中使用BUGer服务的具体步骤和代码：

  1. 安装依赖

   1 # 在B项目目录中安装axios
   2 npm install axios

  2. 创建环境配置文件

  在B项目根目录创建 .env 文件：

   1 # .env
   2 BUGER_API_URL=http://localhost:3003/api
   3 BUGER_API_KEY=sk_test_xyz123
   4 PROJECT_ID=test-project

  3. 创建BUG报告客户端

  创建 src/utils/bug-reporter.js 文件：

     1 // src/utils/bug-reporter.js
     2 const axios = require('axios');
     3 require('dotenv').config();
     4
     5 class BugReporter {
     6   constructor() {
     7     this.apiURL = process.env.BUGER_API_URL || 'http://localhost:3003/api';
     8     this.apiKey = process.env.BUGER_API_KEY || 'sk_test_xyz123';
     9     this.projectId = process.env.PROJECT_ID || 'test-project';
    10     this.queue = [];
    11     this.batchSize = 10;
    12     this.flushInterval = 30000; // 30秒
    13
    14     // 启动定时刷新
    15     this.startAutoFlush();
    16   }
    17
    18   // 上报单个BUG
    19   async reportBug(bugData) {
    20     try {
    21       const response = await axios.post(`${this.apiURL}/bugs`, bugData, {
    22         headers: {
    23           'X-API-Key': this.apiKey,
    24           'Content-Type': 'application/json'
    25         }
    26       });
    27       console.log('BUG上报成功:', response.data.data.bugId);
    28       return response.data;
    29     } catch (error) {
    30       console.error('BUG上报失败:', error.response?.data || error.message);
    31       throw error;
    32     }
    33   }
    34
    35   // 批量上报BUG
    36   async reportBugsBatch(bugs) {
    37     try {
    38       const response = await axios.post(`${this.apiURL}/bugs/batch`,
    39         { bugs },
    40         {
    41           headers: {
    42             'X-API-Key': this.apiKey,
    43             'Content-Type': 'application/json'
    44           }
    45         }
    46       );
    47       console.log(`批量上报完成: ${response.data.data.summary.successful}成功,
       ${response.data.data.summary.failed}失败`);
    48       return response.data;
    49     } catch (error) {
    50       console.error('批量BUG上报失败:', error.response?.data || error.message);
    51       throw error;
    52     }
    53   }
    54
    55   // 格式化错误信息
    56   formatError(error, context = {}) {
    57     return {
    58       errorCode: error.code || error.name || 'UNKNOWN_ERROR',
    59       title: error.message || '未知错误',
    60       message: error.stack || error.message || '无详细信息',
    61       severity: this.getSeverity(error),
    62       stackTrace: error.stack || '',
    63       context: {
    64         timestamp: new Date().toISOString(),
    65         ...context
    66       }
    67     };
    68   }
    69
    70   // 根据错误类型确定严重级别
    71   getSeverity(error) {
    72     // 根据错误类型或状态码确定严重级别
    73     if (error.code) {
    74       if (error.code.includes('DATABASE') || error.code.includes('CONNECTION')) {
    75         return 'critical';
    76       }
    77       if (error.code.includes('AUTH') || error.code.includes('PERMISSION')) {
    78         return 'high';
    79       }
    80     }
    81
    82     if (error.statusCode) {
    83       if (error.statusCode >= 500) return 'critical';
    84       if (error.statusCode >= 400) return 'medium';
    85     }
    86
    87     return 'medium';
    88   }
    89
    90   // 收集错误到队列（用于批量上报）
    91   collectError(error, context = {}) {
    92     const bugData = this.formatError(error, context);
    93     this.queue.push(bugData);
    94
    95     // 如果队列达到批处理大小，立即发送
    96     if (this.queue.length >= this.batchSize) {
    97       this.flushQueue();
    98     }
    99   }
   100
   101   // 刷新队列并发送所有待处理的BUG
   102   async flushQueue() {
   103     if (this.queue.length === 0) return;
   104
   105     const bugsToSend = [...this.queue];
   106     this.queue = []; // 清空队列
   107
   108     try {
   109       await this.reportBugsBatch(bugsToSend);
   110     } catch (error) {
   111       console.error('刷新队列失败:', error.message);
   112       // 如果发送失败，将BUG重新加入队列
   113       this.queue.unshift(...bugsToSend);
   114     }
   115   }
   116
   117   // 启动自动刷新定时器
   118   startAutoFlush() {
   119     setInterval(() => {
   120       if (this.queue.length > 0) {
   121         this.flushQueue();
   122       }
   123     }, this.flushInterval);
   124   }
   125 }
   126
   127 // 创建单例实例
   128 const bugReporter = new BugReporter();
   129
   130 module.exports = { BugReporter, bugReporter };

  4. 在主应用中集成错误处理

  在 src/app.js 或主入口文件中：

    1 // src/app.js
    2 const { bugReporter } = require('./utils/bug-reporter');
    3
    4 // 捕获未处理的异常
    5 process.on('uncaughtException', async (error) => {
    6   console.error('未捕获的异常:', error);
    7
    8   try {
    9     await bugReporter.reportBug(bugReporter.formatError(error, {
   10       process: 'main',
   11       type: 'uncaughtException'
   12     }));
   13   } catch (reportError) {
   14     console.error('错误上报失败:', reportError.message);
   15   }
   16
   17   process.exit(1);
   18 });
   19
   20 // 捕获未处理的Promise拒绝
   21 process.on('unhandledRejection', async (reason, promise) => {
   22   console.error('未处理的Promise拒绝:', reason);
   23
   24   try {
   25     await bugReporter.reportBug(bugReporter.formatError(reason, {
   26       process: 'main',
   27       type: 'unhandledRejection'
   28     }));
   29   } catch (reportError) {
   30     console.error('错误上报失败:', reportError.message);
   31   }
   32 });
   33
   34 // 其他应用代码...

  5. 在业务逻辑中使用BUG报告

  在您的业务逻辑中：

    1 // src/services/user-service.js
    2 const { bugReporter } = require('../utils/bug-reporter');
    3
    4 class UserService {
    5   async getUserById(userId) {
    6     try {
    7       // 模拟业务逻辑
    8       if (!userId) {
    9         throw new Error('用户ID不能为空');
   10       }
   11
   12       // 模拟数据库查询
   13       const user = await this.database.findUser(userId);
   14       return user;
   15     } catch (error) {
   16       // 格式化并上报错误
   17       const context = {
   18         service: 'UserService',
   19         method: 'getUserById',
   20         userId: userId
   21       };
   22
   23       // 收集错误（用于批量上报）
   24       bugReporter.collectError(error, context);
   25
   26       // 或者立即上报单个错误
   27       // await bugReporter.reportBug(bugReporter.formatError(error, context));
   28
   29       // 重新抛出错误
   30       throw error;
   31     }
   32   }
   33
   34   async batchProcessUsers(userIds) {
   35     const errors = [];
   36
   37     for (const userId of userIds) {
   38       try {
   39         await this.getUserById(userId);
   40       } catch (error) {
   41         errors.push({ userId, error });
   42       }
   43     }
   44
   45     // 如果有错误，批量上报
   46     if (errors.length > 0) {
   47       await bugReporter.flushQueue(); // 先发送队列中的错误
   48     }
   49
   50     return { processed: userIds.length, errors: errors.length };
   51   }
   52 }
   53
   54 module.exports = { UserService };

  6. 使用示例

    1 // example-usage.js
    2 const { bugReporter } = require('./src/utils/bug-reporter');
    3
    4 // 立即上报单个错误
    5 async function reportSingleError() {
    6   try {
    7     throw new Error('这是一个测试错误');
    8   } catch (error) {
    9     await bugReporter.reportBug(bugReporter.formatError(error, {
   10       component: 'ExampleComponent',
   11       action: 'testErrorReporting'
   12     }));
   13   }
   14 }
   15
   16 // 收集错误用于批量上报
   17 function collectErrors() {
   18   try {
   19     throw new Error('批量错误1');
   20   } catch (error) {
   21     bugReporter.collectError(error, { batch: 'test1' });
   22   }
   23
   24   try {
   25     throw new Error('批量错误2');
   26   } catch (error) {
   27     bugReporter.collectError(error, { batch: 'test2' });
   28   }
   29 }
   30
   31 // 手动刷新队列
   32 async function flushErrors() {
   33   await bugReporter.flushQueue();
   34 }
   35
   36 // 使用示例
   37 reportSingleError();
   38 collectErrors();
   39 // 30秒后会自动刷新队列，或者手动调用flushErrors()

  7. package.json依赖

  确保您的 package.json 包含必要的依赖：

   1 {
   2   "dependencies": {
   3     "axios": "^1.6.0",
   4     "dotenv": "^16.3.1"
   5   }
   6 }
