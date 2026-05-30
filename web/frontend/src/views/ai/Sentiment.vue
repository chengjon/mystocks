<script setup lang="ts">
import { onMounted } from 'vue'

import { ArtDecoButton, ArtDecoIcon } from '@/components/artdeco'
import { useAiSentimentWorkbench } from './composables/useAiSentimentWorkbench'
import AiSentimentHero from './components/AiSentimentHero.vue'
import AiSentimentSummaryCards from './components/AiSentimentSummaryCards.vue'
import AiSentimentWorkbenchPanels from './components/AiSentimentWorkbenchPanels.vue'

const {
  analysisSource,
  analysisText,
  announcements,
  contentShellDescription,
  displayRequestId,
  formatPublishDate,
  lastAnalysis,
  loading,
  marketAverageScore,
  marketOverview,
  marketSentimentLabel,
  openAnnouncement,
  pageStatusText,
  pageStatusType,
  refreshWorkbench,
  runTextAnalysis,
  runtimeMessage,
  selectedSymbol,
  stockAverageScore,
  stockTrend,
  stockTrendLabel,
  summaryCards,
} = useAiSentimentWorkbench('ai')

const onSelectSymbol = (value: string) => {
  selectedSymbol.value = value
}

const onAnalysisTextChange = (value: string) => {
  analysisText.value = value
}

const onAnalysisSourceChange = (value: string) => {
  analysisSource.value = value
}

onMounted(() => {
  void refreshWorkbench()
})
</script>

<template>
  <div class="ai-sentiment-page page-enter" data-testid="ai-sentiment-page">
    <AiSentimentHero
      eyebrow="AI sentiment workbench"
      title="情感分析工作台"
      subtitle="把新闻公告、文本情感、个股趋势和市场概览放进同一 AI 主入口"
      :request-id="displayRequestId"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      data-testid="ai-sentiment-header"
    >
      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          data-testid="ai-sentiment-refresh"
          @click="refreshWorkbench"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新工作台
        </ArtDecoButton>
      </template>
    </AiSentimentHero>

    <AiSentimentSummaryCards :cards="summaryCards" data-testid="ai-sentiment-status-strip" />

    <AiSentimentWorkbenchPanels
      :announcements="announcements"
      :market-overview="marketOverview"
      :stock-trend="stockTrend"
      :analysis-text="analysisText"
      :analysis-source="analysisSource"
      :selected-symbol="selectedSymbol"
      :show-text-analyzer="true"
      :loading="loading"
      :runtime-message="runtimeMessage"
      :content-shell-description="contentShellDescription"
      :market-sentiment-label="marketSentimentLabel"
      :market-average-score="marketAverageScore"
      :stock-trend-label="stockTrendLabel"
      :stock-average-score="stockAverageScore"
      :last-analysis="lastAnalysis"
      :format-publish-date="formatPublishDate"
      :open-announcement="openAnnouncement"
      data-testid="ai-sentiment-primary-surface"
      @update:analysis-text="onAnalysisTextChange"
      @update:selected-symbol="onSelectSymbol"
      @update:analysis-source="onAnalysisSourceChange"
      @analyze="runTextAnalysis"
      @refresh="refreshWorkbench"
    />
  </div>
</template>

<style scoped lang="scss" src="./styles/SentimentWorkbench.scss"></style>
