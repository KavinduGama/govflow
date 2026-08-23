import Header from '../../components/layout/Header';

export default function About() {
  return (
    <>
      <Header />
      <main className="main-content">
        <div style={{ maxWidth: '1200px', margin: '4rem auto', padding: '0 2rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }} className="fade-in-up">
            <h1 className="gradient-text" style={{ fontSize: '3rem', marginBottom: '1rem' }}>About GovFlow AI</h1>
            <p className="hero-subtitle" style={{ margin: '0 auto', maxWidth: '600px' }}>
              Simplifying Sri Lankan government services with intelligent, conversational AI.
            </p>
          </div>
          
          <div className="glass-card fade-in-up" style={{maxWidth: '800px', margin: '0 auto', padding: '3rem', animationDelay: '0.2s'}}>
            <h2 style={{fontSize: '1.8rem', marginBottom: '1.5rem', color: 'var(--text-main)'}}>Our Mission</h2>
            <p style={{color: 'var(--text-muted)', lineHeight: '1.7', marginBottom: '2rem'}}>
              GovFlow AI was built to bridge the gap between citizens and government bureaucracy. 
              By leveraging advanced language models and deterministic rule engines, we provide accurate, 
              personalized, and easy-to-follow guidance for complex procedures like getting a National Identity Card or renewing a Driving Licence.
            </p>
            
            <h2 style={{fontSize: '1.8rem', marginBottom: '1.5rem', color: 'var(--text-main)'}}>How it works</h2>
            <ul style={{color: 'var(--text-muted)', lineHeight: '1.7', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
              <li><strong>Select a Service:</strong> Browse our database of verified official procedures.</li>
              <li><strong>Chat with AI:</strong> Our assistant asks you specific questions to determine your exact requirements and eligibility.</li>
              <li><strong>Get Your Plan:</strong> Receive a tailored, step-by-step workflow with exactly what documents you need and where you need to go.</li>
            </ul>
          </div>
        </div>
      </main>
    </>
  );
}
