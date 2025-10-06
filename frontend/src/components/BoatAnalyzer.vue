<template>
  <div class="boat-analyzer">
    <div class="analyzer-card">
      <h2>🔍 Analyze Your Boat</h2>
      
      <!-- Upload Section -->
      <div class="upload-section">
        <ImageUploader 
          @image-selected="handleImageSelected"
          @image-cleared="clearResults"
          :loading="analyzing"
        />
        
        <!-- Optional boat details -->
        <div class="boat-details" v-if="selectedImage">
          <div class="input-group">
            <label for="brand">Boat Brand (Optional):</label>
            <input 
              id="brand"
              v-model="boatBrand" 
              type="text" 
              placeholder="e.g., SeaCraft, Catalina"
              :disabled="analyzing"
            />
          </div>
          
          <div class="input-group">
            <label for="model">Boat Model (Optional):</label>
            <input 
              id="model"
              v-model="boatModel" 
              type="text" 
              placeholder="e.g., X123, 2585 QL"
              :disabled="analyzing"
            />
          </div>
          
          <button 
            @click="analyzeImage" 
            :disabled="analyzing || !selectedImage"
            class="analyze-btn"
          >
            {{ analyzing ? '🔄 Analyzing...' : '🚀 Analyze Boat' }}
          </button>
        </div>
      </div>
      
      <!-- Results Section -->
      <AnalysisResults 
        v-if="analysisResult" 
        :result="analysisResult"
        :error="analysisError"
      />
    </div>
  </div>
</template>

<script>
import ImageUploader from './ImageUploader.vue'
import AnalysisResults from './AnalysisResults.vue'
import { analyzeBoat } from '../services/api.js'

export default {
  name: 'BoatAnalyzer',
  components: {
    ImageUploader,
    AnalysisResults
  },
  data() {
    return {
      selectedImage: null,
      boatBrand: '',
      boatModel: '',
      analyzing: false,
      analysisResult: null,
      analysisError: null
    }
  },
  methods: {
    handleImageSelected(imageFile) {
      this.selectedImage = imageFile
      this.clearResults()
    },
    
    clearResults() {
      this.analysisResult = null
      this.analysisError = null
    },
    
    async analyzeImage() {
      if (!this.selectedImage) return
      
      this.analyzing = true
      this.clearResults()
      
      try {
        const formData = new FormData()
        formData.append('image', this.selectedImage)
        
        if (this.boatBrand.trim()) {
          formData.append('brand', this.boatBrand.trim())
        }
        
        if (this.boatModel.trim()) {
          formData.append('model', this.boatModel.trim())
        }
        
        const result = await analyzeBoat(formData)
        this.analysisResult = result
        this.analysisError = null
        
      } catch (error) {
        console.error('Analysis error:', error)
        this.analysisError = error.response?.data || { ERROR: 'Failed to analyze image', CODE: 'NET001' }
        this.analysisResult = null
      } finally {
        this.analyzing = false
      }
    }
  }
}
</script>

<style scoped>
.boat-analyzer {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.analyzer-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.analyzer-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 1.8rem;
}

.upload-section {
  margin-bottom: 2rem;
}

.boat-details {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-group input:disabled {
  background-color: #f5f5f5;
  color: #999;
}

.analyze-btn {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>