// frontend/src/mockApi.js
export async function verifyCallMock() {
  // Simulate network delay
  await new Promise((res) => setTimeout(res, 500))

  // Return a simulated response
  return {
    caller: "+34 600 123 456",
    recipient: "+34 600 987 654",
    trust_score: 91,
    status: "VERIFIED",
    details: {
      sim_status: "Stable ✔",
      device_match: "Yes ✔",
      location_match: "Yes ✔"
    }
  }
}