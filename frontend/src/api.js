import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export const uploadPaper = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getPapers = () => api.get('/papers/')

export const askQuestion = (query, paperId = null) =>
  api.post('/qa/ask', { query, paper_id: paperId })

export const summarizePaper = (paperId) =>
  api.get(`/analysis/summarize/${paperId}`)

export const getMethodologyResults = (paperId) =>
  api.get(`/analysis/methodology-results/${paperId}`)

export const getCitations = (paperId) =>
  api.get(`/analysis/citations/${paperId}`)

export const comparePapers = (paperIdA, paperIdB) =>
  api.post('/analysis/compare', { paper_id_a: paperIdA, paper_id_b: paperIdB })

export const getRelationships = (paperId) =>
  api.get(`/analysis/relationships/${paperId}`)

export const generateLiteratureReview = (paperIds = null) =>
  api.post('/analysis/literature-review', { paper_ids: paperIds })

export default api