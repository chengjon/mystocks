<template>
  <div class="trading-decision-center">
    <DecisionHeader />
    <section id="portfolio-panel">
      <DecisionPortfolio />
    </section>
    <section id="positions-panel">
      <DecisionPositions />
    </section>
    <section id="orders-panel">
      <DecisionOrders />
    </section>
  </div>
</template>

<script setup lang="ts">
import DecisionHeader from './trading-decision/DecisionHeader.vue'
import DecisionPositions from './trading-decision/DecisionPositions.vue'
import DecisionOrders from './trading-decision/DecisionOrders.vue'
import DecisionPortfolio from './trading-decision/DecisionPortfolio.vue'
</script>
