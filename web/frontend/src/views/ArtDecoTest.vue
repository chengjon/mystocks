<template>
  <div class="artdeco-test-page">
    <h1>ArtDeco Component Test Page</h1>
    <p>This page tests all ArtDeco components</p>

    <div class="test-section">
      <h2>Base Components</h2>

      <div class="test-row">
        <h3>ArtDecoCard</h3>
        <ArtDecoCard title="Test Card" hoverable>
          <p>This is a test card content</p>
        </ArtDecoCard>
      </div>

      <div class="test-row">
        <h3>ArtDecoStatCard</h3>
        <ArtDecoStatCard
          label="测试指标"
          value="123.45"
          change="+5.67"
          change-percent
          variant="gold"
        />
      </div>

      <div class="test-row">
        <h3>ArtDecoButton</h3>
        <ArtDecoButton variant="primary">Primary Button</ArtDecoButton>
        <ArtDecoButton variant="outline">Outline Button</ArtDecoButton>
        <ArtDecoButton variant="gold">Gold Button</ArtDecoButton>
      </div>

      <div class="test-row">
        <h3>ArtDecoBadge</h3>
        <ArtDecoBadge variant="primary">Primary Badge</ArtDecoBadge>
        <ArtDecoBadge variant="success">Success Badge</ArtDecoBadge>
        <ArtDecoBadge variant="gold">Gold Badge</ArtDecoBadge>
      </div>
    </div>

    <div class="test-section">
      <h2>Core Components</h2>

      <div class="test-row">
        <h3>ArtDecoHeader</h3>
        <ArtDecoHeader title="Test Header">
          <template #actions>
            <ArtDecoButton size="sm">Action</ArtDecoButton>
          </template>
        </ArtDecoHeader>
      </div>

      <div class="test-row">
        <h3>ArtDecoIcon</h3>
        <ArtDecoIcon name="activity" />
        <ArtDecoIcon name="trending-up" />
        <ArtDecoIcon name="clock" />
      </div>
    </div>

    <div class="test-section">
      <h2>Specialized Components</h2>

      <div class="test-row">
        <h3>ArtDecoCollapsible</h3>
        <ArtDecoCollapsible title="Test Collapsible">
          <p>This is collapsible content</p>
        </ArtDecoCollapsible>
      </div>
    </div>

    <div class="test-section">
      <h2>Style Test</h2>
      <div class="style-test">
        <p>Background should be black (#0A0A0A)</p>
        <p class="gold-text">This text should be gold (#D4AF37)</p>
        <p class="border-test">This should have a gold border</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ArtDecoCard,
  ArtDecoStatCard,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoHeader,
  ArtDecoIcon,
  ArtDecoCollapsible
} from '@/components/artdeco'

console.log('ArtDecoTest.vue loaded')
console.log('Imported components:', {
  ArtDecoCard,
  ArtDecoStatCard,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoHeader,
  ArtDecoIcon,
  ArtDecoCollapsible
})
</script>

<style scoped lang="scss">
.artdeco-test-page {
  padding: 2rem;
  background: var(--artdeco-bg-primary, #0A0A0A);
  color: var(--artdeco-fg-primary, #F2F0E4);
  min-height: 100vh;

  h1 {
    color: var(--artdeco-gold-primary, #D4AF37);
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  h2 {
    color: var(--artdeco-gold-primary, #D4AF37);
    font-size: 1.5rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--artdeco-gold-primary, #D4AF37);
    padding-bottom: 0.5rem;
  }

  h3 {
    color: var(--artdeco-fg-primary, #F2F0E4);
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
  }

  p {
    color: var(--artdeco-fg-primary, #F2F0E4);
  }
}

.test-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid rgba(212, 175, 55, 0.2);
  background: var(--artdeco-bg-card, #141414);
}

.test-row {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid rgba(212, 175, 55, 0.1);
  background: var(--artdeco-bg-surface, #1a1a1a);

  > * {
    margin-right: 1rem;
  }
}

.style-test {
  padding: 1rem;
  background: var(--artdeco-bg-card, #141414);
  border: 1px solid var(--artdeco-border, #2A2A2A);

  .gold-text {
    color: var(--artdeco-gold-primary, #D4AF37);
    font-size: 1.2rem;
    font-weight: bold;
  }

  .border-test {
    padding: 0.5rem;
    border: 2px solid var(--artdeco-gold-primary, #D4AF37);
    display: inline-block;
    margin-top: 0.5rem;
  }
}
</style>
