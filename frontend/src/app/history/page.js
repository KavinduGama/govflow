"use client";

import { useState, useEffect, useContext } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthContext } from "../../context/AuthContext";
import Header from "../../components/layout/Header";
import WorkflowSidebar from "../../components/WorkflowSidebar";
import "./history.css";
import { API_URL } from "@/lib/api";

export default function History() {
  const { user, token, loading } = useContext(AuthContext);
  const router = useRouter();
  
  const [activeTab, setActiveTab] = useState("chats");
  const [chats, setChats] = useState([]);
  const [plans, setPlans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (token) {
      fetchHistory();
    }
  }, [token, activeTab]);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const endpoint = activeTab === "chats" ? "/history/chats" : "/history/plans";
      const res = await fetch(`${API_URL}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (activeTab === "chats") setChats(data);
        else setPlans(data);
      }
    } catch (err) {
      console.error("Failed to load history", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = async (e, threadId) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat history?")) return;
    
    try {
      const res = await fetch(`${API_URL}/history/chats/${threadId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setChats(chats.filter(c => c.thread_id !== threadId));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeletePlan = async (e, planId) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this saved plan?")) return;
    
    try {
      const res = await fetch(`${API_URL}/history/plans/${planId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setPlans(plans.filter(p => p.id !== planId));
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading || !user) return null;

  return (
    <>
      <Header />
      <main className="main-content">
        <div className="history-container fade-in-up">
          <div className="history-header">
            <h2>My History</h2>
            <div className="history-tabs">
              <button 
                className={`tab-btn ${activeTab === "chats" ? "active" : ""}`}
                onClick={() => setActiveTab("chats")}
              >
                Conversations
              </button>
              <button 
                className={`tab-btn ${activeTab === "plans" ? "active" : ""}`}
                onClick={() => setActiveTab("plans")}
              >
                Saved Plans
              </button>
            </div>
          </div>

          <div className="history-content">
            {isLoading ? (
              <div className="loading-spinner">Loading...</div>
            ) : activeTab === "chats" ? (
              <div className="history-list">
                {chats.length === 0 ? (
                  <div className="empty-state">No chat history found.</div>
                ) : (
                  chats.map((chat) => (
                    <div 
                      key={chat.thread_id} 
                      className="history-card"
                      onClick={() => router.push(`/?thread_id=${chat.thread_id}`)}
                    >
                      <div className="history-card-content">
                        <h3>{chat.title || "New Conversation"}</h3>
                        <p className="history-meta">
                          {new Date(chat.created_at).toLocaleDateString()}
                          {chat.service_code && ` • Service: ${chat.service_code}`}
                        </p>
                      </div>
                      <button className="delete-btn" onClick={(e) => handleDeleteChat(e, chat.thread_id)}>
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div className="history-list">
                {plans.length === 0 ? (
                  <div className="empty-state">No saved plans found.</div>
                ) : (
                  plans.map((plan) => (
                    <div 
                      key={plan.id} 
                      className="history-card"
                      onClick={() => setSelectedPlan(plan.workflow_data)}
                    >
                      <div className="history-card-content">
                        <h3>Procedure: {plan.service_code}</h3>
                        <p className="history-meta">
                          Saved on {new Date(plan.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button className="delete-btn" onClick={(e) => handleDeletePlan(e, plan.id)}>
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
        
        <WorkflowSidebar 
          workflow={selectedPlan} 
          onClose={() => setSelectedPlan(null)} 
        />
      </main>
    </>
  );
}
