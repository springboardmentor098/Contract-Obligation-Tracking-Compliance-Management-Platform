import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Clock, ShieldCheck, Download } from 'lucide-react';

const Sidebar = () => {
  return (
    <div style={{ width: '240px', background: '#1e293b', color: '#fff', minHeight: '100vh', padding: '20px' }}>
      <h2 style={{ fontSize: '20px', fontWeight: 'bold' }}>ContractIQ 📊</h2>
      <nav style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <Link to="/contracts" style={{ color: '#fff', textDecoration: 'none', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <FileText size={18} /> Contracts
        </Link>
        <Link to="/renewals" style={{ color: '#fff', textDecoration: 'none', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <Clock size={18} /> Renewals
        </Link>
        <Link to="/compliance" style={{ color: '#fff', textDecoration: 'none', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <ShieldCheck size={18} /> Compliance
        </Link>
        <Link to="/exports" style={{ color: '#fff', textDecoration: 'none', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <Download size={18} /> Export Reports
        </Link>
      </nav>
    </div>
  );
};

export default Sidebar;