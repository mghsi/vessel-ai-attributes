<template>
  <div class="analysis-results">
    <div v-if="error" class="error-card">
      <h3>❌ Analysis Failed</h3>
      <div class="error-details">
        <p><strong>Error:</strong> {{ error.ERROR || 'Unknown error occurred' }}</p>
        <p v-if="error.CODE"><strong>Code:</strong> {{ error.CODE }}</p>
      </div>
    </div>
    
    <div v-else-if="result" class="success-card">
      <h3>✅ Analysis Complete</h3>
      <div class="results-grid">
        <div class="result-item boat-type">
          <div class="result-icon">🚤</div>
          <div class="result-content">
            <h4>Boat Type</h4>
            <p class="result-value">{{ result['Boat Type'] || 'Not determined' }}</p>
          </div>
        </div>
        
        <div class="result-item dimensions">
          <div class="result-icon">📏</div>
          <div class="result-content">
            <h4>Dimensions</h4>
            <div class="dimension-details">
              <span class="dimension">
                <strong>Length:</strong> {{ result.Length || 'N/A' }}{{ result.Length ? ' ft' : '' }}
              </span>
              <span class="dimension">
                <strong>Width:</strong> {{ result.Width || 'N/A' }}{{ result.Width ? ' ft' : '' }}
              </span>
              <span class="dimension">
                <strong>Beam:</strong> {{ result.Beam || 'N/A' }}{{ result.Beam ? ' ft' : '' }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="result-item usage">
          <div class="result-icon">🎯</div>
          <div class="result-content">
            <h4>Usage Classification</h4>
            <div class="usage-details">
              <span class="usage-badge" :class="{ 'commercial': result.Commercial === 'YES', 'recreational': result.Commercial === 'NO' }">
                {{ result.Commercial === 'YES' ? '🏢 Commercial' : result.Commercial === 'NO' ? '🏖️ Recreational' : '❓ Unknown' }}
              </span>
              <span class="aux-badge" :class="{ 'has-aux': result.Aux === 'YES', 'no-aux': result.Aux === 'NO' }">
                {{ result.Aux === 'YES' ? '⚙️ Has Auxiliary Features' : result.Aux === 'NO' ? '🚫 No Auxiliary Features' : '❓ Aux Unknown' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="analysis-summary">
        <h4>📊 Analysis Summary</h4>
        <p>
          This appears to be a <strong>{{ result['Boat Type'] || 'unidentified' }}</strong> boat
          {{ result.Length ? `measuring approximately ${result.Length} feet in length` : '' }}{{ result.Width ? ` by ${result.Width} feet wide` : '' }}.
          {{ result.Commercial === 'YES' ? 'Classified as commercial use.' : result.Commercial === 'NO' ? 'Classified for recreational use.' : '' }}
          {{ result.Aux === 'YES' ? 'Additional auxiliary features detected.' : '' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnalysisResults',
  props: {
    result: {
      type: Object,
      default: null
    },
    error: {
      type: Object,
      default: null
    }
  }
}
</script>

<style scoped>
.analysis-results {
  margin-top: 2rem;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-card, .success-card {
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.error-card {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.success-card {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  color: white;
}

.error-card h3, .success-card h3 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
  text-align: center;
}

.error-details p {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.results-grid {
  display: grid;
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.result-item {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.result-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.result-content {
  flex: 1;
}

.result-content h4 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.95);
}

.result-value {
  font-size: 1.4rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.dimension-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.dimension {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.95rem;
  white-space: nowrap;
}

.usage-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.usage-badge, .aux-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
}

.usage-badge.commercial {
  background: rgba(255, 193, 7, 0.9);
  color: #333;
}

.usage-badge.recreational {
  background: rgba(33, 150, 243, 0.9);
  color: white;
}

.aux-badge.has-aux {
  background: rgba(76, 175, 80, 0.9);
  color: white;
}

.aux-badge.no-aux {
  background: rgba(158, 158, 158, 0.9);
  color: white;
}

.analysis-summary {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.analysis-summary h4 {
  margin-bottom: 1rem;
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.95);
}

.analysis-summary p {
  font-size: 1.1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

@media (max-width: 768px) {
  .dimension-details {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .usage-details {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .result-item {
    flex-direction: column;
    text-align: center;
  }
  
  .result-icon {
    align-self: center;
  }
}
</style>