import { useState } from 'react';
import { Send, MapPin } from 'lucide-react';
import API from '../api';

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', message: '' });
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setSuccess(false); setLoading(true);
    try {
      await API.post('/contact_us/', {
        name: form.name,
        email: form.email,
        message: form.message,
      });
      setSuccess(true);
      setForm({ name: '', email: '', message: '' });
      // Auto-hide success message after 4 seconds
      setTimeout(() => setSuccess(false), 4000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>📧 Contact Us</h1>
        <p>Have questions? We'd love to hear from you.</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 24, maxWidth: 900, margin: '0 auto' }}>
        <div className="glass-card" style={{ padding: 36 }}>
          <h3 style={{ marginBottom: 20 }}>📍 Get in Touch</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <p className="form-label" style={{ marginBottom: 2 }}>Email</p>
              <p style={{ color: 'var(--text-primary)', fontSize: 14 }}>smartagri2026@gmail.com</p>
            </div>
            <div>
              <p className="form-label" style={{ marginBottom: 2 }}>Phone</p>
              <p style={{ color: 'var(--text-primary)', fontSize: 14 }}>+91 98765 43210</p>
            </div>
            <div>
              <p className="form-label" style={{ marginBottom: 2 }}>Location</p>
              <p style={{ color: 'var(--text-primary)', fontSize: 14 }}>Islington College, Kamal Marg, Kathmandu 44600</p>
            </div>
          </div>
          <div style={{ marginTop: 20, borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border-input)', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <a 
              href="https://www.google.com/maps/place/Islington+College/@27.7060791,85.3210451,17z/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="map-link"
              style={{ display: 'block', position: 'relative' }}
            >
              <img 
                src="/src/assets/college_map.png" 
                alt="Islington College Map" 
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
                style={{ width: '100%', height: '200px', objectFit: 'cover', display: 'block' }} 
              />
              <div style={{
                width: '100%', height: '200px', 
                background: 'linear-gradient(135deg, #2d3436 0%, #000000 100%)',
                display: 'none', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                gap: '12px', color: 'white'
              }}>
                <MapPin size={40} style={{ opacity: 0.8 }} />
                <span style={{ fontSize: '13px', fontWeight: '500', opacity: 0.7 }}>Open in Google Maps</span>
              </div>
              <div style={{
                position: 'absolute', bottom: '10px', right: '10px',
                background: 'rgba(255,255,255,0.95)', padding: '6px 14px',
                borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '6px',
                fontSize: '11px', fontWeight: '700', color: '#1a1a1a',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)', backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255,255,255,0.5)'
              }}>
                <MapPin size={14} /> Live Map
              </div>
            </a>
          </div>
        </div>
        <div className="glass-card" style={{ padding: 36 }}>
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">✅ Message sent successfully!</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Your Name</label>
              <input className="form-input" placeholder="John Doe" required
                value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className="form-input" type="email" placeholder="you@example.com" required
                value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Message</label>
              <textarea className="form-input" rows={4} placeholder="Write your message..." required style={{ resize: 'vertical' }}
                value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} />
            </div>
            <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
              {loading ? <div className="spinner" /> : <><Send size={18} /> Send Message</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
