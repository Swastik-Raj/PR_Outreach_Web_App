const API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:5000';

class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  async request(method, endpoint, data = null) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(error.message || `API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  get(endpoint) {
    return this.request('GET', endpoint);
  }

  post(endpoint, data) {
    return this.request('POST', endpoint, data);
  }

  put(endpoint, data) {
    return this.request('PUT', endpoint, data);
  }

  delete(endpoint) {
    return this.request('DELETE', endpoint);
  }

  // Start a new campaign (scrapes, generates emails, and queues for sending)
  async startCampaign(company, topic, geography = '') {
    return this.post('/start-campaign', { company, topic, geography });
  }

  // Get all campaigns
  async getCampaigns() {
    return this.get('/campaigns');
  }

  // Get campaign details with emails
  async getCampaignDetails(campaignId) {
    return this.get(`/campaigns/${campaignId}`);
  }

  // Get campaign analytics
  async getCampaignAnalytics(campaignId) {
    return this.get(`/campaigns/${campaignId}/analytics`);
  }

  // Generate a single email (for preview/testing)
  async generateEmail(data) {
    return this.post('/generate-email', data);
  }

  // Get rate limiter queue status
  async getRateLimiterStatus() {
    return this.get('/rate-limiter/status');
  }
}

export const api = new APIClient(API_URL);
