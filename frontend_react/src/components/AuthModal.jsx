import React, { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const AuthModal = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [studentId, setStudentId] = useState('IT-2026-NP');
  const [password, setPassword] = useState('password123');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const url = isLogin ? `${API_BASE}/auth/login` : `${API_BASE}/auth/register`;
    const payload = isLogin ? { student_id: studentId, password } : { student_id: studentId, name, password };

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.ok && isLogin) {
        onLogin(data.access_token, data.name);
      } else if (res.ok && !isLogin) {
        setIsLogin(true); // Switch to login after register
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Cannot connect to backend server');
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 style={{ textAlign: 'center', margin: 0 }}>Admit-Assist</h2>
        <div style={{ textAlign: 'center', fontSize: 12, opacity: 0.6 }}>Premium Student Portal Authentication</div>
        
        {error && <div style={{ color: '#ff8a80', fontSize: 13, textAlign: 'center' }}>{error}</div>}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {!isLogin && (
            <input 
              type="text" 
              className="modal-input" 
              placeholder="Full Name" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              required 
            />
          )}
          <input 
            type="text" 
            className="modal-input" 
            placeholder="Student ID (e.g. IT-2026-NP)" 
            value={studentId} 
            onChange={e => setStudentId(e.target.value)} 
            required 
          />
          <input 
            type="password" 
            className="modal-input" 
            placeholder="Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
          />
          <button type="submit" className="modal-btn">
            {isLogin ? 'Sign In' : 'Register'}
          </button>
        </form>

        <div 
          onClick={() => setIsLogin(!isLogin)} 
          style={{ textAlign: 'center', fontSize: 12, cursor: 'pointer', opacity: 0.7, textDecoration: 'underline' }}
        >
          {isLogin ? "Don't have an account? Register" : "Already have an account? Sign In"}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
