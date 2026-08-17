import { useState } from 'react'
import { uploadPaper } from '../api'

function PaperUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState(null)

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setStatus(null)

    try {
      const response = await uploadPaper(file)
      setStatus({ type: 'success', message: `${response.data.status}: ${response.data.title}` })
      onUploadSuccess(response.data)
    } catch (error) {
      setStatus({ type: 'error', message: 'Upload failed. Is the backend running?' })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-box">
      <h2>Upload a Paper</h2>
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {status && (
        <p className={status.type === 'error' ? 'error-text' : 'success-text'}>
          {status.message}
        </p>
      )}
    </div>
  )
}

export default PaperUpload