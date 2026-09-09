import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ContractsDashboard from './pages/ContractsDashboard';
import RenewalsDashboard from './pages/RenewalsDashboard';
import ComplianceDashboard from './pages/ComplianceDashboard';
import ExportScreen from './pages/ExportScreen';
import Login from './pages/Login';
import { LogOut, User } from 'lucide-react';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <Login onLoginSuccess={(newToken) => setToken(newToken)} />;
  }

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#f8fafc' }}>
          {/* Top Header Bar */}
          <header style={{ height: '64px', background: '#fff', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px' }}>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>ContractIQ / Workspace</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155', fontSize: '14px', fontWeight: '500' }}>
                <User size={18} color="#2563eb" /> Administrator
              </div>
              <button 
                onClick={handleLogout} 
                style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', background: '#fee2e2', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600', color: '#991b1b' }}
              >
                <LogOut size={14} /> Logout
              </button>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<Navigate to="/contracts" replace />} />
            <Route path="/contracts" element={<ContractsDashboard />} />
            <Route path="/renewals" element={<RenewalsDashboard />} />
            <Route path="/compliance" element={<ComplianceDashboard />} />
            <Route path="/exports" element={<ExportScreen />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;