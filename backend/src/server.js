import express from "express";
import cors from "cors";
import { startCampaign } from "./controller.js";
import dotenv from "dotenv";
import path from "path";

dotenv.config({
  path: path.resolve(process.cwd(), "..", ".env")
});

console.log("CWD:", process.cwd());
console.log("GOOGLE_API_KEY loaded:", !!process.env.GOOGLE_API_KEY);

const app = express();
app.use(cors());
app.use(express.json());

app.post("/start-campaign", startCampaign);

app.listen(5000, () => {
  console.log("Backend running on http://localhost:5000");
});
