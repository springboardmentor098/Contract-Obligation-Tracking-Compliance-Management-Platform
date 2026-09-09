import React, { useState } from 'react';
import API from '../services/api';
import { FileSpreadsheet, FileText, Download, CheckCircle2 } from 'lucide-react';

const ExportScreen = () => {
  const [downloading, setDownloading] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  const downloadFile = async (type) => {
    setDownloading(type);
    setSuccessMsg('');
    try {
      // Send authenticated request for binary stream 🐍
      const response = await API.get(`/reports/contracts/export/${type}`, {
        responseType: 'blob',
      });
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `contract_report.${type === 'excel' ? 'xlsx' : 'pdf'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccessMsg(`Successfully generated and downloaded ${type.toUpperCase()} report!`);
    } catch (err) {
      console.error('Error downloading report:', err);
      alert('Failed to download report. Ensure backend PDF/Excel dependencies are installed.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div style={{ padding: '30px', flex: 1 }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', margin: 0 }}>📥 Document Export Center</h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: '4px 0 0 0' }}>Export system contract analytical reports in standard Excel and PDF formats.</p>
      </div>

      <div className="dashboard-card">
        {successMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#dcfce7', color: '#15803d', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px', fontWeight: '500' }}>
            <CheckCircle2 size={18} /> {successMsg}
          </div>
        )}

        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <button 
            onClick={() => downloadFile('excel')} 
            disabled={downloading === 'excel'}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '14px 24px', background: '#16a34a', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '14px' }}
          >
            <FileSpreadsheet size={20} />
            {downloading === 'excel' ? 'Generating Excel...' : 'Export Excel (.xlsx)'}
            <Download size={16} />
          </button>

          <button 
            onClick={() => downloadFile('pdf')} 
            disabled={downloading === 'pdf'}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '14px 24px', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '14px' }}
          >
            <FileText size={20} />
            {downloading === 'pdf' ? 'Generating PDF...' : 'Export PDF (.pdf)'}
            <Download size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportScreen;