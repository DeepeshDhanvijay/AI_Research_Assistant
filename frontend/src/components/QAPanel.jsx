import { useState } from 'react'
import { askQuestion } from '../api'

function QAPanel({ selectedPaperId, selectedPaperTitle }) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
    if (!query.trim()) return

    setLoading(true)
    setResult(null)

    try {
      const response = await askQuestion(query, selectedPaperId)
      setResult(response.data)
    } catch (error) {
      setResult({ answer: 'Something went wrong asking that question.', sources: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="qa-panel">
      <h2>Ask a Question</h2>
      <p className="muted">
        {selectedPaperId
          ? `Scoped to: ${selectedPaperTitle}`
          : 'Searching across all papers (select a paper to scope your question)'}
      </p>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="What routing protocol does this paper use?"
        rows={3}
      />
      <button onClick={handleAsk} disabled={loading || !query.trim()}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      {result && (
        <div className="qa-result">
          <h3>Answer</h3>
          <p>{result.answer}</p>

          {result.sources?.length > 0 && (
            <details>
              <summary>{result.sources.length} sources used</summary>
              <ul>
                {result.sources.map((s) => (
                  <li key={s.chunk_id}>
                    <code>{s.paper_id}</code>: {s.text.slice(0, 100)}...
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </div>
  )
}

export default QAPanel