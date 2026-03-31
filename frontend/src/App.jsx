import { useState } from 'react'
import './App.css'

const API_BASE = "http://localhost:8000/api/v1";

function App() {
  const [activeTab, setActiveTab] = useState("domains");
  const [searchQuery, setSearchQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const tabs = [
    { id: "domains", label: "Domain" },
    { id: "ips", label: "IP Address" },
    { id: "files", label: "File Hash" }
  ];

  const handleSearch = async (refresh = false) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);

    let endpoint = "";
    if (activeTab === "domains") endpoint = `/domains/${encodeURIComponent(searchQuery)}`;
    else if (activeTab === "ips") endpoint = `/ips/${encodeURIComponent(searchQuery)}`;
    else if (activeTab === "files") endpoint = `/files/${encodeURIComponent(searchQuery)}`;

    if (refresh) {
      endpoint += "?refresh=true";
    }

    try {
      const resp = await fetch(`${API_BASE}${endpoint}`);
      const json = await resp.json();
      if (json.error || resp.status !== 200) {
        setError(`Error: ${json.error || resp.status}. Could not find ${searchQuery}.`);
      } else {
        setData(json);
        updateHistory({ type: activeTab, query: searchQuery, time: new Date().toLocaleTimeString() });
      }
    } catch (err) {
      setError(`Failed to fetch: ${err.message}. Ensure backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const updateHistory = (item) => {
    setHistory(prev => {
      const filtered = prev.filter(h => h.query !== item.query || h.type !== item.type);
      return [item, ...filtered].slice(0, 6);
    });
  };

  const totalVotes = data ? (
    (data.malicious_count || 0) + (data.suspicious_count || 0) + (data.harmless_count || 0) + (data.undetected_count || 0)
  ) : 0;
  
  const getPercent = (count) => totalVotes > 0 ? ((count || 0) / totalVotes) * 100 : 0;

  return (
    <div className="app-container">
      <header>
        <h1>VT Threat Dashboard</h1>
        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => { setActiveTab(tab.id); setData(null); setError(null); setSearchQuery(""); }}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="search-section">
          <input
            type="text"
            className="search-input"
            placeholder={`Enter ${tabs.find(t=>t.id===activeTab).label}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-primary" onClick={() => handleSearch(false)}>Lookup</button>
          {data && <button className="btn btn-secondary" onClick={() => handleSearch(true)}>Refresh Data</button>}
        </div>
      </header>

      <main className="main-content">
        <div className="dashboard-panel">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Analyzing indicator...</p>
            </div>
          )}
          
          {error && <div className="error-card">{error}</div>}

          {data && !loading && !error && (
            <>
              <div className="results-header">
                <h2>{activeTab === 'domains' ? data.domain : activeTab === 'ips' ? data.ip_address : data.file_hash}</h2>
                <div className={`source-badge source-${data.source || 'default'}`}>
                  Source: {data.source}
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card stat-malicious">
                  <div className="stat-value">{data.malicious_count || 0}</div>
                  <div className="stat-label">Malicious</div>
                </div>
                <div className="stat-card stat-suspicious">
                  <div className="stat-value">{data.suspicious_count || 0}</div>
                  <div className="stat-label">Suspicious</div>
                </div>
                <div className="stat-card stat-harmless">
                  <div className="stat-value">{data.harmless_count || 0}</div>
                  <div className="stat-label">Harmless</div>
                </div>
                <div className="stat-card stat-undetected">
                  <div className="stat-value">{data.undetected_count || 0}</div>
                  <div className="stat-label">Undetected</div>
                </div>
              </div>

              <div className="chart-card">
                <h3 className="chart-title">Detection Breakdown</h3>
                {totalVotes > 0 ? (
                  <>
                    <div className="bar-chart-container">
                      {getPercent(data.malicious_count) > 0 && <div className="bar-segment bar-malicious" style={{ width: `${getPercent(data.malicious_count)}%` }}></div>}
                      {getPercent(data.suspicious_count) > 0 && <div className="bar-segment bar-suspicious" style={{ width: `${getPercent(data.suspicious_count)}%` }}></div>}
                      {getPercent(data.harmless_count) > 0 && <div className="bar-segment bar-harmless" style={{ width: `${getPercent(data.harmless_count)}%` }}></div>}
                      {getPercent(data.undetected_count) > 0 && <div className="bar-segment bar-undetected" style={{ width: `${getPercent(data.undetected_count)}%` }}></div>}
                    </div>
                    <div className="chart-legend">
                      <div className="legend-item"><div className="legend-color bar-malicious"></div> Malicious</div>
                      <div className="legend-item"><div className="legend-color bar-suspicious"></div> Suspicious</div>
                      <div className="legend-item"><div className="legend-color bar-harmless"></div> Harmless</div>
                      <div className="legend-item"><div className="legend-color bar-undetected"></div> Undetected</div>
                    </div>
                  </>
                ) : (
                  <p style={{ color: "var(--text-secondary)" }}>No vendor detections available.</p>
                )}
              </div>

              <table className="details-table">
                <tbody>
                  <tr>
                    <th>Reputation Score</th>
                    <td>{data.reputation !== undefined ? data.reputation : "N/A"}</td>
                  </tr>
                  <tr>
                    <th>Created At</th>
                    <td>{data.created_at ? new Date(data.created_at).toLocaleString() : "N/A"}</td>
                  </tr>
                  {activeTab === 'ips' && (
                    <>
                      <tr><th>ASN</th><td>{data.asn || "N/A"}</td></tr>
                      <tr><th>Owner</th><td>{data.as_owner || "N/A"}</td></tr>
                      <tr><th>Country</th><td>{data.country || "N/A"}</td></tr>
                    </>
                  )}
                  {activeTab === 'files' && (
                    <>
                      <tr><th>File Name</th><td>{data.file_name || "N/A"}</td></tr>
                      <tr><th>File Type</th><td>{data.file_type || "N/A"}</td></tr>
                      <tr><th>Size</th><td>{data.file_size ? `${(data.file_size/1024).toFixed(2)} KB` : "N/A"}</td></tr>
                      <tr><th>SHA-256</th><td>{data.sha256 || "N/A"}</td></tr>
                    </>
                  )}
                </tbody>
              </table>
            </>
          )}

          {!data && !loading && !error && (
            <div style={{ color: "var(--text-secondary)", textAlign: "center", padding: "4rem" }}>
              <h2>Waiting for Query</h2>
              <p style={{ marginTop: "1rem" }}>Select a resource type and enter an identifier above to begin analyzing.</p>
            </div>
          )}
        </div>

        <aside className="history-sidebar">
          <h3 className="history-title">Recent Lookups</h3>
          {history.length > 0 ? (
             <ul className="history-list">
              {history.map((h, i) => (
                <li key={i} className="history-item" onClick={() => {
                  setActiveTab(h.type);
                  setSearchQuery(h.query);
                }}>
                  <div className="history-query" title={h.query}>{h.query}</div>
                  <div className="history-type">{h.type.replace('s', '')}</div>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>No recent queries.</p>
          )}
        </aside>
      </main>
    </div>
  )
}

export default App
