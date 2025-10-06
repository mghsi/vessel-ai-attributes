<template>
  <div class="agentic-workflow">
    <!-- Header -->
    <div class="workflow-header">
      <h2>🤖 Agentic Boat Profiling Workflow</h2>
      <p>Multi-agent system for comprehensive vessel baseline profiling</p>
    </div>

    <!-- Workflow Progress -->
    <div class="workflow-progress" v-if="workflowStarted">
      <div class="progress-header">
        <h3>Workflow Progress</h3>
        <div class="session-info">
          Session: <code>{{ sessionId?.substring(0, 8) }}...</code>
        </div>
      </div>
      
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>
      
      <div class="step-indicators">
        <div 
          v-for="(step, index) in workflowSteps" 
          :key="index"
          class="step-indicator"
          :class="{
            'completed': index < currentStep,
            'active': index === currentStep,
            'pending': index > currentStep
          }"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-name">{{ step.name }}</div>
          <div class="step-status">{{ getStepStatus(index) }}</div>
        </div>
      </div>
    </div>

    <!-- Input Section -->
    <div class="input-section" v-if="!workflowStarted">
      <div class="input-tabs">
        <button 
          @click="inputMode = 'image'"
          :class="{ active: inputMode === 'image' }"
          class="tab-button"
        >
          📸 Upload Image
        </button>
        <button 
          @click="inputMode = 'manual'"
          :class="{ active: inputMode === 'manual' }"
          class="tab-button"
        >
          ✏️ Manual Input
        </button>
      </div>

      <!-- Image Upload Mode -->
      <div v-if="inputMode === 'image'" class="image-input-mode">
        <ImageUploader 
          @image-selected="handleImageSelected"
          @image-cleared="clearImageData"
          :loading="processingWorkflow"
        />
        
        <div class="boat-details" v-if="selectedImage">
          <div class="input-group">
            <label for="brand">Boat Brand (Optional):</label>
            <input 
              id="brand"
              v-model="boatBrand" 
              type="text" 
              placeholder="e.g., SeaCraft, Catalina"
              :disabled="processingWorkflow"
            />
          </div>
          
          <div class="input-group">
            <label for="model">Boat Model (Optional):</label>
            <input 
              id="model"
              v-model="boatModel" 
              type="text" 
              placeholder="e.g., X123, 2585 QL"
              :disabled="processingWorkflow"
            />
          </div>
        </div>
      </div>

      <!-- Manual Input Mode -->
      <div v-if="inputMode === 'manual'" class="manual-input-mode">
        <div class="required-fields">
          <h4>Required Information</h4>
          <div class="input-group">
            <label for="builder_make">Builder/Make *:</label>
            <input 
              id="builder_make"
              v-model="manualData.builder_make" 
              type="text" 
              placeholder="e.g., Boston Whaler, Catalina"
              required
            />
          </div>
          
          <div class="input-group">
            <label for="class_model">Class/Model *:</label>
            <input 
              id="class_model"
              v-model="manualData.class_model" 
              type="text" 
              placeholder="e.g., Outrage 23, 355 CC"
              required
            />
          </div>
        </div>

        <div class="optional-fields">
          <h4>Optional Information</h4>
          <div class="input-row">
            <div class="input-group">
              <label for="vessel_name">Name:</label>
              <input 
                id="vessel_name"
                v-model="manualData.name" 
                type="text" 
                placeholder="Vessel name"
              />
            </div>
            
            <div class="input-group">
              <label for="mmsi">MMSI:</label>
              <input 
                id="mmsi"
                v-model="manualData.mmsi" 
                type="text" 
                placeholder="Maritime Mobile Service Identity"
              />
            </div>
          </div>

          <div class="input-row">
            <div class="input-group">
              <label for="length">Length (ft):</label>
              <input 
                id="length"
                v-model.number="manualData.length" 
                type="number" 
                placeholder="25"
                min="10"
                max="200"
              />
            </div>
            
            <div class="input-group">
              <label for="beam">Beam (ft):</label>
              <input 
                id="beam"
                v-model.number="manualData.beam" 
                type="number" 
                placeholder="8"
                min="3"
                max="50"
              />
            </div>
          </div>

          <div class="input-group">
            <label for="boat_type">Boat Type:</label>
            <select id="boat_type" v-model="manualData.boat_type">
              <option value="">Select type (optional)</option>
              <option value="V-Bottom">V-Bottom</option>
              <option value="Flat Bottom">Flat Bottom</option>
              <option value="Multi-hull">Multi-hull</option>
              <option value="Pontoon">Pontoon</option>
              <option value="RHIB">RHIB</option>
              <option value="Semi-Displacement">Semi-Displacement</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Start Workflow Button -->
      <div class="action-buttons">
        <button 
          @click="startWorkflow" 
          :disabled="!canStartWorkflow || processingWorkflow"
          class="start-workflow-btn"
        >
          {{ processingWorkflow ? '🔄 Processing...' : '🚀 Start Agentic Workflow' }}
        </button>
      </div>
    </div>

    <!-- Step Results Display -->
    <div class="step-results" v-if="stepResults.length > 0">
      <h3>Agent Results</h3>
      <div 
        v-for="(result, index) in stepResults" 
        :key="index"
        class="step-result-card"
        :class="{ 'active': index === currentStep - 1 }"
      >
        <div class="result-header">
          <h4>{{ result.agent_name }}</h4>
          <div class="result-status" :class="result.status">
            {{ result.status }}
          </div>
        </div>
        
        <div class="result-content">
          <!-- Agent 1: Boat Image/Data Analyzer -->
          <div v-if="result.agent_name === 'BoatImageAnalyzer'" class="analyzer-result">
            <div v-if="result.result.status === 'success'">
              <h5>Boat Specifications</h5>
              <div class="specs-grid">
                <div class="spec-item" v-for="(value, key) in result.result.boat_specifications" :key="key">
                  <strong>{{ formatKey(key) }}:</strong> {{ formatValue(value) }}
                </div>
              </div>
              <div v-if="result.result.suggestions_for_review" class="suggestions">
                <h6>Please Review:</h6>
                <ul>
                  <li v-for="suggestion in result.result.suggestions_for_review" :key="suggestion">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="error-message">
              {{ result.result.error }}
            </div>
          </div>

          <!-- Agent 2: Boat Profile Builder -->
          <div v-if="result.agent_name === 'BoatProfileBuilder'" class="profile-result">
            <div v-if="result.result.status === 'success'">
              <h5>Normalized Profile Attributes</h5>
              <div class="profile-attributes">
                <div 
                  v-for="attr in result.result.profile_attributes" 
                  :key="attr.name"
                  class="attribute-item"
                  :class="attr.category.toLowerCase()"
                >
                  <span class="attr-category">{{ attr.category }}</span>
                  <span class="attr-name">{{ attr.name }}</span>
                  <span class="attr-value">{{ attr.value }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent 3: Performance Curve Generator -->
          <div v-if="result.agent_name === 'PerformanceCurveGenerator'" class="curves-result">
            <div v-if="result.result.status === 'success'">
              <h5>Generated Performance Curves</h5>
              
              <!-- Naval Architecture Analysis -->
              <div v-if="result.result.naval_analysis" class="naval-analysis">
                <h6>Naval Architecture Analysis</h6>
                <div class="analysis-content">{{ result.result.naval_analysis }}</div>
              </div>
              
              <!-- Methodology Explanation -->
              <div v-if="result.result.methodology" class="methodology">
                <h6>Methodology</h6>
                <div class="methodology-content">{{ result.result.methodology }}</div>
              </div>
              
              <!-- Download CSV Button -->
              <div v-if="result.result.download_available" class="download-section">
                <button 
                  @click="downloadPerformanceCsv()" 
                  class="download-btn"
                  :disabled="downloadingCsv"
                >
                  <span v-if="downloadingCsv">📊 Downloading...</span>
                  <span v-else>📊 Download Performance Curves (CSV)</span>
                </button>
                <p class="download-info">
                  Download detailed speed-thrust-power-battery curves with naval architecture calculations
                </p>
              </div>
              
              <div class="curve-info">
                <div class="validation-notice">
                  ⚠️ Performance curves generated using Holtrop-Mennen resistance prediction methods. Suitable for baseline profiling.
                </div>
                <div class="curves-list">
                  <div v-for="(curve, curveName) in result.result.performance_curves" :key="curveName" class="curve-item">
                    <h6>{{ formatCurveName(curveName) }}</h6>
                    <p>{{ curve.curve_equation }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent 4: Telemetry Data Processor -->
          <div v-if="result.agent_name === 'TelemetryDataProcessor'" class="telemetry-result">
            <div v-if="result.result.status === 'success'">
              <h5>Telemetry Analysis Summary</h5>
              <div class="telemetry-stats">
                <div class="stat-item">
                  <span class="stat-label">Data Points:</span>
                  <span class="stat-value">{{ result.result.telemetry_summary.total_data_points }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Voyage Count:</span>
                  <span class="stat-value">{{ result.result.telemetry_summary.voyage_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Dwell Periods:</span>
                  <span class="stat-value">{{ result.result.telemetry_summary.dwell_periods }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent 5: Voyage Analytics Engine -->
          <div v-if="result.agent_name === 'VoyageAnalyticsEngine'" class="analytics-result">
            <div v-if="result.result.status === 'success'">
              <h5>Fuel & Emissions Analytics</h5>
              <div class="analytics-summary">
                <div class="summary-card">
                  <h6>Total Fuel Consumption</h6>
                  <div class="big-number">
                    {{ result.result.emissions_summary.total_fuel_consumption_gallons }} gal
                  </div>
                </div>
                <div class="summary-card">
                  <h6>CO₂ Emissions</h6>
                  <div class="big-number">
                    {{ result.result.emissions_summary.total_co2_emissions_tons }} tons
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent 6: Report & Chart Generator -->
          <div v-if="result.agent_name === 'ReportChartGenerator'" class="report-result">
            <div v-if="result.result.status === 'success'">
              <h5>📊 Baseline Profile Complete</h5>
              <div class="executive-summary">
                <div class="summary-header">
                  <h6>{{ result.result.executive_summary.vessel_name || 'Vessel Profile' }}</h6>
                  <p>{{ result.result.executive_summary.vessel_type }}</p>
                  <p>{{ result.result.executive_summary.vessel_specifications }}</p>
                </div>
                
                <div class="summary-metrics">
                  <div class="metric">
                    <span class="metric-value">
                      {{ result.result.executive_summary.operational_summary.total_operating_hours }}
                    </span>
                    <span class="metric-label">Operating Hours</span>
                  </div>
                  <div class="metric">
                    <span class="metric-value">
                      {{ result.result.executive_summary.operational_summary.total_distance_nautical_miles }}
                    </span>
                    <span class="metric-label">Nautical Miles</span>
                  </div>
                  <div class="metric">
                    <span class="metric-value">
                      {{ result.result.executive_summary.operational_summary.average_fuel_efficiency_nmpg }}
                    </span>
                    <span class="metric-label">NM/Gal</span>
                  </div>
                </div>

                <div class="next-steps">
                  <h6>Next Steps:</h6>
                  <ul>
                    <li v-for="step in result.result.executive_summary.next_steps" :key="step">
                      {{ step }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Chart Display -->
              <div class="charts-section" v-if="result.result.charts">
                <h6>Performance Charts</h6>
                <div class="charts-grid">
                  <div v-for="(chartData, chartName) in result.result.charts.performance_curves" :key="chartName" class="chart-container">
                    <img :src="'data:image/png;base64,' + chartData" :alt="chartName" class="chart-image" />
                  </div>
                  <div v-for="(chartData, chartName) in result.result.charts.voyage_analytics" :key="chartName" class="chart-container">
                    <img :src="'data:image/png;base64,' + chartData" :alt="chartName" class="chart-image" />
                  </div>
                  <div v-if="result.result.charts.emissions_breakdown" class="chart-container">
                    <img :src="'data:image/png;base64,' + result.result.charts.emissions_breakdown" alt="Emissions Breakdown" class="chart-image" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-display">
      <h4>❌ Workflow Error</h4>
      <p>{{ error }}</p>
      <button @click="resetWorkflow" class="reset-btn">Start Over</button>
    </div>
  </div>
</template>

<script>
import ImageUploader from './ImageUploader.vue'
import { executeFullWorkflow, downloadPerformanceCsv } from '../services/api.js'

export default {
  name: 'AgenticWorkflow',
  components: {
    ImageUploader
  },
  data() {
    return {
      // Workflow state
      workflowStarted: false,
      processingWorkflow: false,
      sessionId: null,
      currentStep: 0,
      stepResults: [],
      error: null,
      downloadingCsv: false,
      
      // Input modes
      inputMode: 'image', // 'image' or 'manual'
      
      // Image input data
      selectedImage: null,
      boatBrand: '',
      boatModel: '',
      
      // Manual input data
      manualData: {
        builder_make: '',
        class_model: '',
        name: '',
        mmsi: '',
        length: null,
        beam: null,
        boat_type: ''
      },
      
      // Workflow steps definition
      workflowSteps: [
        { name: 'Image/Data Analysis', description: 'Analyze boat specifications' },
        { name: 'Profile Building', description: 'Create normalized profile' },
        { name: 'Performance Curves', description: 'Generate performance curves' },
        { name: 'Telemetry Processing', description: 'Process operational data' },
        { name: 'Voyage Analytics', description: 'Calculate fuel & emissions' },
        { name: 'Report Generation', description: 'Create comprehensive report' }
      ]
    }
  },
  computed: {
    canStartWorkflow() {
      if (this.inputMode === 'image') {
        return this.selectedImage !== null
      } else {
        return this.manualData.builder_make.trim() && this.manualData.class_model.trim()
      }
    },
    
    progressPercentage() {
      return (this.currentStep / this.workflowSteps.length) * 100
    }
  },
  methods: {
    handleImageSelected(imageFile) {
      this.selectedImage = imageFile
      this.error = null
    },
    
    clearImageData() {
      this.selectedImage = null
      this.boatBrand = ''
      this.boatModel = ''
    },
    
    async startWorkflow() {
      if (!this.canStartWorkflow) return
      
      this.processingWorkflow = true
      this.error = null
      
      try {
        let workflowData = {}
        
        if (this.inputMode === 'image') {
          // Convert image to base64
          const imageBase64 = await this.fileToBase64(this.selectedImage)
          workflowData = {
            image_data: imageBase64,
            brand: this.boatBrand.trim(),
            model: this.boatModel.trim()
          }
        } else {
          // Clean manual data
          const cleanManualData = { ...this.manualData }
          Object.keys(cleanManualData).forEach(key => {
            if (typeof cleanManualData[key] === 'string') {
              cleanManualData[key] = cleanManualData[key].trim()
            }
          })
          workflowData = {
            manual_data: cleanManualData
          }
        }
        
        // Execute full workflow
        const result = await executeFullWorkflow(workflowData)
        
        this.workflowStarted = true
        this.sessionId = result.session_id
        this.stepResults = result.step_results || []
        this.currentStep = result.total_steps_completed || 0
        
      } catch (error) {
        console.error('Workflow execution error:', error)
        this.error = error.response?.data?.error || 'Failed to execute workflow'
      } finally {
        this.processingWorkflow = false
      }
    },
    
    resetWorkflow() {
      this.workflowStarted = false
      this.processingWorkflow = false
      this.sessionId = null
      this.currentStep = 0
      this.stepResults = []
      this.error = null
      this.clearImageData()
      this.manualData = {
        builder_make: '',
        class_model: '',
        name: '',
        mmsi: '',
        length: null,
        beam: null,
        boat_type: ''
      }
    },
    
    fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result.split(',')[1])
        reader.onerror = error => reject(error)
      })
    },
    
    getStepStatus(stepIndex) {
      if (stepIndex < this.currentStep) return '✅ Complete'
      if (stepIndex === this.currentStep && this.processingWorkflow) return '⏳ Processing'
      if (stepIndex === this.currentStep) return '🔄 Current'
      return '⏸️ Pending'
    },
    
    formatKey(key) {
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatValue(value) {
      if (typeof value === 'object') return JSON.stringify(value)
      return value
    },
    
    formatCurveName(curveName) {
      return curveName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    async downloadPerformanceCsv() {
      if (!this.sessionId || this.downloadingCsv) return
      
      this.downloadingCsv = true
      
      try {
        // Use the API service function
        const blob = await downloadPerformanceCsv(this.sessionId)
        
        // Create filename
        const filename = `vessel_performance_curves_${this.sessionId.slice(0, 8)}.csv`
        
        // Create download
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        
      } catch (error) {
        console.error('Failed to download performance curves:', error)
        this.error = `Failed to download CSV: ${error.message}`
      } finally {
        this.downloadingCsv = false
      }
    }
  }
}
</script>

<style scoped>
.agentic-workflow {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 1rem;
}

.workflow-header {
  text-align: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.workflow-header h2 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.workflow-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.workflow-progress {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.session-info code {
  background: #f8f9fa;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.step-indicators {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.step-indicator {
  flex: 1;
  min-width: 150px;
  text-align: center;
  padding: 1rem;
  border-radius: 10px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.step-indicator.completed {
  background: #d4edda;
  border: 2px solid #28a745;
}

.step-indicator.active {
  background: #fff3cd;
  border: 2px solid #ffc107;
}

.step-indicator.pending {
  background: #f8f9fa;
  border: 2px solid #dee2e6;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
  font-weight: bold;
}

.step-indicator.completed .step-number {
  background: #28a745;
}

.step-indicator.active .step-number {
  background: #ffc107;
  color: #212529;
}

.step-name {
  font-weight: bold;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.step-status {
  font-size: 0.8rem;
  color: #6c757d;
}

.input-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.input-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tab-button {
  flex: 1;
  padding: 1rem 2rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: bold;
  transition: all 0.3s ease;
}

.tab-button.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
}

.tab-button:hover {
  border-color: #667eea;
}

.required-fields, .optional-fields {
  margin-bottom: 2rem;
}

.required-fields h4, .optional-fields h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #eee;
}

.input-group {
  margin-bottom: 1rem;
}

.input-row {
  display: flex;
  gap: 1rem;
}

.input-row .input-group {
  flex: 1;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #495057;
}

.input-group input, .input-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-group input:focus, .input-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.action-buttons {
  text-align: center;
  margin-top: 2rem;
}

.start-workflow-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 1rem 3rem;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
}

.start-workflow-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
}

.start-workflow-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  box-shadow: none;
}

.step-results {
  margin-top: 2rem;
}

.step-results h3 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.step-result-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #dee2e6;
  transition: all 0.3s ease;
}

.step-result-card.active {
  border-left-color: #667eea;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.result-header h4 {
  color: #2c3e50;
  margin: 0;
}

.result-status {
  padding: 0.25rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
}

.result-status.success {
  background: #d4edda;
  color: #155724;
}

.result-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.spec-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.profile-attributes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1rem 0;
}

.attribute-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
  min-width: 120px;
  text-align: center;
}

.attribute-item.physical {
  border-top: 3px solid #17a2b8;
}

.attribute-item.operational {
  border-top: 3px solid #28a745;
}

.attr-category {
  font-size: 0.7rem;
  text-transform: uppercase;
  font-weight: bold;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.attr-name {
  font-size: 0.9rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.attr-value {
  font-size: 1.1rem;
  color: #2c3e50;
}

.validation-notice {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.naval-analysis {
  margin-bottom: 1.5rem;
}

.naval-analysis h6 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.analysis-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  max-height: 300px;
  overflow-y: auto;
}

.methodology {
  margin-bottom: 1.5rem;
}

.methodology h6 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.methodology-content {
  background: #e3f2fd;
  border-radius: 8px;
  padding: 1rem;
  white-space: pre-wrap;
  font-size: 0.9rem;
}

.download-section {
  margin: 1.5rem 0;
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
}

.download-btn {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.download-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.download-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.download-info {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.curves-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.curve-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #ffc107;
}

.curve-item h6 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.telemetry-stats, .analytics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.stat-item, .summary-card {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-label, .summary-card h6 {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.stat-value, .big-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.executive-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  margin: 1rem 0;
}

.summary-header h6 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.summary-metrics {
  display: flex;
  justify-content: space-around;
  margin: 2rem 0;
  flex-wrap: wrap;
  gap: 1rem;
}

.metric {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.next-steps {
  margin-top: 2rem;
}

.next-steps ul {
  margin-left: 1rem;
}

.charts-section {
  margin-top: 2rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-image {
  width: 100%;
  height: auto;
  border-radius: 4px;
}

.error-display {
  background: #f8d7da;
  color: #721c24;
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
  margin: 2rem 0;
}

.reset-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s ease;
}

.reset-btn:hover {
  background: #c82333;
}

.suggestions ul {
  text-align: left;
  margin-left: 1rem;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 8px;
  border-left: 3px solid #dc3545;
}

@media (max-width: 768px) {
  .step-indicators {
    flex-direction: column;
  }
  
  .input-row {
    flex-direction: column;
  }
  
  .summary-metrics {
    flex-direction: column;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>