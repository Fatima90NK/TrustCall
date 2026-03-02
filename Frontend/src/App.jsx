import { useState } from "react"
import { verifyCallMock as verifyCallVerified } from "./mockApi"
import { verifyCallMock as verifyCallNotVerified } from "./mockAPInotVerified"
import "./App.css"

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const verifyCall = async () => {
    setLoading(true)
    setResult(null)

    const chosenVerifyCall =
      Date.now() % 2 === 0 ? verifyCallVerified : verifyCallNotVerified

    try {
      const data = await chosenVerifyCall()
      setResult(data)
    } catch (err) {
      console.error(err)
    }

    setLoading(false)
  }

  return (
    <div className="app">
      <div className="left-side">
        <h1>📞 TrustCall</h1>
        <p className="description">TrustCall is a network-level caller identity engine that verifies calls in real time and assigns a trust score before you answer.</p>
        <h3>Incoming Call Simulation</h3>
        <div className="caller-info">
        <p><strong>Caller:</strong> Santander Fraud Team</p>
        <p><strong>Number:</strong> +34 600 123 456</p>
      </div>
    </div>

      <div className="right-side">
        <div className="action-row">
          <button className="verify-btn" onClick={verifyCall} disabled={loading}>
            Verify Call
          </button>
          {loading && (
            <span className="loading" aria-live="polite">
              Verifying…
            </span>
          )}
        </div>

        <div className="result-section">
          <h2>Verification Result</h2>
          {loading && (
            <p className="result-placeholder">Checking call authenticity…</p>
          )}
          {!loading && result && (
            <>
              <p><strong>Trust Score:</strong> {result.trust_score}</p>
              <div className={`badge badge--${result.status === "VERIFIED" ? "verified" : "unverified"}`}>
                {result.status}
              </div>
              <div className="result-details">
                <p>SIM Status: {result.details.sim_status}</p>
                <p>Device Match: {result.details.device_match}</p>
                <p>Location Match: {result.details.location_match}</p>
              </div>
            </>
          )}
          {!loading && !result && (
            <p className="result-placeholder">No result yet. Click Verify Call to check.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
