<template>
  <div class="agent-result">
    <div class="result-status" :class="result.status">
      <span class="status-indicator">
        {{ result.status === 'success' ? '✅' : '❌' }}
      </span>
      <span class="status-text">{{ getStatusText() }}</span>
    </div>

    <!-- Boat Image Analyzer Results -->
    <div v-if="agentName === 'BoatImageAnalyzer' && result.status === 'success'" class="result-content">
      <h5>Boat Specifications Identified:</h5>
      <div class="specs-grid">
        <div v-if="result.boat_specifications" class="spec-item">
          <strong>Analysis Method:</strong> {{ result.analysis_method || 'AI Analysis' }}
        </div>
        <div v-if="result.boat_specifications?.['Boat Type']" class="spec-item">
          <strong>Boat Type:</strong> {{ result.boat_specifications['Boat Type'] }}
        </div>
        <div v-if="result.boat_specifications?.Length" class="spec-item">
          <strong>Length:</strong> {{ result.boat_specifications.Length }}
        </div>
        <div v-if="result.boat_specifications?.Beam" class="spec-item">
          <strong>Beam:</strong> {{ result.boat_specifications.Beam }}
        </div>
        <div v-if="result.boat_specifications?.Commercial" class="spec-item">
          <strong>Commercial Use:</strong> {{ result.boat_specifications.Commercial }}
        </div>
      </div>
      
      <div v-if="result.suggestions_for_review" class="suggestions">
        <h6>Review Suggestions:</h6>
        <ul>
          <li v-for="suggestion in result.suggestions_for_review" :key="suggestion">
            {{ suggestion }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Boat Profile Builder Results -->
    <div v-if="agentName === 'BoatProfileBuilder' && result.status === 'success'" class="result-content">
      <h5>Normalized Vessel Profile Created:</h5>
      
      <div v-if="result.normalized_profile" class="profile-sections">
        <div class="profile-section">
          <h6>Vessel Identity:</h6>
          <div class="profile-data">
            <div v-for="(value, key) in result.normalized_profile.vessel_identity" :key="key">
              <strong>{{ formatKey(key) }}:</strong> {{ value || 'Not specified' }}
            </div>
          </div>
        </div>
        
        <div class="profile-section">
          <h6>Physical Specifications:</h6>
          <div class="profile-data">
            <div v-for="(value, key) in result.normalized_profile.physical_specifications" :key="key">
              <strong>{{ formatKey(key) }}:</strong> {{ value || 'Not specified' }}
            </div>
          </div>
        </div>
        
        <div class="profile-section">
          <h6>Operational Profile:</h6>
          <div class="profile-data">
            <div v-for="(value, key) in result.normalized_profile.operational_profile" :key="key">
              <strong>{{ formatKey(key) }}:</strong> {{ formatValue(value) }}
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="result.profile_attributes" class="attributes-summary">
        <h6>Key Attributes:</h6>
        <div class="attributes-grid">
          <div v-for="attr in result.profile_attributes" :key="attr.name" class="attribute-tag">
            <span class="attr-category">{{ attr.category }}</span>
            <span class="attr-name">{{ attr.name }}:</span>
            <span class="attr-value">{{ attr.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Curve Generator Results -->
    <div v-if="agentName === 'PerformanceCurveGenerator' && result.status === 'success'" class="result-content">
      <h5>Performance Curves Generated:</h5>
      
      <div class="curves-summary">
        <div v-if="result.performance_curves" class="curve-list">
          <div v-for="(curve, curveName) in result.performance_curves" :key="curveName" class="curve-item">
            <h6>{{ formatCurveName(curveName) }}</h6>
            <div class="curve-info">
              <span><strong>X-Axis:</strong> {{ curve.x_axis?.label }}</span>
              <span><strong>Y-Axis:</strong> {{ curve.y_axis?.label }}</span>
              <span><strong>Data Points:</strong> {{ curve.data_points?.length || 0 }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="result.validation_notes" class="validation-notes">
          <h6>Important Notes:</h6>
          <ul>
            <li v-for="note in result.validation_notes" :key="note">{{ note }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Telemetry Data Processor Results -->
    <div v-if="agentName === 'TelemetryDataProcessor' && result.status === 'success'" class="result-content">
      <h5>Telemetry Data Processing Complete:</h5>
      
      <div class="telemetry-summary">
        <div v-if="result.telemetry_summary" class="summary-stats">
          <div class="stat-item">
            <strong>Total Data Points:</strong> {{ result.telemetry_summary.total_data_points?.toLocaleString() }}
          </div>
          <div class="stat-item">
            <strong>Voyage Count:</strong> {{ result.telemetry_summary.voyage_count }}
          </div>
          <div class="stat-item">
            <strong>Dwell Periods:</strong> {{ result.telemetry_summary.dwell_periods }}
          </div>
          <div v-if="result.telemetry_summary.date_range" class="stat-item">
            <strong>Data Period:</strong> 
            {{ formatDate(result.telemetry_summary.date_range.start) }} - 
            {{ formatDate(result.telemetry_summary.date_range.end) }}
          </div>
        </div>
        
        <div v-if="result.voyage_statistics" class="voyage-stats">
          <h6>Voyage Statistics:</h6>
          <div class="stats-grid">
            <div v-if="result.voyage_statistics.away_from_dock" class="stat-section">
              <h7>Away from Dock:</h7>
              <ul>
                <li>Average Duration: {{ result.voyage_statistics.away_from_dock.avg_duration_hours?.toFixed(1) }} hours</li>
                <li>Average Distance: {{ result.voyage_statistics.away_from_dock.avg_distance_nm?.toFixed(1) }} nm</li>
                <li>Average Speed: {{ result.voyage_statistics.away_from_dock.avg_speed_knots?.toFixed(1) }} knots</li>
              </ul>
            </div>
            <div v-if="result.voyage_statistics.at_dock" class="stat-section">
              <h7>At Dock:</h7>
              <ul>
                <li>Average Dwell: {{ result.voyage_statistics.at_dock.avg_dwell_duration_hours?.toFixed(1) }} hours</li>
                <li>Total Dwell Time: {{ result.voyage_statistics.at_dock.total_dwell_hours?.toFixed(1) }} hours</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Voyage Analytics Engine Results -->
    <div v-if="agentName === 'VoyageAnalyticsEngine' && result.status === 'success'" class="result-content">
      <h5>Voyage Analytics Complete:</h5>
      
      <div class="analytics-summary">
        <div v-if="result.voyage_analytics?.aggregate_totals" class="totals-section">
          <h6>Operational Totals:</h6>
          <div class="totals-grid">
            <div class="total-item">
              <span class="total-label">Total Fuel</span>
              <span class="total-value">{{ result.voyage_analytics.aggregate_totals.total_fuel_gallons }} gal</span>
            </div>
            <div class="total-item">
              <span class="total-label">Total Distance</span>
              <span class="total-value">{{ result.voyage_analytics.aggregate_totals.total_distance_nm?.toFixed(1) }} nm</span>
            </div>
            <div class="total-item">
              <span class="total-label">Operating Hours</span>
              <span class="total-value">{{ result.voyage_analytics.aggregate_totals.total_operating_hours?.toFixed(1) }} hrs</span>
            </div>
            <div class="total-item">
              <span class="total-label">CO₂ Emissions</span>
              <span class="total-value">{{ result.voyage_analytics.aggregate_totals.total_co2_lbs?.toFixed(1) }} lbs</span>
            </div>
          </div>
        </div>
        
        <div v-if="result.emissions_summary" class="emissions-section">
          <h6>Environmental Impact:</h6>
          <div class="emissions-data">
            <div class="emission-item">
              <strong>Total CO₂:</strong> {{ result.emissions_summary.total_co2_emissions_tons }} tons
            </div>
            <div v-if="result.emissions_summary.fuel_breakdown_percentage" class="breakdown">
              <strong>Fuel Breakdown:</strong>
              <span>{{ result.emissions_summary.fuel_breakdown_percentage.operational }}% Operational, </span>
              <span>{{ result.emissions_summary.fuel_breakdown_percentage.auxiliary }}% Auxiliary</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Chart Generator Results -->
    <div v-if="agentName === 'ReportChartGenerator' && result.status === 'success'" class="result-content">
      <h5>Comprehensive Report Generated:</h5>
      
      <div class="report-summary">
        <div v-if="result.executive_summary" class="executive-summary">
          <h6>Executive Summary:</h6>
          <div class="summary-data">
            <div><strong>Vessel:</strong> {{ result.executive_summary.vessel_name }} ({{ result.executive_summary.vessel_type }})</div>
            <div><strong>Specifications:</strong> {{ result.executive_summary.vessel_specifications }}</div>
            <div><strong>Status:</strong> {{ result.executive_summary.baseline_status }}</div>
          </div>
        </div>
        
        <div v-if="result.deliverables" class="deliverables-checklist">
          <h6>Deliverables Completed:</h6>
          <div class="checklist">
            <div v-for="(completed, deliverable) in result.deliverables" :key="deliverable" class="checklist-item">
              <span class="check-icon">{{ completed ? '✅' : '❌' }}</span>
              <span>{{ formatDeliverable(deliverable) }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="result.charts" class="charts-info">
          <h6>Generated Charts:</h6>
          <div class="chart-list">
            <div v-for="(chartData, chartName) in result.charts" :key="chartName" class="chart-item">
              {{ formatChartName(chartName) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="result.status === 'failed'" class="error-content">
      <h5>Agent Error:</h5>
      <div class="error-message">{{ result.error }}</div>
      <div v-if="result.code" class="error-code">Code: {{ result.code }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AgentResultDisplay',
  props: {
    agentName: {
      type: String,
      required: true
    },
    result: {
      type: Object,
      required: true
    }
  },
  methods: {
    getStatusText() {
      return this.result.status === 'success' ? 'Completed Successfully' : 'Failed'
    },
    
    formatKey(key) {
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatValue(value) {
      if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No'
      }
      return value || 'Not specified'
    },
    
    formatCurveName(name) {
      const names = {
        'speed_vs_fuel_rate': 'Speed vs Fuel Rate',
        'speed_vs_shaft_power': 'Speed vs Shaft Power',
        'speed_vs_thrust': 'Speed vs Thrust',
        'acceleration_vs_power': 'Acceleration vs Power'
      }
      return names[name] || name
    },
    
    formatDate(dateString) {
      try {
        return new Date(dateString).toLocaleDateString()
      } catch {
        return dateString
      }
    },
    
    formatDeliverable(deliverable) {
      const names = {
        'baseline_profile_complete': 'Baseline Profile Complete',
        'performance_curves_generated': 'Performance Curves Generated',
        'voyage_analytics_complete': 'Voyage Analytics Complete',
        'emissions_calculated': 'Emissions Calculated',
        'frontend_compatible': 'Frontend Compatible Format'
      }
      return names[deliverable] || deliverable.replace(/_/g, ' ')
    },
    
    formatChartName(chartName) {
      const names = {
        'performance_curves': 'Performance Curves Charts',
        'voyage_analytics': 'Voyage Analytics Charts',
        'emissions_breakdown': 'Emissions Breakdown Chart'
      }
      return names[chartName] || chartName.replace(/_/g, ' ')
    }
  }
}
</script>

<style scoped>
.agent-result {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 4px;
}

.result-status.success {
  background: #d4edda;
  color: #155724;
}

.result-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.status-indicator {
  font-size: 1.2rem;
}

.result-content h5 {
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.result-content h6 {
  color: #34495e;
  margin: 1rem 0 0.5rem 0;
  font-size: 1rem;
}

.result-content h7 {
  color: #5a6c7d;
  margin: 0.5rem 0 0.25rem 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.spec-item {
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid #3498db;
}

.profile-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.profile-section {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #2ecc71;
}

.profile-data {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.attributes-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.attribute-tag {
  background: #e3f2fd;
  padding: 0.25rem 0.5rem;
  border-radius: 15px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.attr-category {
  background: #1976d2;
  color: white;
  padding: 0.1rem 0.3rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
}

.curve-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.curve-item {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #f39c12;
}

.curve-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.totals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.total-item {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  text-align: center;
  border-top: 3px solid #e74c3c;
}

.total-label {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 0.25rem;
}

.total-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.stat-section {
  background: white;
  padding: 1rem;
  border-radius: 6px;
}

.stat-section ul {
  margin-top: 0.5rem;
  padding-left: 1rem;
}

.stat-section li {
  margin-bottom: 0.25rem;
}

.checklist {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem;
}

.check-icon {
  font-size: 1.1rem;
}

.suggestions ul,
.validation-notes ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.suggestions li,
.validation-notes li {
  margin-bottom: 0.5rem;
  color: #34495e;
}

.error-content {
  background: #fff3cd;
  border: 1px solid #fecba1;
  border-radius: 6px;
  padding: 1rem;
}

.error-message {
  color: #856404;
  margin-bottom: 0.5rem;
}

.error-code {
  color: #6c757d;
  font-size: 0.9rem;
}
</style>