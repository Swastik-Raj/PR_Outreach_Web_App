import { startCampaign } from "./controller.js";
import dotenv from "dotenv";
import path from "path";

dotenv.config({
  path: path.resolve(process.cwd(), "..", ".env")
});

const req = {
  body: {
    company: "Dumroo.ai",
    topic: "AI Teaching Tools"
  }
};

const res = {
  status: (code) => ({
    json: (data) => {
      console.log(`Response [${code}]:`, JSON.stringify(data, null, 2));
      return res;
    }
  }),
  json: (data) => {
    console.log('Response [200]:', JSON.stringify(data, null, 2));
    return res;
  }
};

console.log('Starting campaign with:', req.body);

startCampaign(req, res)
  .then(() => {
    console.log('Campaign started successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Campaign failed:', error);
    process.exit(1);
  });
