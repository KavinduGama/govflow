"use client";

import { useState, useEffect } from 'react';
import Header from '../../components/layout/Header';
import './workflow.css';
import Link from 'next/link';

export default function Workflow() {
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completedSteps, setCompletedSteps] = useState({});
  const [completedDocs, setCompletedDocs] = useState({});

  useEffect(() => {
    // Load workflow from localStorage
    const saved = localStorage.getItem('govflow_current_workflow');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setWorkflow(parsed);
        
        // Also try to load progress if it exists for this service
        const savedProgress = localStorage.getItem(`govflow_progress_${parsed.service_code}`);
        if (savedProgress) {
          const { steps, docs } = JSON.parse(savedProgress);
          if (steps) setCompletedSteps(steps);
          if (docs) setCompletedDocs(docs);
        }
      } catch (e) {
        console.error("Failed to parse workflow", e);
      }
    }
    setLoading(false);
  }, []);

  const toggleStep = (stepId) => {
    const nextState = { ...completedSteps, [stepId]: !completedSteps[stepId] };
    setCompletedSteps(nextState);
    saveProgress(nextState, completedDocs);
  };

  const toggleDoc = (docKey) => {
    const nextState = { ...completedDocs, [docKey]: !completedDocs[docKey] };
    setCompletedDocs(nextState);
    saveProgress(completedSteps, nextState);
  };

  const saveProgress = (steps, docs) => {
    if (workflow) {
      localStorage.setItem(`govflow_progress_${workflow.service_code}`, JSON.stringify({
        steps, docs
      }));
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <main className="main-content">
          <div className="workflow-container loading-skeleton fade-in"></div>
        </main>
      </>
    );
  }

  if (!workflow) {
    return (
      <>
        <Header />
        <main className="main-content">
          <div className="error-container fade-in">
            <h2>No Procedure Found</h2>
            <p>We couldn't find your generated procedure. Please start a chat to generate one.</p>
            <Link href="/services" className="primary-btn">Go to Services</Link>
          </div>
        </main>
      </>
    );
  }

  const stepsDone = Object.values(completedSteps).filter(Boolean).length;
  const docsDone = Object.values(completedDocs).filter(Boolean).length;
  const totalSteps = workflow.steps?.length || 0;
  const totalDocs = workflow.documents?.length || 0;
  
  const stepProgress = totalSteps > 0 ? (stepsDone / totalSteps) * 100 : 0;
  const docProgress = totalDocs > 0 ? (docsDone / totalDocs) * 100 : 0;

  return (
    <>
      <Header />
      <main className="main-content workflow-bg">
        <div className="workflow-container fade-in-up">
          <div className="workflow-header">
            <Link href="/services" className="back-link">← Back to Services</Link>
            <h1>Your Personalized Procedure</h1>
            <h2>{workflow.service_name}</h2>
          </div>

          <div className="workflow-grid">
            <div className="workflow-main">
              <div className="section-header">
                <h3>Step-by-Step Guide</h3>
                <span className="progress-text">{stepsDone} of {totalSteps} completed</span>
              </div>
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: `${stepProgress}%` }}></div>
              </div>

              <div className="timeline">
                {workflow.steps?.map((step, idx) => (
                  <div 
                    key={step.id} 
                    className={`timeline-item ${completedSteps[step.id] ? 'completed' : ''}`}
                  >
                    <div className="timeline-marker" onClick={() => toggleStep(step.id)}>
                      {completedSteps[step.id] ? '✓' : idx + 1}
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <h4>{step.title}</h4>
                        {step.location_type && (
                          <span className="location-badge">📍 {step.location_type}</span>
                        )}
                      </div>
                      <p>{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="workflow-sidebar">
              <div className="checklist-card">
                <div className="section-header">
                  <h3>Required Documents</h3>
                  <span className="progress-text">{docsDone} of {totalDocs}</span>
                </div>
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill docs-fill" style={{ width: `${docProgress}%` }}></div>
                </div>
                
                <div className="document-list">
                  {workflow.documents?.map((doc) => (
                    <label key={doc.document_key} className={`doc-item ${completedDocs[doc.document_key] ? 'completed' : ''}`}>
                      <input 
                        type="checkbox" 
                        checked={!!completedDocs[doc.document_key]}
                        onChange={() => toggleDoc(doc.document_key)}
                      />
                      <div className="doc-content">
                        <div className="doc-header">
                          <span className="doc-name">{doc.name}</span>
                          {doc.requirement_type === 'optional' && <span className="optional-badge">Optional</span>}
                        </div>
                        {doc.description && <p className="doc-desc">{doc.description}</p>}
                      </div>
                    </label>
                  ))}
                  {(!workflow.documents || workflow.documents.length === 0) && (
                    <p className="no-docs">No specific documents required.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
