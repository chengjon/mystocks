<template>
  <div class="test-page">
    <h1>MyStocks Test Page</h1>
    <p>If you can see this, Vue is working!</p>
    <p>Current time: {{ currentTime }}</p>
    <button @click="updateTime">Update Time</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const currentTime = ref(new Date().toLocaleString())

const updateTime = () => {
  currentTime.value = new Date().toLocaleString()
}
</script>

<style scoped>
.test-page {
  padding: 20px;
  text-align: center;
}

h1 {
  color: #409eff;
}

button {
  background: #409eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #66b1ff;
}
</style>