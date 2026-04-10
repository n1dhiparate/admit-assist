import React from 'react';

const StudentDashboard = ({ items }) => {
  const completed = items.filter(i => i.done).length;
  const pct = Math.round((completed / items.length) * 100) || 0;

  return (
    <div className="view-container">
      <h2 style={{ marginBottom: 30, fontWeight: 800 }}>Academic Insights</h2>
      <div className="dash-grid">
        <div className="dash-card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: 11, opacity: 0.5, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 15 }}>Enrollment Progress</h3>
          <div style={{ fontSize: 48, fontWeight: 800, color: 'var(--primary)' }}>{pct}%</div>
          <p style={{ fontSize: 12, marginTop: 10, fontWeight: 700 }}>
            {pct === 100 ? 'Enrollment Active' : 'Action Required'}
          </p>
        </div>
        <div className="dash-card">
          <h3 style={{ fontSize: 11, opacity: 0.5, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 15 }}>Upcoming Milestones</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: 13, fontWeight: 600 }}>
            <div style={{ color: '#ef5350' }}>🚩 Aug 25: Fee Payment Deadline</div>
            <div style={{ color: 'var(--primary)' }}>🚩 Sept 5: IT Orientation Day</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
