import { useState } from 'react';
import { BarChart3, FlaskConical } from 'lucide-react';
import API from '../api';

export default function NutritionPrediction() {
  const [form, setForm] = useState({ temperature: '', humidity: '', soil_ph: '', rainfall: '', soil_moisture: '' });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fields = [
    { key: 'temperature', label: 'Temperature (°C)', placeholder: 'e.g. 28' },
    { key: 'humidity', label: 'Humidity (%)', placeholder: 'e.g. 70' },
    { key: 'soil_ph', label: 'Soil pH', placeholder: 'e.g. 6.5', step: '0.1' },
    { key: 'rainfall', label: 'Rainfall (mm)', placeholder: 'e.g. 150' },
    { key: 'soil_moisture', label: 'Soil Moisture (%)', placeholder: 'e.g. 35' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setResult('');

    // Agricultural Validation
    const validation = [
      { condition: parseFloat(form.temperature) < -10 || parseFloat(form.temperature) > 60, msg: '🌡️ Temperature must be between -10°C and 60°C.' },
      { condition: parseFloat(form.humidity) < 0 || parseFloat(form.humidity) > 100, msg: '💧 Humidity must be between 0% and 100%.' },
      { condition: parseFloat(form.soil_ph) < 0 || parseFloat(form.soil_ph) > 14, msg: '🌱 pH must be on the standard scale of 0 to 14.' },
      { condition: parseFloat(form.rainfall) < 0 || parseFloat(form.rainfall) > 2000, msg: '🌧️ Rainfall values are outside typical agricultural modeling ranges.' },
      { condition: parseFloat(form.soil_moisture) < 0 || parseFloat(form.soil_moisture) > 100, msg: '💧 Soil moisture must be within 0% to 100%.' },
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
      const res = await API.post('/predict_nutrition/', fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Nutrition prediction failed. Please ensure values are realistic.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🧪 Nutrition Prediction</h1>
        <p>Predict optimal soil nutrients for maximum crop yield</p>
      </div>
      <div className="glass-card prediction-container" style={{ maxWidth: 550, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          {fields.map(f => (
            <div className="form-group" key={f.key}>
              <label className="form-label">{f.label}</label>
              <input className="form-input" type="number" step={f.step || '1'} placeholder={f.placeholder} required
                value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
            </div>
          ))}
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 24 }}>
            {loading ? <div className="spinner" /> : <><FlaskConical size={18} /> Get Recommendation</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '24px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)' }}>Recommended Nutrition Plan</p>
              <h2 style={{ fontSize: '1.8rem', color: 'var(--olive-green)', margin: 0 }}>{result.nutrition_recommendation}</h2>
            </div>
            
            <div className="glass-card" style={{ marginTop: 16, padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(20, 184, 166, 0.2)' }}>
              <h4 style={{ fontSize: 14, color: '#14b8a6', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>🧪 Application Instructions</h4>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.tips}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
