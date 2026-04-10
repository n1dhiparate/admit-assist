import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const AdminPanel = ({ token }) => {
  const [stats, setStats] = useState({ total_students: 0, enrolled: 0, pending_fees: 0, pending_docs: 0, high_risk_alerts: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Fetch stats error", err);
      }
    };
    fetchStats();
  }, [token]);

  return (
    <div className="view-container">
      <h2 style={{ marginBottom: 10, fontWeight: 800 }}>Campus Governance</h2>
      <p style={{ opacity: 0.5, fontSize: 13, marginBottom: 30 }}>Overview for IT Admission Department</p>
      
      <div className="admin-stat-row">
        <div className="admin-card"><div className="val">{stats.total_students}</div><div className="lab">Total Students</div></div>
        <div className="admin-card"><div className="val">{stats.enrolled}</div><div className="lab">Enrolled</div></div>
        <div className="admin-card"><div className="val">{stats.pending_fees}</div><div className="lab">Pending Fees</div></div>
        <div className="admin-card"><div className="val">{stats.pending_docs}</div><div className="lab">Pending Docs</div></div>
      </div>

      <div className="dash-card" style={{ background: 'rgba(239, 83, 80, 0.05)', border: '1px solid rgba(239, 83, 80, 0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 800, color: '#ef5350' }}>High Risk Intervention</h3>
            <p style={{ fontSize: 12, opacity: 0.6 }}>Students within 48h of Fee Deadline without payment.</p>
          </div>
          <div className="risk-badge">{stats.high_risk_alerts} CRITICAL ALERTS</div>
        </div>
        <div style={{ height: 8, background: 'rgba(0,0,0,0.1)', borderRadius: 10, overflow: 'hidden' }}>
          <div style={{ width: '75%', height: '100%', background: '#ef5350' }}></div>
        </div>
        <button style={{ marginTop: 20, background: '#ef5350', color: '#fff', border: 'none', padding: 10, borderRadius: 8, fontWeight: 800 }}>
          🔔 DISPATCH BULK ALERTS
        </button>
      </div>
    </div>
  );
};

export default AdminPanel;
