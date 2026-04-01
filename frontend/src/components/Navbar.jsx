import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Sprout, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';
import './Navbar.css';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [logoutMsg, setLogoutMsg] = useState('');
  const userName = localStorage.getItem('user_name');
  const userRole = localStorage.getItem('user_role');

  const links = [
    { to: '/', label: 'Home' },
    { to: '/crop', label: 'Crop' },
    { to: '/soil', label: 'Soil' },
    { to: '/vegetable', label: 'Vegetable' },
    { to: '/climate', label: 'Climate' },
    { to: '/leaf-disease', label: 'Leaf Disease' },
    { to: '/nutrition', label: 'Nutrition' },
    { to: '/contact', label: 'Contact' },
    { to: '/about', label: 'About Us' },
  ];

  // Only show Dashboard link for admin users
  if (userRole === 'admin') {
    links.push({ to: '/admin', label: 'Dashboard' });
  }

  const handleLogout = () => {
    setLogoutMsg('Logout successful! See you soon.');
    localStorage.clear();
    setTimeout(() => {
      setLogoutMsg('');
      navigate('/login');
    }, 1500);
  };

  return (
    <>
      {logoutMsg && (
        <div style={{
          position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)',
          background: 'var(--green-success)', color: 'white', padding: '12px 24px',
          borderRadius: '8px', zIndex: 9999, fontWeight: 600, boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          {logoutMsg}
        </div>
      )}
      <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          <Sprout size={28} />
          <span>AgriSmart</span>
        </Link>

        <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="navbar-actions">
          {userName ? (
            <div className="user-area">
              <span className="user-badge">{userName[0]?.toUpperCase()}</span>
              <button className="logout-btn" onClick={handleLogout} title="Logout">
                <LogOut size={18} />
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-primary" style={{ padding: '10px 24px', fontSize: '13px' }}>
              Login
            </Link>
          )}
        </div>
      </div>
      </nav>
    </>
  );
}
