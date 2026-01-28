import { useState } from 'react';
import { Upload, Filter, Trash2, Download } from 'lucide-react';
import './EmailLists.css';

export default function EmailLists() {
  const [lists, setLists] = useState([
    {
      id: '1',
      name: 'Tech Journalists',
      source: 'Scraped',
      status: 'Active',
      count: 156,
      unsubscribed: 3,
      blocked: 2,
    },
  ]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [uploading, setUploading] = useState(false);

  function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    // TODO: Parse CSV and upload to Supabase
    setTimeout(() => {
      setUploading(false);
    }, 2000);
  }

  const filteredLists = lists.filter(list => {
    if (filterStatus === 'all') return true;
    return list.status.toLowerCase() === filterStatus;
  });

  return (
    <div className="email-lists">
      <div className="page-header">
        <h1>Email Lists</h1>
        <p>Manage scraped and uploaded email lists</p>
      </div>

      <div className="lists-toolbar">
        <label className="upload-btn">
          <Upload size={18} />
          Upload CSV
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploading}
            hidden
          />
        </label>

        <div className="filter-group">
          <Filter size={18} />
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      <div className="lists-table">
        <div className="table-header">
          <div>List Name</div>
          <div>Source</div>
          <div>Contacts</div>
          <div>Unsubscribed</div>
          <div>Blocked</div>
          <div>Status</div>
          <div>Actions</div>
        </div>

        {filteredLists.length === 0 ? (
          <div className="empty-state">
            <p>No lists found. Upload or scrape contacts to get started.</p>
          </div>
        ) : (
          filteredLists.map(list => (
            <div key={list.id} className="table-row">
              <div><strong>{list.name}</strong></div>
              <div>{list.source}</div>
              <div>{list.count}</div>
              <div className="unsubscribed">{list.unsubscribed}</div>
              <div className="blocked">{list.blocked}</div>
              <div><span className={`badge status-${list.status.toLowerCase()}`}>{list.status}</span></div>
              <div className="actions">
                <button title="Download"><Download size={18} /></button>
                <button title="Delete"><Trash2 size={18} /></button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
