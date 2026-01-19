<template>
  <div class="test-page">
    <h1>ArtDeco Integration Test</h1>
    <p>This is a simple test page to verify Vue rendering</p>
    <div class="test-content">
      <h2>Basic Elements Test</h2>
      <button class="test-button">Test Button</button>
      <div class="test-card">
        <h3>Test Card</h3>
        <p>Card content</p>
      </div>
    </div>
  </div>
</template>

<script setup>
console.log('Test page loaded successfully')
</script>

<style scoped>
.test-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.test-button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.test-card {
  border: 1px solid #ddd;
  padding: 15px;
  margin: 10px 0;
  border-radius: 8px;
}
</style>