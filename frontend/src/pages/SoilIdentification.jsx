import { useState } from 'react';
import { FlaskConical } from 'lucide-react';
import API from '../api';

export default function SoilIdentification() {
  const [form, setForm] = useState({ ph: '', moisture: '', nitrogen: '', phosphorus: '', potassium: '' });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fields = [
    { key: 'ph', label: 'Soil pH', placeholder: 'e.g. 6.5', step: '0.1', min: 0, max: 14 },
    { key: 'moisture', label: 'Soil Moisture (%)', placeholder: 'e.g. 45', min: 0, max: 100 },
    { key: 'nitrogen', label: 'Nitrogen (N)', placeholder: 'e.g. 50', min: 0, max: 500 },
    { key: 'phosphorus', label: 'Phosphorus (P)', placeholder: 'e.g. 30', min: 0, max: 500 },
    { key: 'potassium', label: 'Potassium (K)', placeholder: 'e.g. 40', min: 0, max: 500 },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setResult('');

    // Agricultural Range Validation
    const validation = [
      { condition: parseFloat(form.ph) < 0 || parseFloat(form.ph) > 14, msg: '🌱 pH should be between 0 and 14. Standard soil is usually between 4 and 9.' },
      { condition: parseFloat(form.moisture) < 0 || parseFloat(form.moisture) > 100, msg: '💧 Moisture percentage must be between 0% and 100%.' },
      { condition: parseFloat(form.nitrogen) < 0 || parseFloat(form.nitrogen) > 500, msg: '🧪 Nitrogen levels must be between 0 and 500.' },
      { condition: parseFloat(form.phosphorus) < 0 || parseFloat(form.phosphorus) > 500, msg: '🧪 Phosphorus levels must be between 0 and 500.' },
      { condition: parseFloat(form.potassium) < 0 || parseFloat(form.potassium) > 500, msg: '🧪 Potassium levels must be between 0 and 500.' },
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
      const res = await API.post('/identify_soil/', fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Our system could not process this data. Please ensure the values are realistic.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🌱 Soil Type Identification</h1>
        <p>Identify your soil type based on key chemical parameters</p>
      </div>
      <div className="glass-card" style={{ maxWidth: 550, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          {fields.map(f => (
            <div className="form-group" key={f.key}>
              <label className="form-label">{f.label}</label>
              <input className="form-input" type="number" step={f.step || '1'} 
                placeholder={f.placeholder} required
                value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
            </div>
          ))}
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? <div className="spinner" /> : <><FlaskConical size={18} /> Identify Soil</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '24px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)' }}>Predicted Soil Type</p>
              <h2 style={{ fontSize: '2rem', color: 'var(--soil-brown)', margin: 0 }}>{result.soil_type}</h2>
            </div>

            <div className="glass-card" style={{ marginTop: 16, padding: 20, background: 'rgba(255,255,255,0.4)', border: '1px solid rgba(194, 166, 121, 0.2)' }}>
              <h4 style={{ fontSize: 14, color: 'var(--olive-green)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                🌾 Recommended Crops
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {result.recommended_crops.map((crop, idx) => (
                  <span key={idx} className="badge badge-success" style={{ fontSize: 13, padding: '4px 12px' }}>{crop}</span>
                ))}
              </div>
              
              <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid rgba(194, 166, 121, 0.15)' }} />
              
              <h4 style={{ fontSize: 14, color: 'var(--soil-brown)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                💡 Management Tips
              </h4>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{result.management_tips}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
