import fetch from "node-fetch";

const API_KEY = process.env.GOOGLE_API_KEY; // or paste your key directly (not recommended)

async function listModels() {
  const res = await fetch("https://generativelanguage.googleapis.com/v1beta2/models", {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  });

  console.log("Status:", res.status);
  const raw = await res.text();
  console.log("Response body:", raw);
}

listModels();
