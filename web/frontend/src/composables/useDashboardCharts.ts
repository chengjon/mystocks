import { ref, Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { dashboardService } from '@/services/dashboardService'

interface ChartDataPoint {
  name: string
  value: number
}

interface ChartOptions {
  [key: string]: unknown
}

export function useDashboardCharts(industryStandard: Ref<string>) {
  // Chart data refs
  const priceDistributionData = ref<ChartDataPoint[]>([])
  const priceDistributionOptions = ref<ChartOptions>({})
  const marketHeatData = ref<ChartDataPoint[]>([])
  const marketHeatOptions = ref<ChartOptions>({})
  const leadingSectorData = ref<ChartDataPoint[]>([])
  const leadingSectorOptions = ref<ChartOptions>({})
  const capitalFlowData = ref<ChartDataPoint[]>([])
  const capitalFlowOptions = ref<ChartOptions>({})
  const capitalFlowData2 = ref<ChartDataPoint[]>([])
  const capitalFlowOptions2 = ref<ChartOptions>({})
  const industryData = ref<ChartDataPoint[]>([])
  const industryOptions = ref<ChartOptions>({})

  // Chart refs for DOM access
  const priceDistributionChartRef = ref()
  const marketHeatChartRef = ref()
  const leadingSectorChartRef = ref()
  const capitalFlowChartRef = ref()
  const capitalFlowChartRef2 = ref()
  const industryChartRef = ref()

  const updatePriceDistributionChart = (distributionData: Record<string, number>): void => {
    const data: ChartDataPoint[] = Object.entries(distributionData).map(([name, value]) => ({
      name,
      value: Number(value)
    }))
    priceDistributionData.value = data
    priceDistributionOptions.value = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}只 ({d}%)'
      },
      legend: {
        bottom: '5%',
        left: 'center'
      },
      series: [
        {
          name: '涨跌分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{c}只'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data: data
        }
      ]
    }
  }

  const initMarketHeatChart = async (): Promise<void> => {
    try {
      const response = await dashboardService.getMarketHeatChartData()
      if (response.success && response.data) {
        marketHeatData.value = response.data
        marketHeatOptions.value = {
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          xAxis: { type: 'value', name: '热度指数' },
          yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name) },
          series: [
            {
              name: '市场热度',
              type: 'bar',
              data: response.data.map((item: ChartDataPoint) => item.value)
            }
          ]
        }
      } else {
        ElMessage.error(response.message || '加载市场热度失败')
      }
    } catch (error) {
      console.error('加载市场热度失败:', error)
      ElMessage.error('加载市场热度失败')
    }
  }

  const initLeadingSectorChart = async (): Promise<void> => {
    try {
      const response = await dashboardService.getLeadingSectorChartData()
      if (response.success && response.data) {
        leadingSectorData.value = response.data
        leadingSectorOptions.value = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: '{b}: {c}%'
          },
          xAxis: {
            type: 'value',
            name: '涨幅(%)',
            axisLabel: { formatter: '{value}%' }
          },
          yAxis: {
            type: 'category',
            data: response.data.map((item: ChartDataPoint) => item.name)
          },
          series: [
            {
              name: '涨幅',
              type: 'bar',
              data: response.data.map((item: ChartDataPoint) => item.value)
            }
          ]
        }
      } else {
        ElMessage.error(response.message || '加载领涨板块失败')
      }
    } catch (error) {
      console.error('加载领涨板块失败:', error)
      ElMessage.error('加载领涨板块失败')
    }
  }

  const initCapitalFlowChart = async (): Promise<void> => {
    try {
      const response = await dashboardService.getCapitalFlowChartData()
      if (response.success && response.data) {
        capitalFlowData.value = response.data
        capitalFlowOptions.value = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: (params: unknown) => {
              const value = (params as Record<string, unknown>[])[0].value as number
              const _absValue = Math.abs(value)
              return `${(params as Record<string, unknown>[])[0].name as string}: ${value > 0 ? '+' : ''}${value}亿 (${
                value > 0 ? '流入' : '流出'
              })`
            }
          },
          xAxis: {
            type: 'value',
            name: '资金流向(亿元)',
            axisLabel: { formatter: (value: number) => (value > 0 ? `+${value}` : value) }
          },
          yAxis: {
            type: 'category',
            data: response.data.map((item: ChartDataPoint) => item.name)
          },
          series: [
            {
              name: '资金流向',
              type: 'bar',
              data: response.data.map((item: ChartDataPoint) => item.value)
            }
          ]
        }
      } else {
        ElMessage.error(response.message || '加载资金流向失败')
      }
    } catch (error) {
      console.error('加载资金流向失败:', error)
      ElMessage.error('加载资金流向失败')
    }
  }

  const initCapitalFlowChart2 = async (): Promise<void> => {
    try {
      const response = await dashboardService.getCapitalFlowChartData()
      if (response.success && response.data) {
        capitalFlowData2.value = response.data
        capitalFlowOptions2.value = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: (params: unknown) =>
              `${(params as Record<string, unknown>[])[0].name as string}: ${(params as Record<string, unknown>[])[0].value as number > 0 ? '+' : ''}${
                (params as Record<string, unknown>[])[0].value as number
              }亿`
          },
          xAxis: { type: 'value', name: '资金流向(亿元)' },
          yAxis: {
            type: 'category',
            data: response.data.map((item: ChartDataPoint) => item.name)
          },
          series: [
            {
              name: '资金流向',
              type: 'bar',
              data: response.data.map((item: ChartDataPoint) => item.value)
            }
          ]
        }
      } else {
        ElMessage.error(response.message || '加载资金流向失败')
      }
    } catch (error) {
      console.error('加载资金流向失败:', error)
      ElMessage.error('加载资金流向失败')
    }
  }

  const initIndustryChart = async (): Promise<void> => {
    try {
      const response = await dashboardService.getIndustryCapitalFlowChartData(industryStandard.value)
      if (response.success && response.data) {
        industryData.value = response.data
        industryOptions.value = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: (params: unknown) =>
              `${(params as Record<string, unknown>[])[0].name as string}: ${(params as Record<string, unknown>[])[0].value as number > 0 ? '+' : ''}${
                (params as Record<string, unknown>[])[0].value as number
              }亿`
          },
          xAxis: {
            type: 'value',
            name: '资金流向(亿元)',
            axisLabel: { formatter: (value: number) => (value > 0 ? `+${value}` : value) }
          },
          yAxis: {
            type: 'category',
            data: response.data.map((item: ChartDataPoint) => item.name),
            axisLabel: { interval: 0, fontSize: 11 }
          },
          series: [
            {
              name: '资金流向',
              type: 'bar',
              data: response.data.map((item: ChartDataPoint) => item.value),
              label: {
                show: true,
                position: 'right',
                formatter: (params: unknown) =>
                  `${(params as Record<string, unknown>).value as number > 0 ? '+' : ''}${(params as Record<string, unknown>).value as number}亿`,
                fontSize: 10
              }
            }
          ]
        }
      } else {
        ElMessage.error(response.message || '加载行业资金流向失败')
      }
    } catch (error) {
      console.error('加载行业资金流向失败:', error)
      ElMessage.error('加载行业资金流向失败')
    }
  }

  const initCharts = async () => {
    await Promise.all([
      initMarketHeatChart(),
      initLeadingSectorChart(),
      initCapitalFlowChart(),
      initCapitalFlowChart2(),
      initIndustryChart()
    ])
  }

  return {
    // Data refs
    priceDistributionData,
    priceDistributionOptions,
    marketHeatData,
    marketHeatOptions,
    leadingSectorData,
    leadingSectorOptions,
    capitalFlowData,
    capitalFlowOptions,
    capitalFlowData2,
    capitalFlowOptions2,
    industryData,
    industryOptions,
    // Chart refs
    priceDistributionChartRef,
    marketHeatChartRef,
    leadingSectorChartRef,
    capitalFlowChartRef,
    capitalFlowChartRef2,
    industryChartRef,
    // Functions
    updatePriceDistributionChart,
    initMarketHeatChart,
    initLeadingSectorChart,
    initCapitalFlowChart,
    initCapitalFlowChart2,
    initIndustryChart,
    initCharts
  }
}
