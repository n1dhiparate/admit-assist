import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import AuthModal from './components/AuthModal';
import AssistantChat from './components/AssistantChat';
import StudentDashboard from './components/StudentDashboard';
import AdminPanel from './components/AdminPanel';
import { Toaster, toast } from 'react-hot-toast';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('jwt_token') || null);
  const [studentName, setStudentName] = useState(localStorage.getItem('student_name') || 'Student');
  const [view, setView] = useState('chat');
  
  const [items, setItems] = useState([
    { id: "doc", label: "Document Verification (Aug 1-10)", done: false },
    { id: "fee", label: "Semester Fees (Deadline: Aug 25)", done: false },
    { id: "reg", label: "Course Registration (Opens Aug 20)", done: false },
    { id: "hostel", label: "Hostel Application (List: Aug 18)", done: false },
    { id: "lms", label: "LMS Onboarding", done: false }
  ]);

  const handleLogin = (jwt, name) => {
    localStorage.setItem('jwt_token', jwt);
    localStorage.setItem('student_name', name);
    setToken(jwt);
    setStudentName(name);
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('student_name');
    setToken(null);
    toast('Logged out successfully', { icon: '👋' });
  };

  const fetchOnboarding = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/get-onboarding`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dbStatus = await res.json();
      if (!dbStatus.error) {
        setItems(prevItems => prevItems.map(item => ({
          ...item,
          done: dbStatus[item.id] !== undefined ? dbStatus[item.id] : item.done
        })));
      }
    } catch (err) {
      console.error(err);
    }
  }, [token]);

  useEffect(() => {
    fetchOnboarding();
  }, [fetchOnboarding, view]); // simple refresh on view change

  const toggleItem = async (id) => {
    const newItems = items.map(i => i.id === id ? { ...i, done: !i.done } : i);
    setItems(newItems);

    const statusObject = {
      doc: newItems.find(x => x.id === "doc").done,
      fee: newItems.find(x => x.id === "fee").done,
      reg: newItems.find(x => x.id === "reg").done,
      hostel: newItems.find(x => x.id === "hostel").done,
      lms: newItems.find(x => x.id === "lms").done
    };

    try {
      await fetch(`${API_BASE}/api/update-onboarding`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: statusObject })
      });
      const toggled = newItems.find(x => x.id === id);
      if (toggled.done) toast.success(`Completed: ${toggled.label.split('(')[0]}`);
      else toast('Marked as pending.');
    } catch (err) {
      console.error(err);
      toast.error('Failed to update status.');
    }
  };

  if (!token) {
    return <AuthModal onLogin={handleLogin} />;
  }

  return (
    <div className="layout">
      <Toaster 
        position="bottom-right" 
        toastOptions={{ style: { background: '#2d221e', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' } }} 
      />
      <Sidebar 
        view={view} 
        setView={setView} 
        items={items} 
        toggleItem={toggleItem} 
        studentName={studentName} 
        logout={handleLogout}
      />
      {view === 'chat' && <AssistantChat token={token} />}
      {view === 'dash' && <StudentDashboard items={items} />}
      {view === 'admin' && <AdminPanel token={token} />}
    </div>
  );
};

export default App;
