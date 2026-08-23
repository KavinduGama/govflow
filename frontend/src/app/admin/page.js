"use client";

import { useState, useEffect } from 'react';
import Header from '../../components/layout/Header';
import './admin.css';
import Link from 'next/link';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch stats and services in parallel
    Promise.all([
      fetch('http://localhost:8000/api/v1/admin/dashboard').then(res => res.json()),
      fetch('http://localhost:8000/api/v1/admin/services').then(res => res.json())
    ])
      .then(([statsData, servicesData]) => {
        setStats(statsData);
        setServices(servicesData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Admin fetch error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
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
            <a href="#" className="active">Dashboard</a>
            <a href="#">Services</a>
            <a href="#">Users</a>
            <a href="#">Settings</a>
          </nav>
        </div>
        
        <div className="admin-main fade-in-up">
          <div className="admin-header">
            <h1>Dashboard Overview</h1>
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
                <h3>Source URLs</h3>
                <div className="stat-value">{stats.source_documents}</div>
              </div>
            </div>
          )}

          <div className="admin-section">
            <div className="section-header">
              <h2>Manage Services</h2>
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
