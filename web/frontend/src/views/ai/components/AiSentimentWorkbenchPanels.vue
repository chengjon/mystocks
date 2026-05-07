<script setup lang="ts">
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon } from '@/components/artdeco'
import type { SentimentNewsItem } from '@/api/aiSentiment'
import type { SentimentStockTrendResponse, SentimentMarketOverviewResponse } from '@/api/aiSentiment'

defineProps<{
  announcements: SentimentNewsItem[]
  marketOverview: SentimentMarketOverviewResponse | null
  stockTrend: SentimentStockTrendResponse | null
  analysisText: string
  analysisSource: string
  selectedSymbol: string
  showTextAnalyzer: boolean
  loading: boolean
  runtimeMessage: string
  contentShellDescription: string
  marketSentimentLabel: string
  marketAverageScore: string
  stockTrendLabel: string
  stockAverageScore: string
  lastAnalysis: {
    sentiment: string
    confidence: number
    positiveScore: number
    negativeScore: number
    neutralScore: number
    keyPhrases: string[]
    analyzedAt: string
    source: string | null
  } | null
  formatPublishDate: (date?: string, time?: string | null) => string
  openAnnouncement: (url?: string | null) => void
}>()

const emit = defineEmits<{
  'update:analysisText': [value: string]
  'update:selectedSymbol': [value: string]
  'update:analysisSource': [value: string]
  analyze: []
  refresh: []
}>()

function importanceType(level?: number | null): 'danger' | 'warning' | 'success' | 'info' {
  const value = Number(level || 0)
  if (value >= 4) return 'danger'
  if (value >= 3) return 'warning'
  if (value >= 1) return 'success'
  return 'info'
}
</script>

<template>
  <section class="content-shell artdeco-card-shell">
    <div class="content-shell-header">
      <div class="content-shell-copy">
        <span class="content-shell-kicker">sentiment desk</span>
        <h2 class="content-shell-title">AI 情感工作台</h2>
        <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
      </div>
      <div class="content-shell-meta">
        <span>MARKET: {{ marketSentimentLabel }}</span>
        <span>STOCK: {{ stockTrendLabel }}</span>
        <span>AVG: {{ marketAverageScore }}</span>
      </div>
    </div>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

    <div class="workspace-grid">
      <div class="workspace-column workspace-column--news">
        <ArtDecoCard title="公告与舆情流" hoverable>
          <div v-if="announcements.length === 0" class="empty-state">暂无公告数据，公告流为空。</div>
          <el-table v-else :data="announcements" stripe empty-text="暂无公告数据">
            <el-table-column prop="stock_code" label="代码" width="110" />
            <el-table-column prop="stock_name" label="名称" width="140" />
            <el-table-column prop="announcement_type" label="类型" width="140" show-overflow-tooltip />
            <el-table-column prop="announcement_title" label="标题" min-width="280" show-overflow-tooltip />
            <el-table-column label="重要性" width="120">
              <template #default="{ row }">
                <el-tag :type="importanceType(row.importance_level)">{{ row.importance_level ?? 0 }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="发布时间" width="180">
              <template #default="{ row }">
                <span class="mono">{{ formatPublishDate(row.publish_date, row.publish_time) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" :disabled="!row.url" @click="openAnnouncement(row.url)">查看原文</el-button>
              </template>
            </el-table-column>
          </el-table>
        </ArtDecoCard>
      </div>

      <div class="workspace-column workspace-column--analysis">
        <ArtDecoCard title="市场情绪概览" hoverable>
          <div class="analysis-stack">
            <div class="analysis-item">
              <span class="analysis-label">市场情绪</span>
              <strong>{{ marketOverview?.sentiment || 'neutral' }}</strong>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">平均情绪</span>
              <strong>{{ marketAverageScore }}</strong>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">热点标的</span>
              <strong>{{ marketOverview?.hot_symbols?.join(' / ') || '--' }}</strong>
            </div>
          </div>
        </ArtDecoCard>

        <ArtDecoCard title="个股情绪趋势" hoverable>
          <div class="analysis-stack">
            <div class="analysis-item">
              <span class="analysis-label">标的</span>
              <strong>{{ selectedSymbol }}</strong>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">趋势</span>
              <strong>{{ stockTrendLabel }}</strong>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">平均情绪</span>
              <strong>{{ stockAverageScore }}</strong>
            </div>
          </div>
          <div v-if="stockTrend?.timeline?.length" class="timeline-list">
            <div v-for="item in stockTrend.timeline" :key="`${item.date}-${item.sentiment}`" class="timeline-row">
              <span>{{ item.date }}</span>
              <span>{{ item.sentiment }}</span>
              <span>{{ item.score }}</span>
              <span>{{ item.confidence }}</span>
            </div>
          </div>
        </ArtDecoCard>

        <ArtDecoCard v-if="showTextAnalyzer" title="文本情感分析" hoverable>
          <div class="form-stack">
            <label class="field">
              <span>标的代码</span>
              <input
                :value="selectedSymbol"
                type="text"
                maxlength="16"
                @input="emit('update:selectedSymbol', ($event.target as HTMLInputElement).value)"
              />
            </label>

            <label class="field">
              <span>情感来源</span>
              <input
                :value="analysisSource"
                type="text"
                @input="emit('update:analysisSource', ($event.target as HTMLInputElement).value)"
              />
            </label>

            <label class="field">
              <span>分析文本</span>
              <textarea
                :value="analysisText"
                rows="5"
                @input="emit('update:analysisText', ($event.target as HTMLTextAreaElement).value)"
              />
            </label>

            <div class="action-row">
              <ArtDecoButton variant="solid" size="sm" :loading="loading" @click="emit('analyze')">
                <template #icon>
                  <ArtDecoIcon name="search" />
                </template>
                分析文本
              </ArtDecoButton>
              <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="emit('refresh')">
                <template #icon>
                  <ArtDecoIcon name="refresh" />
                </template>
                刷新工作台
              </ArtDecoButton>
            </div>
          </div>

          <div v-if="lastAnalysis" class="analysis-result">
            <strong>结果: {{ lastAnalysis.sentiment }}</strong>
            <span>confidence: {{ lastAnalysis.confidence.toFixed(2) }}</span>
            <span>positive: {{ lastAnalysis.positiveScore.toFixed(2) }}</span>
            <span>negative: {{ lastAnalysis.negativeScore.toFixed(2) }}</span>
            <span>neutral: {{ lastAnalysis.neutralScore.toFixed(2) }}</span>
            <span>phrases: {{ lastAnalysis.keyPhrases.join(' / ') || '--' }}</span>
          </div>
        </ArtDecoCard>
      </div>
    </div>
  </section>
</template>
