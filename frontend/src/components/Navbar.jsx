import React from 'react';
import { Sun, Moon, Database, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ 
  activePage, 
  theme, 
  toggleTheme, 
  backendStatus, 
  currentFileName 
}) {
  const pageTitles = {
    dashboard: 'Dataset Quality Overview',
    analyze: 'Upload & Quality Analysis',
    cleaning: 'Interactive Data Cleansing',
    reports: 'Comprehensive Quality Audit',
    about: 'Methodology & Architecture',
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="topbar-title">{pageTitles[activePage] || 'Dashboard'}</h1>
        {currentFileName ? (
          <div className="topbar-badge">
            <Database size={13} />
            <span>{currentFileName}</span>
          </div>
        ) : (
          <div className="topbar-badge" style={{ backgroundColor: 'var(--bg-card-subtle)', color: 'var(--text-muted)' }}>
            No dataset loaded
          </div>
        )}
      </div>

      <div className="topbar-right">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
          {backendStatus === 'healthy' ? (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--success-600)' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--success-500)', display: 'inline-block' }}></span>
              API Connected
            </span>
          ) : (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--danger-500)' }}>
              <AlertCircle size={14} />
              API Disconnected
            </span>
          )}
        </div>

        <button 
          className="icon-btn" 
          onClick={toggleTheme} 
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
