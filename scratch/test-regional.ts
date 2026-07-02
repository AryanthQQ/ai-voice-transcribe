async function testRegionalAbuses() {
  console.log("🚀 Testing Regional Abusive Words API...");

  const payload = {
    calls: [
      {
        user_id: "USR-PUN",
        advisor_id: "ADV-01",
        transcript: "Oye pancho ki haal hai tera fuddu"
      },
      {
        user_id: "USR-MAR",
        advisor_id: "ADV-02",
        transcript: "Kay re zavadya aai zavun takel"
      },
      {
        user_id: "USR-BEN",
        advisor_id: "ADV-03",
        transcript: "Tui ekta bokachoda shala"
      },
      {
        user_id: "USR-SOUTH",
        advisor_id: "ADV-04",
        transcript: "punda mavane thevidiya"
      },
      {
        user_id: "USR-TYPO",
        advisor_id: "ADV-05",
        transcript: "tu ek number ka bkl aur mdrc hai"
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
    console.dir(data, { depth: null });
  } catch (error) {
    console.error("❌ Test Failed:", error);
  }
}

testRegionalAbuses();
