import { useRef, useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:4000'
const PROCESSING_DELAY_MS = 10000

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [status, setStatus] = useState('')
  const [phase, setPhase] = useState('idle') // 'idle' | 'processing' | 'done'
  const [results, setResults] = useState({ columns: [], rows: [] })
  const [summary, setSummary] = useState({ filename: null, content: '' })
  const timeoutRef = useRef(null)

  const loadResults = async () => {
    try {
      const res = await fetch(`${API_URL}/api/results`)
      const data = await res.json()
      setResults(data)
    } catch {
      // server not reachable yet; ignore
    }
  }

  const loadSummary = async () => {
    try {
      const res = await fetch(`${API_URL}/api/latest-summary`)
      const data = await res.json()
      setSummary(data)
    } catch {
      // server not reachable yet; ignore
    }
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
    setStatus('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) {
      setStatus('Please choose a file first.')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    setStatus('Uploading...')
    try {
      const res = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Upload failed')
      setStatus(`Uploaded: ${data.filename}`)
      setSelectedFile(null)
      e.target.reset()

      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      setPhase('processing')
      timeoutRef.current = setTimeout(async () => {
        await Promise.all([loadResults(), loadSummary()])
        setPhase('done')
      }, PROCESSING_DELAY_MS)
    } catch (err) {
      setStatus(`Error: ${err.message}`)
    }
  }

  return (
    <div
      style={{
        maxWidth: 800,
        width: '90%',
        boxSizing: 'border-box',
        margin: '4rem auto',
        fontFamily: 'sans-serif',
      }}
    >
      <h1>File Upload</h1>
      <form onSubmit={handleUpload}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" style={{ marginLeft: '1rem' }}>
          Upload
        </button>
      </form>
      {status && <p>{status}</p>}

      {phase === 'processing' && <p>Processing...</p>}

      {phase === 'done' && (
        <>
          <h2>Results</h2>
          {results.rows.length === 0 ? (
            <p>No results found.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                <thead>
                  <tr>
                    {results.columns.map((col) => (
                      <th
                        key={col}
                        style={{ border: '1px solid #ccc', padding: '4px 8px', textAlign: 'left' }}
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.rows.map((row, i) => (
                    <tr key={i}>
                      {results.columns.map((col) => (
                        <td key={col} style={{ border: '1px solid #ccc', padding: '4px 8px' }}>
                          {row[col]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <h2>Latest Summary</h2>
          {summary.filename ? (
            <>
              <p>
                <strong>{summary.filename}</strong>
              </p>
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  background: '#f5f5f5',
                  padding: '1rem',
                  borderRadius: '4px',
                }}
              >
                {summary.content}
              </pre>
            </>
          ) : (
            <p>No summaries found.</p>
          )}
        </>
      )}
    </div>
  )
}

export default App
