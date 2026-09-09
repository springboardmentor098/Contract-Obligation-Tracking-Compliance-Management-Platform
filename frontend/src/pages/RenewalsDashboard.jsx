import React, { useEffect, useState } from 'react';
import API from '../services/api';
import { RefreshCw, CalendarClock, AlertCircle, CheckCircle2 } from 'lucide-react';

const RenewalsDashboard = () => {
  const [data, setData] = useState({ total: 0, breakdown: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/reports/renewals/summary')
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching renewals summary:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' }}>
        <div className="spinner"></div> <span>Loading Renewals Tracker...</span>
      </div>
    );
  }

  return (
    <div style={{ padding: '30px', flex: 1 }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', margin: 0 }}>🔄 Renewals Dashboard</h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: '4px 0 0 0' }}>Track contract expiration dates and pending renewal workflows.</p>
      </div>
      
      {/* 📊 KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="dashboard-card" style={{ borderLeft: '4px solid #3b82f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Total Tracked</span>
            <RefreshCw color="#3b82f6" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{data.total}</h2>
        </div>

        <div className="dashboard-card" style={{ borderLeft: '4px solid #eab308' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Upcoming Renewals</span>
            <CalendarClock color="#eab308" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{data.breakdown.Upcoming || 0}</h2>
        </div>

        <div className="dashboard-card" style={{ borderLeft: '4px solid #ef4444' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Expired Contracts</span>
            <AlertCircle color="#ef4444" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{data.breakdown.Expired || 0}</h2>
        </div>
      </div>

      {/* 💡 Renewal Status Summary Section */}
      <div className="dashboard-card">
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#1e293b' }}>Renewal Health & Operations</h3>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center', background: '#f1f5f9', padding: '16px', borderRadius: '8px' }}>
          <CheckCircle2 color="#16a34a" size={24} />
          <div>
            <div style={{ fontWeight: '600', fontSize: '14px', color: '#0f172a' }}>Automated Reminders Active</div>
            <div style={{ fontSize: '13px', color: '#64748b' }}>ContractIQ is sending email notifications 30 days prior to contract expiration dates.</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RenewalsDashboard;