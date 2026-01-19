<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script setup>
// MyStocks Vue Application - Root Component
// The router-view will render the appropriate page component
console.log('App.vue loaded')
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  width: 100%;
}
</style>
