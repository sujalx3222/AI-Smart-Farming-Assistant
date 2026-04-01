import { useState } from 'react';
import { Carrot } from 'lucide-react';
import API from '../api';

export default function VegetableRecommendation() {
  const [form, setForm] = useState({ temperature: '', season: '', soil_type: '' });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setResult('');

    // Agricultural Validation
    if (parseFloat(form.temperature) < -10 || parseFloat(form.temperature) > 60) {
      setError('🌡️ Temperature must be between -10°C and 60°C for a realistic recommendation.');
      return;
    }

    setLoading(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      const uid = localStorage.getItem('user_id');
      if (uid) fd.append('user_id', uid);
      const res = await API.post('/vegetable_recommendation/', fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Please ensure your climatic data is realistic.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🥕 Vegetable Recommendation</h1>
        <p>Get AI-powered vegetable suggestions based on your conditions</p>
      </div>
      <div className="glass-card" style={{ maxWidth: 550, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Temperature (°C)</label>
            <input className="form-input" type="number" placeholder="e.g. 28" required
              value={form.temperature} onChange={e => setForm({ ...form, temperature: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Season</label>
            <select className="form-select" required value={form.season} onChange={e => setForm({ ...form, season: e.target.value })}>
              <option value="">Select Season</option>
              <option value="Summer">Summer</option>
              <option value="Winter">Winter</option>
              <option value="Rainy">Rainy</option>
              <option value="Monsoon">Monsoon</option>
              <option value="Spring">Spring</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Soil Type</label>
            <select className="form-select" required value={form.soil_type} onChange={e => setForm({ ...form, soil_type: e.target.value })}>
              <option value="">Select Soil Type</option>
              <option value="Loamy">Loamy</option>
              <option value="Sandy">Sandy</option>
              <option value="Clay">Clay</option>
              <option value="Peaty">Peaty</option>
              <option value="Saline">Saline</option>
            </select>
          </div>
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? <div className="spinner" /> : <><Carrot size={18} /> Recommend Vegetable</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '24px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)' }}>Recommended Vegetable</p>
              <h2 style={{ fontSize: '2.4rem', color: 'var(--olive-green)', margin: 0 }}>{result.recommended_vegetable}</h2>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20 }}>
              <div className="glass-card" style={{ padding: 16, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(194, 166, 121, 0.2)' }}>
                <h4 style={{ fontSize: 13, color: 'var(--soil-brown)', marginBottom: 8 }}>📝 About</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.details.description}</p>
              </div>
              <div className="glass-card" style={{ padding: 16, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(194, 166, 121, 0.2)' }}>
                <h4 style={{ fontSize: 13, color: 'var(--soil-brown)', marginBottom: 8 }}>✅ Suitability</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.details.suitability}</p>
              </div>
              <div className="glass-card" style={{ padding: 16, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(194, 166, 121, 0.2)' }}>
                <h4 style={{ fontSize: 13, color: 'var(--soil-brown)', marginBottom: 8 }}>💡 Grow Tips</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.details.tips}</p>
              </div>
              <div className="glass-card" style={{ padding: 16, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(194, 166, 121, 0.2)' }}>
                <h4 style={{ fontSize: 13, color: 'var(--soil-brown)', marginBottom: 8 }}>🍎 Health Benefit</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.details.benefit}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
