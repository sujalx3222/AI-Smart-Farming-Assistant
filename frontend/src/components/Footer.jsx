import { Sprout } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-glass)',
      padding: '24px',
      textAlign: 'center',
      color: 'var(--text-muted)',
      fontSize: '13px',
      marginTop: '60px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '6px' }}>
        <Sprout size={16} style={{ color: 'var(--olive-green)' }} />
        <span style={{ fontFamily: 'Outfit', fontWeight: 600, color: 'var(--text-secondary)' }}>AgriSmart</span>
      </div>
      Smart Agriculture Recommendation System &bull; FYP Project 2026
    </footer>
  );
}
