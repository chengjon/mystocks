<template>
  <div class="minimal-test">
    <h1>MINIMAL TEST PAGE</h1>
    <p>If you can see this, routing is working!</p>
    <p>Timestamp: {{ timestamp }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

console.log('✅ MinimalTest.vue component loaded')

const timestamp = ref(new Date().toISOString())

onMounted(() => {
  console.log('✅ MinimalTest.vue mounted')
})
</script>

<style scoped>
.minimal-test {
  padding: 2rem;
  background: #000;
  color: #fff;
}

h1 {
  color: #D4AF37;
}
</style>
