// Minimal main.js for debugging
import { createApp } from 'vue'

console.log('🔍 Step 1: Vue imported')

// Simple App component
const SimpleApp = {
  template: `
    <div class="simple-app">
      <h1>🎉 SIMPLE APP IS WORKING!</h1>
      <p>Vue mount test successful</p>
      <p>Timestamp: {{ new Date().toISOString() }}</p>
    </div>
  `,
  setup() {
    console.log('🔍 Step 2: SimpleApp component defined')
    return {}
  }
}

console.log('🔍 Step 3: Creating Vue app...')

const app = createApp(SimpleApp)

console.log('🔍 Step 4: Mounting to #app...')

try {
  app.mount('#app')
  console.log('✅ SUCCESS: Vue app mounted!')
} catch (error) {
  console.error('❌ FAILED to mount:', error)
}

console.log('🔍 Step 5: main.js completed')
