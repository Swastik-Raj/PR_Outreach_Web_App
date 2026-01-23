import { startCampaign } from "./controller.js"; // adjust the path
import fs from "fs";

// Mock request and response objects
const req = {
  body: {
    company: "Dumroo.ai",
    topic: "AI Teaching Tools"
  }
};

const res = {
  json: (data) => {
    console.log("Response JSON:", JSON.stringify(data, null, 2));
  },
  status: (code) => {
    return {
      json: (data) => console.log(`Error ${code}:`, data)
    };
  }
};

// Call the function
startCampaign(req, res);
