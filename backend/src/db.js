import fs from "fs";
import path from "path"

const DB_FILE = path.join(process.cwd(), "data.json");

export function saveCampaign(data) {
  let existing = [];

  if (fs.existsSync(DB_FILE)) {
    existing = JSON.parse(fs.readFileSync(DB_FILE, "utf-8"));
  }

  existing.push(data);

  fs.writeFileSync(DB_FILE, JSON.stringify(existing, null, 2));
}