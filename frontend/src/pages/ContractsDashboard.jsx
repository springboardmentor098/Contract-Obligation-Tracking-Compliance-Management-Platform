import React, { useEffect, useState } from 'react';
import API from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FileText, CheckCircle2, Clock } from 'lucide-react';

const ContractsDashboard = () => {
  const [summary, setSummary] = useState({ total: 0, breakdown: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/reports/contracts/summary')
      .then((res) => {
        setSummary(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching contracts summary:', err);
        setLoading(false);
      });
  }, []);

  const chartData = Object.keys(summary.breakdown).map((key) => ({
    status: key,
    count: summary.breakdown[key],
  }));

  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' }}>
        <div className="spinner"></div> <span>Loading Contracts Data...</span>
      </div>
    );
  }

  return (
    <div style={{ padding: '30px', flex: 1 }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', margin: 0 }}>📄 Contracts Analytics</h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: '4px 0 0 0' }}>Real-time contract status and breakdown visualization.</p>
      </div>
      
      {/* 📊 KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="dashboard-card" style={{ borderLeft: '4px solid #2563eb' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Total Contracts</span>
            <FileText color="#2563eb" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{summary.total}</h2>
        </div>

        <div className="dashboard-card" style={{ borderLeft: '4px solid #16a34a' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Active Status</span>
            <CheckCircle2 color="#16a34a" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{summary.breakdown.Active || 0}</h2>
        </div>

        <div className="dashboard-card" style={{ borderLeft: '4px solid #ca8a04' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>Draft Mode</span>
            <Clock color="#ca8a04" size={20} />
          </div>
          <h2 style={{ fontSize: '32px', fontWeight: '800', margin: '12px 0 0 0', color: '#0f172a' }}>{summary.breakdown.Draft || 0}</h2>
        </div>
      </div>

      {/* 📈 Enhanced Recharts Bar Graph */}
      <div className="dashboard-card" style={{ height: '380px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '20px', color: '#1e293b' }}>Contract Status Distribution</h3>
        <ResponsiveContainer width="100%" height="85%">
          <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="status" tick={{ fill: '#64748b', fontSize: 13 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 13 }} />
            <Tooltip 
              contentStyle={{ background: '#0f172a', borderRadius: '8px', border: 'none', color: '#fff' }}
              itemStyle={{ color: '#60a5fa' }}
            />
            <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ContractsDashboard;