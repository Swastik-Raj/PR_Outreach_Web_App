import fetch from "node-fetch";

const SCRAPY_SERVICE_URL = process.env.SCRAPY_EMAIL_SERVICE_URL || 'http://localhost:5001';

export async function findJournalistEmail({ firstName, lastName, domain }) {
  if (!domain) {
    console.log(`⚠️  No domain provided for ${firstName} ${lastName}`);
    return null;
  }

  try {
    const url = `${SCRAPY_SERVICE_URL}/find-and-verify`;

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        firstName,
        lastName,
        domain
      })
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(`Scrapy service error for ${firstName} ${lastName}:`, data);
      return null;
    }

    if (!data?.email) {
      console.log(`No email found for ${firstName} ${lastName} at ${domain}`);
      return null;
    }

    console.log(`✓ Found email for ${firstName} ${lastName}: ${data.email} (confidence: ${data.confidence}%, verified: ${data.verified})`);

    return {
      email: data.email,
      confidence: data.confidence,
      source: data.source,
      verified: data.verified,
      dns_valid: data.dns_valid,
      smtp_valid: data.smtp_valid,
      match_type: data.match_type,
      source_url: data.source_url
    };
  } catch (error) {
    console.error(`Error fetching email for ${firstName} ${lastName}:`, error.message);
    return null;
  }
}

export async function verifyEmail(email) {
  try {
    const url = `${SCRAPY_SERVICE_URL}/verify-email`;

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email })
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(`Email verification error for ${email}:`, data);
      return null;
    }

    return {
      email: data.email,
      valid_format: data.valid_format,
      dns_valid: data.dns_valid,
      smtp_valid: data.smtp_valid,
      deliverable: data.deliverable,
      confidence: data.confidence,
      mx_records: data.mx_records
    };
  } catch (error) {
    console.error(`Error verifying email ${email}:`, error.message);
    return null;
  }
}

export async function verifyEmailsBatch(emails) {
  try {
    const url = `${SCRAPY_SERVICE_URL}/verify-emails-batch`;

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ emails })
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(`Batch email verification error:`, data);
      return null;
    }

    return data.results;
  } catch (error) {
    console.error(`Error verifying emails batch:`, error.message);
    return null;
  }
}

export async function checkServiceHealth() {
  try {
    const url = `${SCRAPY_SERVICE_URL}/health`;
    const res = await fetch(url);
    const data = await res.json();

    return res.ok && data.status === 'healthy';
  } catch (error) {
    console.error('Scrapy service health check failed:', error.message);
    return false;
  }
}
