<template>
  <div class="image-uploader">
    <div 
      class="upload-area"
      :class="{ 
        'drag-over': dragOver,
        'has-image': previewUrl,
        'loading': loading
      }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="!loading && triggerFileInput()"
    >
      <input 
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Processing image...</p>
      </div>
      
      <div v-else-if="previewUrl" class="image-preview">
        <img :src="previewUrl" alt="Boat preview" />
        <div class="image-overlay">
          <button @click.stop="clearImage" class="clear-btn">
            ✕ Remove Image
          </button>
        </div>
      </div>
      
      <div v-else class="upload-prompt">
        <div class="upload-icon">📸</div>
        <h3>Upload Boat Image</h3>
        <p>Drag and drop an image here, or click to select</p>
        <small>Supported formats: JPG, PNG, GIF (Max: 10MB)</small>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      <strong>Error:</strong> {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUploader',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['image-selected', 'image-cleared'],
  data() {
    return {
      dragOver: false,
      previewUrl: null,
      selectedFile: null,
      error: null
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.processFile(file)
      }
    },
    
    handleDrop(event) {
      event.preventDefault()
      this.dragOver = false
      
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },
    
    handleDragOver(event) {
      event.preventDefault()
      this.dragOver = true
    },
    
    handleDragLeave() {
      this.dragOver = false
    },
    
    processFile(file) {
      this.error = null
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        this.error = 'Please select a valid image file'
        return
      }
      
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        this.error = 'Image size must be less than 10MB'
        return
      }
      
      this.selectedFile = file
      
      // Create preview URL
      const reader = new FileReader()
      reader.onload = (e) => {
        this.previewUrl = e.target.result
      }
      reader.readAsDataURL(file)
      
      // Emit the selected file
      this.$emit('image-selected', file)
    },
    
    clearImage() {
      this.selectedFile = null
      this.previewUrl = null
      this.error = null
      this.$refs.fileInput.value = ''
      this.$emit('image-cleared')
    }
  }
}
</script>

<style scoped>
.image-uploader {
  margin-bottom: 1rem;
}

.upload-area {
  border: 3px dashed #d0d0d0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover:not(.loading) {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-area.drag-over {
  border-color: #667eea;
  background: #e8f0ff;
  transform: scale(1.02);
}

.upload-area.has-image {
  padding: 0;
  border: none;
  background: transparent;
}

.upload-area.loading {
  cursor: not-allowed;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.image-preview {
  position: relative;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: contain;
  display: block;
}

.image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
}

.clear-btn {
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.clear-btn:hover {
  background: rgba(255, 0, 0, 1);
}

.upload-prompt {
  color: #666;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-prompt h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.upload-prompt p {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.upload-prompt small {
  color: #999;
  font-size: 0.9rem;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ffebee;
  border: 1px solid #e57373;
  border-radius: 8px;
  color: #c62828;
}
</style>