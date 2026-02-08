<template>
  <div class="fundflow-panel">
    <h3>FundFlow</h3>
    <p>FundFlow content</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps({
  // FundFlow props
})

// FundFlow logic
const loadData = async () => {
  // Load FundFlow data
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.fundflow-panel {
  padding: 20px;
}
</style>
