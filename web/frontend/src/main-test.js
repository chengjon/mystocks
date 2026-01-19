// ULTRA-minimal test - no router, no imports except Vue
console.log('TEST: Starting ultra-minimal test...')

import { createApp } from 'vue'

console.log('TEST: Vue imported, creating app...')

const TestApp = {
  template: '<div><h1 style="color: red;">TEST: If you see this, VUE WORKS!</h1></div>',
  setup() {
    console.log('TEST: Component setup running')
    return {}
  }
}

console.log('TEST: Creating Vue app instance...')
const app = createApp(TestApp)

console.log('TEST: About to mount...')
try {
  app.mount('#app')
  console.log('✅✅✅ TEST: SUCCESS! Vue mounted!')
} catch (error) {
  console.error('❌ TEST: Mount failed:', error)
}
