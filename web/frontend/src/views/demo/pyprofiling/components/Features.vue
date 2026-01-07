<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔬 FEATURE ENGINEERING</span>
      <span class="badge badge-info">TECHNICAL</span>
    </div>

    <div class="features-section">
      <h3>ROLLING WINDOW FEATURES</h3>
      <div class="info-grid" style="margin-top: 15px">
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

      <h3 style="margin-top: 30px">FEATURE SELECTION ALGORITHMS</h3>
      <table class="table" style="margin-top: 15px">
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

.demo-card {
  padding: var(--spacing-5);
  margin-bottom: var(--spacing-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-5);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--font-size-h5);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--fg-primary);
}

.features-section {
  padding: var(--spacing-2) 0;

  h3 {
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    color: var(--accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-4);
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

.info-item {
  padding: var(--spacing-4);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.info-label {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin-bottom: var(--spacing-2);
}

.info-value {
  font-family: var(--font-body);
  color: var(--fg-primary);
  font-size: var(--font-size-small);

  &.highlight {
    color: var(--accent-gold);
    font-weight: 600;
  }

  &.code {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 2px solid var(--accent-gold);
    text-align: left;
  }

  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    color: var(--fg-secondary);
    font-size: var(--font-size-small);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.03);
  }

  .method-name {
    font-family: var(--font-display);
    color: var(--accent-gold);
    font-weight: 600;
  }

  .module-path {
    font-family: var(--font-mono);
    font-size: var(--font-size-xs);
  }
}

  padding: var(--spacing-4);
  border: 1px solid;

  .alert-title {
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-2);
  }

  .alert-content {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    line-height: 1.6;
  }
}

  background: rgba(230, 126, 34, 0.1);
  border-color: rgba(230, 126, 34, 0.4);

  .alert-title {
    color: #E67E22;
  }
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border-radius: 0;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
}

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

code {
  background: rgba(212, 175, 55, 0.1);
  padding: 2px 6px;
  border-radius: 0;
  font-family: var(--font-mono);
  color: var(--accent-gold);
  display: inline;
}
</style>
