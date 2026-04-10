import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Sun, Moon, Bot } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const AssistantChat = ({ token }) => {
  const [messages, setMessages] = useState([{ text: "Welcome to your intelligent onboarding assistant. Ask me anything about your admission!", sender: 'ai' }]);
  const [inputBox, setInputBox] = useState('');
  const [isDark, setIsDark] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, isTyping]);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) document.body.classList.add('dark-mode');
    else document.body.classList.remove('dark-mode');
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputBox.trim()) return;

    const userText = inputBox.trim();
    setInputBox('');
    setMessages(prev => [...prev, { text: userText, sender: 'user' }]);

    try {
      setIsTyping(true);
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userText })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { text: data.reply, sender: 'ai', source: data.source }]);
    } catch (err) {
      setMessages(prev => [...prev, { text: "Network error fetching RAG contextual answer.", sender: 'ai' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const chips = [
    "When is the hostel deadline?",
    "How do I verify documents?",
    "What are the semester fees?"
  ];

  return (
    <main className="main-view">
      <header className="chat-header">
        <div className="weather-info">
          <span>Campus</span><span>•</span><span>25°C Clear</span>
        </div>
        <div className="deadline-header-box">
          <span className="label">⏳ Fee Deadline:</span>
          <span className="time">Aug 25</span>
        </div>
        <button className="btn-theme" onClick={toggleTheme} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {isDark ? <><Sun size={14} /> Light Mode</> : <><Moon size={14} /> Dark Mode</>}
        </button>
      </header>
      
      <div className="messages no-scrollbar">
        {messages.map((msg, i) => (
          <div key={i} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start', marginBottom: 24 }}>
            {msg.sender === 'ai' && (
              <div className="ai-badge">
                <Bot size={14} />
                <span>AI-generated response</span>
                {msg.source && <span className="source-tag">📄 Source: {msg.source}</span>}
              </div>
            )}
            <div className={`bubble ${msg.sender}`}>
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          </div>
        ))}
        {isTyping && (
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginBottom: 24 }}>
            <div className="ai-badge" style={{ opacity: 0.5 }}>
                <Bot size={14} />
                <span>AI is thinking...</span>
            </div>
            <div className="bubble ai">
              <div style={{ display: 'flex', gap: 6, padding: '6px 4px' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'currentColor', opacity: 0.4, animation: 'msgFade 1s infinite alternate' }}></div>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'currentColor', opacity: 0.4, animation: 'msgFade 1s infinite alternate 0.3s' }}></div>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'currentColor', opacity: 0.4, animation: 'msgFade 1s infinite alternate 0.6s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="quick-chips">
        {chips.map((c, i) => (
          <button key={i} onClick={() => setInputBox(c)}>{c}</button>
        ))}
      </div>

      <div className="chat-input-area">
        <form className="input-wrap" onSubmit={handleSend}>
          <input 
            type="text" 
            placeholder="Ask anything about your IT registration..." 
            value={inputBox}
            onChange={e => setInputBox(e.target.value)}
          />
          <button type="submit" className="btn-send" disabled={!inputBox.trim() || isTyping}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
};

export default AssistantChat;
