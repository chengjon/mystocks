<!-- PageTitleDemo.vue - 演示动态标题管理功能 -->
<template>
    <div class="page-title-demo">
        <div class="demo-header">
            <h1>页面标题管理演示</h1>
            <p>展示动态标题生成、Meta标签设置和模板功能</p>
        </div>

        <div class="demo-section">
            <h2>1. 基本标题设置</h2>
            <div class="demo-controls">
                <el-input v-model="basicTitle" placeholder="输入标题" style="width: 300px" />
                <el-button @click="setBasicTitle" type="primary">设置标题</el-button>
                <el-button @click="resetTitle" type="warning">重置标题</el-button>
            </div>
            <div class="demo-result">
                <strong>当前标题:</strong>
                {{ currentTitle }}
            </div>
        </div>

        <div class="demo-section">
            <h2>2. 动态标题生成</h2>
            <div class="demo-controls">
                <el-input
                    v-model="template"
                    placeholder="输入模板，如: {{user.username}}的{{data.type}}页面"
                    style="width: 400px"
                />
                <el-button @click="generateDynamicTitle" type="primary">生成标题</el-button>
            </div>
            <div class="demo-result">
                <strong>生成的标题:</strong>
                {{ generatedTitle }}
            </div>
        </div>

        <div class="demo-section">
            <h2>3. Meta标签设置</h2>
            <div class="demo-controls">
                <el-input
                    v-model="metaDescription"
                    placeholder="输入页面描述"
                    style="width: 400px; margin-bottom: 10px"
                />
                <br />
                <el-input
                    v-model="metaKeywords"
                    placeholder="输入关键词，用逗号分隔"
                    style="width: 400px; margin-bottom: 10px"
                />
                <br />
                <el-button @click="setMetaTags" type="primary">设置Meta标签</el-button>
            </div>
            <div class="demo-result">
                <strong>当前Meta:</strong>
                <div style="margin-top: 10px">
                    <div>
                        <strong>Description:</strong>
                        {{ currentMeta.description || '未设置' }}
                    </div>
                    <div>
                        <strong>Keywords:</strong>
                        {{ currentMeta.keywords?.join(', ') || '未设置' }}
                    </div>
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2>4. 数据驱动标题更新</h2>
            <div class="demo-controls">
                <el-input v-model="stockSymbol" placeholder="输入股票代码" style="width: 200px; margin-right: 10px" />
                <el-input v-model="stockName" placeholder="输入股票名称" style="width: 200px; margin-right: 10px" />
                <el-button @click="updateFromData" type="primary">基于数据更新标题</el-button>
            </div>
            <div class="demo-result">
                <strong>股票信息:</strong>
                {{ stockSymbol }} - {{ stockName }}
            </div>
        </div>

        <div class="demo-section">
            <h2>5. 预定义模板</h2>
            <div class="demo-controls">
                <el-select v-model="selectedTemplate" placeholder="选择预定义模板" style="width: 300px">
                    <el-option
                        v-for="template in templateOptions"
                        :key="template.value"
                        :label="template.label"
                        :value="template.value"
                    />
                </el-select>
                <el-button @click="usePredefinedTemplate" type="primary">使用模板</el-button>
            </div>
            <div class="demo-result">
                <strong>模板标题:</strong>
                {{ templateTitle }}
            </div>
        </div>

        <div class="demo-section">
            <h2>6. SEO优化设置</h2>
            <div class="demo-controls">
                <el-input v-model="seoTitle" placeholder="SEO标题" style="width: 300px; margin-bottom: 10px" />
                <br />
                <el-input v-model="seoDescription" placeholder="SEO描述" style="width: 300px; margin-bottom: 10px" />
                <br />
                <el-input v-model="seoImage" placeholder="图片URL (可选)" style="width: 300px; margin-bottom: 10px" />
                <br />
                <el-button @click="setSEOOptimized" type="primary">设置SEO优化</el-button>
            </div>
            <div class="demo-result">
                <strong>SEO设置:</strong>
                {{ seoTitle }} - {{ seoDescription }}
            </div>
        </div>

        <div class="demo-section">
            <h2>7. 标题历史记录</h2>
            <div class="demo-result">
                <div v-for="(record, index) in titleHistory.slice(-5)" :key="index" class="history-item">
                    <span class="timestamp">{{ formatTime(record.timestamp) }}</span>
                    <span class="title">{{ record.title }}</span>
                    <span class="type" :class="record.dynamic ? 'dynamic' : 'static'">
                        {{ record.dynamic ? '动态' : '静态' }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, reactive, onMounted } from 'vue'
    import { usePageTitle } from '@/composables/usePageTitle'

    // 使用标题管理Composable
    const {
        setTitle,
        setMeta,
        generateTitle,
        updateTitleFromData,
        useTemplate,
        setSEOOptimized,
        resetTitle,
        getTitleInfo
    } = usePageTitle()

    // 响应式数据
    const basicTitle = ref('')
    const template = ref('')
    const generatedTitle = ref('')
    const metaDescription = ref('')
    const metaKeywords = ref('')
    const stockSymbol = ref('')
    const stockName = ref('')
    const selectedTemplate = ref('')
    const seoTitle = ref('')
    const seoDescription = ref('')
    const seoImage = ref('')
    const templateTitle = ref('')
    const titleHistory = ref([])

    // 计算属性
    const currentTitle = ref('')
    const currentMeta = reactive({
        description: '',
        keywords: []
    })

    // 模板选项
    const templateOptions = [
        { label: '股票详情模板', value: 'STOCK_DETAIL' },
        { label: '用户仪表盘模板', value: 'USER_DASHBOARD' },
        { label: '策略详情模板', value: 'STRATEGY_DETAIL' }
    ]

    // 方法
    const setBasicTitle = () => {
        if (basicTitle.value) {
            setTitle(basicTitle.value)
            updateHistory(basicTitle.value, false)
            currentTitle.value = basicTitle.value
        }
    }

    const generateDynamicTitle = () => {
        if (template.value) {
            const result = generateTitle(template.value)
            generatedTitle.value = result
            setTitle(result)
            updateHistory(result, true)
            currentTitle.value = result
        }
    }

    const setMetaTags = () => {
        const keywords = metaKeywords.value ? metaKeywords.value.split(',').map(k => k.trim()) : []
        setMeta({
            description: metaDescription.value,
            keywords
        })
        currentMeta.description = metaDescription.value
        currentMeta.keywords = keywords
    }

    const updateFromData = () => {
        if (stockSymbol.value && stockName.value) {
            const data = {
                symbol: stockSymbol.value,
                name: stockName.value
            }
            updateTitleFromData(data, '{{name}} ({{symbol}}) - 股票信息')
            const newTitle = `${stockName.value} (${stockSymbol.value}) - 股票信息`
            updateHistory(newTitle, true)
            currentTitle.value = newTitle
        }
    }

    const usePredefinedTemplate = () => {
        if (selectedTemplate.value) {
            useTemplate(selectedTemplate.value)
            const titleInfo = getTitleInfo()
            templateTitle.value = titleInfo.title
            updateHistory(titleInfo.title, true)
            currentTitle.value = titleInfo.title
        }
    }

    const setSEOOptimizedTitle = () => {
        if (seoTitle.value && seoDescription.value) {
            setSEOOptimized({
                title: seoTitle.value,
                description: seoDescription.value,
                image: seoImage.value || undefined
            })
            const newTitle = seoTitle.value
            updateHistory(newTitle, true)
            currentTitle.value = newTitle
        }
    }

    const updateHistory = (title, isDynamic) => {
        titleHistory.value.push({
            title,
            dynamic: isDynamic,
            timestamp: Date.now()
        })
    }

    const formatTime = timestamp => {
        return new Date(timestamp).toLocaleTimeString()
    }

    // 初始化
    onMounted(() => {
        const titleInfo = getTitleInfo()
        currentTitle.value = titleInfo.title
        Object.assign(currentMeta, titleInfo.meta)
    })
</script>

<style scoped lang="scss">
    .page-title-demo {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .demo-header {
        text-align: center;
        margin-bottom: 40px;

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5rem;
        }

        p {
            color: #7f8c8d;
            font-size: 1.1rem;
        }
    }

    .demo-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;

        h2 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.4rem;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }

        .demo-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .demo-result {
            background: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            font-family: monospace;

            strong {
                color: #007bff;
            }
        }
    }

    .history-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
            border-bottom: none;
        }

        .timestamp {
            color: #6c757d;
            font-size: 0.9rem;
            min-width: 120px;
        }

        .title {
            flex: 1;
            color: #495057;
            font-weight: 500;
        }

        .type {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;

            &.dynamic {
                background: #d4edda;
                color: #155724;
            }

            &.static {
                background: #cce5ff;
                color: #004085;
            }
        }
    }

    @media (max-width: 768px) {
        .page-title-demo {
            padding: 10px;
        }

        .demo-section {
            padding: 15px;
        }

        .demo-controls {
            flex-direction: column;
            align-items: stretch;

            .el-input {
                width: 100% !important;
            }

            .el-button {
                width: 100%;
            }
        }

        .history-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;

            .timestamp {
                min-width: auto;
            }
        }
    }
</style>
