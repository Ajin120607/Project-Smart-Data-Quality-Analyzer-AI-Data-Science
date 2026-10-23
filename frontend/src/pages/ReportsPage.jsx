import React from 'react';
import { 
  FileText, 
  Download, 
  AlertCircle, 
  CheckCircle2, 
  HelpCircle, 
  Copy, 
  Layers, 
  ArrowRight 
} from 'lucide-react';

export default function ReportsPage({ report, onNavigate }) {
  if (!report) {
    return (
      <div className="page-container">
        <div className="card" style={{ textAlign: 'center', padding: '64px 24px' }}>
          <FileText size={40} color="var(--primary-600)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>No Quality Report Generated</h2>
          <p style={{ color: 'var(--text-muted)', margin: '8px auto 20px', maxWidth: '400px', fontSize: '14px' }}>
            Upload or inspect a dataset first to generate a full diagnostic quality audit.
          </p>
          <button className="btn btn-primary" onClick={() => onNavigate('analyze')}>
            Upload Dataset
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    );
  }

  const { 
    report_id, 
    generated_at, 
    summary, 
    quality_score, 
    missing, 
    duplicates, 
    outliers, 
    data_types, 
    category_consistency, 
    constant_and_low_variance, 
    recommendations 
  } = report;

  const handleExportJSON = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(report, null, 2)
    )}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `quality_report_${summary.file_name}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Map column diagnostics
  const missingMap = {};
  missing.by_column.forEach(c => { missingMap[c.column] = c; });

  const outlierMap = {};
  outliers.by_column.forEach(c => { outlierMap[c.column] = c; });

  const constantSet = new Set(constant_and_low_variance.map(c => c.column));

  return (
    <div className="page-container">
      {/* Header Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <FileText size={20} color="var(--primary-600)" />
              Dataset Quality Audit Report
            </div>
            <div className="card-subtitle">
              Generated on {new Date(generated_at).toLocaleString()} | Report UUID: <code style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{report_id}</code>
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleExportJSON}>
            <Download size={16} />
            Export JSON Audit Report
          </button>
        </div>

        {/* Scoring Methodology Banner */}
        <div style={{
          padding: '16px 20px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderRadius: 'var(--radius-md)',
          borderLeft: '4px solid var(--primary-500)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Transparent Scoring Formula
          </div>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--primary-600)', background: 'var(--bg-card)', padding: '8px 12px', borderRadius: '4px' }}>
            {quality_score.formula_explanation}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {quality_score.disclaimer}
          </div>
        </div>
      </div>

      {/* Column by Column Diagnostic Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            Column-by-Column Diagnostic Matrix
          </div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Inferred Type</th>
                <th>Missing Values</th>
                <th>Outliers</th>
                <th>Variance Flag</th>
                <th>Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {data_types.map((dt) => {
                const miss = missingMap[dt.column] || { missing_count: 0, missing_percentage: 0 };
                const out = outlierMap[dt.column] || { outlier_count: 0, outlier_percentage: 0 };
                const isConst = constantSet.has(dt.column);

                return (
                  <tr key={dt.column}>
                    <td><strong>{dt.column}</strong></td>
                    <td>
                      <span className="badge badge-info" style={{ fontSize: '11px' }}>
                        {dt.inferred_type}
                      </span>
                      {dt.numeric_as_text && (
                        <div style={{ fontSize: '10px', color: 'var(--warning-600)' }}>
                          Numeric stored as text
                        </div>
                      )}
                      {dt.datetime_as_text && (
                        <div style={{ fontSize: '10px', color: 'var(--primary-600)' }}>
                          Date stored as text
                        </div>
                      )}
                    </td>
                    <td>
                      {miss.missing_count > 0 ? (
                        <span className={`badge badge-${miss.severity === 'none' ? 'success' : miss.severity === 'low' ? 'info' : 'warning'}`}>
                          {miss.missing_count} ({miss.missing_percentage}%)
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>0 (0%)</span>
                      )}
                    </td>
                    <td>
                      {out.outlier_count > 0 ? (
                        <span className="badge badge-warning">
                          {out.outlier_count} values
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>0</span>
                      )}
                    </td>
                    <td>
                      {isConst ? (
                        <span className="badge badge-danger">Zero / Low Variance</span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Normal</span>
                      )}
                    </td>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '320px' }}>
                      {dt.suggestion || miss.recommendation || out.recommendation || 'Column passes standard hygiene checks.'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Duplicate Samples Preview if duplicates exist */}
      {duplicates.duplicate_row_count > 0 && (
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Copy size={18} color="var(--danger-500)" />
                Detected Duplicate Records ({duplicates.duplicate_row_count} total rows)
              </div>
              <div className="card-subtitle">
                Sample preview of redundant rows identified by exact-match hashing:
              </div>
            </div>
          </div>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {summary.column_names.map(c => <th key={c}>{c}</th>)}
                </tr>
              </thead>
              <tbody>
                {duplicates.sample_duplicates.map((row, idx) => (
                  <tr key={idx}>
                    {summary.column_names.map(c => (
                      <td key={c}>{row[c] !== null && row[c] !== undefined ? String(row[c]) : <span className="cell-null">null</span>}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Category Casing Discrepancies */}
      {category_consistency.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              Inconsistent Category Labels
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {category_consistency.map((ci, idx) => (
              <div key={idx} style={{
                padding: '14px 18px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-card-subtle)'
              }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                  Column '{ci.column}' — {ci.unique_count} distinct categories:
                </div>
                {ci.clusters.map((cluster, cidx) => (
                  <div key={cidx} style={{ fontSize: '12px', color: 'var(--text-secondary)', marginLeft: '12px', marginBottom: '6px' }}>
                    &bull; Normalized Suggestion: <strong>{cluster.canonical}</strong> &larr; Found variations: {cluster.variations.map(v => `"${v}" (${cluster.frequency_breakdown[v] || 1})`).join(', ')}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
