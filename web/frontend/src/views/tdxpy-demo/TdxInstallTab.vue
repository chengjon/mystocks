<template>
    <el-card v-show="activeTab === 'install'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 安装和配置</span>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 安装方式</h3>
        <p>pytdx 可以通过 pip 直接安装:</p>

        <pre v-pre class="code-block"># 安装 pytdx
pip install pytdx

# 或者从源码安装
git clone https://github.com/rainx/pytdx.git
cd pytdx
python setup.py install</pre>

        <h3 style="margin-top: 30px;">🔧 基础配置</h3>
        <p>pytdx 提供了两种主要的 API 类型:</p>

        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="标准行情 API">
            <div class="tab-content">
              <h4>📊 TdxHq_API - 标准行情接口</h4>
              <p>用于获取基础行情数据,如K线、实时价格等:</p>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# 创建 API 对象
api = TdxHq_API()

# 连接服务器
if api.connect('119.147.212.81', 7709):
    print("连接成功!")

    # 在这里执行数据查询...

    # 断开连接
    api.disconnect()
else:
    print("连接失败")</pre>

              <h4 style="margin-top: 20px;">🌐 可用服务器列表</h4>
              <el-table :data="standardServers" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="ip" label="IP地址" width="150" />
                <el-table-column prop="port" label="端口" width="80" />
                <el-table-column prop="location" label="位置" />
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="扩展行情 API">
            <div class="tab-content">
              <h4>🔌 TdxExHq_API - 扩展行情接口</h4>
              <p>提供更详细的行情数据,包括 Level-2、财务数据等:</p>

              <pre v-pre class="code-block">from pytdx.exhq import TdxExHq_API

# 创建扩展 API 对象
api = TdxExHq_API()

# 连接服务器 (扩展行情服务器)
if api.connect('106.14.95.149', 7727):
    print("连接成功!")

    # 执行扩展数据查询...

    api.disconnect()
else:
    print("连接失败")</pre>

              <h4 style="margin-top: 20px;">🌐 扩展服务器列表</h4>
              <el-table :data="extendedServers" stripe size="small" style="margin-top: 10px;">
                <el-table-column prop="ip" label="IP地址" width="150" />
                <el-table-column prop="port" label="端口" width="80" />
                <el-table-column prop="location" label="位置" />
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="自动服务器选择">
            <div class="tab-content">
              <h4>🔄 BestIP - 自动选择最佳服务器</h4>
              <p>pytdx 提供自动选择延迟最低的服务器功能:</p>

              <pre v-pre class="code-block">from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import select_best_ip

# 自动选择最佳服务器
best_ip = select_best_ip()
print(f"最佳服务器: {best_ip['ip']}:{best_ip['port']}")

# 连接到最佳服务器
api = TdxHq_API()
if api.connect(best_ip['ip'], best_ip['port']):
    print("连接成功!")
    api.disconnect()</pre>

              <el-alert type="info" :closable="false" style="margin-top: 15px;">
                <p><strong>💡 建议:</strong> 在生产环境中使用自动服务器选择功能,可以提高连接成功率和数据获取速度。</p>
              </el-alert>
            </div>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">🔐 with 语句管理连接</h3>
        <p>推荐使用 with 语句管理连接,自动处理连接和断开:</p>

        <pre v-pre class="code-block">from pytdx.hq import TdxHq_API

# 使用 with 语句
with TdxHq_API() as api:
    if api.connect('119.147.212.81', 7709):
        # 查询数据
        data = api.get_security_quotes([(0, '000001')])
        print(data)
    # 自动断开连接</pre>
      </div>
    </el-card>

    <!-- 3. API 使用示例 -->
</template>

<script setup lang="ts">
defineProps<{
  activeTab: string
  standardServers: Array<{ ip: string; port: string; location: string }>
  extendedServers: Array<{ ip: string; port: string; location: string }>
}>()
</script>
