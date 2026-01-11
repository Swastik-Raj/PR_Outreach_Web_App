import { exec } from "child_process";
import { generatePersonalizedEmail  } from "./ai.service.js";
import { sendEmail } from "./email.service.js";
import { saveCampaign } from "./db.js";
import journalists from "./data.json" assert { type: "json" };



export const startCampaign = (req, res) => {
  const { company, topic } = req.body;

  const sender = {
    name: "PR Team",
    title: "Communications",
    company
  };

  exec(`python C:/Users/swast/Projects/PR_Outreach-App/scraper/run_scraper.py "${topic}"`, async (err, stdout) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: err.message });
    }

    let scrapedJournalists;
    try {
      scrapedJournalists = JSON.parse(stdout);
    } catch (e) {
      console.error("Invalid scraper output:", stdout);
      return res.status(500).json({ error: "Invalid scraper output" });
    }

    const results = [];

    for (const j of scrapedJournalists) {
      const emailBody = await generatePersonalizedEmail({
        journalistName: j.name || "there",
        publication: j.publication || "your publication",
        articleTitle: j.article || "your recent article",
        topic,
        company,
        senderName: sender.name,
        senderTitle: sender.title
      });
      await sendEmail(j.email, "Story idea for you", emailBody);

      results.push({
        ...j,
        emailBody
      });
    }

    saveCampaign({ company, topic, results });
    res.json({ results });
  });
};

