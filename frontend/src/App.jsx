import React, { useState } from 'react';
import { submitCodeReview } from './api';

const SAMPLE_CODE = `def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)
`;

export default function App() {
  const [code, setCode] = useState(SAMPLE_CODE);
  const [language, setLanguage] = useState('python');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleReview = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await submitCodeReview(code, language);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>AI Code Review Assistant</h1>
          <p style={styles.subtitle}>
            Automated code quality, security analysis, and optimization suggestions
          </p>
        </div>
        <div style={styles.badge}>FastAPI + Vite React</div>
      </header>

      {/* Main Grid */}
      <main style={styles.grid}>
        {/* Left Column: Code Input */}
        <section style={styles.card}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Source Code</span>
            <div style={styles.selectWrapper}>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={styles.select}
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
              </select>
            </div>
          </div>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            style={styles.textarea}
            spellCheck="false"
            placeholder="Paste your code here..."
          />

          <button
            onClick={handleReview}
            disabled={loading || !code.trim()}
            style={{
              ...styles.button,
              opacity: loading || !code.trim() ? 0.6 : 1,
              cursor: loading || !code.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Analyzing Code...' : 'Run Review'}
          </button>
        </section>

        {/* Right Column: Review Results */}
        <section style={styles.card}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Analysis Findings</span>
            {result?.summary && (
              <span style={styles.statusBadge}>Ready</span>
            )}
          </div>

          <div style={styles.resultContainer}>
            {loading && (
              <div style={styles.centerMessage}>
                <div style={styles.spinner} />
                <p style={{ marginTop: '14px', color: '#64748b' }}>
                  Evaluating syntax, security vulnerabilities, and logic flaws...
                </p>
              </div>
            )}

            {error && (
              <div style={styles.errorBox}>
                <strong>Review Failed:</strong> {error}
              </div>
            )}

            {!loading && !error && !result && (
              <div style={styles.centerMessage}>
                <p style={{ color: '#94a3b8' }}>
                  Click <strong>Run Review</strong> to inspect your code snippet.
                </p>
              </div>
            )}

            {!loading && result && (
              <div style={styles.resultsContent}>
                {/* Summary */}
                {result.summary && (
                  <div style={styles.summaryBox}>
                    <h3 style={styles.summaryHeading}>Executive Summary</h3>
                    <p style={styles.summaryText}>{result.summary}</p>
                  </div>
                )}

                {/* Issues List */}
                <h3 style={styles.issuesHeading}>
                  Findings ({result.findings?.length || 0})
                </h3>

                {(!result.findings || result.findings.length === 0) ? (
                  <p style={{ color: '#16a34a', fontSize: '14px' }}>
                    No critical issues found in this snippet.
                  </p>
                ) : (
                  result.findings.map((finding, idx) => (
                    <div key={idx} style={styles.findingCard}>
                      <div style={styles.findingHeader}>
                        <span
                          style={{
                            ...styles.severityTag,
                            backgroundColor: getSeverityColor(finding.severity),
                          }}
                        >
                          {finding.severity || 'INFO'}
                        </span>
                        <span style={styles.findingCategory}>
                          {finding.category || 'Quality'}
                        </span>
                        {finding.line && (
                          <span style={styles.lineTag}>Line {finding.line}</span>
                        )}
                      </div>
                      <p style={styles.findingMessage}>{finding.message}</p>
                      {finding.suggestion && (
                        <div style={styles.suggestionBox}>
                          <span style={styles.suggestionLabel}>Suggestion:</span>
                          <span style={styles.suggestionText}>
                            {finding.suggestion}
                          </span>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function getSeverityColor(severity) {
  switch ((severity || '').toLowerCase()) {
    case 'error':
    case 'critical':
    case 'high':
      return '#ef4444';
    case 'warning':
    case 'medium':
      return '#f59e0b';
    case 'info':
    case 'low':
      return '#3b82f6';
    default:
      return '#64748b';
  }
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '24px',
    boxSizing: 'border-box',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1300px',
    margin: '0 auto 24px auto',
    paddingBottom: '16px',
    borderBottom: '1px solid #1e293b',
  },
  title: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#f8fafc',
    margin: '0 0 4px 0',
  },
  subtitle: {
    fontSize: '14px',
    color: '#94a3b8',
    margin: 0,
  },
  badge: {
    backgroundColor: '#1e293b',
    border: '1px solid #334155',
    padding: '6px 12px',
    borderRadius: '6px',
    fontSize: '12px',
    color: '#38bdf8',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '24px',
    maxWidth: '1300px',
    margin: '0 auto',
  },
  card: {
    backgroundColor: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh - 160px)',
    overflow: 'hidden',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid #334155',
    backgroundColor: '#1e293b',
  },
  cardTitle: {
    fontWeight: '600',
    fontSize: '14px',
    color: '#f8fafc',
  },
  selectWrapper: {
    display: 'flex',
    alignItems: 'center',
  },
  select: {
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    border: '1px solid #475569',
    borderRadius: '4px',
    padding: '4px 8px',
    fontSize: '12px',
  },
  textarea: {
    flex: 1,
    backgroundColor: '#0b1120',
    color: '#f1f5f9',
    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
    fontSize: '13px',
    padding: '16px',
    border: 'none',
    outline: 'none',
    resize: 'none',
    lineHeight: '1.5',
  },
  button: {
    margin: '12px 16px',
    padding: '10px 16px',
    backgroundColor: '#2563eb',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    fontWeight: '600',
    fontSize: '14px',
    transition: 'background-color 0.2s',
  },
  resultContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
  },
  centerMessage: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center',
  },
  spinner: {
    width: '32px',
    height: '32px',
    border: '3px solid #334155',
    borderTop: '3px solid #38bdf8',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  errorBox: {
    backgroundColor: '#451a1a',
    border: '1px solid #7f1d1d',
    color: '#fca5a5',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '13px',
  },
  resultsContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  summaryBox: {
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    padding: '12px 16px',
    borderRadius: '6px',
  },
  summaryHeading: {
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: '#94a3b8',
    margin: '0 0 6px 0',
  },
  summaryText: {
    fontSize: '13px',
    lineHeight: '1.5',
    margin: 0,
    color: '#f1f5f9',
  },
  issuesHeading: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#f8fafc',
    margin: '12px 0 6px 0',
  },
  findingCard: {
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    borderRadius: '6px',
    padding: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  findingHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  severityTag: {
    fontSize: '10px',
    fontWeight: '700',
    padding: '2px 6px',
    borderRadius: '4px',
    color: '#ffffff',
    textTransform: 'uppercase',
  },
  findingCategory: {
    fontSize: '12px',
    color: '#94a3b8',
  },
  lineTag: {
    fontSize: '11px',
    backgroundColor: '#1e293b',
    padding: '2px 6px',
    borderRadius: '4px',
    color: '#cbd5e1',
    marginLeft: 'auto',
  },
  findingMessage: {
    fontSize: '13px',
    lineHeight: '1.4',
    margin: 0,
    color: '#f8fafc',
  },
  suggestionBox: {
    display: 'flex',
    gap: '6px',
    fontSize: '12px',
    backgroundColor: '#1e293b',
    padding: '8px 10px',
    borderRadius: '4px',
    borderLeft: '3px solid #38bdf8',
  },
  suggestionLabel: {
    fontWeight: '600',
    color: '#38bdf8',
  },
  suggestionText: {
    color: '#cbd5e1',
  },
  statusBadge: {
    fontSize: '11px',
    backgroundColor: '#14532d',
    color: '#86efac',
    padding: '2px 8px',
    borderRadius: '12px',
  },
};