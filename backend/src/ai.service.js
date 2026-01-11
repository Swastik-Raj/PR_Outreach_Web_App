export async function generatePersonalizedEmail({
  journalistName,
  publication,
  articleTitle,
  topic,
  company,
  senderName,
  senderTitle
}) {
  // Confirm the API key is loaded
  if (!process.env.GOOGLE_API_KEY) {
    console.error("ERROR: GOOGLE_API_KEY not set in environment!");
    return fallbackEmail(journalistName, publication, articleTitle, topic, company);
  }

  console.log("Gemini key loaded:", !!process.env.GOOGLE_API_KEY);

  const prompt = `
You are a PR outreach assistant.

Write a short, friendly, personalized outreach email.

Context:
- Journalist: ${journalistName}
- Publication: ${publication}
- Article they wrote: "${articleTitle}"
- Company pitching the story: ${company}
- Campaign topic: ${topic}
- Sender name: ${senderName}
- Sender role: ${senderTitle}

Guidelines:
- Sign the email using the sender name and role
- Do NOT use placeholders like [Your Name]
- Mention the article naturally
- Explain why the topic fits their beat
- Be concise (max 120 words)
- No emojis, no buzzwords
- End with a soft call-to-action

Email:
`;

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key=${process.env.GOOGLE_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
  contents: [
    {
      parts: [
           { text: prompt }
        ]
      }
      ]
    })
      }
    );

    if (!response.ok) {
      const raw = await response.text();
      console.error("Gemini API error:", response.status, raw);
      return fallbackEmail(journalistName, publication, articleTitle, topic, company);
    }

    const data = await response.json();

    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!text) {
      console.warn("Gemini returned empty response", data);
      return fallbackEmail(journalistName, publication, articleTitle, topic, company);
    }

    return text.trim();

  } catch (err) {
    console.error("AI email generation failed:", err);
    return fallbackEmail(journalistName, publication, articleTitle, topic, company);
  } // <-- closes catch

} // <-- closes generatePersonalizedEmail

/**
 * Fallback email template if AI fails
 */
function fallbackEmail(
  name,
  publication,
  article,
  topic,
  company,
  senderName = "PR Team",
  senderTitle = ""
) {
  return `Hi ${name || "there"},

I recently read your article "${article}" in ${publication} and thought it aligned well with the work we're doing at ${company}.

We’re currently exploring ${topic}, and I believe it could be a useful angle for your audience.

If this sounds interesting, I’d be happy to share more details.

Best regards,
${senderName}
${senderTitle}
${company}`;
}