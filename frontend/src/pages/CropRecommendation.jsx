import { useState } from 'react';
import { Sprout } from 'lucide-react';
import API from '../api';

export default function CropRecommendation() {
  const [form, setForm] = useState({ n: '', p: '', k: '', temperature: '', humidity: '', ph: '', rainfall: '' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fields = [
    { key: 'n', label: 'Nitrogen (N)', placeholder: 'e.g. 90', min: 0, max: 200 },
    { key: 'p', label: 'Phosphorus (P)', placeholder: 'e.g. 42', min: 0, max: 200 },
    { key: 'k', label: 'Potassium (K)', placeholder: 'e.g. 43', min: 0, max: 200 },
    { key: 'temperature', label: 'Temperature (°C)', placeholder: 'e.g. 25', min: -10, max: 60 },
    { key: 'humidity', label: 'Humidity (%)', placeholder: 'e.g. 80', min: 0, max: 100 },
    { key: 'ph', label: 'Soil pH', placeholder: 'e.g. 6.5', step: '0.1', min: 0, max: 14 },
    { key: 'rainfall', label: 'Rainfall (mm)', placeholder: 'e.g. 200', min: 0, max: 1000 },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setResult(null); 

    // Agricultural Validation
    const validation = [
      { condition: parseFloat(form.n) < 0 || parseFloat(form.n) > 200, msg: '🧪 Nitrogen levels should be between 0 and 200.' },
      { condition: parseFloat(form.p) < 0 || parseFloat(form.p) > 200, msg: '🧪 Phosphorus levels should be between 0 and 200.' },
      { condition: parseFloat(form.k) < 0 || parseFloat(form.k) > 200, msg: '🧪 Potassium levels should be between 0 and 200.' },
      { condition: parseFloat(form.temperature) < -10 || parseFloat(form.temperature) > 60, msg: '🌡️ Temperature must be between -10°C and 60°C.' },
      { condition: parseFloat(form.humidity) < 0 || parseFloat(form.humidity) > 100, msg: '💧 Humidity must be between 0 and 100.' },
      { condition: parseFloat(form.ph) < 0 || parseFloat(form.ph) > 14, msg: '🌱 Soil pH must be between 0 and 14.' },
      { condition: parseFloat(form.rainfall) < 0 || parseFloat(form.rainfall) > 2000, msg: '🌧️ Rainfall must be between 0 and 2000mm.' },
    ];

    const failed = validation.find(v => v.condition);
    if (failed) {
      setError(failed.msg);
      return;
    }

    setLoading(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      const uid = localStorage.getItem('user_id');
      if (uid) fd.append('user_id', uid);
      const res = await API.post('/recommend_crop/', fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Please ensure all values are within typical environmental ranges.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🌾 Crop Recommendation</h1>
        <p>Enter soil and climate parameters to get an AI-powered crop suggestion</p>
      </div>
      <div className="glass-card" style={{ maxWidth: 600, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {fields.map(f => (
              <div className="form-group" key={f.key}>
                <label className="form-label">{f.label}</label>
                <input className="form-input" type="number" step={f.step || '1'} 
                   placeholder={f.placeholder} required
                  value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
              </div>
            ))}
          </div>
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 12 }}>
            {loading ? <div className="spinner" /> : <><Sprout size={18} /> Recommend Crop</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '32px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>Top recommendation</p>
              <h1 style={{ fontSize: '3rem', color: 'var(--olive-green)', margin: 0, fontFamily: "'Playfair Display', serif" }}>{result.recommended_crop}</h1>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20 }}>
              <div className="glass-card" style={{ padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(107, 142, 35, 0.1)' }}>
                <h4 style={{ fontSize: 14, color: 'var(--soil-brown)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>📖 About Crop</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.details.desc}</p>
              </div>
              <div className="glass-card" style={{ padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(107, 142, 35, 0.1)' }}>
                <h4 style={{ fontSize: 14, color: 'var(--soil-brown)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>💎 Market Demand</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.details.market}</p>
              </div>
              <div className="glass-card" style={{ padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(107, 142, 35, 0.1)' }}>
                <h4 style={{ fontSize: 14, color: 'var(--soil-brown)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>⏳ Growth Duration</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.details.time}</p>
              </div>
              <div className="glass-card" style={{ padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(107, 142, 35, 0.1)' }}>
                <h4 style={{ fontSize: 14, color: 'var(--soil-brown)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>🚜 Cultivation Care</h4>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.details.care}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
