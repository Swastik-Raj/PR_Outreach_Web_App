import { generatePersonalizedEmail } from "./ai.service.js";
import 'dotenv/config';

const email = await generatePersonalizedEmail({
  journalistName: "Jane Doe",
  publication: "EdTech Magazine",
  articleTitle: "AI Tools for Teachers",
  topic: "AI Teaching Tools",
  company: "Dumroo.ai"
});

console.log("Generated email:\n", email);