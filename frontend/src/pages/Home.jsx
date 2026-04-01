import { Link } from 'react-router-dom';
import { Sprout, Leaf, Sun, FlaskConical, Carrot, Bug, BarChart3, ArrowRight } from 'lucide-react';
import './Home.css';

const features = [
  { icon: <Sprout size={28} />, title: 'Crop Recommendation', desc: 'AI-powered crop suggestions based on soil & climate data.', to: '/crop', color: '#2e7d32' },
  { icon: <FlaskConical size={28} />, title: 'Soil Identification', desc: 'Classify your soil type using key parameters.', to: '/soil', color: '#5c4033' },
  { icon: <Carrot size={28} />, title: 'Vegetable Recommendation', desc: 'Get optimal vegetable suggestions for your conditions.', to: '/vegetable', color: '#d4a017' },
  { icon: <Sun size={28} />, title: 'Micro-Climate Modeling', desc: 'Predict micro-climate trends for precision farming.', to: '/climate', color: '#d4a017' },
  { icon: <Bug size={28} />, title: 'Leaf Disease Detection', desc: 'Upload leaf images to detect diseases instantly.', to: '/leaf-disease', color: '#c0392b' },
  { icon: <BarChart3 size={28} />, title: 'Nutrition Prediction', desc: 'Predict optimal soil nutrients for maximum yield.', to: '/nutrition', color: '#6b8e23' },
];

export default function Home() {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-glow" />
        <div className="hero-content">
          <div className="hero-badge">
            <Leaf size={14} /> AI-Powered Agriculture
          </div>
          <h1 className="hero-title">
            Smart Agriculture <br />
            <span className="hero-gradient-text">Recommendation System</span>
          </h1>
          <p className="hero-desc">Harness the power of artificial intelligence to optimize your farming decisions. From crop selection to disease detection — all in one platform.</p>
          <div className="hero-actions">
            <Link to="/register" className="btn-primary">
              Get Started <ArrowRight size={18} />
            </Link>
            <Link to="/crop" className="btn-secondary">
              Explore Features
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="features-section">
        <h2>Our Features</h2>
        <div className="features-grid">
          {features.map((f, i) => (
            <Link to={f.to} key={i} className="feature-card glass-card">
              <div className="feature-icon" style={{ background: `${f.color}15`, color: f.color }}>
                {f.icon}
              </div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              <span className="feature-arrow">
                <ArrowRight size={16} />
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
