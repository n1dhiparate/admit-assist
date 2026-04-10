import React from 'react';
import { MessageSquare, LayoutDashboard, Shield, LogOut, Check } from 'lucide-react';

const Sidebar = ({ view, setView, items, toggleItem, studentName, logout }) => {
  const completed = items.filter(i => i.done).length;
  const pct = Math.round((completed / items.length) * 100) || 0;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div style={{ width: 40, height: 40, background: 'var(--sidebar-accent)', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--bg)', fontWeight: 800 }}>
          {studentName.charAt(0)}
        </div>
        <h1 style={{ color: 'var(--sidebar-fg)', fontSize: 20, fontWeight: 800, margin: 0 }}>Admit-assist</h1>
      </div>

      <div className="scroll-area">
        <div className="id-card-preview">
          <div className="id-photo"><div style={{width:'100%', height:'100%', background:'var(--sidebar-muted)'}}></div></div>
          <div className="id-info">
            <h4>{studentName}</h4>
            <p id="idStatus" style={{ color: pct === 100 ? '#10b981' : '' }}>
              {pct === 100 ? "Enrollment Active" : "2nd Year B.Tech IT"}
            </p>
          </div>
        </div>

        <div className="sidebar-label">Portal Views</div>
        <ul className="checklist" style={{ marginBottom: 24 }}>
          <li>
            <button className={view === 'chat' ? 'done' : ''} onClick={() => setView('chat')}>
              <div className="check-mark" style={{ border: 'none', background: 'transparent' }}><MessageSquare size={16} /></div><span>Assistant</span>
            </button>
          </li>
          <li>
            <button className={view === 'dash' ? 'done' : ''} onClick={() => setView('dash')}>
              <div className="check-mark" style={{ border: 'none', background: 'transparent' }}><LayoutDashboard size={16} /></div><span>Student Dash</span>
            </button>
          </li>
          <li>
            <button className={view === 'admin' ? 'done' : ''} onClick={() => setView('admin')}>
              <div className="check-mark" style={{ border: 'none', background: 'transparent' }}><Shield size={16} /></div><span>Admin Panel</span>
            </button>
          </li>
        </ul>

        <div className="sidebar-label">Onboarding Progress <span style={{ float: 'right' }}>{pct}%</span></div>
        <div style={{ height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 10, margin: '0 12px 28px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: 'var(--sidebar-accent)', transition: '1.2s' }}></div>
        </div>

        <div className="sidebar-label">Action Items</div>
        <ul className="checklist">
          {items.map(i => (
            <li key={i.id}>
              <button className={i.done ? 'done' : ''} onClick={() => toggleItem(i.id)}>
                <div className="check-mark">{i.done ? <Check size={14} strokeWidth={3} /> : ''}</div>
                <span>{i.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-footer" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div className="avatar">{studentName.substring(0, 2).toUpperCase()}</div>
          <div style={{ color: 'var(--sidebar-fg)' }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>{studentName}</div>
            <div style={{ fontSize: 11, opacity: 0.5 }}>B.Tech IT Student</div>
          </div>
        </div>
        <button onClick={logout} style={{ background: 'transparent', border: 'none', color: '#ff8a80', cursor: 'pointer', display: 'flex' }}>
          <LogOut size={20} />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
