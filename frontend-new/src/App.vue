<script setup lang="ts">
import { ref } from 'vue'

interface FileItem {
  file: File;
  score?: number;
  transcript?: string;
}

const files = ref<FileItem[]>([])
const standardAnswer = ref('')
const submitBtnDisabled = ref(true)
const fileInput = ref<HTMLInputElement | null>(null)

const handleFiles = (newFiles: FileList | null) => {
  if (!newFiles) return
  Array.from(newFiles).forEach(file => {
    if (file.type === 'audio/mp3' || file.name.endsWith('.mp3')) {
      files.value.push({ file })
    }
  })
  updateSubmitButton()
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
  updateSubmitButton()
}

const updateSubmitButton = () => {
  submitBtnDisabled.value = files.value.length === 0 || !standardAnswer.value.trim()
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  const dropZone = e.currentTarget as HTMLElement
  if (dropZone) {
    dropZone.style.borderColor = '#1890ff'
    dropZone.style.backgroundColor = '#f0f7ff'
  }
}

const handleDragLeave = (e: DragEvent) => {
  const dropZone = e.currentTarget as HTMLElement
  if (dropZone) {
    dropZone.style.borderColor = '#d9d9d9'
    dropZone.style.backgroundColor = '#fafafa'
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  const dropZone = e.currentTarget as HTMLElement
  if (dropZone) {
    dropZone.style.borderColor = '#d9d9d9'
    dropZone.style.backgroundColor = '#fafafa'
  }
  handleFiles(e.dataTransfer?.files || null)
}

const submitScore = async () => {
  const formData = new FormData()
  files.value.forEach(item => {
    formData.append('files', item.file)
  })
  formData.append('standard_answer', standardAnswer.value.trim())

  try {
    submitBtnDisabled.value = true
    const response = await fetch('http://localhost:5000/api/process', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) throw new Error('评分请求失败')

    const results = await response.json()
    updateScores(results)
  } catch (error) {
    alert('评分失败：' + (error as Error).message)
  } finally {
    submitBtnDisabled.value = false
  }
}

const updateScores = (results: Array<{ score: number; transcript: string }>) => {
  results.forEach((result, index) => {
    if (index < files.value.length) {
      const score = result.score * 100
      files.value[index].score = score
      files.value[index].transcript = result.transcript
    }
  })
}

const getScoreClass = (score: number | undefined) => {
  if (!score) return ''
  if (score >= 80) return 'high'
  if (score >= 50) return 'medium'
  return 'low'
}
</script>

<template>
  <div class="container">
    <h1>语音相似度评分系统</h1>

    <div class="standard-answer">
      <textarea
        v-model="standardAnswer"
        placeholder="请输入标准答案..."
        @input="updateSubmitButton"
      ></textarea>
    </div>

    <div
      class="file-upload"
      @click="fileInput?.click()"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <input
        type="file"
        ref="fileInput"
        multiple
        accept=".mp3"
        @change="(e) => handleFiles((e.target as HTMLInputElement).files)"
      >
      <p>点击或拖拽MP3文件到此处上传</p>
    </div>

    <div class="file-list">
      <div v-for="(item, index) in files" :key="index" class="file-item">
        <div class="file-header">
          <button
            class="delete-btn"
            @click="removeFile(index)"
          >×</button>
          <div class="file-name">
            <span class="label">文件名：</span>{{ item.file.name }}
          </div>
          <div
            v-if="item.score !== undefined"
            class="file-score"
            :class="getScoreClass(item.score)"
          >
            {{ item.score.toFixed(2) }}%
          </div>
        </div>
        <div class="file-transcript">
          <span class="label">转录结果：</span>{{ item.transcript || '' }}
        </div>
      </div>
    </div>

    <button
      class="submit-btn"
      :disabled="submitBtnDisabled"
      @click="submitScore"
    >
      提交评分
    </button>
  </div>
</template>

<style>
@import './assets/base.css';
@import './assets/layout.css';
@import './assets/components.css';
</style>
