async function testBatchApi() {
  console.log("🚀 Testing Batch Processing API...");

  const payload = {
    calls: [
      {
        user_id: "USER-001",
        advisor_id: "ADV-001",
        transcript: "Hello, this is a very good and clean call without any issues."
      },
      {
        user_id: "USER-002",
        advisor_id: "ADV-002",
        transcript: "You are a chutiya! Also my number is nineight one two three four."
      },
      {
        user_id: "USER-003",
        advisor_id: "ADV-003",
        transcript: "Please note my alternative number ek do teen char panch che saat aath."
      }
    ]
  };

  try {
    const res = await fetch("http://localhost:3000/api/batch-analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    console.log("✅ Response Status:", res.status);
    console.dir(data, { depth: null });
  } catch (error) {
    console.error("❌ Test Failed:", error);
  }
}

testBatchApi();
