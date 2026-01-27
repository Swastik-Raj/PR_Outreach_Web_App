import { exec } from "child_process";
import path from "path";
import { generatePersonalizedEmail } from "./ai.service.js";
import {
  upsertJournalist,
  createCampaign,
  createEmailRecord,
  updateCampaignStats
} from "./supabase.js";
import { rateLimiter } from "./rateLimiter.service.js";

export const startCampaign = async (req, res) => {
  const { company, topic, senderName = "PR Team", senderTitle = "Communications" } = req.body;

  try {
    const scraperPath = path.join(process.cwd(), "..", "scraper", "run_scraper.py");

    exec(`python "${scraperPath}" "${topic}"`, async (err, stdout) => {
      if (err) {
        return res.status(500).json({ error: "Scraper failed" });
      }

      const journalists = JSON.parse(stdout || "[]");
      if (!journalists.length) {
        return res.status(404).json({ error: "No journalists found" });
      }

      const campaign = await createCampaign(company, topic);
      let sentCount = 0;

      for (const j of journalists) {
        const journalist = await upsertJournalist(j);
        const article = journalist.recent_articles?.[0];

        const emailBody = await generatePersonalizedEmail({
          journalistName: `${journalist.first_name} ${journalist.last_name}`.trim(),
          publication: journalist.publication_name,
          articleTitle: article?.title,
          topic,
          company,
          senderName,
          senderTitle
        });

        const email = await createEmailRecord(
          campaign.id,
          journalist.id,
          `Story idea: ${topic}`,
          emailBody
        );

        await rateLimiter.queueEmail({
          to: journalist.email,
          subject: `Story idea: ${topic}`,
          html: emailBody,
          emailId: email.id,
          campaignId: campaign.id
        });

        sentCount++;
      }

      await updateCampaignStats(campaign.id, {
        total_emails: sentCount,
        sent_count: sentCount
      });

      res.json({
        success: true,
        campaignId: campaign.id,
        queued: sentCount
      });
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
