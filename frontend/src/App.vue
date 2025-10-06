<template>
  <div id="app">
    <header class="app-header">
      <h1>🚤 Vessel AI - Baseline Profiling System</h1>
      <p>Multi-agent AI system for comprehensive vessel baseline profiling and analytics</p>
      
      <!-- Mode Selector -->
      <div class="mode-selector">
        <button 
          @click="currentMode = 'simple'"
          :class="{ active: currentMode === 'simple' }"
          class="mode-btn"
        >
          🔍 Simple Analysis
        </button>
        <button 
          @click="currentMode = 'agentic'"
          :class="{ active: currentMode === 'agentic' }"
          class="mode-btn"
        >
          🤖 Agentic Workflow
        </button>
      </div>
    </header>
    
    <main class="main-content">
      <!-- Simple Analysis Mode -->
      <BoatAnalyzer v-if="currentMode === 'simple'" />
      
      <!-- Agentic Workflow Mode -->
      <AgenticWorkflow v-if="currentMode === 'agentic'" />
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2025 BlueGrid Vessel AI - Advanced Baseline Profiling System</p>
    </footer>
  </div>
</template>

<script>
import BoatAnalyzer from './components/BoatAnalyzer.vue'
import AgenticWorkflow from './components/AgenticWorkflow.vue'

export default {
  name: 'App',
  components: {
    BoatAnalyzer,
    AgenticWorkflow
  },
  data() {
    return {
      currentMode: 'agentic' // Default to the new agentic workflow
    }
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
  margin-bottom: 1.5rem;
}

.mode-selector {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.mode-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #dee2e6;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #495057;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.mode-btn.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
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