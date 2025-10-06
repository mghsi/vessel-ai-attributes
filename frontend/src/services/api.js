import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
    baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5001',
    timeout: 30000, // 30 seconds timeout for image analysis
    headers: {
        'Content-Type': 'multipart/form-data'
    }
})

// Request interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
        return config
    },
    (error) => {
        console.error('Request error:', error)
        return Promise.reject(error)
    }
)

// Response interceptor
api.interceptors.response.use(
    (response) => {
        console.log('API Response:', response.status, response.data)
        return response
    },
    (error) => {
        console.error('API Error:', error.response?.status, error.response?.data)

        // Handle different error scenarios
        if (error.response) {
            // Server responded with error status
            return Promise.reject(error)
        } else if (error.request) {
            // Request was made but no response received
            const networkError = {
                response: {
                    data: {
                        ERROR: 'Network error - Unable to connect to the server',
                        CODE: 'NET001'
                    }
                }
            }
            return Promise.reject(networkError)
        } else {
            // Something else happened
            const unknownError = {
                response: {
                    data: {
                        ERROR: 'An unexpected error occurred',
                        CODE: 'SYS001'
                    }
                }
            }
            return Promise.reject(unknownError)
        }
    }
)

// API endpoints
export const apiEndpoints = {
    health: '/api/v1/health',
    analyze: '/api/v1/analyze',
    
    // Agentic Workflow endpoints
    workflowStart: '/api/v1/workflow/start',
    workflowStep: '/api/v1/workflow/step',
    workflowStatus: '/api/v1/workflow/status',
    workflowExecute: '/api/v1/workflow/execute'
}

// Health check function
export const checkHealth = async () => {
    try {
        const response = await api.get(apiEndpoints.health)
        return response.data
    } catch (error) {
        throw error
    }
}

// Analyze boat image function
export const analyzeBoat = async (formData) => {
    try {
        const response = await api.post(apiEndpoints.analyze, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        return response.data
    } catch (error) {
        throw error
    }
}

// Agentic Workflow Functions

// Start a new agentic workflow
export const startAgenticWorkflow = async (workflowData) => {
    try {
        const response = await api.post(apiEndpoints.workflowStart, workflowData, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
        return response.data
    } catch (error) {
        throw error
    }
}

// Execute next step in workflow
export const executeWorkflowStep = async (sessionId) => {
    try {
        const response = await api.post(apiEndpoints.workflowStep, { session_id: sessionId }, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
        return response.data
    } catch (error) {
        throw error
    }
}

// Get workflow status
export const getWorkflowStatus = async (sessionId) => {
    try {
        const response = await api.get(`${apiEndpoints.workflowStatus}?session_id=${sessionId}`)
        return response.data
    } catch (error) {
        throw error
    }
}

// Execute complete workflow from start to finish
export const executeFullWorkflow = async (workflowData) => {
    try {
        const response = await api.post(apiEndpoints.workflowExecute, workflowData, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 120000 // 2 minutes timeout for full workflow
        })
        return response.data
    } catch (error) {
        throw error
    }
}

export default api