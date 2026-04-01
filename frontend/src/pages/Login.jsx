import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogIn, Eye, EyeOff } from 'lucide-react';
import API from '../api';

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('email', form.email);
      formData.append('password', form.password);
      const res = await API.post('/login/', formData);
      
      localStorage.setItem('user_id', res.data.user_id);
      localStorage.setItem('user_name', res.data.user || res.data.user_name || '');
      localStorage.setItem('auth_token', res.data.token);
      localStorage.setItem('user_role', res.data.role || 'farmer');
      
      setSuccess('Login successful! Redirecting to home...');
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container glass-card">
        <div className="auth-header">
          <div className="auth-icon" style={{ background: 'rgba(107, 142, 35, 0.12)', color: 'var(--olive-green)' }}>
            <LogIn size={28} />
          </div>
          <h1>Welcome Back</h1>
          <p>Sign in to your AgriSmart account</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input className="form-input" type="email" placeholder="you@example.com" required
              value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input className="form-input" type={showPw ? 'text' : 'password'} placeholder="Enter your password" required
                value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} 
                minLength="8" />
              <button type="button" onClick={() => setShowPw(!showPw)}
                style={{ position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: '8px' }}>
            {loading ? <div className="spinner" /> : <>Sign In <LogIn size={18} /></>}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register" style={{ color: 'var(--olive-green)', fontWeight: 600 }}>Create one</Link>
        </p>
      </div>
    </div>
  );
}
