<template>
  <ArtDecoCard variant="chart">
    <template #header>
      <div class="card-header">
        <h3>⌨️ 键盘快捷键</h3>
      </div>
    </template>

    <div class="shortcuts-container">
      <!-- 全局快捷键 -->
      <div class="shortcuts-section">
        <h4 class="section-title">全局快捷键</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>K</kbd>
            </div>
            <div class="shortcut-desc">打开命令调色板</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>F5</kbd>
            </div>
            <div class="shortcut-desc">刷新当前页面</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>G</kbd>
            </div>
            <div class="shortcut-desc">跳转到页面</div>
          </div>
        </div>
      </div>

      <!-- 导航快捷键 -->
      <div class="shortcuts-section">
        <h4 class="section-title">导航快捷键</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>D</kbd>
            </div>
            <div class="shortcut-desc">仪表盘</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>T</kbd>
            </div>
            <div class="shortcut-desc">交易决策</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>A</kbd>
            </div>
            <div class="shortcut-desc">分析研究</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>P</kbd>
            </div>
            <div class="shortcut-desc">投资组合</div>
          </div>
        </div>
      </div>

      <!-- 搜索快捷键 -->
      <div class="shortcuts-section">
        <h4 class="section-title">搜索快捷键</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>/</kbd>
            </div>
            <div class="shortcut-desc">向前搜索股票</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>?</kbd>
            </div>
            <div class="shortcut-desc">向后搜索股票</div>
          </div>
        </div>
      </div>

      <!-- 菜单导航快捷键 -->
      <div class="shortcuts-section">
        <h4 class="section-title">菜单导航</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>↑</kbd> / <kbd>↓</kbd>
            </div>
            <div class="shortcut-desc">在菜单中上下导航</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Enter</kbd>
            </div>
            <div class="shortcut-desc">选择当前菜单项</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Esc</kbd>
            </div>
            <div class="shortcut-desc">关闭命令调色板/对话框</div>
          </div>
        </div>
      </div>

      <!-- 数据视图快捷键 -->
      <div class="shortcuts-section">
        <h4 class="section-title">数据视图</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>1</kbd>
            </div>
            <div class="shortcut-desc">标准表格模式</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>2</kbd>
            </div>
            <div class="shortcut-desc">紧凑表格模式（32px）</div>
          </div>
          <div class="shortcut-item">
            <div class="shortcut-key">
              <kbd>Ctrl</kbd> + <kbd>3</kbd>
            </div>
            <div class="shortcut-desc">超紧凑表格模式（24px）</div>
          </div>
        </div>
      </div>
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import ArtDecoCard from './base/ArtDecoCard.vue'
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.card-header {
  h3 {
    font-family: var(--font-display);
    font-weight: 600;
    color: var(--artdeco-gold-primary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin: 0;
  }
}

.shortcuts-container {
  padding: var(--artdeco-spacing-4);
}

.shortcuts-section {
  margin-bottom: var(--artdeco-spacing-6);

  &:last-child {
    margin-bottom: 0;
  }

  .section-title {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-gold-primary);
    margin: 0 0 var(--artdeco-spacing-2) 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: var(--artdeco-spacing-1);
    border-bottom: 1px solid var(--artdeco-border-default);
  }
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  margin-top: var(--artdeco-spacing-3);
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-2);
  transition: background-color var(--artdeco-transition-base);

  &:hover {
    background-color: rgba(212, 175, 55, 0.05);
    border-radius: var(--artdeco-radius-sm);
  }
}

.shortcut-key {
  display: flex;
  align-items: center;
  gap: 4px;

  kbd {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    height: 32px;
    padding: 0 8px;
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
    font-weight: var(--artdeco-font-medium);
    color: var(--artdeco-gold-primary);
    background-color: var(--artdeco-bg-elevated);
    border: 1px solid var(--artdeco-border-gold);
    border-radius: var(--artdeco-radius-sm);
    box-shadow: var(--artdeco-shadow-sm);
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }
}

.shortcut-desc {
  font-family: var(--font-body);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
  flex: 1;
}
</style>
