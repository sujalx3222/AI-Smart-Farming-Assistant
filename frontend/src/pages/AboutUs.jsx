import { Sprout, Target, Lightbulb, GraduationCap } from 'lucide-react';
import './AboutUs.css';

export default function AboutUs() {
  return (
    <div className="about-page">
      {/* Hero */}
      <section className="about-hero">
        <div className="about-hero-glow" />
        <div className="about-hero-content">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 9999, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', color: 'var(--emerald-400)', fontSize: 13, fontWeight: 600, marginBottom: 20 }}>
            <GraduationCap size={14} /> Final Year Project 2026
          </div>
          <h1>About <span className="gradient-text">AgriSmart</span></h1>
          <p>A Smart Agriculture Recommendation System powered by Artificial Intelligence, designed to help farmers make data-driven decisions for better crop yields and sustainable farming.</p>
        </div>
      </section>

      {/* Mission / Vision / Goal */}
      <section className="about-section">
        <div className="values-grid">
          <div className="glass-card value-card">
            <div className="value-icon" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>
              <Target size={28} />
            </div>
            <h3>Our Mission</h3>
            <p>To bridge the gap between technology and agriculture by providing farmers with accessible AI-powered tools for crop recommendation, disease detection, and soil analysis.</p>
          </div>
          <div className="glass-card value-card">
            <div className="value-icon" style={{ background: 'rgba(59,130,246,0.1)', color: '#3b82f6' }}>
              <Lightbulb size={28} />
            </div>
            <h3>Our Vision</h3>
            <p>A future where every farmer, regardless of scale, can leverage artificial intelligence to maximize yield, minimize waste, and practice sustainable agriculture.</p>
          </div>
          <div className="glass-card value-card">
            <div className="value-icon" style={{ background: 'rgba(139,92,246,0.1)', color: '#8b5cf6' }}>
              <Sprout size={28} />
            </div>
            <h3>Our Goal</h3>
            <p>To deliver a unified platform that integrates six AI modules — crop recommendation, soil identification, vegetable suggestion, climate modeling, leaf disease detection, and nutrition prediction.</p>
          </div>
        </div>
      </section>

      {/* About My Project */}
      <section className="about-section">
        <h2 className="section-title">About My Project</h2>
        <p className="section-subtitle">The inspiration and purpose behind AgriSmart</p>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <div className="glass-card" style={{ padding: '40px', marginTop: '20px', textAlign: 'left', lineHeight: '1.8', color: 'var(--text-secondary)' }}>
            <p style={{ marginBottom: '16px' }}>
              AgriSmart was uniquely developed as a Final Year Project to solve real-world agricultural challenges using modern technology. The primary goal is to empower farmers and agricultural enthusiasts with accessible, data-driven insights. 
            </p>
            <p>
              By successfully integrating advanced machine learning models for crop recommendation, soil identification, climate modeling, and disease detection, this platform aims to reduce crop waste, optimize resource usage, and improve overall yield in a sustainable manner.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
