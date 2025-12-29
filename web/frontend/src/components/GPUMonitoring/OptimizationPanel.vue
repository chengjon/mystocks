<template>
  <el-card>
    <template #header>
      <span>智能优化建议</span>
      <el-button size="small" @click="fetchRecommendations">刷新</el-button>
    </template>

    <el-alert
      v-for="rec in recommendations"
      :key="rec.title"
      :title="rec.title"
      :type="getSeverityType(rec.severity)"
      :closable="false"
      class="recommendation-alert"
    >
      <template #default>
        <p><strong>问题描述:</strong> {{ rec.description }}</p>
        <p><strong>预期改善:</strong> {{ rec.expected_improvement }}</p>
        <div class="action-steps">
          <strong>建议操作:</strong>
          <ol>
            <li v-for="step in rec.action_steps" :key="step">{{ step }}</li>
          </ol>
        </div>
      </template>
    </el-alert>

    <el-empty v-if="recommendations.length === 0" description="暂无优化建议,系统运行良好" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface Recommendation {
  title: string;
  category: string;
  severity: string;
  description: string;
  expected_improvement: string;
  action_steps: string[];
}

const recommendations = ref<Recommendation[]>([]);

const fetchRecommendations = async () => {
  try {
    const response = await axios.get('/api/gpu/recommendations?device_id=0');
    recommendations.value = response.data;
  } catch (error) {
    console.error('获取优化建议失败:', error);
  }
};

const getSeverityType = (severity: string) => {
  const map: Record<string, any> = {
    'info': 'info',
    'warning': 'warning',
    'critical': 'error'
  };
  return map[severity] || 'info';
};

onMounted(fetchRecommendations);
</script>

<style scoped>
.recommendation-alert {
  margin-bottom: 12px;
}

.recommendation-alert p {
  margin: 8px 0;
}

.action-steps {
  margin-top: 8px;
}

.action-steps ol {
  margin: 4px 0;
  padding-left: 20px;
}

.action-steps li {
  margin: 4px 0;
}
</style>
