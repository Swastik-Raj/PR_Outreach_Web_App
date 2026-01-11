/*
import { GoogleAuth } from "google-auth-library";

const keyFile = "C:/Users/swast/Projects/PR_Outreach-App/backend/keys/gen-lang-client-0595573539-c04e97ff1c9f.json";

const auth = new GoogleAuth({
  keyFile,
  scopes: ["https://www.googleapis.com/auth/ai.generativelanguage"]
});

(async () => {
  try {
    const client = await auth.getClient();
    const token = await client.getAccessToken();
    console.log("Access token generated:", token.token);
  } catch (err) {
    console.error("Failed to get access token:", err);
  }
})();
*/
import fs from "fs";

const keyFile = "C:/Users/swast/Projects/PR_Outreach-App/backend/keys/gen-lang-client-0595573539-c04e97ff1c9f.json";

if (fs.existsSync(keyFile)) {
  console.log("File exists, size:", fs.statSync(keyFile).size);
  const content = fs.readFileSync(keyFile, "utf8");
  console.log("First 200 chars of JSON:", content.slice(0, 200));
} else {
  console.error("File not found");
}