import { useState } from "react"
//TODO: Interesting the file reference dont need to be uppercase like the file.js
import { verifyCallMock as verifyCallVerified } from "./mockAPI"
import { verifyCallMock as verifyCallNotVerified } from "./mockAPInotVerified"


function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const verifyCall = async () => {
    setLoading(true)
    setResult(null)

    const chosenVerifyCall =
      Date.now() % 2 === 0 ? verifyCallVerified : verifyCallNotVerified

    try {
      // Call the mock API instead of real backend
      const data = await chosenVerifyCall()
      setResult(data)
    } catch (err) {
      console.error(err)
    }

    setLoading(false)
  }

  const getBadgeStyle = () => {
    console.log(result);
    if (!result) return {/* TODO: thinking component */}
    //TODO: badge component
    return {
      padding: "10px 20px",
      borderRadius: "8px",
      fontWeight: "bold",
      color: "white",
      backgroundColor: result.status === "VERIFIED" ? "#16a34a" : "#dc2626"
    }
  }

  return (
    <div style={{ fontFamily: "Arial", padding: "40px" }}>
      <h1>📞 TrustCall</h1>
      <h3>Incoming Call Simulation</h3>

      <div style={{ marginBottom: "20px" }}>
        <p><strong>Caller:</strong> Santander Fraud Team</p>
        <p><strong>Number:</strong> +34 600 123 456</p>
      </div>

      <button
        onClick={verifyCall}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer"
        }}
      >
        Verify Call
      </button>

      {loading && <p>Verifying...</p>}

      {result && (
        <div style={{ marginTop: "30px" }}>
          <h2>Verification Result</h2>
          <p><strong>Trust Score:</strong> {result.trust_score}</p>
          <div style={getBadgeStyle()}>
            {result.status}
          </div>
          <div style={{ marginTop: "10px" }}>
            <p>SIM Status: {result.details.sim_status}</p>
            <p>Device Match: {result.details.device_match}</p>
            <p>Location Match: {result.details.location_match}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
