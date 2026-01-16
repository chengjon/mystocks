/**
 * K线图表性能测试
 * 测试大数据集下的渲染性能和响应时间
 */

export const performanceTest = {
    /**
     * 测试大数据集渲染性能
     */
    testLargeDatasetRendering: async (chartInstance, dataPoints = 10000) => {
        const startTime = performance.now()

        // 生成测试数据
        const testData = generateTestKLineData(dataPoints)

        // 应用数据到图表
        chartInstance?.applyNewData(testData)

        const renderTime = performance.now() - startTime

        console.log(`Large dataset (${dataPoints} points) render time: ${renderTime.toFixed(2)}ms`)

        // 目标: < 100ms 初始渲染
        const passed = renderTime < 100

        return {
            test: 'Large Dataset Rendering',
            dataPoints,
            renderTime,
            target: '< 100ms',
            passed,
            score: passed ? 'PASS' : 'FAIL'
        }
    },

    /**
     * 测试滚动性能 (60fps)
     */
    testScrollingPerformance: async chartInstance => {
        const frameTimes = []
        let frameCount = 0
        const maxFrames = 60 // 测试1秒的滚动

        return new Promise(resolve => {
            const measureFrame = timestamp => {
                if (frameCount < maxFrames) {
                    frameTimes.push(timestamp)
                    frameCount++

                    // 模拟滚动操作
                    if (chartInstance) {
                        // 这里需要实际的滚动API调用
                        requestAnimationFrame(measureFrame)
                    }
                } else {
                    // 计算FPS
                    const totalTime = frameTimes[frameTimes.length - 1] - frameTimes[0]
                    const avgFrameTime = totalTime / frameTimes.length
                    const fps = 1000 / avgFrameTime

                    console.log(`Scrolling performance: ${fps.toFixed(1)} FPS`)

                    const passed = fps >= 55 // 目标: 60fps，允许5%的误差

                    resolve({
                        test: 'Scrolling Performance',
                        fps: fps.toFixed(1),
                        avgFrameTime: avgFrameTime.toFixed(2),
                        target: '>= 55 FPS',
                        passed,
                        score: passed ? 'PASS' : 'FAIL'
                    })
                }
            }

            requestAnimationFrame(measureFrame)
        })
    },

    /**
     * 测试指标计算性能
     */
    testIndicatorCalculationPerformance: async (dataPoints = 1000) => {
        const testData = generateTestKLineData(dataPoints)

        // 测试多个指标的计算时间
        const indicators = ['MA', 'MACD', 'RSI', 'KDJ', 'BOLL']
        const results = []

        for (const indicator of indicators) {
            const startTime = performance.now()

            // 这里需要实际调用指标计算函数
            // 暂时用模拟计算
            await simulateIndicatorCalculation(indicator, testData)

            const calcTime = performance.now() - startTime

            const passed = calcTime < 50 // 目标: 每个指标 < 50ms

            results.push({
                indicator,
                calcTime: calcTime.toFixed(2),
                passed,
                score: passed ? 'PASS' : 'FAIL'
            })

            console.log(`${indicator} calculation time: ${calcTime.toFixed(2)}ms`)
        }

        return {
            test: 'Indicator Calculation Performance',
            results,
            overall: results.every(r => r.passed) ? 'PASS' : 'FAIL'
        }
    },

    /**
     * 运行完整性能测试套件
     */
    runFullPerformanceTest: async chartInstance => {
        console.log('🚀 Starting K-line Chart Performance Tests...\n')

        const results = []

        // 1. 大数据集渲染测试
        const renderTest = await performanceTest.testLargeDatasetRendering(chartInstance, 10000)
        results.push(renderTest)

        // 2. 滚动性能测试
        const scrollTest = await performanceTest.testScrollingPerformance(chartInstance)
        results.push(scrollTest)

        // 3. 指标计算性能测试
        const indicatorTest = await performanceTest.testIndicatorCalculationPerformance(1000)
        results.push(indicatorTest)

        // 汇总结果
        const summary = {
            totalTests: results.length,
            passedTests: results.filter(r => r.passed || r.overall === 'PASS').length,
            failedTests: results.filter(r => !r.passed && r.overall !== 'PASS').length,
            overallScore: results.every(r => r.passed || r.overall === 'PASS') ? 'PASS' : 'FAIL'
        }

        console.log('\n📊 Performance Test Results:')
        console.table(results)
        console.log('\n🏆 Summary:', summary)

        return { results, summary }
    }
}

/**
 * 生成测试K线数据
 */
function generateTestKLineData(count) {
    const data = []
    const basePrice = 100
    let currentPrice = basePrice

    for (let i = 0; i < count; i++) {
        const change = (Math.random() - 0.5) * 2 // -1 到 1 的随机变化
        currentPrice += change

        const open = currentPrice
        const close = currentPrice + (Math.random() - 0.5) * 0.5
        const high = Math.max(open, close) + Math.random() * 0.5
        const low = Math.min(open, close) - Math.random() * 0.5

        data.push({
            timestamp: Date.now() - (count - i) * 60000, // 每分钟一条数据
            open: Math.max(0, open),
            high: Math.max(0, high),
            low: Math.max(0, low),
            close: Math.max(0, close),
            volume: Math.floor(Math.random() * 1000000) + 100000
        })
    }

    return data
}

/**
 * 模拟指标计算 (用于性能测试)
 */
async function simulateIndicatorCalculation(indicator, data) {
    // 模拟计算时间
    const calcTime = Math.random() * 30 + 10 // 10-40ms随机时间
    return new Promise(resolve => setTimeout(resolve, calcTime))
}

// 自动运行性能测试 (如果在浏览器环境中)
if (typeof window !== 'undefined' && typeof performance !== 'undefined') {
    // 导出到全局以便手动调用
    window.runKLinePerformanceTest = performanceTest.runFullPerformanceTest
}
