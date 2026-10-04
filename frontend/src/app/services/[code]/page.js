"use client";

import { use, useState, useEffect } from 'react';
import Header from '../../../components/layout/Header';
import './service-detail.css';
import Link from 'next/link';

export default function ServiceDetail({ params }) {
  const { code } = use(params);
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/services/${code}`)
      .then(res => {
        if (!res.ok) throw new Error("Service not found");
        return res.json();
      })
      .then(data => {
        setService(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch service:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [code]);

  if (loading) {
    return (
      <>
        <Header />
        <main className="main-content">
          <div className="service-detail-container loading-skeleton fade-in"></div>
        </main>
      </>
    );
  }

  if (error || !service) {
    return (
      <>
        <Header />
        <main className="main-content">
          <div className="error-container fade-in">
            <h2>Oops! Service Not Found</h2>
            <p>We couldn&apos;t find the requested service: {code}</p>
            <Link href="/services" className="back-link">← Back to Services</Link>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="main-content">
        <div className="service-detail-container fade-in-up">
          <Link href="/services" className="back-link">← Back to Services</Link>
          
          <div className="service-header-box">
            <div className="service-icon-large">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <div>
              <span className="badge">{service.department?.name_en || "Official Procedure"}</span>
              <h1 className="service-title-lg">{service.title_en}</h1>
            </div>
          </div>

          <div className="service-content">
            <div className="content-section">
              <h2>About this Service</h2>
              <p>{service.description}</p>
            </div>

            {(service.fee_description || service.processing_time || service.department?.hotline) && (
              <div className="content-section">
                <h2>At a glance</h2>
                <ul className="service-facts">
                  {service.fee_description && <li><strong>Fees:</strong> {service.fee_description}</li>}
                  {service.processing_time && <li><strong>Processing time:</strong> {service.processing_time}</li>}
                  {service.department?.hotline && <li><strong>Hotline:</strong> {service.department.hotline}</li>}
                  {service.department?.website_url && (
                    <li><strong>Official website:</strong>{' '}
                      <a href={service.department.website_url} target="_blank" rel="noopener noreferrer">{service.department.website_url}</a>
                    </li>
                  )}
                </ul>
              </div>
            )}

            <div className="action-card">
              <h3>Need guidance?</h3>
              <p>Our AI assistant will ask you a few simple questions and give you a personalized step-by-step procedure, required documents checklist, and fee details.</p>
              <Link href={`/?service=${service.service_code}`} className="start-btn">
                Start AI Guide
              </Link>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
