import React from 'react';

export default function MetricCard({ 
  title, 
  value, 
  subtext, 
  icon: Icon, 
  variant = 'default',
  badgeText
}) {
  const variantStyles = {
    default: {
      iconBg: 'var(--primary-50)',
      iconColor: 'var(--primary-600)',
    },
    success: {
      iconBg: 'var(--success-50)',
      iconColor: 'var(--success-600)',
    },
    warning: {
      iconBg: 'var(--warning-50)',
      iconColor: 'var(--warning-600)',
    },
    danger: {
      iconBg: 'var(--danger-50)',
      iconColor: 'var(--danger-600)',
    },
  };

  const style = variantStyles[variant] || variantStyles.default;

  return (
    <div className="metric-card">
      <div className="metric-header">
        <span>{title}</span>
        <div 
          className="metric-icon-wrap" 
          style={{ backgroundColor: style.iconBg, color: style.iconColor }}
        >
          {Icon && <Icon size={18} />}
        </div>
      </div>
      <div className="metric-value">{value}</div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="metric-sub">{subtext}</div>
        {badgeText && (
          <span className={`badge badge-${variant}`}>
            {badgeText}
          </span>
        )}
      </div>
    </div>
  );
}
