<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>性能趋势</span>
        <el-radio-group v-model="timeRange" size="small" @change="fetchData">
          <el-radio-button label="1h">1小时</el-radio-button>
          <el-radio-button label="6h">6小时</el-radio-button>
          <el-radio-button label="24h">24小时</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <div ref="chartRef" style="width: 100%; height: 400px;"></div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const timeRange = ref('1h');
const chartRef = ref<HTMLElement>();
let chartInstance: echarts.ECharts | null = null;
let updateInterval: number;

const fetchData = async () => {
  try {
    const hours = parseInt(timeRange.value);
    const response = await axios.get(`/api/gpu/history/0?hours=${hours}`);
    const data = response.data.reverse();

    const timestamps = data.map((d: any) => new Date(d.timestamp).toLocaleTimeString());
    const gflops = data.map((d: any) => d.matrix_gflops);
    const speedup = data.map((d: any) => d.overall_speedup);
    const temperature = data.map((d: any) => d.temperature);
    const utilization = data.map((d: any) => d.gpu_utilization);

    const option = {
      title: {
        text: 'GPU性能趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['GFLOPS', '加速比', '温度', 'GPU利用率']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: timestamps
      },
      yAxis: [
        {
          type: 'value',
          name: 'GFLOPS / 加速比',
          position: 'left'
        },
        {
          type: 'value',
          name: '温度 / 利用率',
          position: 'right'
        }
      ],
      series: [
        {
          name: 'GFLOPS',
          type: 'line',
          smooth: true,
          data: gflops,
          yAxisIndex: 0,
          itemStyle: { color: '#5470C6' }
        },
        {
          name: '加速比',
          type: 'line',
          smooth: true,
          data: speedup,
          yAxisIndex: 0,
          itemStyle: { color: '#91CC75' }
        },
        {
          name: '温度',
          type: 'line',
          smooth: true,
          data: temperature,
          yAxisIndex: 1,
          itemStyle: { color: '#EE6666' }
        },
        {
          name: 'GPU利用率',
          type: 'line',
          smooth: true,
          data: utilization,
          yAxisIndex: 1,
          itemStyle: { color: '#FAC858' }
        }
      ]
    };

    if (chartInstance) {
      chartInstance.setOption(option);
    }
  } catch (error) {
    console.error('获取性能趋势数据失败:', error);
  }
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    fetchData();
    updateInterval = window.setInterval(fetchData, 30000);
  }
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
  }
  if (updateInterval) {
    clearInterval(updateInterval);
  }
});
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
