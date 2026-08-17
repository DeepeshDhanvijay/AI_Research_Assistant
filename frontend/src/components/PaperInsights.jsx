import { useState } from 'react'
import { summarizePaper, getMethodologyResults, getCitations } from '../api'

const TABS = {
  summary: { label: 'Summary', fetcher: summarizePaper },
  methodology: { label: 'Methodology & Results', fetcher: getMethodologyResults },
  citations: { label: 'Citations', fetcher: getCitations },
}

function PaperInsights({ paperId, paperTitle }) {
  const [activeTab, setActiveTab] = useState(null)
  const [content, setContent] = useState({})
  const [loading, setLoading] = useState(false)

  const handleTabClick = async (tabKey) => {
    setActiveTab(tabKey)

    // Cache results per tab so switching back doesn't re-fetch unnecessarily
    if (content[tabKey]) return

    setLoading(true)
    try {
      const response = await TABS[tabKey].fetcher(paperId)
      setContent((prev) => ({ ...prev, [tabKey]: response.data }))
    } catch (error) {
      setContent((prev) => ({ ...prev, [tabKey]: { error: 'Failed to load.' } }))
    } finally {
      setLoading(false)
    }
  }

  if (!paperId) {
    return (
      <div className="paper-insights">
        <p className="muted">Select a paper to see summary, methodology, and citations.</p>
      </div>
    )
  }

  const renderTabContent = () => {
    if (!activeTab) return null
    const data = content[activeTab]
    if (loading) return <p className="muted">Loading...</p>
    if (!data) return null
    if (data.error) return <p className="error-text">{data.error}</p>

    if (activeTab === 'summary') return <p>{data.summary}</p>
    if (activeTab === 'methodology') return <p>{data.extraction}</p>
    if (activeTab === 'citations') {
      return <p>{data.citation_analysis || data.note}</p>
    }
    return null
  }

  return (
    <div className="paper-insights">
      <h2>{paperTitle}</h2>
      <div className="tabs">
        {Object.entries(TABS).map(([key, { label }]) => (
          <button
            key={key}
            className={activeTab === key ? 'tab active' : 'tab'}
            onClick={() => handleTabClick(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="tab-content">{renderTabContent()}</div>
    </div>
  )
}

export default PaperInsights