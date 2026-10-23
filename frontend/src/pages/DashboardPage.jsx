import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend 
} from 'recharts';
import { 
  Database, AlertCircle, Copy, AlertTriangle, 
  CheckCircle2, ArrowRight, ShieldAlert, Sparkles, HelpCircle 
} from 'lucide-react';
import MetricCard from '../components/MetricCard';

const PIE_COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'];

export default function DashboardPage({ report, onNavigate }) {
  if (!report) {
    return (
      <div className="page-container">
        <div className="card" style={{ textAlign: 'center', padding: '64px 24px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'var(--primary-50)',
            color: 'var(--primary-600)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Database size={32} />
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)' }}>
            No Dataset Currently Analyzed
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '480px', margin: '8px auto 24px', fontSize: '14px' }}>
            Upload your CSV file or try one of our built-in sample datasets to trigger automated data quality checks and interactive cleansing.
          </p>
          <button className="btn btn-primary" onClick={() => onNavigate('analyze')}>
            Upload or Load Sample Dataset
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    );
  }

  const { summary, quality_score, missing, duplicates, outliers, recommendations } = report;

  // Prepare chart data for Missing Values by Column
  const missingChartData = missing.by_column
    .filter(c => c.missing_count > 0)
    .map(c => ({
      name: c.column,
      missing: c.missing_count,
      pct: c.missing_percentage
    }));

  // Prepare chart data for Duplicates
  const duplicatePieData = [
    { name: 'Unique Records', value: duplicates.unique_rows },
    { name: 'Duplicate Rows', value: duplicates.duplicate_row_count }
  ];

  // Prepare chart data for Score Penalties
  const penaltyData = Object.entries(quality_score.penalties).map(([k, v]) => ({
    category: k.replace(/_/g, ' '),
    penalty: v,
    max: quality_score.max_penalties[k] || 20
  }));

  // Score Badge Color
  const getScoreColor = (score) => {
    if (score >= 90) return { bg: 'var(--success-50)', color: 'var(--success-600)', border: 'var(--success-500)' };
    if (score >= 75) return { bg: 'var(--warning-50)', color: 'var(--warning-600)', border: 'var(--warning-500)' };
    return { bg: 'var(--danger-50)', color: 'var(--danger-600)', border: 'var(--danger-500)' };
  };
  const scoreColors = getScoreColor(quality_score.overall_score);

  return (
    <div className="page-container">
      {/* Hero Quality Score Card */}
      <div className="card" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '24px',
        background: 'linear-gradient(135deg, var(--bg-card), var(--bg-card-subtle))'
      }}>
        <div style={{ flex: 1, minWidth: '280px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-info">Quality Audit Summary</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Analyzed file: <strong>{summary.file_name}</strong> ({summary.file_size_kb} KB)
            </span>
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Data Quality Score: {quality_score.overall_score} / 100
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '4px', maxWidth: '640px' }}>
            Grade: <strong>{quality_score.grade}</strong>. {quality_score.formula_explanation}
          </p>
          <div style={{ marginTop: '14px', display: 'flex', gap: '10px' }}>
            <button className="btn btn-primary btn-sm" onClick={() => onNavigate('cleaning')}>
              <Sparkles size={14} />
              Open Interactive Cleanser
            </button>
            <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('reports')}>
              View Detailed Audit Report
            </button>
          </div>
        </div>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '6px'
        }}>
          <div 
            className="score-badge"
            style={{ 
              backgroundColor: scoreColors.bg, 
              color: scoreColors.color,
              border: `3px solid ${scoreColors.border}`
            }}
          >
            {quality_score.overall_score}
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', maxWidth: '140px' }}>
            Heuristic Hygiene Index
          </span>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="grid-6">
        <MetricCard
          title="Total Rows"
          value={summary.total_rows.toLocaleString()}
          subtext="Records evaluated"
          icon={Database}
          variant="default"
        />
        <MetricCard
          title="Total Columns"
          value={summary.total_columns}
          subtext={`${summary.column_names.length} attributes`}
          icon={Database}
          variant="default"
        />
        <MetricCard
          title="Missing Cells"
          value={missing.total_missing_cells.toLocaleString()}
          subtext={`${missing.missing_cell_percentage}% overall`}
          icon={AlertCircle}
          variant={missing.total_missing_cells > 0 ? "warning" : "success"}
          badgeText={missing.columns_with_missing > 0 ? `${missing.columns_with_missing} cols` : 'Clean'}
        />
        <MetricCard
          title="Duplicate Rows"
          value={duplicates.duplicate_row_count}
          subtext={`${duplicates.duplicate_percentage}% redundancy`}
          icon={Copy}
          variant={duplicates.duplicate_row_count > 0 ? "danger" : "success"}
          badgeText={duplicates.duplicate_row_count > 0 ? 'Action needed' : '0 Dups'}
        />
        <MetricCard
          title="Outliers Flagged"
          value={outliers.total_outliers}
          subtext={`${outliers.columns_affected} columns affected`}
          icon={AlertTriangle}
          variant={outliers.total_outliers > 0 ? "warning" : "success"}
          badgeText={outliers.method.toUpperCase()}
        />
        <MetricCard
          title="Quality Grade"
          value={quality_score.grade.split(' ')[0]}
          subtext={quality_score.grade.split(' ')[1] || 'Rating'}
          icon={CheckCircle2}
          variant={quality_score.overall_score >= 80 ? "success" : quality_score.overall_score >= 60 ? "warning" : "danger"}
        />
      </div>

      {/* Charts Section */}
      <div className="grid-2">
        {/* Missing Values Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Missing Values by Column</div>
              <div className="card-subtitle">Count of blank, null, or placeholder cells</div>
            </div>
          </div>
          {missingChartData.length > 0 ? (
            <div style={{ height: '240px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={missingChartData}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                    formatter={(val, name, props) => [`${val} cells (${props.payload.pct}%)`, 'Missing']}
                  />
                  <Bar dataKey="missing" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              <CheckCircle2 size={32} color="var(--success-500)" style={{ margin: '0 auto 8px' }} />
              <p>Zero missing values detected across all columns.</p>
            </div>
          )}
        </div>

        {/* Duplicate Breakdown Pie */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Unique vs. Duplicate Records</div>
              <div className="card-subtitle">Redundancy distribution in dataset</div>
            </div>
          </div>
          <div style={{ height: '240px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={duplicatePieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  <Cell fill="#3b82f6" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Score Penalty Breakdown Chart & Recommendations */}
      <div className="grid-2">
        {/* Penalty Breakdown */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Quality Score Penalty Breakdown</div>
              <div className="card-subtitle">Deductions by defect category (Starting at 100 points)</div>
            </div>
          </div>
          <div style={{ height: '260px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={penaltyData} layout="vertical">
                <XAxis type="number" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                <YAxis dataKey="category" type="category" width={140} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                  formatter={(val, name, item) => [`-${val} pts (Max penalty: ${item.payload.max} pts)`, 'Penalty']}
                />
                <Bar dataKey="penalty" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Actionable Recommendations Feed */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Actionable Recommendations</div>
              <div className="card-subtitle">Data-driven rules based on detected anomalies</div>
            </div>
          </div>
          <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((rec, i) => (
                <div key={i} className={`rec-card ${rec.severity}`}>
                  <div className="rec-title">
                    <span>{rec.title}</span>
                    <span className={`badge badge-${rec.severity}`}>
                      {rec.severity}
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {rec.description}
                  </div>
                  <div className="rec-action">
                    Action: {rec.suggested_action}
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>
                No critical issues found. Dataset is in good shape.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
