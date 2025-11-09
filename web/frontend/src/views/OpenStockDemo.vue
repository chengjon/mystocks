<template>
  <div class="openstock-demo">
    <div class="demo-header">
      <h1>🎯 OpenStock 迁移功能演示</h1>
      <p class="subtitle">集中展示所有从 OpenStock 迁移的功能，测试完成后可分散集成到各个页面</p>

      <!-- 认证状态提示 -->
      <el-alert
        v-if="!isAuthenticated"
        type="warning"
        title="未登录"
        description="您还未登录，请先登录后再使用搜索功能"
        show-icon
        :closable="false"
        style="margin-top: 10px"
      >
        <template #default>
          <el-button type="primary" size="small" @click="goToLogin">
            前往登录
          </el-button>
        </template>
      </el-alert>
    </div>

    <!-- 功能导航 -->
    <div class="function-nav">
      <el-button
        v-for="tab in tabs"
        :key="tab.key"
        :type="activeTab === tab.key ? 'primary' : ''"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <!-- 1. 股票搜索功能 -->
    <el-card v-show="activeTab === 'search'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🔍 股票搜索（支持 A 股 + H 股）</span>
          <el-tag type="success">已迁移</el-tag>
        </div>
      </template>

      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-input
              v-model="searchQuery"
              placeholder="输入股票代码或名称（如：茅台、600000、00700）"
              @keyup.enter="handleSearch"
              clearable
            >
              <template #prepend>
                <el-select v-model="searchMarket" style="width: 100px">
                  <el-option label="自动" value="auto" />
                  <el-option label="A股" value="cn" />
                  <el-option label="H股" value="hk" />
                </el-select>
              </template>
            </el-input>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="handleSearch" :loading="searchLoading">
              搜索
            </el-button>
            <el-button @click="clearSearch">清空</el-button>
          </el-col>
        </el-row>

        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <h3>搜索结果 ({{ searchResults.length }})</h3>
          <el-table :data="searchResults" stripe>
            <el-table-column prop="symbol" label="代码" width="120" />
            <el-table-column prop="description" label="名称" width="150" />
            <el-table-column prop="exchange" label="交易所" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column label="操作" width="400">
              <template #default="scope">
                <el-button size="small" @click="getQuote(scope.row)">
                  获取行情
                </el-button>
                <el-button size="small" @click="getNews(scope.row)">
                  获取新闻
                </el-button>
                <el-popover placement="top" :width="280" trigger="click">
                  <template #reference>
                    <el-button size="small" type="success">
                      加入自选
                    </el-button>
                  </template>
                  <div>
                    <p style="margin-bottom: 10px;">输入或选择分组:</p>
                    <el-autocomplete
                      v-model="selectedGroupName"
                      :fetch-suggestions="queryGroupSuggestions"
                      placeholder="输入分组名称（不存在则自动创建）"
                      style="width: 100%; margin-bottom: 10px;"
                      clearable
                    >
                      <template #default="{ item }">
                        <div>{{ item.value }} ({{ item.count }}只)</div>
                      </template>
                    </el-autocomplete>
                    <el-button size="small" type="primary" style="width: 100%;" @click="addToWatchlist(scope.row)">
                      确认添加
                    </el-button>
                  </div>
                </el-popover>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <!-- 2. 实时行情 -->
    <el-card v-show="activeTab === 'quote'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📈 实时行情查询</span>
          <el-tag type="success">已迁移</el-tag>
        </div>
      </template>

      <div class="quote-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input v-model="quoteSymbol" placeholder="输入股票代码">
              <template #prepend>代码</template>
            </el-input>
          </el-col>
          <el-col :span="8">
            <el-select v-model="quoteMarket">
              <el-option label="A股" value="cn" />
              <el-option label="H股" value="hk" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="fetchQuote" :loading="quoteLoading">
              查询行情
            </el-button>
          </el-col>
        </el-row>

        <!-- 行情展示 -->
        <div v-if="currentQuote" class="quote-display">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="股票名称">
              {{ currentQuote.name || currentQuote.symbol }}
            </el-descriptions-item>
            <el-descriptions-item label="股票代码">
              {{ currentQuote.symbol }}
            </el-descriptions-item>
            <el-descriptions-item label="当前价">
              <span :class="currentQuote.change >= 0 ? 'price-up' : 'price-down'">
                {{ currentQuote.current.toFixed(2) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="涨跌幅">
              <span :class="currentQuote.percent_change >= 0 ? 'price-up' : 'price-down'">
                {{ currentQuote.percent_change.toFixed(2) }}%
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="涨跌额">
              <span :class="currentQuote.change >= 0 ? 'price-up' : 'price-down'">
                {{ currentQuote.change.toFixed(2) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="开盘价">
              {{ currentQuote.open.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="最高价">
              {{ currentQuote.high.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="最低价">
              {{ currentQuote.low.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="昨收价">
              {{ currentQuote.previous_close.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="成交量" v-if="currentQuote.volume">
              {{ formatVolume(currentQuote.volume) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

    <!-- 3. 股票新闻 -->
    <el-card v-show="activeTab === 'news'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📰 股票新闻</span>
          <el-tag type="success">已迁移</el-tag>
        </div>
      </template>

      <div class="news-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input v-model="newsSymbol" placeholder="输入股票代码">
              <template #prepend>代码</template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-select v-model="newsMarket">
              <el-option label="A股" value="cn" />
              <el-option label="H股" value="hk" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="newsDays">
              <el-option label="最近3天" :value="3" />
              <el-option label="最近7天" :value="7" />
              <el-option label="最近15天" :value="15" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="fetchNews" :loading="newsLoading">
              查询新闻
            </el-button>
          </el-col>
        </el-row>

        <!-- 新闻列表 -->
        <div v-if="newsList.length > 0" class="news-list">
          <el-timeline>
            <el-timeline-item
              v-for="(news, index) in newsList"
              :key="index"
              :timestamp="formatTime(news.datetime)"
            >
              <el-card>
                <h4>{{ news.headline }}</h4>
                <p>{{ news.summary }}</p>
                <div class="news-footer">
                  <el-tag size="small">{{ news.source }}</el-tag>
                  <el-link v-if="news.url" :href="news.url" target="_blank" type="primary">
                    阅读原文
                  </el-link>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>

    <!-- 4. 自选股管理（分组） -->
    <el-card v-show="activeTab === 'watchlist'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⭐ 自选股管理（分组）</span>
          <el-tag type="success">已迁移</el-tag>
        </div>
      </template>

      <div class="watchlist-section">
        <el-row :gutter="20">
          <!-- 左侧：分组列表（使用组件） -->
          <el-col :span="6">
            <WatchlistGroupManager
              ref="groupManagerRef"
              v-model="currentGroupId"
              @group-selected="handleGroupSelected"
              @group-created="handleGroupCreated"
              @group-updated="handleGroupUpdated"
              @group-deleted="handleGroupDeleted"
            />
          </el-col>

          <!-- 右侧：当前分组的股票列表 -->
          <el-col :span="18">
            <div class="group-stocks">
              <div class="group-stocks-header">
                <h4>{{ currentGroupName }} ({{ currentGroupStocks.length }} 只)</h4>
                <div>
                  <el-button type="primary" @click="fetchGroupStocks">
                    刷新
                  </el-button>
                  <el-button type="danger" @click="clearCurrentGroup">
                    清空当前分组
                  </el-button>
                </div>
              </div>

              <!-- 股票列表表格 -->
              <el-table :data="currentGroupStocks" stripe v-loading="watchlistLoading">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="display_name" label="名称" width="120" />
                <el-table-column prop="market" label="市场" width="80">
                  <template #default="scope">
                    <el-tag size="small" :type="scope.row.market === 'CN' ? 'success' : 'warning'">
                      {{ scope.row.market === 'CN' ? 'A股' : 'H股' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="exchange" label="交易所" />
                <el-table-column prop="notes" label="备注">
                  <template #default="scope">
                    <el-input
                      v-model="scope.row.notes"
                      placeholder="添加备注"
                      size="small"
                      @blur="updateNotes(scope.row)"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="300">
                  <template #default="scope">
                    <el-button size="small" @click="getQuoteFromWatchlist(scope.row)">
                      查看行情
                    </el-button>
                    <el-popover placement="top" :width="200" trigger="click">
                      <template #reference>
                        <el-button size="small" type="primary">
                          移动
                        </el-button>
                      </template>
                      <div>
                        <p style="margin-bottom: 10px;">移动到:</p>
                        <el-select
                          v-model="moveToGroupId"
                          placeholder="选择目标分组"
                          style="width: 100%; margin-bottom: 10px;"
                        >
                          <el-option
                            v-for="group in groups.filter(g => g.id !== currentGroupId)"
                            :key="group.id"
                            :label="group.group_name"
                            :value="group.id"
                          />
                        </el-select>
                        <el-button
                          size="small"
                          type="primary"
                          style="width: 100%;"
                          @click="moveStock(scope.row)"
                        >
                          确认移动
                        </el-button>
                      </div>
                    </el-popover>
                    <el-button size="small" type="danger" @click="removeFromWatchlist(scope.row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 5. klinecharts K线图表 -->
    <el-card v-show="activeTab === 'klinechart'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📊 K线图表（klinecharts）</span>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>

      <div class="klinechart-section">
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="8">
            <el-input v-model="chartSymbol" placeholder="输入股票代码">
              <template #prepend>代码</template>
            </el-input>
          </el-col>
          <el-col :span="8">
            <el-select v-model="chartMarket">
              <el-option label="A股" value="CN" />
              <el-option label="H股" value="HK" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="loadKlineChart" :loading="chartLoading">
              加载图表
            </el-button>
          </el-col>
        </el-row>

        <!-- klinecharts 图表容器 -->
        <div id="kline-chart" class="klinechart-container"></div>

        <el-alert
          title="K线图表说明"
          type="info"
          :closable="false"
          style="margin-top: 20px"
        >
          <p>使用 klinecharts 实现的专业K线图表，支持多种技术指标和图表类型。</p>
          <p style="margin-top: 8px; font-size: 12px; color: #909399;">
            💡 图表支持鼠标缩放、拖动等交互操作。如需更多技术指标，可通过图表工具栏添加。
          </p>
        </el-alert>
      </div>
    </el-card>

    <!-- 6. ECharts 股票热力图 -->
    <el-card v-show="activeTab === 'heatmap'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🔥 股票热力图（ECharts）</span>
          <el-tag type="success">已集成</el-tag>
        </div>
      </template>

      <div class="heatmap-section">
        <!-- 市场选择和刷新按钮 -->
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="16">
            <el-radio-group v-model="heatmapMarket" @change="loadHeatmapData">
              <el-radio-button label="cn">中国A股</el-radio-button>
              <el-radio-button label="hk">港股</el-radio-button>
            </el-radio-group>
          </el-col>
          <el-col :span="8" style="text-align: right">
            <el-button type="primary" @click="loadHeatmapData" :loading="heatmapLoading">
              刷新数据
            </el-button>
          </el-col>
        </el-row>

        <!-- ECharts 热力图容器 -->
        <div
          ref="heatmapContainerRef"
          class="echarts-heatmap-container"
          v-loading="heatmapLoading"
          element-loading-text="加载热力图中..."
        ></div>

        <el-alert
          title="股票热力图说明"
          type="info"
          :closable="false"
          style="margin-top: 20px"
        >
          <p>使用 ECharts 实现的股票市场热力图，实时展示各板块和个股的涨跌情况。</p>
          <ul style="margin-top: 10px; font-size: 12px; color: #909399; padding-left: 20px;">
            <li>方块大小代表市值或成交额，颜色深浅代表涨跌幅度</li>
            <li>红色表示上涨，绿色表示下跌（符合中国股市习惯）</li>
            <li>支持中国A股和港股市场切换</li>
            <li>鼠标悬停可查看详细信息</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 7. 功能测试状态 -->
    <el-card v-show="activeTab === 'status'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>✅ 功能测试状态</span>
        </div>
      </template>

      <div class="status-section">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="股票搜索 API">
            <el-tag :type="apiStatus.search ? 'success' : 'info'">
              {{ apiStatus.search ? '✅ 已测试' : '⏳ 待测试' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实时行情 API">
            <el-tag :type="apiStatus.quote ? 'success' : 'info'">
              {{ apiStatus.quote ? '✅ 已测试' : '⏳ 待测试' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="股票新闻 API">
            <el-tag :type="apiStatus.news ? 'success' : 'info'">
              {{ apiStatus.news ? '✅ 已测试' : '⏳ 待测试' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自选股管理 API">
            <el-tag :type="apiStatus.watchlist ? 'success' : 'info'">
              {{ apiStatus.watchlist ? '✅ 已测试' : '⏳ 待测试' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="K线图表 API">
            <el-tag :type="apiStatus.klinechart ? 'success' : 'info'">
              {{ apiStatus.klinechart ? '✅ 已测试' : '⏳ 待测试' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="股票热力图">
            <el-tag :type="apiStatus.heatmap ? 'success' : 'info'">
              {{ apiStatus.heatmap ? '✅ 已集成' : '⏳ 待集成' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px">
          <h3>📝 集成建议</h3>
          <el-alert type="warning" :closable="false">
            <template #title>
              <div>测试完成后，可以将这些功能集成到以下页面：</div>
            </template>
            <ul>
              <li><strong>股票搜索</strong>: 可集成到首页、市场页面的全局搜索</li>
              <li><strong>实时行情</strong>: 可集成到股票详情页、自选股页面</li>
              <li><strong>股票新闻</strong>: 可集成到股票详情页、资讯页面</li>
              <li><strong>自选股管理</strong>: 可作为独立页面，支持分组管理和批量操作</li>
              <li><strong>K线图表</strong>: 可集成到股票详情页、技术分析页，支持多种技术指标</li>
              <li><strong>股票热力图</strong>: 可集成到市场概览页、首页，实时展示市场整体涨跌情况</li>
            </ul>
          </el-alert>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import WatchlistGroupManager from '@/components/watchlist/WatchlistGroupManager.vue'
import * as echarts from 'echarts'
import { init as klinechartsInit, dispose as klinechartsDispose } from 'klinecharts'

const router = useRouter()

// API 基础地址 - 使用相对路径让Vite代理处理
const API_BASE = '/api'

// 获取 token
const getToken = () => {
  return localStorage.getItem('token') || ''
}

// 认证状态检查
const isAuthenticated = computed(() => {
  const token = getToken()
  return token && token.length > 0
})

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// Tab 切换
const activeTab = ref('search')
const tabs = [
  { key: 'search', label: '股票搜索', icon: '🔍' },
  { key: 'quote', label: '实时行情', icon: '📈' },
  { key: 'news', label: '股票新闻', icon: '📰' },
  { key: 'watchlist', label: '自选股管理', icon: '⭐' },
  { key: 'klinechart', label: 'K线图表', icon: '📊' },
  { key: 'heatmap', label: '股票热力图', icon: '🔥' },
  { key: 'status', label: '测试状态', icon: '✅' }
]

// API 测试状态
const apiStatus = ref({
  search: false,
  quote: false,
  news: false,
  watchlist: false,
  klinechart: false,
  heatmap: false
})

// ========== 股票搜索 ==========
const searchQuery = ref('')
const searchMarket = ref('auto')
const searchResults = ref([])
const searchLoading = ref(false)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  // 检查是否已登录
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录后再使用搜索功能')
    return
  }

  searchLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/stock-search/search`, {
      params: {
        q: searchQuery.value,
        market: searchMarket.value
      },
      headers: {
        Authorization: `Bearer ${getToken()}`
      }
    })
    searchResults.value = response.data
    apiStatus.value.search = true
    ElMessage.success(`找到 ${response.data.length} 条结果`)
  } catch (error) {
    ElMessage.error('搜索失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    searchLoading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
}

// ========== 实时行情 ==========
const quoteSymbol = ref('')
const quoteMarket = ref('cn')
const currentQuote = ref(null)
const quoteLoading = ref(false)

const getQuote = (stock) => {
  quoteSymbol.value = stock.symbol
  quoteMarket.value = stock.market === 'CN' ? 'cn' : 'hk'
  activeTab.value = 'quote'
  fetchQuote()
}

const fetchQuote = async () => {
  if (!quoteSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  quoteLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE}/stock-search/quote/${quoteSymbol.value}`,
      {
        params: { market: quoteMarket.value },
        headers: { Authorization: `Bearer ${getToken()}` }
      }
    )
    currentQuote.value = response.data
    apiStatus.value.quote = true
    ElMessage.success('行情获取成功')
  } catch (error) {
    ElMessage.error('获取行情失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    quoteLoading.value = false
  }
}

const formatVolume = (volume) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

// ========== 股票新闻 ==========
const newsSymbol = ref('')
const newsMarket = ref('cn')
const newsDays = ref(7)
const newsList = ref([])
const newsLoading = ref(false)

const getNews = (stock) => {
  newsSymbol.value = stock.symbol
  newsMarket.value = stock.market === 'CN' ? 'cn' : 'hk'
  activeTab.value = 'news'
  fetchNews()
}

const fetchNews = async () => {
  if (!newsSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  newsLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE}/stock-search/news/${newsSymbol.value}`,
      {
        params: {
          market: newsMarket.value,
          days: newsDays.value
        },
        headers: { Authorization: `Bearer ${getToken()}` }
      }
    )
    newsList.value = response.data
    apiStatus.value.news = true
    ElMessage.success(`获取到 ${response.data.length} 条新闻`)
  } catch (error) {
    ElMessage.error('获取新闻失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    newsLoading.value = false
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// ========== 自选股分组管理 ==========
const groupManagerRef = ref(null) // 分组管理组件引用
const currentGroupId = ref(null)
const currentGroupName = ref('')
const currentGroupStocks = ref([])
const watchlistLoading = ref(false)
const selectedGroupName = ref('') // 用于自动完成输入框（搜索结果添加到自选时使用）
const moveToGroupId = ref(null)
const groups = ref([]) // 保留用于自动完成建议

// 获取分组列表（用于自动完成建议）
const fetchGroups = async () => {
  try {
    const response = await axios.get(`${API_BASE}/watchlist/groups`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    groups.value = response.data
  } catch (error) {
    console.error('获取分组失败:', error)
  }
}

// 自动完成建议函数（用于搜索结果添加到自选时的分组名称输入）
const queryGroupSuggestions = (queryString, callback) => {
  const suggestions = groups.value.map(group => ({
    value: group.group_name,
    count: group.stock_count,
    id: group.id
  }))

  // 如果有输入，进行过滤
  const results = queryString
    ? suggestions.filter(item => item.value.toLowerCase().includes(queryString.toLowerCase()))
    : suggestions

  callback(results)
}

// 处理分组选中事件（来自组件）
const handleGroupSelected = (group) => {
  currentGroupId.value = group.id
  currentGroupName.value = group.group_name
  fetchGroupStocks()
}

// 处理分组创建事件（来自组件）
const handleGroupCreated = (group) => {
  fetchGroups() // 刷新分组列表用于自动完成
}

// 处理分组更新事件（来自组件）
const handleGroupUpdated = (group) => {
  if (currentGroupId.value === group.id) {
    currentGroupName.value = group.group_name
  }
  fetchGroups()
}

// 处理分组删除事件（来自组件）
const handleGroupDeleted = (group) => {
  fetchGroups()
}

// 获取指定分组的股票
const fetchGroupStocks = async () => {
  if (!currentGroupId.value) return

  watchlistLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/watchlist/group/${currentGroupId.value}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    currentGroupStocks.value = response.data
    apiStatus.value.watchlist = true
  } catch (error) {
    ElMessage.error('获取分组股票失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    watchlistLoading.value = false
  }
}

// 添加到自选股（支持输入分组名称自动创建）
const addToWatchlist = async (stock) => {
  try {
    // 获取分组名称（优先使用输入的名称）
    const groupName = selectedGroupName.value?.trim() || '默认分组'

    if (!groupName) {
      ElMessage.warning('请输入分组名称')
      return
    }

    const response = await axios.post(
      `${API_BASE}/watchlist/add`,
      {
        symbol: stock.symbol,
        display_name: stock.description,
        exchange: stock.exchange,
        market: stock.market,
        group_name: groupName  // 使用分组名称，后端会自动创建
      },
      {
        headers: { Authorization: `Bearer ${getToken()}` }
      }
    )

    ElMessage.success(`已添加到分组 "${response.data.group_name}"`)

    // 清空输入框
    selectedGroupName.value = ''

    // 刷新分组列表
    await fetchGroups()

    // 如果添加到当前分组，刷新股票列表
    fetchGroupStocks()
  } catch (error) {
    ElMessage.error('添加失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 移动股票到其他分组
const moveStock = async (stock) => {
  if (!moveToGroupId.value) {
    ElMessage.warning('请选择目标分组')
    return
  }

  try {
    await axios.put(
      `${API_BASE}/watchlist/move`,
      {
        symbol: stock.symbol,
        from_group_id: currentGroupId.value,
        to_group_id: moveToGroupId.value
      },
      {
        headers: { Authorization: `Bearer ${getToken()}` }
      }
    )
    ElMessage.success('股票已移动')
    fetchGroups()
    fetchGroupStocks()
    moveToGroupId.value = null
  } catch (error) {
    ElMessage.error('移动失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 清空当前分组
const clearCurrentGroup = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清空分组 "${currentGroupName.value}" 中的所有股票吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 逐个删除当前分组的股票
    for (const stock of currentGroupStocks.value) {
      await axios.delete(`${API_BASE}/watchlist/remove/${stock.symbol}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
    }

    ElMessage.success('分组已清空')
    fetchGroups()
    fetchGroupStocks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const removeFromWatchlist = async (stock) => {
  try {
    await ElMessageBox.confirm('确定要从自选股中删除吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`${API_BASE}/watchlist/remove/${stock.symbol}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    ElMessage.success('已从自选股删除')
    fetchGroups()
    fetchGroupStocks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const updateNotes = async (stock) => {
  try {
    await axios.put(
      `${API_BASE}/watchlist/notes/${stock.symbol}`,
      { notes: stock.notes },
      {
        headers: { Authorization: `Bearer ${getToken()}` }
      }
    )
    ElMessage.success('备注已更新')
  } catch (error) {
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  }
}

const getQuoteFromWatchlist = (stock) => {
  quoteSymbol.value = stock.symbol
  quoteMarket.value = stock.market === 'CN' ? 'cn' : 'hk'
  activeTab.value = 'quote'
  fetchQuote()
}

// ========== klinecharts K线图表 ==========
const chartSymbol = ref('600000')
const chartMarket = ref('CN')
const chartLoading = ref(false)
let chart = null

const loadKlineChart = async () => {
  if (!chartSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  chartLoading.value = true

  try {
    // 清除旧图表
    if (chart) {
      try {
        // 尝试销毁图表（如果 klinecharts 提供 dispose 方法）
        const container = document.getElementById('kline-chart')
        if (container) {
          container.innerHTML = ''
        }
        chart = null
      } catch (e) {
        console.warn('清除旧图表时出错:', e)
      }
    }

    // 从后端获取K线数据
    const response = await axios.get(`${API_BASE}/market/kline`, {
      params: {
        symbol: chartSymbol.value,
        market: chartMarket.value
      },
      headers: { Authorization: `Bearer ${getToken()}` }
    })

    // 初始化图表
    const container = document.getElementById('kline-chart')
    if (!container) {
      ElMessage.error('图表容器未找到')
      return
    }

    // 创建图表实例（使用本地安装的 klinecharts）
    chart = klinechartsInit('kline-chart')

    // 设置股票代码
    chart.setSymbol({ ticker: chartSymbol.value })

    // 设置时间周期
    chart.setPeriod({ span: 1, type: 'day' })

    // 加载数据
    if (response.data && response.data.length > 0) {
      chart.applyNewData(response.data)
      apiStatus.value.klinechart = true
      ElMessage.success(`成功加载 ${response.data.length} 条K线数据`)
    } else {
      ElMessage.warning('没有获取到K线数据')
    }
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('K线数据接口未实现，请先实现后端接口: GET /api/market/kline')
    } else {
      ElMessage.error('加载图表失败: ' + (error.response?.data?.detail || error.message))
    }
    console.error('klinecharts Error:', error)
  } finally {
    chartLoading.value = false
  }
}

// ========== ECharts 股票热力图 ==========
const heatmapMarket = ref('cn') // 市场选择：cn-中国A股，hk-港股
const heatmapLoading = ref(false)
const heatmapContainerRef = ref(null)
let heatmapChart = null

// 初始化ECharts热力图
const initHeatmapChart = () => {
  if (!heatmapContainerRef.value) return

  // 如果图表已存在，先销毁
  if (heatmapChart) {
    heatmapChart.dispose()
  }

  // 创建新图表
  heatmapChart = echarts.init(heatmapContainerRef.value)

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (heatmapChart) {
      heatmapChart.resize()
    }
  })
}

// 加载热力图数据
const loadHeatmapData = async () => {
  heatmapLoading.value = true

  try {
    // 从后端API获取市场热力图数据
    const response = await axios.get(`${API_BASE}/market/heatmap`, {
      params: {
        market: heatmapMarket.value
      },
      headers: { Authorization: `Bearer ${getToken()}` }
    })

    if (!response.data || response.data.length === 0) {
      ElMessage.warning('暂无热力图数据')
      return
    }

    // 渲染热力图
    renderHeatmap(response.data)
    apiStatus.value.heatmap = true
    ElMessage.success('热力图加载成功')
  } catch (error) {
    console.error('加载热力图失败:', error)

    // 如果后端API未实现，使用模拟数据
    if (error.response?.status === 404) {
      ElMessage.warning('热力图API未实现，使用模拟数据展示')
      renderHeatmap(generateMockHeatmapData())
    } else {
      ElMessage.error('加载热力图失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    heatmapLoading.value = false
  }
}

// 渲染热力图
const renderHeatmap = (data) => {
  if (!heatmapChart || !data || data.length === 0) return

  // 将数据转换为树形结构
  const treeData = {
    name: heatmapMarket.value === 'cn' ? 'A股市场' : '港股市场',
    children: data.map(item => ({
      name: item.name,
      value: item.change_pct,
      symbol: item.symbol,
      price: item.price,
      change: item.change,
      volume: item.volume,
      market_cap: item.market_cap
    }))
  }

  const option = {
    title: {
      text: heatmapMarket.value === 'cn' ? '中国A股市场热力图' : '港股市场热力图',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 18
      }
    },
    tooltip: {
      formatter: (info) => {
        const data = info.data
        if (!data) return ''

        return [
          `<div style="font-weight: bold; margin-bottom: 5px;">${data.name} (${data.symbol || '-'})</div>`,
          `涨跌幅: <span style="color: ${data.value >= 0 ? '#ef5350' : '#26a69a'};">${data.value >= 0 ? '+' : ''}${data.value?.toFixed(2) || 0}%</span>`,
          `当前价: ${data.price?.toFixed(2) || '-'}`,
          `涨跌额: ${data.change >= 0 ? '+' : ''}${data.change?.toFixed(2) || '-'}`,
          data.market_cap ? `市值: ${(data.market_cap / 100000000).toFixed(2)}亿` : ''
        ].filter(Boolean).join('<br/>')
      }
    },
    series: [{
      type: 'treemap',
      data: treeData.children,
      width: '100%',
      height: '100%',
      label: {
        show: true,
        formatter: '{b}\n{c}%',
        fontSize: 12
      },
      upperLabel: {
        show: true,
        height: 30,
        color: '#fff'
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2,
        gapWidth: 2
      },
      // 颜色映射：中国习惯红涨绿跌
      visualDimension: 'value',
      visualMin: -10,
      visualMax: 10,
      colorMappingBy: 'value',
      colorAlpha: [0.8, 1],
      colorSaturation: [0.3, 0.7],
      // 红色表示上涨，绿色表示下跌
      color: (params) => {
        const value = params.value
        if (value > 5) return '#d32f2f'    // 深红（大涨）
        if (value > 2) return '#ef5350'    // 红色（涨）
        if (value > 0) return '#ffcdd2'    // 浅红（微涨）
        if (value === 0) return '#e0e0e0'  // 灰色（平盘）
        if (value > -2) return '#a5d6a7'   // 浅绿（微跌）
        if (value > -5) return '#66bb6a'   // 绿色（跌）
        return '#2e7d32'                    // 深绿（大跌）
      }
    }]
  }

  heatmapChart.setOption(option)
}

// 生成模拟热力图数据（用于测试）
const generateMockHeatmapData = () => {
  const sectors = ['金融', '科技', '医药', '消费', '能源', '制造', '房地产', '通信']
  const data = []

  for (let i = 0; i < 30; i++) {
    const sector = sectors[Math.floor(Math.random() * sectors.length)]
    const changePct = (Math.random() - 0.5) * 20 // -10% 到 +10%

    data.push({
      name: `${sector}${i + 1}`,
      symbol: `${(600000 + i).toString().padStart(6, '0')}`,
      price: 10 + Math.random() * 90,
      change: changePct * 0.1,
      change_pct: changePct,
      volume: Math.floor(Math.random() * 1000000),
      market_cap: Math.floor(Math.random() * 10000000000)
    })
  }

  return data
}

// 页面加载时获取分组和自选股
onMounted(() => {
  fetchGroups()

  // 初始化热力图（延迟以确保DOM已渲染）
  nextTick(() => {
    setTimeout(() => {
      initHeatmapChart()
      loadHeatmapData()
    }, 500)
  })
})
</script>

<style scoped>
.openstock-demo {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-header {
  text-align: center;
  margin-bottom: 30px;
}

.demo-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
  color: #409eff;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.function-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.demo-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.search-section,
.quote-section,
.news-section,
.watchlist-section,
.tradingview-section,
.status-section {
  padding: 10px 0;
}

.search-results {
  margin-top: 20px;
}

.quote-display {
  margin-top: 20px;
}

.price-up {
  color: #f56c6c;
  font-weight: bold;
}

.price-down {
  color: #67c23a;
  font-weight: bold;
}

.news-list {
  margin-top: 20px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.watchlist-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.klinechart-container {
  width: 100%;
  height: 600px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 20px;
}

/* ECharts热力图样式 */
.heatmap-section {
  padding: 10px 0;
}

.echarts-heatmap-container {
  width: 100%;
  height: 600px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.status-section ul {
  margin-top: 10px;
  line-height: 1.8;
}

/* 分组管理样式 */
.group-sidebar {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  min-height: 500px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.group-header h4 {
  margin: 0;
  font-size: 16px;
}

.group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.group-actions {
  display: flex;
  gap: 5px;
}

.group-stocks {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  min-height: 500px;
}

.group-stocks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.group-stocks-header h4 {
  margin: 0;
  font-size: 18px;
  color: #409eff;
}

.el-menu-item {
  margin-bottom: 5px;
}
</style>
