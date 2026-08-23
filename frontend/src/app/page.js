"use client";

import { useState, useEffect, useRef, Suspense, useContext } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Header from '../components/layout/Header';
import ReactMarkdown from 'react-markdown';
import WorkflowSidebar from '../components/WorkflowSidebar';
import { AuthContext } from '../context/AuthContext';
import './chat.css';

// Simple UUID generator for browser
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function ChatInner() {
  const searchParams = useSearchParams();
  const initialService = searchParams.get('service');
  const historyThreadId = searchParams.get('thread_id');
  const router = useRouter();
  
  const { token, user } = useContext(AuthContext);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState('');
  const [sidebarWorkflow, setSidebarWorkflow] = useState(null);
  const messagesEndRef = useRef(null);
  const [progress, setProgress] = useState(null);
  
  // History state for sidebar
  const [historyList, setHistoryList] = useState([]);

  // Fetch history list
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/api/v1/history/chats', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => res.ok ? res.json() : [])
      .then(data => setHistoryList(data))
      .catch(err => console.error(err));
    }
  }, [token, threadId]); // Refetch when threadId changes to update list with new chat

  // Initial state handling inside useEffect
  useEffect(() => {
    if (historyThreadId) {
        setThreadId(historyThreadId);
        // Load history from API
        const fetchHistory = async () => {
            if (!token) return;
            try {
                const res = await fetch(`http://localhost:8000/api/v1/history/chats/${historyThreadId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setMessages(data);
                    
                    // Auto-open workflow if the last message has one
                    if (data.length > 0) {
                        const lastMsg = data[data.length - 1];
                        if (lastMsg.workflow) {
                            setSidebarWorkflow(lastMsg.workflow);
                        }
                    }
                }
            } catch (err) {
                console.error("Failed to load history", err);
            }
        };
        fetchHistory();
    } else {
        setThreadId(generateUUID());
        setMessages([
          { 
            role: 'assistant', 
            content: initialService 
              ? `Hi! I see you need help with "${initialService}". How can I assist you with this procedure?` 
              : "Hello! I am GovFlow AI. What government service or procedure do you need help with today?" 
          }
        ]);
    }
    setProgress(null);
    setSidebarWorkflow(null); // Clear right sidebar on new chat
  }, [initialService, historyThreadId, token]);

  // Auto-scroll to the bottom when messages or loading state changes
  useEffect(() => {
      const timer = setTimeout(() => {
          if (messagesEndRef.current) {
              messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
          }
      }, 100);
      return () => clearTimeout(timer);
  }, [messages, isLoading, progress]);

  const handleNewChat = () => {
    router.push('/');
  };

  const handleSelectChat = (id) => {
    router.push(`/?thread_id=${id}`);
  };

  // Handle submit inside ChatInner
  const handleSubmit = async (e) => {
      e.preventDefault();
      if (!input.trim() || isLoading) return;
  
      const userMessage = input.trim();
      setInput('');
      setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
      setIsLoading(true);
  
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch('http://localhost:8000/api/v1/chat', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            thread_id: threadId,
            message: userMessage
          })
        });
  
        if (!response.ok) throw new Error("API responded with an error");
  
        const data = await response.json();
  
        if (data.final_workflow) {
          localStorage.setItem('govflow_current_workflow', JSON.stringify(data.final_workflow));
        }
  
        if (data.questions_progress) {
          setProgress(data.questions_progress);
        }
  
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.reply,
          workflow: data.final_workflow 
        }]);
  
      } catch (error) {
        console.error("Chat error:", error);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later." 
        }]);
      } finally {
        setIsLoading(false);
      }
    };

  const submitFeedback = async (isPositive) => {
    try {
      await fetch('http://localhost:8000/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: threadId,
          is_positive: isPositive
        })
      });
    } catch (error) {
      console.error("Feedback error:", error);
    }
  };

    return (
        <>
          <Header />
          <div className="chat-page-layout fade-in-up">
            
            {/* LEFT SIDEBAR - History */}
            <aside className="chat-left-sidebar">
              <button className="new-chat-btn" onClick={handleNewChat}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                New Chat
              </button>
              
              <div className="history-list-sidebar">
                {user ? (
                  historyList.length > 0 ? (
                    historyList.map(chat => (
                      <div 
                        key={chat.thread_id} 
                        className={`history-item-sidebar ${chat.thread_id === threadId ? 'active' : ''}`}
                        onClick={() => handleSelectChat(chat.thread_id)}
                        title={chat.title || "Conversation"}
                      >
                        {chat.title || "New Conversation"}
                      </div>
                    ))
                  ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '1rem', textAlign: 'center' }}>
                      No previous conversations.
                    </div>
                  )
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '1rem', textAlign: 'center' }}>
                    Login to save and view your chat history.
                  </div>
                )}
              </div>
            </aside>

            {/* CENTER - Main Chat */}
            <main className="chat-main-area">
              <div className="chat-box">
                {/* Progress Indicator */}
                {progress && progress.total > 0 && progress.answered < progress.total && (
                  <div className="chat-progress-container">
                    <div className="chat-progress-text">
                      Step {progress.answered} of {progress.total}
                    </div>
                    <div className="chat-progress-bar-bg">
                      <div 
                        className="chat-progress-bar-fill" 
                        style={{ width: `${(progress.answered / progress.total) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}
    
                <div className="chat-messages">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`message-wrapper ${msg.role}`}>
                      <div className="message-bubble">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                      
                      {/* Feedback UI */}
                      {msg.role === 'assistant' && !msg.workflow && (
                        <div className="feedback-container">
                          <button 
                            className="feedback-btn" 
                            onClick={() => submitFeedback(true)}
                            title="Helpful"
                          >👍</button>
                          <button 
                            className="feedback-btn" 
                            onClick={() => submitFeedback(false)}
                            title="Not Helpful"
                          >👎</button>
                        </div>
                      )}
                      
                      {/* Render Final Workflow Link if available */}
                      {msg.workflow && (
                        <div className="workflow-card">
                          <h3>🎉 Your Personalized Procedure is Ready</h3>
                          <p>We've generated a step-by-step guide and document checklist based on your answers.</p>
                          <button 
                            onClick={() => setSidebarWorkflow(msg.workflow)}
                            className="view-workflow-btn"
                            style={{ border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}
                          >
                            View Procedure Plan <span>→</span>
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Centralized input if no messages yet (excluding the initial greeting) */}
                <div className={`chat-input-area ${messages.length <= 1 ? 'initial-center' : ''}`}>
                  {messages.length <= 1 && (
                    <div className="initial-greeting">
                      <h1 className="glow-text">How can I help you today?</h1>
                      <p>GovFlow AI is ready to assist with government procedures.</p>
                    </div>
                  )}
                  <form onSubmit={handleSubmit} className="chat-form">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Type your message here..."
                      className="chat-input"
                      disabled={isLoading}
                    />
                    <button type="submit" className="chat-submit" disabled={isLoading || !input.trim()}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                      </svg>
                    </button>
                  </form>
                </div>
              </div>
            </main>

            {/* RIGHT SIDEBAR - Workflow */}
            {sidebarWorkflow && (
              <aside className="chat-right-sidebar">
                <WorkflowSidebar 
                  workflow={sidebarWorkflow} 
                  onClose={() => setSidebarWorkflow(null)} 
                  embedded={true}
                />
              </aside>
            )}
          </div>
        </>
    );
}

export default function Chat() {
  return (
    <Suspense fallback={
      <>
        <Header />
        <div className="chat-page-layout fade-in-up">
          <div className="chat-main-area">
            <div className="chat-box">
              <div className="chat-messages">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </>
    }>
      <ChatInner />
    </Suspense>
  );
}

