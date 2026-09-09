import React, { useEffect, useState } from 'react';
import API from '../services/api';
import { ShieldAlert } from 'lucide-react';

const ComplianceDashboard = () => {
  const [riskData, setRiskData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/reports/risk')
      .then((res) => {
        setRiskData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching risk report:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' }}>
        <div className="spinner"></div> <span>Loading Risk Analysis...</span>
      </div>
    );
  }

  return (
    <div style={{ padding: '30px', flex: 1 }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', margin: 0 }}>🛡️ Compliance & Risk Center</h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: '4px 0 0 0' }}>Contracts flagged for overdue obligations or low compliance scores.</p>
      </div>

      <div className="dashboard-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontSize: '13px' }}>
              <th style={{ padding: '16px 20px' }}>CONTRACT ID</th>
              <th style={{ padding: '16px 20px' }}>NUMBER</th>
              <th style={{ padding: '16px 20px' }}>RISK LEVEL</th>
              <th style={{ padding: '16px 20px' }}>OVERDUE OBLIGATIONS</th>
              <th style={{ padding: '16px 20px' }}>SCORE</th>
            </tr>
          </thead>
          <tbody>
            {riskData.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                  <ShieldAlert size={36} color="#22c55e" style={{ marginBottom: '8px' }} />
                  <div>All clear! No high-risk contracts detected.</div>
                </td>
              </tr>
            ) : (
              riskData.map((item) => (
                <tr key={item.contract_id} style={{ borderBottom: '1px solid #f1f5f9', fontSize: '14px' }}>
                  <td style={{ padding: '16px 20px', fontWeight: '600' }}>#{item.contract_id}</td>
                  <td style={{ padding: '16px 20px', color: '#334155' }}>{item.contract_number}</td>
                  <td style={{ padding: '16px 20px' }}>
                    <span className="badge badge-risk">{item.risk_level}</span>
                  </td>
                  <td style={{ padding: '16px 20px', color: '#64748b' }}>{item.overdue_obligations} item(s)</td>
                  <td style={{ padding: '16px 20px', fontWeight: '700', color: item.compliance_score < 50 ? '#ef4444' : '#f59e0b' }}>
                    {item.compliance_score}%
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComplianceDashboard;