import fs from "fs";

async function test() {
  const formData = new FormData();
  formData.append("user_id", "USR-001");
  formData.append("advisor_id", "ADV-002");
  formData.append("transcript", "n i n e e i g h t o n e s e v e n t w o");

  const res = await fetch("http://localhost:3000/api/analyze-call", {
    method: "POST",
    body: formData,
  });

  const json = await res.json();
  console.log(JSON.stringify(json, null, 2));
}

test();
