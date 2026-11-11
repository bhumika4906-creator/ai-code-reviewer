import { useState } from 'react';
import { submitCodeReview } from './api';

export default function App() {
  const [code, setCode] = useState('def divide(a, b):\n    return a / b\n');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await submitCodeReview(code);
      setResult(data);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 980, margin: '40px auto', padding: 20 }}>
      <h1>AI Code Reviewer</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={16}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 14, padding: 12 }}
        />
        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={loading}>
            {loading ? 'Reviewing...' : 'Review code'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ marginTop: 20, color: 'crimson' }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>Summary</h2>
          <p>{result.summary}</p>
          <ul>
            {result.findings.map((finding, index) => (
              <li key={`${finding.line}-${index}`}>
                <strong>Line {finding.line}</strong> · {finding.category} · {finding.severity}
                <div>{finding.description}</div>
                <div><em>Fix:</em> {finding.suggested_fix}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
