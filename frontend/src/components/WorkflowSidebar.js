import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import './WorkflowSidebar.css';
import { API_URL } from "@/lib/api";

export default function WorkflowSidebar({ workflow, onClose, embedded = false }) {
  const { token, user } = useContext(AuthContext);
  const [completedSteps, setCompletedSteps] = useState({});
  const [completedDocs, setCompletedDocs] = useState({});

  useEffect(() => {
    if (workflow) {
      // Always check localStorage first for quick load
      const savedProgress = localStorage.getItem(`govflow_progress_${workflow.service_code}`);
      if (savedProgress) {
        try {
          const { steps, docs } = JSON.parse(savedProgress);
          if (steps) setCompletedSteps(steps);
          if (docs) setCompletedDocs(docs);
        } catch (e) {
          console.error("Failed to parse progress", e);
        }
      }

      // If user is logged in, fetch authoritative progress from backend
      if (token) {
        fetch(`${API_URL}/history/plans`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(plans => {
          const myPlan = plans.find(p => p.service_code === workflow.service_code);
          if (myPlan && myPlan.progress_data) {
            if (myPlan.progress_data.steps) setCompletedSteps(myPlan.progress_data.steps);
            if (myPlan.progress_data.docs) setCompletedDocs(myPlan.progress_data.docs);
          }
        })
        .catch(err => console.error(err));
      }
    }
  }, [workflow, token]);

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
      const dataToSave = { steps, docs };
      localStorage.setItem(`govflow_progress_${workflow.service_code}`, JSON.stringify(dataToSave));
      
      if (token) {
        fetch(`${API_URL}/history/plans/${workflow.service_code}/progress`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ progress_data: dataToSave })
        }).catch(err => console.error("Failed to sync progress:", err));
      }
    }
  };

  if (!workflow) return null;

  const stepsDone = Object.values(completedSteps).filter(Boolean).length;
  const docsDone = Object.values(completedDocs).filter(Boolean).length;
  const totalSteps = workflow.steps?.length || 0;
  const totalDocs = workflow.documents?.length || 0;
  
  const stepProgress = totalSteps > 0 ? (stepsDone / totalSteps) * 100 : 0;
  const docProgress = totalDocs > 0 ? (docsDone / totalDocs) * 100 : 0;

  return (
    <>
      {!embedded && <div className="workflow-sidebar-overlay" onClick={onClose}></div>}
      <div className={`workflow-sidebar-panel ${embedded ? 'embedded' : 'slide-in-right'}`}>
        <div className="workflow-sidebar-header">
          <div className="workflow-sidebar-header-top">
            <h2>Your Procedure Plan</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <h3 className="workflow-service-name">{workflow.service_name}</h3>
        </div>

        <div className="workflow-sidebar-content">
          <div className="workflow-section">
            <div className="section-header">
              <h4>Step-by-Step Guide</h4>
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
                      <h5>{step.title}</h5>
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

          <div className="workflow-section docs-section">
            <div className="section-header">
              <h4>Required Documents</h4>
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
    </>
  );
}
