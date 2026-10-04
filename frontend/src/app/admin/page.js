"use client";

import { useState, useEffect, useContext, useCallback } from 'react';
import Header from '../../components/layout/Header';
import { AuthContext } from '../../context/AuthContext';
import './admin.css';
import Link from 'next/link';
import { API_URL } from "@/lib/api";

const SYNC_POLL_MS = 2000;

async function loadAdminData(token) {
  const headers = { Authorization: `Bearer ${token}` };
  const getJson = (path) =>
    fetch(`${API_URL}/admin/${path}`, { headers }).then(res => {
      if (!res.ok) throw new Error(`Admin request failed: ${res.status}`);
      return res.json();
    });

  const [statsData, servicesData, kbData] = await Promise.all([
    getJson('dashboard'),
    getJson('services'),
    getJson('knowledge-base/stats'),
  ]);
  return { statsData, servicesData, kbData };
}

export default function AdminDashboard() {
  const { user, token, loading: authLoading } = useContext(AuthContext);
  const isAdmin = user?.role === 'admin';

  const [stats, setStats] = useState(null);
  const [services, setServices] = useState([]);
  const [kbStats, setKbStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Sync state
  const [isSyncing, setIsSyncing] = useState(false);
  const [forceLive, setForceLive] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const [syncError, setSyncError] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null); // queued | running | succeeded | failed

  const fetchDashboardData = useCallback(
    () => loadAdminData(token)
      .then(({ statsData, servicesData, kbData }) => {
        setStats(statsData);
        setServices(servicesData);
        setKbStats(kbData);
      })
      .catch(err => console.error("Admin fetch error:", err))
      .finally(() => setLoading(false)),
    [token]
  );

  useEffect(() => {
    // The page is only usable by admins; the API enforces this too, the UI check just avoids a broken screen.
    if (!isAdmin) return;
    fetchDashboardData();
  }, [isAdmin, fetchDashboardData]);

  // The sync runs in the background on the server: we queue it, then poll its status.
  const waitForSyncRun = async (runId) => {
    const headers = { Authorization: `Bearer ${token}` };
    for (;;) {
      await new Promise(resolve => setTimeout(resolve, SYNC_POLL_MS));
      const res = await fetch(`${API_URL}/admin/sync-runs/${runId}`, { headers });
      if (!res.ok) throw new Error(`Could not check sync status (${res.status})`);
      const run = await res.json();
      setSyncStatus(run.status);
      if (run.status === 'succeeded') return run.result;
      if (run.status === 'failed') throw new Error(run.error || 'Sync failed');
    }
  };

  const handleScrapeAndSync = async () => {
    setIsSyncing(true);
    setSyncError(null);
    setSyncResult(null);
    setSyncStatus('queued');

    try {
      const res = await fetch(`${API_URL}/admin/scrape-sync?force_live=${forceLive}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await res.json().catch(() => ({}));

      let runId;
      if (res.status === 202) {
        runId = body.id;
      } else if (res.status === 409) {
        // Someone (maybe another tab) already started one: follow that run instead
        runId = body.detail.run.id;
      } else {
        throw new Error(body.detail || `Server error: ${res.status}`);
      }

      setSyncResult(await waitForSyncRun(runId));
      // Refresh statistics after sync
      await fetchDashboardData();
    } catch (err) {
      console.error("Scrape & Sync error:", err);
      setSyncError(err.message || "Failed to trigger Scrape & Sync pipeline.");
    } finally {
      setIsSyncing(false);
    }
  };

  if (!authLoading && !isAdmin) {
    return (
      <>
        <Header />
        <main className="admin-content">
          <div className="admin-main fade-in">
            <h1>Admins only</h1>
            <p className="admin-subtitle">
              {user ? "Your account doesn't have admin access." : "Please log in with an admin account."}
            </p>
            <Link href={user ? "/" : "/login"} style={{ color: 'var(--primary-light)' }}>
              {user ? "← Back to chat" : "Go to login →"}
            </Link>
          </div>
        </main>
      </>
    );
  }

  if (authLoading || loading) {
    return (
      <>
        <Header />
        <main className="admin-content">
          <div className="admin-container loading-skeleton fade-in"></div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="admin-content">
        <div className="admin-sidebar">
          <h2>Admin Panel</h2>
          <nav>
            <a href="#overview" className="active">Overview</a>
            <a href="#knowledge-base">Knowledge Base & Sync</a>
            <a href="#services">Services</a>
            <Link href="/" style={{ marginTop: '20px', color: 'var(--primary-light)' }}>
              &larr; Back to Citizen Chat
            </Link>
          </nav>
        </div>
        
        <div className="admin-main fade-in-up">
          <div className="admin-header" id="overview">
            <h1>Dashboard Overview</h1>
            <p className="admin-subtitle">Monitor services, workflow engine, and RAG vector store synchronization.</p>
          </div>

          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Services</h3>
                <div className="stat-value">{stats.services}</div>
              </div>
              <div className="stat-card">
                <h3>Questions</h3>
                <div className="stat-value">{stats.questions}</div>
              </div>
              <div className="stat-card">
                <h3>Workflow Steps</h3>
                <div className="stat-value">{stats.workflow_steps}</div>
              </div>
              <div className="stat-card">
                <h3>Required Docs</h3>
                <div className="stat-value">{stats.required_documents}</div>
              </div>
              <div className="stat-card">
                <h3>Source Documents</h3>
                <div className="stat-value">{stats.source_documents}</div>
              </div>
              <div className="stat-card highlight">
                <h3>Vector Chunks</h3>
                <div className="stat-value">{stats.document_chunks || kbStats?.total_chunks || 0}</div>
              </div>
            </div>
          )}

          {/* ── Knowledge Base & Scrape & Sync Section ── */}
          <div className="admin-section kb-section" id="knowledge-base">
            <div className="section-header">
              <div>
                <h2>Knowledge Base &amp; Vector Synchronization</h2>
                <p className="section-desc">
                  Scrape official government portals and ingest FAQs, procedures, and forms with SHA-256 change detection.
                </p>
              </div>
              <div className="sync-actions">
                <label className="checkbox-container">
                  <input 
                    type="checkbox" 
                    checked={forceLive} 
                    onChange={(e) => setForceLive(e.target.checked)}
                    disabled={isSyncing}
                  />
                  <span>Live Web Scraper</span>
                </label>
                <button 
                  className={`primary-btn-sync ${isSyncing ? 'loading' : ''}`}
                  onClick={handleScrapeAndSync}
                  disabled={isSyncing}
                >
                  {isSyncing ? (
                    <>
                      <span className="spinner"></span>
                      <span>{syncStatus === 'running' ? 'Scraping & syncing…' : 'Queued…'}</span>
                    </>
                  ) : (
                    <>
                      <span className="sync-icon">🔄</span>
                      <span>Scrape &amp; Sync</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Sync Results Banner */}
            {syncResult && (
              <div className="sync-result-card success fade-in">
                <div className="result-header">
                  <span className="result-icon">✓</span>
                  <div>
                    <strong>Sync Completed Successfully</strong>
                    <p>
                      {syncResult.scraped_live 
                        ? 'Scraped live portal and synchronized vector database.' 
                        : 'Synchronized verified dataset into vector database.'}
                    </p>
                    {syncResult.live_scrape_error && (
                      <p className="sync-warning">
                        Live scrape skipped, so the last good copy was used: {syncResult.live_scrape_error}
                      </p>
                    )}
                  </div>
                </div>
                <div className="result-stats-row">
                  <div className="result-stat-item">
                    <span className="result-label">Docs Processed</span>
                    <span className="result-val">{syncResult.documents_processed}</span>
                  </div>
                  <div className="result-stat-item">
                    <span className="result-label">New Chunks</span>
                    <span className="result-val highlight">{syncResult.new_chunks}</span>
                  </div>
                  <div className="result-stat-item">
                    <span className="result-label">Unchanged (Skipped)</span>
                    <span className="result-val">{syncResult.unchanged_chunks}</span>
                  </div>
                  <div className="result-stat-item">
                    <span className="result-label">Total Active Chunks</span>
                    <span className="result-val">{syncResult.total_active_chunks}</span>
                  </div>
                  <div className="result-stat-item badge-item">
                    <span className="result-label">OpenAI Cost Saved</span>
                    <span className="savings-badge">{syncResult.cost_saved_percent}% Saved</span>
                  </div>
                </div>
              </div>
            )}

            {syncError && (
              <div className="sync-result-card error fade-in">
                <span className="result-icon">⚠️</span>
                <div>
                  <strong>Sync Failed</strong>
                  <p>{syncError}</p>
                </div>
              </div>
            )}

            {/* Ingested Documents List */}
            {kbStats && kbStats.documents && (
              <div className="kb-table-wrapper">
                <div className="kb-table-header">
                  <h3>Ingested Official Documents ({kbStats.documents.length})</h3>
                  {kbStats.last_sync && (
                    <span className="last-sync-badge">
                      Last Synced: {new Date(kbStats.last_sync).toLocaleString()}
                    </span>
                  )}
                </div>
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Type</th>
                        <th>Source URL</th>
                        <th>Chunks</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {kbStats.documents.map((doc) => (
                        <tr key={doc.id}>
                          <td className="doc-title-cell">
                            <strong>{doc.title}</strong>
                          </td>
                          <td>
                            <span className={`type-tag ${doc.source_type}`}>
                              {doc.source_type}
                            </span>
                          </td>
                          <td>
                            <a 
                              href={doc.url} 
                              target="_blank" 
                              rel="noreferrer" 
                              className="source-link"
                            >
                              {doc.url.length > 45 ? `${doc.url.slice(0, 42)}...` : doc.url}
                            </a>
                          </td>
                          <td>
                            <span className="chunk-pill">{doc.chunk_count} chunks</span>
                          </td>
                          <td>
                            <span className="status-badge active">Active</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* ── Services Section ── */}
          <div className="admin-section" id="services" style={{ marginTop: '40px' }}>
            <div className="section-header">
              <div>
                <h2>Manage Services</h2>
                <p className="section-desc">Active government service decision trees and requirements.</p>
              </div>
              <button className="primary-btn-sm">+ New Service</button>
            </div>
            
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {services.map(svc => (
                    <tr key={svc.id}>
                      <td><code>{svc.service_code}</code></td>
                      <td>{svc.title_en}</td>
                      <td><span className="status-badge active">Active</span></td>
                      <td>
                        <button className="action-btn">Edit</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
