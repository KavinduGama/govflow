"use client";

import { useState, useEffect } from 'react';
import Header from '../../components/layout/Header';
import './services.css';
import Link from 'next/link';
import { API_URL } from "@/lib/api";

export default function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/services`)
      .then(res => res.json())
      .then(data => {
        setServices(data.services || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch services:", err);
        setLoading(false);
      });
  }, []);

  return (
    <>
      <Header />
      <main className="main-content">
        <div className="services-container">
          <div className="services-header fade-in-up">
            <h1 className="gradient-text">Government Services</h1>
            <p className="hero-subtitle">
              Browse the official procedures and let our AI guide you through every step.
            </p>
          </div>

          <div className="services-grid">
            {loading ? (
              Array(6).fill(0).map((_, i) => (
                <div key={i} className="loading-pulse fade-in-up" style={{animationDelay: `${i * 0.1}s`}}></div>
              ))
            ) : (
              services.map((svc, index) => (
                <Link href={`/services/${svc.service_code}`} key={svc.id} style={{textDecoration: 'none'}}>
                  <div className="service-card fade-in-up" style={{animationDelay: `${index * 0.1}s`}}>
                    <div className="service-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                      </svg>
                    </div>
                    <div>
                      <div className="service-dept">{svc.department?.name_en || "Official Procedure"}</div>
                      <h2 className="service-title">{svc.title_en}</h2>
                    </div>
                    <p className="service-desc">{svc.description || "Get an interactive step-by-step guide for this service using GovFlow AI."}</p>
                    
                    <div className="service-action">
                      View Details <span>→</span>
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </main>
    </>
  );
}
