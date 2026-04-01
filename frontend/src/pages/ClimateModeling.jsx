import { useState } from 'react';
import { Sun } from 'lucide-react';
import API from '../api';

export default function ClimateModeling() {
  const [form, setForm] = useState({ temperature: '', humidity: '', soil_moisture: '', sunlight_hours: '', wind_speed: '' });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fields = [
    { key: 'temperature', label: 'Temperature (°C)', placeholder: 'e.g. 30' },
    { key: 'humidity', label: 'Humidity (%)', placeholder: 'e.g. 75' },
    { key: 'soil_moisture', label: 'Soil Moisture (%)', placeholder: 'e.g. 40' },
    { key: 'sunlight_hours', label: 'Sunlight (hours)', placeholder: 'e.g. 8' },
    { key: 'wind_speed', label: 'Wind Speed (km/h)', placeholder: 'e.g. 15' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setResult('');

    // Agricultural Validation
    const validation = [
      { condition: parseFloat(form.temperature) < -10 || parseFloat(form.temperature) > 60, msg: '🌡️ Temperature must be between -10°C and 60°C for accurate modeling.' },
      { condition: parseFloat(form.humidity) < 0 || parseFloat(form.humidity) > 100, msg: '💧 Humidity must be a valid percentage (0-100%).' },
      { condition: parseFloat(form.soil_moisture) < 0 || parseFloat(form.soil_moisture) > 100, msg: '💧 Soil Moisture should be between 0% and 100%.' },
      { condition: parseFloat(form.sunlight_hours) < 0 || parseFloat(form.sunlight_hours) > 24, msg: '☀️ Sunlight hours cannot exceed 24 hours per day.' },
      { condition: parseFloat(form.wind_speed) < 0 || parseFloat(form.wind_speed) > 200, msg: '💨 Wind speed above 200 km/h is extreme. Please verify the input.' },
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
      const res = await API.post('/climate_modeling/', fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Climate modeling failed. Please check your environmental values.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🌤️ Micro-Climate Modeling</h1>
        <p>Predict micro-climate trends for precision agriculture</p>
      </div>
      <div className="glass-card" style={{ maxWidth: 550, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          {fields.map(f => (
            <div className="form-group" key={f.key}>
              <label className="form-label">{f.label}</label>
              <input className="form-input" type="number" placeholder={f.placeholder} required
                value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
            </div>
          ))}
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? <div className="spinner" /> : <><Sun size={18} /> Model Climate</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '24px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)' }}>Best Crop for this Climate</p>
              <h2 style={{ fontSize: '2.4rem', color: 'var(--olive-green)', margin: 0 }}>{result.predicted_crop}</h2>
            </div>
            
            <div className="glass-card" style={{ marginTop: 16, padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
              <h4 style={{ fontSize: 14, color: '#8b5cf6', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>⚠️ Climate Advisory</h4>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.risk_advice}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
