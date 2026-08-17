import { useState } from 'react'
import PaperUpload from './components/PaperUpload'
import PaperList from './components/PaperList'
import QAPanel from './components/QAPanel'
import PaperInsights from './components/PaperInsights'
import MultiPaperTools from './components/MultiPaperTools'

function App() {
  const [papers, setPapers] = useState([])
  const [selectedPaperId, setSelectedPaperId] = useState(null)

  const handleUploadSuccess = (paperData) => {
    setPapers((prev) => {
      const exists = prev.some((p) => p.paper_id === paperData.paper_id)
      return exists ? prev : [...prev, paperData]
    })
  }

  const handleSelectPaper = (paperId) => {
    setSelectedPaperId((prev) => (prev === paperId ? null : paperId))
  }

  const selectedPaper = papers.find((p) => p.paper_id === selectedPaperId)

  return (
    <div className="app-container">
      <h1>AI Research Platform</h1>

      <div className="layout">
        <div className="sidebar">
          <PaperUpload onUploadSuccess={handleUploadSuccess} />
          <PaperList
            papers={papers}
            selectedPaperId={selectedPaperId}
            onSelectPaper={handleSelectPaper}
          />
        </div>

        <div className="main-content">
          <QAPanel
            selectedPaperId={selectedPaperId}
            selectedPaperTitle={selectedPaper?.title}
          />
          <PaperInsights
            paperId={selectedPaperId}
            paperTitle={selectedPaper?.title}
          />
          <MultiPaperTools papers={papers} />
        </div>
      </div>
    </div>
  )
}

export default App