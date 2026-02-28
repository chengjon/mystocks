<template>
  <footer class="artdeco-footer">
    <div class="footer-left">
      <slot name="left"></slot>
    </div>
    <div class="footer-center">
      <slot></slot>
    </div>
    <div class="footer-right">
      <slot name="right"></slot>
    </div>
  </footer>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-footer {
  height: 32px;
  background-color: var(--artdeco-bg-secondary);
  border-top: 1px solid var(--artdeco-border-default);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-size: 12px;
  color: var(--artdeco-fg-muted);

  .footer-left, .footer-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}
</style>