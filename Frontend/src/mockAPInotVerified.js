// frontend/src/mockApi.js
export async function verifyCallMock() {
  // Simulate network delay
  await new Promise((res) => setTimeout(res, 500))

  // Return a simulated response
  //{"trust_score": 91,  "status": "Verified Business",  "color": "green"}
  return {
    caller: "+34 600 123 456",
    recipient: "+34 600 987 654",
    trust_score: 10,
    status: "FRAUDLENT",
    details: {
      sim_status: "not stable ✖",
      device_match: "not matched ✖",
      location_match: "not matched ✖"
    }
  }
}