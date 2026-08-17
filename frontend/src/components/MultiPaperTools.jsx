import { useState } from 'react'
import { comparePapers, getRelationships, generateLiteratureReview } from '../api'


function MultiPaperTools({ papers }) {
  const [mode, setMode] = useState('compare')
  const [selectedIds, setSelectedIds] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const toggleSelection = (paperId) => {
    setSelectedIds((prev) =>
      prev.includes(paperId) ? prev.filter((id) => id !== paperId) : [...prev, paperId]
    )
    setResult(null)  // clear stale results when the selection changes
  }

  const handleRun = async () => {
    setLoading(true)
    setResult(null)

    try {
      let response
      if (mode === 'compare') {
        if (selectedIds.length !== 2) {
          setResult({ error: 'Select exactly 2 papers to compare.' })
          setLoading(false)
          return
        }
        response = await comparePapers(selectedIds[0], selectedIds[1])
        setResult({ text: response.data.comparison })
      } else if (mode === 'relationships') {
        if (selectedIds.length !== 1) {
          setResult({ error: 'Select exactly 1 paper to find related papers.' })
          setLoading(false)
          return
        }
        response = await getRelationships(selectedIds[0])
        setResult({ text: response.data.explanation, related: response.data.related_papers })
      } else if (mode === 'litreview') {
        response = await generateLiteratureReview(selectedIds.length > 0 ? selectedIds : null)
        setResult({ text: response.data.literature_review })
      }
    } catch (error) {
      setResult({ error: 'Something went wrong running this analysis.' })
    } finally {
      setLoading(false)
    }
  }

  if (papers.length < 2) {
    return (
      <div className="multi-tools">
        <p className="muted">Upload at least 2 papers to use comparison, relationships, or literature review tools.</p>
      </div>
    )
  }

  return (
    <div className="multi-tools">
      <h2>Multi-Paper Tools</h2>

      <div className="tabs">
        <button className={mode === 'compare' ? 'tab active' : 'tab'} onClick={() => { setMode('compare'); setResult(null) }}>Compare</button>
        <button className={mode === 'relationships' ? 'tab active' : 'tab'} onClick={() => { setMode('relationships'); setResult(null) }}>Relationships</button>
        <button className={mode === 'litreview' ? 'tab active' : 'tab'} onClick={() => { setMode('litreview'); setResult(null) }}>Literature Review</button>
      </div>

      <p className="muted">
        {mode === 'compare' && 'Select exactly 2 papers.'}
        {mode === 'relationships' && 'Select exactly 1 paper.'}
        {mode === 'litreview' && 'Select papers to include, or none to use all.'}
      </p>

      <div className="checkbox-list">
        {papers.map((p) => (
          <label key={p.paper_id} className="checkbox-item">
            <input
              type="checkbox"
              checked={selectedIds.includes(p.paper_id)}
              onChange={() => toggleSelection(p.paper_id)}
            />
            {p.title || p.filename}
          </label>
        ))}
      </div>

      <button onClick={handleRun} disabled={loading}>
        {loading ? 'Running...' : 'Run'}
      </button>

      {result && (
        <div className="qa-result">
          {result.error ? (
            <p className="error-text">{result.error}</p>
          ) : (
            <>
              <p>{result.text}</p>
              {result.related && (
                <p className="muted">Related paper IDs: {result.related.join(', ')}</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default MultiPaperTools