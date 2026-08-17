function PaperList({ papers, selectedPaperId, onSelectPaper }) {
  if (papers.length === 0) {
    return <p className="muted">No papers uploaded yet.</p>
  }

  return (
    <div className="paper-list">
      <h2>Your Papers ({papers.length})</h2>
      <ul>
        {papers.map((p) => (
          <li
            key={p.paper_id}
            onClick={() => onSelectPaper(p.paper_id)}
            className={p.paper_id === selectedPaperId ? 'paper-item selected' : 'paper-item'}
          >
            <strong>{p.title || p.filename}</strong>
            <span className="muted"> — {p.num_pages} pages</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default PaperList