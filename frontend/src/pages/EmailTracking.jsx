import { useState } from 'react';
import './EmailTracking.css';

export default function EmailTracking() {
  const [activeTab, setActiveTab] = useState('delivered');

  const trackingData = {
    delivered: { count: 145, items: [] },
    opened: { count: 67, items: [] },
    clicked: { count: 23, items: [] },
    bounced: { count: 5, items: [] },
    responses: { count: 12, items: [] },
    unsubscribed: { count: 0, items: [] },
  };

  const kpis = [
    { label: 'Open Rate', value: '46.2%', color: 'blue' },
    { label: 'Click Rate', value: '15.9%', color: 'purple' },
    { label: 'Bounce Rate', value: '3.4%', color: 'red' },
  ];

  return (
    <div className="email-tracking">
      <div className="page-header">
        <h1>Email Tracking Dashboard</h1>
        <p>Monitor campaign performance and email engagement</p>
      </div>

      <div className="kpi-grid">
        {kpis.map(kpi => (
          <div key={kpi.label} className={`kpi-card kpi-${kpi.color}`}>
            <div className="kpi-label">{kpi.label}</div>
            <div className="kpi-value">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="tracking-tabs">
        {Object.entries(trackingData).map(([key, data]) => (
          <button
            key={key}
            className={`tab-btn ${activeTab === key ? 'active' : ''}`}
            onClick={() => setActiveTab(key)}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)} ({data.count})
          </button>
        ))}
      </div>

      <div className="tracking-table">
        <div className="table-header">
          <div>Recipient</div>
          <div>Email</div>
          <div>Campaign</div>
          <div>Status</div>
          <div>Timestamp</div>
        </div>

        <div className="empty-state">
          <p>No data available for this tracking status</p>
        </div>
      </div>
    </div>
  );
}
