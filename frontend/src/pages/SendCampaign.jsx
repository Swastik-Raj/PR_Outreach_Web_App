import { useState } from 'react';
import { Play, Pause, AlertCircle } from 'lucide-react';
import './SendCampaign.css';

export default function SendCampaign() {
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [sendingSpeed, setSendingSpeed] = useState('Medium');
  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState(null);

  async function handleStartSending() {
    setSending(true);
    try {
      // TODO: Call backend email sending API
      setProgress({ sent: 0, total: 150, remaining: 150 });

      await new Promise(resolve => setTimeout(resolve, 2000));
      setProgress({ sent: 45, total: 150, remaining: 105 });
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="send-campaign">
      <div className="page-header">
        <h1>Send Email Campaign</h1>
        <p>Control email sending with intelligent rate limiting</p>
      </div>

      <div className="send-container">
        <div className="config-section">
          <h2>Campaign Settings</h2>

          <div className="form-group">
            <label htmlFor="campaign">Select Campaign</label>
            <select
              id="campaign"
              value={selectedCampaign}
              onChange={e => setSelectedCampaign(e.target.value)}
              disabled={sending}
            >
              <option value="">-- Choose a campaign --</option>
              <option value="1">Q1 EdTech Outreach</option>
              <option value="2">AI Newsletter Pitch</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="emailAccount">Email Account</label>
            <div className="email-account">
              <span className="verified-badge">✓ Verified</span>
              <span>campaigns@dumroo.ai</span>
            </div>
          </div>

          <div className="form-group">
            <label>Sending Speed</label>
            <div className="speed-options">
              <button
                className={`speed-btn ${sendingSpeed === 'Slow' ? 'active' : ''}`}
                onClick={() => setSendingSpeed('Slow')}
                disabled={sending}
              >
                <div className="speed-label">Slow</div>
                <small>Safe (60s apart)</small>
              </button>
              <button
                className={`speed-btn ${sendingSpeed === 'Medium' ? 'active' : ''}`}
                onClick={() => setSendingSpeed('Medium')}
                disabled={sending}
              >
                <div className="speed-label">Medium</div>
                <small>Standard (30s apart)</small>
              </button>
              <button
                className={`speed-btn ${sendingSpeed === 'Fast' ? 'active' : ''}`}
                onClick={() => setSendingSpeed('Fast')}
                disabled={sending}
              >
                <div className="speed-label">Fast</div>
                <small>Quick (5s apart)</small>
              </button>
            </div>
          </div>

          {sendingSpeed === 'Fast' && (
            <div className="warning-banner">
              <AlertCircle size={20} />
              <span>Fast sending may impact deliverability. Use with caution.</span>
            </div>
          )}

          <div className="action-buttons">
            <button
              className="btn btn-primary"
              onClick={handleStartSending}
              disabled={!selectedCampaign || sending}
            >
              <Play size={18} />
              Start Campaign
            </button>
            <button className="btn btn-secondary" disabled={!sending}>
              <Pause size={18} />
              Pause
            </button>
          </div>
        </div>

        {progress && (
          <div className="progress-section">
            <h2>Send Progress</h2>

            <div className="progress-stats">
              <div className="stat">
                <div className="stat-label">Sent</div>
                <div className="stat-value">{progress.sent}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Remaining</div>
                <div className="stat-value">{progress.remaining}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Total</div>
                <div className="stat-value">{progress.total}</div>
              </div>
            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${(progress.sent / progress.total) * 100}%` }}
              ></div>
            </div>

            <div className="progress-info">
              {((progress.sent / progress.total) * 100).toFixed(1)}% Complete
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
