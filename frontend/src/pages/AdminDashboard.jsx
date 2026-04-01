import { useState, useEffect, useRef, useCallback } from 'react';
import { Users, Sprout, Bug, FlaskConical, Sun, Carrot, BarChart3, Mail, RefreshCw, Calendar, ChevronDown, ChevronUp, Clock, Shield, Trash2, Edit, UserPlus, X, Search, CheckCircle, AlertCircle } from 'lucide-react';
import API from '../api';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedMsg, setExpandedMsg] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingFarmer, setEditingFarmer] = useState(null);
  const [farmerForm, setFarmerForm] = useState({ name: '', email: '', password: '', role: 'farmer' });
  const [actionLoading, setActionLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [lastRefreshed, setLastRefreshed] = useState(null);
  const [toast, setToast] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const toastTimeoutRef = useRef(null);

  const showToast = useCallback((type, message) => {
    if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
    setToast({ type, message });
    toastTimeoutRef.current = setTimeout(() => setToast(null), 3500);
  }, []);

  const fetchData = async (isManual = false, silent = false) => {
    if (isManual) setRefreshing(true);
    if (!silent) setLoading(true);
    try {
      const res = await API.get('/api/admin/dashboard/');
      setStats(res.data.stats);
      setActivity(res.data.recent_activity || []);
      setFarmers(res.data.farmers || []);
      setMessages(res.data.messages || []);
      setLastRefreshed(new Date());
      if (isManual) showToast('success', 'Dashboard data refreshed successfully!');
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      if (isManual) showToast('error', 'Failed to refresh: ' + (err.response?.data?.error || err.message));
    } finally {
      if (!silent) setLoading(false);
      setRefreshing(false);
    }
  };

  const handleDeleteFarmer = async (id) => {
    if (!window.confirm('Are you sure you want to delete this farmer? This action cannot be undone.')) return;
    setActionLoading(true);
    try {
      await API.delete(`/api/farmers/${id}/`);
      showToast('success', 'Farmer deleted successfully!');
      fetchData(false, true); // silent refresh
    } catch (err) {
      showToast('error', 'Failed to delete farmer: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleSaveFarmer = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      if (editingFarmer) {
        await API.put(`/api/farmers/${editingFarmer.id}/`, farmerForm);
        showToast('success', 'Farmer updated successfully!');
      } else {
        await API.post('/api/farmers/', farmerForm);
        showToast('success', 'New farmer added successfully!');
      }
      setShowModal(false);
      fetchData(false, true); // silent refresh
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      showToast('error', errorMsg);
    } finally {
      setActionLoading(false);
    }
  };

  const openModal = (farmer = null) => {
    if (farmer) {
      setEditingFarmer(farmer);
      setFarmerForm({ name: farmer.name, email: farmer.email, password: '', role: farmer.role });
    } else {
      setEditingFarmer(null);
      setFarmerForm({ name: '', email: '', password: '', role: 'farmer' });
    }
    setShowModal(true);
  };

  useEffect(() => { fetchData(); }, []);

  // Cleanup toast timeout on unmount
  useEffect(() => {
    return () => { if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current); };
  }, []);

  const formatLastRefreshed = () => {
    if (!lastRefreshed) return '';
    const now = new Date();
    const diff = Math.floor((now - lastRefreshed) / 1000);
    if (diff < 5) return 'Just now';
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return lastRefreshed.toLocaleTimeString();
  };

  const statCards = stats ? [
    { icon: <Users size={24} />, label: 'Total Farmers', value: stats.total_farmers, color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
    { icon: <Sprout size={24} />, label: 'Crop Predictions', value: stats.crop_predictions, color: '#3b82f6', bg: 'rgba(59,130,246,0.1)' },
    { icon: <Bug size={24} />, label: 'Disease Detections', value: stats.disease_detections, color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
    { icon: <FlaskConical size={24} />, label: 'Soil Analyses', value: stats.soil_analysis, color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)' },
    { icon: <Sun size={24} />, label: 'Climate Predictions', value: stats.climate_predictions, color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
    { icon: <Carrot size={24} />, label: 'Vegetable Recs', value: stats.vegetable_recommendations, color: '#06b6d4', bg: 'rgba(6,182,212,0.1)' },
    { icon: <BarChart3 size={24} />, label: 'Nutrition Predictions', value: stats.nutrition_predictions, color: '#14b8a6', bg: 'rgba(20,184,166,0.1)' },
    { icon: <Mail size={24} />, label: 'Contact Messages', value: stats.contact_messages, color: '#ec4899', bg: 'rgba(236,72,153,0.1)' },
  ] : [];

  const totalPredictions = stats
    ? stats.crop_predictions + stats.disease_detections + stats.soil_analysis +
    stats.climate_predictions + stats.vegetable_recommendations + stats.nutrition_predictions
    : 0;

  const tabs = [
    { id: 'overview', label: '📊 Overview' },
    { id: 'farmers', label: '👥 Farmers' },
    { id: 'messages', label: '📧 Messages' },
    { id: 'activity', label: '🕐 Activity' },
  ];

  const filteredFarmers = farmers.filter(f => 
    f.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    f.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredMessages = messages.filter(m => 
    m.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    m.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.message?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredActivity = activity.filter(a => 
    a.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    a.feature_used?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.result?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="page-wrapper" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40, borderWidth: 3 }} />
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">
            <Shield size={32} style={{ color: 'var(--olive-green)' }} />
            Admin Dashboard
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
            System overview &bull; {totalPredictions} total predictions &bull; {stats?.total_farmers || 0} registered farmers
          </p>
        </div>
        
        <div className="header-actions" style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="search-wrapper" style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              placeholder="Search everything..." 
              value={searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)}
              className="dashboard-search"
            />
          </div>

          {/* Refresh button */}
          <button 
            className="btn-secondary btn-refresh" 
            onClick={() => fetchData(true)} 
            disabled={refreshing}
            style={{ gap: 8 }}
          >
            <RefreshCw size={16} className={refreshing ? 'spin-icon' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Last refreshed indicator */}
      {lastRefreshed && (
        <div className="last-refreshed-bar">
          <Clock size={13} />
          <span>Last refreshed: {formatLastRefreshed()}</span>
        </div>
      )}

      {/* Toast notification */}
      {toast && (
        <div className={`toast-notification toast-${toast.type}`}>
          {toast.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{toast.message}</span>
          <button className="toast-close" onClick={() => setToast(null)}><X size={14} /></button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-nav">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Tab: Overview ── */}
      {activeTab === 'overview' && (
        <>
          {/* Stat Cards */}
          <div className="dashboard-stats">
            {statCards.map((s, i) => (
              <div className="glass-card stat-card" key={i}>
                <div className="stat-icon" style={{ background: s.bg, color: s.color }}>{s.icon}</div>
                <div className="stat-info">
                  <h3>{s.value ?? 0}</h3>
                  <p>{s.label}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Usage Chart */}
          <div className="glass-card" style={{ padding: 32, marginBottom: 24 }}>
            <h3 style={{ marginBottom: 24, fontSize: '1.1rem' }}>📈 Feature Usage Breakdown</h3>
            <div className="usage-bars">
              {[
                { label: 'Crop Recommendation', value: stats?.crop_predictions || 0, color: '#3b82f6' },
                { label: 'Disease Detection', value: stats?.disease_detections || 0, color: '#ef4444' },
                { label: 'Soil Analysis', value: stats?.soil_analysis || 0, color: '#8b5cf6' },
                { label: 'Climate Modeling', value: stats?.climate_predictions || 0, color: '#f59e0b' },
                { label: 'Vegetable Recommendation', value: stats?.vegetable_recommendations || 0, color: '#06b6d4' },
                { label: 'Nutrition Prediction', value: stats?.nutrition_predictions || 0, color: '#14b8a6' },
              ].map((bar, i) => {
                const max = Math.max(...[stats?.crop_predictions, stats?.disease_detections, stats?.soil_analysis, stats?.climate_predictions, stats?.vegetable_recommendations, stats?.nutrition_predictions].map(v => v || 0), 1);
                const pct = Math.round(((bar.value || 0) / max) * 100);
                return (
                  <div className="usage-bar-row" key={i}>
                    <span className="bar-label">{bar.label}</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${pct}%`, background: bar.color }} />
                    </div>
                    <span className="bar-value">{bar.value}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Stats Summary */}
          <div className="glass-card" style={{ padding: 32 }}>
            <h3 style={{ marginBottom: 20, fontSize: '1.1rem' }}>⚡ System Summary</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Total Predictions Made</span>
                <span className="summary-value" style={{ color: 'var(--emerald-400)' }}>{totalPredictions}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Avg Predictions/Farmer</span>
                <span className="summary-value">{stats?.total_farmers ? (totalPredictions / stats.total_farmers).toFixed(1) : '0'}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Most Used Feature</span>
                <span className="summary-value" style={{ fontSize: 14 }}>
                  {(() => {
                    const feats = [
                      { n: 'Crop', v: stats?.crop_predictions || 0 },
                      { n: 'Disease', v: stats?.disease_detections || 0 },
                      { n: 'Soil', v: stats?.soil_analysis || 0 },
                      { n: 'Climate', v: stats?.climate_predictions || 0 },
                      { n: 'Vegetable', v: stats?.vegetable_recommendations || 0 },
                      { n: 'Nutrition', v: stats?.nutrition_predictions || 0 },
                    ];
                    const top = feats.reduce((a, b) => a.v > b.v ? a : b);
                    return top.v > 0 ? `${top.n} (${top.v})` : 'N/A';
                  })()}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Unread Messages</span>
                <span className="summary-value" style={{ color: 'var(--amber-400)' }}>{stats?.contact_messages || 0}</span>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ── Tab: Farmers ── */}
      {activeTab === 'farmers' && (
        <div className="glass-card" style={{ padding: 32 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ fontSize: '1.1rem' }}>👥 Registered Farmers ({filteredFarmers.length})</h3>
            <button className="btn-primary" onClick={() => openModal()} style={{ gap: 8, padding: '8px 16px' }}>
              <UserPlus size={16} /> Add Farmer
            </button>
          </div>
          {filteredFarmers.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>{searchTerm ? 'No farmers match your search.' : 'No farmers registered yet.'}</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th><Calendar size={13} style={{ marginRight: 4 }} />Joined</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFarmers.map((f, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{
                            width: 32, height: 32, borderRadius: '50%', background: 'var(--gradient-primary)',
                            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                            color: 'white', fontWeight: 700, fontSize: 13, flexShrink: 0
                          }}>{f.name?.[0]?.toUpperCase() || '?'}</span>
                          {f.name}
                        </div>
                      </td>
                      <td>{f.email}</td>
                      <td>
                        <span className={`badge ${f.role === 'admin' ? 'badge-admin' : 'badge-success'}`} style={{ fontSize: 11 }}>
                          {f.role || 'Farmer'}
                        </span>
                      </td>
                      <td>{new Date(f.joined).toLocaleDateString()}</td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                          <button className="action-btn edit" onClick={() => openModal(f)} title="Edit">
                            <Edit size={16} />
                          </button>
                          <button className="action-btn delete" onClick={() => handleDeleteFarmer(f.id)} title="Delete">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Messages ── */}
      {activeTab === 'messages' && (
        <div className="glass-card" style={{ padding: 32 }}>
          <h3 style={{ marginBottom: 20, fontSize: '1.1rem' }}>📧 Contact Messages ({filteredMessages.length})</h3>
          {filteredMessages.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>{searchTerm ? 'No messages match your search.' : 'No messages received yet.'}</p>
          ) : (
            <div className="messages-list">
              {filteredMessages.map((m, i) => (
                <div className="message-card" key={i} onClick={() => setExpandedMsg(expandedMsg === i ? null : i)}>
                  <div className="message-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{
                        width: 40, height: 40, borderRadius: '50%',
                        background: 'rgba(236,72,153,0.1)', color: '#ec4899',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: 700, fontSize: 15, flexShrink: 0
                      }}>{m.name?.[0]?.toUpperCase() || '?'}</span>
                      <div>
                        <p style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 14 }}>{m.name}</p>
                        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{m.email}</p>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        <Clock size={12} style={{ marginRight: 4 }} />
                        {new Date(m.date).toLocaleDateString()}
                      </span>
                      {expandedMsg === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>
                  </div>
                  {expandedMsg === i && (
                    <div className="message-body">
                      <p>{m.message}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Activity ── */}
      {activeTab === 'activity' && (
        <div className="glass-card" style={{ padding: 32 }}>
          <h3 style={{ marginBottom: 20, fontSize: '1.1rem' }}>🕐 Recent Activity ({filteredActivity.length})</h3>
          {filteredActivity.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>{searchTerm ? 'No activity matches your search.' : 'No activity yet.'}</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  {/* ... headers ... */}
                </thead>
                <tbody>
                  {filteredActivity.map((a, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-primary)' }}>{a.user_email || 'Anonymous'}</td>
                      <td>
                        <span className="badge badge-success" style={{ fontSize: 11 }}>{a.feature_used}</span>
                      </td>
                      <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {a.result || '—'}
                      </td>
                      <td>{new Date(a.timestamp).toLocaleString()}</td>
                      <td>
                        <span style={{ color: 'var(--emerald-400)', fontSize: 13 }}>✓ {a.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Farmer Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card animated fadeIn">
            <div className="modal-header">
              <h2>{editingFarmer ? 'Edit Farmer' : 'Add New Farmer'}</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}><X size={20} /></button>
            </div>
            <form onSubmit={handleSaveFarmer}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-input" type="text" value={farmerForm.name} required
                  onChange={e => setFarmerForm({...farmerForm, name: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input className="form-input" type="email" value={farmerForm.email} required
                  onChange={e => setFarmerForm({...farmerForm, email: e.target.value})} />
              </div>
              {!editingFarmer && (
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input className="form-input" type="password" value={farmerForm.password} required
                    onChange={e => setFarmerForm({...farmerForm, password: e.target.value})} />
                </div>
              )}
              <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
                <button className="btn-secondary" type="button" onClick={() => setShowModal(false)} style={{ flex: 1 }}>Cancel</button>
                <button className="btn-primary" type="submit" disabled={actionLoading} style={{ flex: 1 }}>
                  {actionLoading ? <div className="spinner" /> : (editingFarmer ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
