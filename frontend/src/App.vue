<template>
  <div id="app">
    <header class="app-header">
      <h1>🚤 Boat Analyzer AI</h1>
      <p>AI-powered boat image analysis for type, dimensions, and usage detection</p>
    </header>
    
    <main class="main-content">
      <BoatAnalyzer />
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2025 BlueGrid Vessel AI - Proof of Concept</p>
    </footer>
  </div>
</template>

<script>
import BoatAnalyzer from './components/BoatAnalyzer.vue'

export default {
  name: 'App',
  components: {
    BoatAnalyzer
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.app-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.app-footer {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}
</style>