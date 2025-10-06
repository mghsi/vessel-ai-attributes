<template>
  <div class="final-results">
    <div class="results-header">
      <h3>🎉 Baseline Vessel Profile Complete!</h3>
      <p>Your comprehensive boat profiling workflow has been successfully completed</p>
    </div>

    <!-- Executive Summary -->
    <div v-if="executiveSummary" class="executive-summary-section">
      <h4>📊 Executive Summary</h4>
      <div class="summary-card">
        <div class="vessel-overview">
          <div class="vessel-header">
            <h5>{{ executiveSummary.vessel_name || 'Vessel Profile' }}</h5>
            <span class="vessel-type">{{ executiveSummary.vessel_type }}</span>
          </div>
          <div class="vessel-specs">{{ executiveSummary.vessel_specifications }}</div>
        </div>
        
        <div class="summary-metrics">
          <div class="metric-grid">
            <div class="metric-item">
              <span class="metric-label">Operating Hours</span>
              <span class="metric-value">{{ executiveSummary.operational_summary?.total_operating_hours || 0 }} hrs</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Distance Traveled</span>
              <span class="metric-value">{{ executiveSummary.operational_summary?.total_distance_nautical_miles || 0 }} nm</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Fuel Efficiency</span>
              <span class="metric-value">{{ executiveSummary.operational_summary?.average_fuel_efficiency_nmpg || 0 }} nm/gal</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">CO₂ Emissions</span>
              <span class="metric-value">{{ executiveSummary.environmental_impact?.total_co2_emissions_tons || 0 }} tons</span>
            </div>
          </div>
        </div>
        
        <div class="status-indicator">
          <span class="status-badge">{{ executiveSummary.baseline_status }}</span>
        </div>
      </div>
    </div>

    <!-- Generated Charts Display -->
    <div v-if="hasCharts" class="charts-section">
      <h4>📈 Generated Performance Charts</h4>
      <div class="charts-grid">
        <div v-for="(chartData, chartName) in allCharts" :key="chartName" class="chart-card">
          <h5>{{ formatChartTitle(chartName) }}</h5>
          <div class="chart-container">
            <img 
              v-if="chartData && typeof chartData === 'string'" 
              :src="`data:image/png;base64,${chartData}`" 
              :alt="formatChartTitle(chartName)"
              class="chart-image"
            />
            <div v-else class="chart-placeholder">
              Chart data not available
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Findings -->
    <div v-if="keyFindings && keyFindings.length" class="findings-section">
      <h4>🔍 Key Findings</h4>
      <div class="findings-list">
        <div v-for="(finding, index) in keyFindings" :key="index" class="finding-item">
          <span class="finding-number">{{ index + 1 }}</span>
          <span class="finding-text">{{ finding }}</span>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations && recommendations.length" class="recommendations-section">
      <h4>💡 Recommendations</h4>
      <div class="recommendations-list">
        <div v-for="(recommendation, index) in recommendations" :key="index" class="recommendation-item">
          <span class="recommendation-icon">🎯</span>
          <span class="recommendation-text">{{ recommendation }}</span>
        </div>
      </div>
    </div>

    <!-- Next Steps -->
    <div v-if="nextSteps && nextSteps.length" class="next-steps-section">
      <h4>🚀 Next Steps</h4>
      <div class="next-steps-list">
        <div v-for="(step, index) in nextSteps" :key="index" class="next-step-item">
          <span class="step-number">{{ index + 1 }}</span>
          <span class="step-text">{{ step }}</span>
        </div>
      </div>
    </div>

    <!-- Data Export Options -->
    <div class="export-section">
      <h4>📁 Export Options</h4>
      <div class="export-buttons">
        <button @click="exportCSV" class="export-btn csv-btn">
          📊 Export CSV Data
        </button>
        <button @click="exportReport" class="export-btn report-btn">
          📄 Download Full Report
        </button>
        <button @click="exportCharts" class="export-btn charts-btn">
          📈 Download Charts
        </button>
      </div>
    </div>

    <!-- Workflow Summary -->
    <div class="workflow-summary">
      <h4>⚙️ Workflow Summary</h4>
      <div class="summary-stats">
        <div class="stat-item">
          <span class="stat-label">Total Agents:</span>
          <span class="stat-value">{{ totalAgents }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Completed Steps:</span>
          <span class="stat-value">{{ completedSteps }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Session ID:</span>
          <span class="stat-value">{{ sessionId?.substring(0, 8) }}...</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Generated At:</span>
          <span class="stat-value">{{ formatDateTime(createdAt) }}</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button @click="startNewWorkflow" class="action-btn primary-btn">
        🔄 Start New Analysis
      </button>
      <button @click="shareResults" class="action-btn secondary-btn">
        📤 Share Results
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinalResultsDisplay',
  props: {
    workflowResults: {
      type: Object,
      required: true
    }
  },
  computed: {
    executiveSummary() {
      // Try to get executive summary from different possible locations
      const reportAgent = this.workflowResults.agent_outputs?.ReportChartGenerator?.output
      return reportAgent?.executive_summary || null
    },
    
    keyFindings() {
      const reportAgent = this.workflowResults.agent_outputs?.ReportChartGenerator?.output
      return reportAgent?.comprehensive_report?.key_findings || []
    },
    
    recommendations() {
      const reportAgent = this.workflowResults.agent_outputs?.ReportChartGenerator?.output
      return reportAgent?.comprehensive_report?.recommendations || []
    },
    
    nextSteps() {
      return this.executiveSummary?.next_steps || []
    },
    
    allCharts() {
      const reportAgent = this.workflowResults.agent_outputs?.ReportChartGenerator?.output
      if (!reportAgent?.charts) return {}
      
      let charts = {}
      
      // Flatten all chart categories
      Object.keys(reportAgent.charts).forEach(category => {
        const categoryCharts = reportAgent.charts[category]
        if (typeof categoryCharts === 'object') {
          Object.keys(categoryCharts).forEach(chartName => {
            charts[`${category}_${chartName}`] = categoryCharts[chartName]
          })
        } else {
          charts[category] = categoryCharts
        }
      })
      
      return charts
    },
    
    hasCharts() {
      return Object.keys(this.allCharts).length > 0
    },
    
    totalAgents() {
      return Object.keys(this.workflowResults.agent_outputs || {}).length
    },
    
    completedSteps() {
      return this.totalAgents
    },
    
    sessionId() {
      return this.workflowResults.session_id
    },
    
    createdAt() {
      return this.workflowResults.created_at || new Date().toISOString()
    }
  },
  methods: {
    formatChartTitle(chartName) {
      const titles = {
        'performance_curves_speed_vs_fuel': 'Speed vs Fuel Consumption',
        'performance_curves_speed_vs_power': 'Speed vs Shaft Power',
        'performance_curves_speed_vs_thrust': 'Speed vs Thrust',
        'voyage_analytics_fuel_by_voyage': 'Fuel Consumption by Voyage',
        'voyage_analytics_efficiency_by_voyage': 'Fuel Efficiency by Voyage',
        'emissions_breakdown': 'Emissions Breakdown'
      }
      
      return titles[chartName] || chartName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatDateTime(dateString) {
      try {
        return new Date(dateString).toLocaleString()
      } catch {
        return 'Unknown'
      }
    },
    
    exportCSV() {
      // Get CSV data from voyage analytics
      const voyageAgent = this.workflowResults.agent_outputs?.VoyageAnalyticsEngine?.output
      if (voyageAgent?.csv_outputs) {
        this.downloadFile(voyageAgent.csv_outputs.voyage_data, 'voyage_analytics.csv', 'text/csv')
        if (voyageAgent.csv_outputs.dwell_data) {
          this.downloadFile(voyageAgent.csv_outputs.dwell_data, 'dwell_analytics.csv', 'text/csv')
        }
      } else {
        alert('CSV data not available')
      }
    },
    
    exportReport() {
      // Generate and download comprehensive report
      const report = this.generateReportContent()
      this.downloadFile(report, 'vessel_baseline_profile_report.txt', 'text/plain')
    },
    
    exportCharts() {
      // Download all charts as images
      Object.keys(this.allCharts).forEach(chartName => {
        const chartData = this.allCharts[chartName]
        if (chartData && typeof chartData === 'string') {
          this.downloadBase64Image(chartData, `${chartName}_chart.png`)
        }
      })
    },
    
    generateReportContent() {
      let report = 'VESSEL BASELINE PROFILE REPORT\n'
      report += '=' + '='.repeat(35) + '\n\n'
      
      if (this.executiveSummary) {
        report += 'EXECUTIVE SUMMARY\n'
        report += '-'.repeat(17) + '\n'
        report += `Vessel: ${this.executiveSummary.vessel_name || 'Unknown'}\n`
        report += `Type: ${this.executiveSummary.vessel_type || 'Unknown'}\n`
        report += `Specifications: ${this.executiveSummary.vessel_specifications || 'N/A'}\n`
        report += `Status: ${this.executiveSummary.baseline_status || 'Unknown'}\n\n`
      }
      
      if (this.keyFindings.length) {
        report += 'KEY FINDINGS\n'
        report += '-'.repeat(12) + '\n'
        this.keyFindings.forEach((finding, index) => {
          report += `${index + 1}. ${finding}\n`
        })
        report += '\n'
      }
      
      if (this.recommendations.length) {
        report += 'RECOMMENDATIONS\n'
        report += '-'.repeat(15) + '\n'
        this.recommendations.forEach((rec, index) => {
          report += `${index + 1}. ${rec}\n`
        })
        report += '\n'
      }
      
      report += `Generated: ${this.formatDateTime(this.createdAt)}\n`
      report += `Session ID: ${this.sessionId}\n`
      
      return report
    },
    
    downloadFile(content, filename, contentType) {
      const blob = new Blob([content], { type: contentType })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    
    downloadBase64Image(base64Data, filename) {
      const link = document.createElement('a')
      link.href = `data:image/png;base64,${base64Data}`
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    
    startNewWorkflow() {
      this.$emit('start-new-workflow')
    },
    
    shareResults() {
      // Copy session ID or results to clipboard
      if (navigator.clipboard) {
        const shareData = {
          sessionId: this.sessionId,
          summary: this.executiveSummary?.vessel_name + ' - Baseline Profile Complete',
          timestamp: this.formatDateTime(this.createdAt)
        }
        
        navigator.clipboard.writeText(JSON.stringify(shareData, null, 2))
          .then(() => alert('Results copied to clipboard'))
          .catch(() => alert('Failed to copy to clipboard'))
      } else {
        alert(`Session ID: ${this.sessionId}`)
      }
    }
  }
}
</script>

<style scoped>
.final-results {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.results-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
  border-radius: 15px;
}

.results-header h3 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.results-header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.executive-summary-section,
.charts-section,
.findings-section,
.recommendations-section,
.next-steps-section,
.export-section,
.workflow-summary {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.executive-summary-section h4,
.charts-section h4,
.findings-section h4,
.recommendations-section h4,
.next-steps-section h4,
.export-section h4,
.workflow-summary h4 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 1.5rem;
}

.vessel-overview {
  margin-bottom: 1.5rem;
}

.vessel-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.vessel-header h5 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin: 0;
}

.vessel-type {
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.vessel-specs {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  border-top: 3px solid #3498db;
}

.metric-label {
  display: block;
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.metric-value {
  display: block;
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
}

.status-badge {
  background: #27ae60;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-card h5 {
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.chart-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-placeholder {
  color: #7f8c8d;
  font-style: italic;
  text-align: center;
}

.findings-list,
.recommendations-list,
.next-steps-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.finding-item,
.recommendation-item,
.next-step-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.finding-number,
.step-number {
  background: #3498db;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.recommendation-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.finding-text,
.recommendation-text,
.step-text {
  color: #2c3e50;
  line-height: 1.5;
}

.export-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.export-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.csv-btn {
  background: #27ae60;
  color: white;
}

.report-btn {
  background: #3498db;
  color: white;
}

.charts-btn {
  background: #f39c12;
  color: white;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-label {
  color: #7f8c8d;
  font-weight: 600;
}

.stat-value {
  color: #2c3e50;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 3rem;
}

.action-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.secondary-btn {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
</style>