<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔬 FEATURE ENGINEERING</span>
      <span class="badge badge-info">TECHNICAL</span>
    </div>

    <div class="features-section">
      <h3>ROLLING WINDOW FEATURES</h3>
      <div class="info-grid features-grid-offset">
        <div class="info-item">
          <div class="info-label">WINDOW SIZE (step)</div>
          <div class="info-value">10 Trading Days</div>
        </div>
        <div class="info-item">
          <div class="info-label">ORIGINAL FEATURES</div>
          <div class="info-value">6 Columns (code, tradeDate, open, high, low, close, amount, vol)</div>
        </div>
        <div class="info-item">
          <div class="info-label">GENERATED FEATURES</div>
          <div class="info-value highlight">10 steps × 6 features = 60 Column Feature Vector</div>
        </div>
        <div class="info-item">
          <div class="info-label">TARGET VARIABLE</div>
          <div class="info-value code">nextClose (Next Day Close Price, shift(-1))</div>
        </div>
      </div>

      <h3 class="features-section-heading">FEATURE SELECTION ALGORITHMS</h3>
      <table class="table features-table-offset">
        <thead>
          <tr>
            <th>METHOD</th>
            <th>MODULE PATH</th>
            <th>DESCRIPTION</th>
            <th>STATUS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="method in featureSelectionMethods" :key="method.method">
            <td class="method-name">{{ method.method }}</td>
            <td class="module-path">{{ method.module }}</td>
            <td>{{ method.description }}</td>
            <td><span class="badge badge-warning">INDEPENDENT</span></td>
          </tr>
        </tbody>
      </table>

      <div class="alert-card">
        <div class="alert-title">INTEGRATION NOTE</div>
        <div class="alert-content">
          Feature selection modules are currently standalone examples and not integrated with the main prediction pipeline. To use them, import from <code>featselection/</code> directory and manually integrate into <code>model.py</code>.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FEATURE_SELECTION_METHODS } from '../config'

const featureSelectionMethods = FEATURE_SELECTION_METHODS
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.demo-card {
  padding: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: var(--artdeco-spacing-4);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 30%, transparent);
}

.card-title {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-lg);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.features-section {
  padding: var(--artdeco-spacing-2) 0;

  h3 {
    margin-bottom: var(--artdeco-spacing-4);
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-base);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-4);
}

.features-grid-offset,
.features-table-offset {
  margin-top: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-px) * 5);
}

.features-section-heading {
  margin-top: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-3) / 2);
}

.info-item {
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
}

.info-label {
  margin-bottom: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.info-value {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-sm);

  &.highlight {
    color: var(--artdeco-gold-primary);
    font-weight: var(--artdeco-font-semibold);
  }

  &.code {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
  }
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wider);
    text-align: left;
    text-transform: uppercase;
  }

  td {
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }

  tr:hover td {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, transparent);
  }

  .method-name {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
  }

  .module-path {
    font-family: var(--artdeco-font-accent, var(--font-mono));
    font-size: var(--artdeco-text-xs);
  }
}

.alert-card {
  padding: var(--artdeco-spacing-4);
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-warning) 10%, var(--artdeco-bg-card));

  .alert-title {
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-warning);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }

  .alert-content {
    font-family: var(--artdeco-font-body, var(--font-body));
    font-size: var(--artdeco-text-sm);
    line-height: 1.6;
  }
}

.badge {
  display: inline-block;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  border-radius: var(--artdeco-radius-none);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.badge-info {
  border: 1px solid color-mix(in srgb, var(--artdeco-info) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-info) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-info);
}

.badge-warning {
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-warning) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-warning);
}

code {
  display: inline;
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-none);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-accent, var(--font-mono));
}
</style>
