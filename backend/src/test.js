import fs from "fs";
import path from "path";

const keyFile = path.resolve("..", "keys", "gen-lang-client-0595573539-c04e97ff1c9f.json");

if (fs.existsSync(keyFile)) {
  console.log("Service account file found!");
} else {
  console.error("Cannot find service account file at:", keyFile);
}