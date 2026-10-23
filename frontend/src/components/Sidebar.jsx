import React from 'react';
import { 
  LayoutDashboard, 
  FileSpreadsheet, 
  Sparkles, 
  FileText, 
  Info, 
  ShieldCheck, 
  Layers
} from 'lucide-react';

export default function Sidebar({ activePage, setActivePage, hasData }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analyze', label: 'Analyze Dataset', icon: FileSpreadsheet },
    { id: 'cleaning', label: 'Clean Dataset', icon: Sparkles, badge: hasData ? 'Ready' : null },
    { id: 'reports', label: 'Quality Reports', icon: FileText },
    { id: 'about', label: 'About & Formula', icon: Info },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <ShieldCheck size={22} />
        </div>
        <div>
          <div className="sidebar-brand-title">Smart Data Quality</div>
          <div className="sidebar-brand-sub">AI & Data Science Suite</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={18} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge && (
                <span className="badge badge-info" style={{ fontSize: '10px' }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8' }}>
          <Layers size={14} />
          <span>v1.0.0 Student Portfolio</span>
        </div>
        <div style={{ fontSize: '11px', color: '#64748b' }}>
          Explainable Data Hygiene Engine
        </div>
      </div>
    </aside>
  );
}
