<template>
  <div class="font-size-setting">
    <el-card>
      <template #header>
        <span>字体大小设置</span>
      </template>

      <div class="setting-content">
        <div class="setting-description">
          <p>选择全局字体大小，设置会立即应用到所有页面</p>
        </div>

        <el-radio-group v-model="selectedFontSize" @change="handleFontSizeChange" size="large" class="font-size-options">
          <el-radio-button label="12px">
            <span class="font-option">
              <span class="font-label">特小</span>
              <span class="font-value">12px</span>
            </span>
          </el-radio-button>
          <el-radio-button label="14px">
            <span class="font-option">
              <span class="font-label">小</span>
              <span class="font-value">14px</span>
            </span>
          </el-radio-button>
          <el-radio-button label="16px">
            <span class="font-option">
              <span class="font-label">中</span>
              <span class="font-value">16px</span>
            </span>
          </el-radio-button>
          <el-radio-button label="18px">
            <span class="font-option">
              <span class="font-label">大</span>
              <span class="font-value">18px</span>
            </span>
          </el-radio-button>
          <el-radio-button label="20px">
            <span class="font-option">
              <span class="font-label">特大</span>
              <span class="font-value">20px</span>
            </span>
          </el-radio-button>
        </el-radio-group>

        <div class="preview-section">
          <h4>预览效果</h4>
          <div class="preview-text">
            <p class="preview-helper">辅助文字示例 (基础字号 - 2px)</p>
            <p class="preview-body">正文文字示例 (基础字号)</p>
            <p class="preview-subtitle">副标题文字示例 (基础字号 + 2px)</p>
            <p class="preview-title">标题文字示例 (基础字号 + 4px)</p>
            <p class="preview-heading">大标题文字示例 (基础字号 + 8px)</p>
          </div>
        </div>

        <div class="current-size-info">
          <el-tag type="info">当前字体大小: {{ selectedFontSize }}</el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { usePreferencesStore } from '@/stores/preferences'

const preferencesStore = usePreferencesStore()
const selectedFontSize = ref('16px') // Default: Medium

/**
 * Handle font size change (FR-015)
 * Updates CSS variable immediately and saves to LocalStorage
 */
const handleFontSizeChange = (newSize) => {
  console.log(`[FontSizeSetting] Font size changed to: ${newSize}`)

  // Apply to CSS custom property immediately (FR-015)
  document.documentElement.style.setProperty('--font-size-base', newSize)

  // Save to LocalStorage via preferences store (FR-019)
  preferencesStore.updatePreference('fontSize', newSize)

  ElMessage.success(`字体大小已更新为 ${newSize}`)

  // Log for observability
  console.log(`[FontSizeSetting] CSS variable --font-size-base updated to ${newSize}`)
  console.log(`[FontSizeSetting] Preference saved to LocalStorage`)
}

/**
 * Initialize font size from saved preference
 */
onMounted(() => {
  // Load saved preference from store
  const savedFontSize = preferencesStore.preferences.fontSize

  if (savedFontSize) {
    selectedFontSize.value = savedFontSize
    console.log(`[FontSizeSetting] Loaded saved font size: ${savedFontSize}`)
  } else {
    // Default to Medium (16px) if no preference saved (FR-014)
    selectedFontSize.value = '16px'
    console.log('[FontSizeSetting] Using default font size: 16px')
  }
})
</script>

<style scoped>
.font-size-setting {
  max-width: 800px;
}

.setting-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setting-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.font-size-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.font-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
}

.font-label {
  font-weight: 500;
}

.font-value {
  font-size: 12px;
  color: #909399;
}

.preview-section {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}

.preview-section h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #303133;
}

.preview-text {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-helper {
  font-size: var(--font-size-helper);
  color: #909399;
  margin: 0;
}

.preview-body {
  font-size: var(--font-size-body);
  color: #606266;
  margin: 0;
}

.preview-subtitle {
  font-size: var(--font-size-subtitle);
  color: #303133;
  margin: 0;
}

.preview-title {
  font-size: var(--font-size-title);
  color: #303133;
  font-weight: 500;
  margin: 0;
}

.preview-heading {
  font-size: var(--font-size-heading);
  color: #303133;
  font-weight: 600;
  margin: 0;
}

.current-size-info {
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

/* Responsive layout (FR-020) */
@media (max-width: 768px) {
  .font-size-options {
    flex-direction: column;
  }

  .font-size-options :deep(.el-radio-button) {
    width: 100%;
  }
}
</style>
