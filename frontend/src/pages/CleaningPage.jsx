import React, { useState } from 'react';
import { 
  Sparkles, 
  Download, 
  Check, 
  AlertTriangle, 
  ArrowRight, 
  Layers, 
  Trash2, 
  CheckCircle2, 
  RotateCcw 
} from 'lucide-react';
import DataTable from '../components/DataTable';
import MetricCard from '../components/MetricCard';
import { cleanDataset, triggerDownload } from '../services/api';

export default function CleaningPage({ report, onNavigate }) {
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [normalizeCategories, setNormalizeCategories] = useState(true);
  const [missingNumStrategy, setMissingNumStrategy] = useState('median');
  const [missingCatStrategy, setMissingCatStrategy] = useState('mode');
  const [missingCatPlaceholder, setMissingCatPlaceholder] = useState('Unknown');
  const [outlierStrategy, setOutlierStrategy] = useState('clip_iqr');
  const [columnsToDrop, setColumnsToDrop] = useState([]);

  const [isCleaning, setIsCleaning] = useState(false);
  const [cleanResult, setCleanResult] = useState(null);
  const [cleanError, setCleanError] = useState('');

  if (!report) {
    return (
      <div className="page-container">
        <div className="card" style={{ textAlign: 'center', padding: '64px 24px' }}>
          <Sparkles size={40} color="var(--primary-600)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>No Active Dataset Loaded</h2>
          <p style={{ color: 'var(--text-muted)', margin: '8px auto 20px', maxWidth: '400px', fontSize: '14px' }}>
            Please upload a dataset or load one of the demo datasets to use the interactive cleaning studio.
          </p>
          <button className="btn btn-primary" onClick={() => onNavigate('analyze')}>
            Upload Dataset First
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    );
  }

  const toggleDropCol = (col) => {
    if (columnsToDrop.includes(col)) {
      setColumnsToDrop(columnsToDrop.filter(c => c !== col));
    } else {
      setColumnsToDrop([...columnsToDrop, col]);
    }
  };

  const handleApplyClean = async () => {
    setIsCleaning(true);
    setCleanError('');
    try {
      const payload = {
        session_id: report.session_id,
        report_id: report.report_id,
        remove_duplicates: removeDuplicates,
        normalize_categories: normalizeCategories,
        handle_missing_num: missingNumStrategy === 'none' ? null : missingNumStrategy,
        handle_missing_cat: missingCatStrategy === 'none' ? null : missingCatStrategy,
        missing_cat_placeholder: missingCatPlaceholder,
        handle_outliers: outlierStrategy === 'none' ? null : outlierStrategy,
        drop_columns: columnsToDrop.length > 0 ? columnsToDrop : null,
      };

      const res = await cleanDataset(payload);
      setCleanResult(res);
    } catch (err) {
      setCleanError(err.message || 'Cleaning execution encountered an error.');
    } finally {
      setIsCleaning(false);
    }
  };

  const handleDownload = async () => {
    if (cleanResult?.file_id) {
      await triggerDownload(cleanResult.file_id, `cleaned_${report.summary.file_name}`);
    }
  };

  return (
    <div className="page-container">
      {/* Configuration Header Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Sparkles size={20} color="var(--primary-600)" />
              Interactive Data Cleansing Studio
            </div>
            <div className="card-subtitle">
              Configure and apply explicit cleaning rules. The original dataset remains completely untouched.
            </div>
          </div>
          <button
            className="btn btn-success"
            onClick={handleApplyClean}
            disabled={isCleaning}
          >
            <Check size={16} />
            {isCleaning ? 'Applying Cleaning...' : 'Execute Cleansing'}
          </button>
        </div>

        {cleanError && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: 'var(--danger-50)',
            color: 'var(--danger-600)',
            borderRadius: 'var(--radius-md)',
            marginBottom: '20px',
            fontSize: '13px'
          }}>
            {cleanError}
          </div>
        )}

        {/* Cleaning Options Grid */}
        <div className="grid-2">
          {/* Card 1: Missing & Duplicates */}
          <div style={{
            padding: '18px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
              1. Deduplication & Casing
            </h4>

            {/* Checkbox: Duplicates */}
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={removeDuplicates}
                onChange={(e) => setRemoveDuplicates(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--primary-600)' }}
              />
              <span>
                <strong>Remove Duplicate Rows:</strong> Drop identical repeated rows (Found {report.duplicates.duplicate_row_count} dups)
              </span>
            </label>

            {/* Checkbox: Categories */}
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={normalizeCategories}
                onChange={(e) => setNormalizeCategories(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--primary-600)' }}
              />
              <span>
                <strong>Normalize Category Labels:</strong> Standardize casing to Title Case and strip whitespace (e.g. "chennai" &rarr; "Chennai")
              </span>
            </label>

            <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '8px' }}>
              2. Missing Value Imputation
            </h4>

            {/* Numerical Imputation */}
            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                Numerical Columns Imputation Strategy:
              </label>
              <select
                value={missingNumStrategy}
                onChange={(e) => setMissingNumStrategy(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  fontSize: '13px'
                }}
              >
                <option value="median">Impute with Median (Recommended for skewed data)</option>
                <option value="mean">Impute with Mean (Average)</option>
                <option value="mode">Impute with Mode (Most frequent)</option>
                <option value="drop_row">Drop Rows with Missing Numerical Values</option>
                <option value="none">Retain Missing Values (Do nothing)</option>
              </select>
            </div>

            {/* Categorical Imputation */}
            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                Categorical / Text Columns Imputation Strategy:
              </label>
              <select
                value={missingCatStrategy}
                onChange={(e) => setMissingCatStrategy(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  fontSize: '13px'
                }}
              >
                <option value="mode">Impute with Mode (Most Frequent Category)</option>
                <option value="placeholder">Fill with Custom Placeholder</option>
                <option value="drop_row">Drop Rows with Missing Text Values</option>
                <option value="none">Retain Missing Values (Do nothing)</option>
              </select>

              {missingCatStrategy === 'placeholder' && (
                <input
                  type="text"
                  value={missingCatPlaceholder}
                  onChange={(e) => setMissingCatPlaceholder(e.target.value)}
                  placeholder="Placeholder label (e.g. Unknown)"
                  style={{
                    width: '100%',
                    marginTop: '6px',
                    padding: '7px 10px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-card)',
                    color: 'var(--text-primary)',
                    fontSize: '12px'
                  }}
                />
              )}
            </div>
          </div>

          {/* Card 2: Outliers & Dropping Columns */}
          <div style={{
            padding: '18px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
              3. Outlier Treatment
            </h4>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                Statistical Outlier Action:
              </label>
              <select
                value={outlierStrategy}
                onChange={(e) => setOutlierStrategy(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-primary)',
                  fontSize: '13px'
                }}
              >
                <option value="clip_iqr">Cap at IQR Bounds (Tukey Winsorization - Preserves rows)</option>
                <option value="remove_rows">Remove Outlier Rows (Filter extreme observations)</option>
                <option value="none">Keep Original Outliers (Unchanged)</option>
              </select>
            </div>

            <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '8px' }}>
              4. Drop Constant or Low-Information Columns
            </h4>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Click on columns you want to permanently exclude from the cleaned dataset:
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {report.summary.column_names.map((col) => {
                const isDropped = columnsToDrop.includes(col);
                return (
                  <button
                    key={col}
                    type="button"
                    onClick={() => toggleDropCol(col)}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      border: '1px solid',
                      borderColor: isDropped ? 'var(--danger-500)' : 'var(--border-subtle)',
                      backgroundColor: isDropped ? 'var(--danger-50)' : 'var(--bg-card)',
                      color: isDropped ? 'var(--danger-600)' : 'var(--text-primary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    {isDropped ? <Trash2 size={12} /> : null}
                    {col} {isDropped ? '(Exclude)' : ''}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Clean Results & Comparison */}
      {cleanResult && (
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title" style={{ color: 'var(--success-600)' }}>
                <CheckCircle2 size={20} />
                Cleansing Completed Successfully
              </div>
              <div className="card-subtitle">
                Compare original vs. cleaned metrics and download the modified dataset.
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleDownload}>
              <Download size={16} />
              Download Cleaned CSV
            </button>
          </div>

          {/* Comparison Metrics Grid */}
          <div className="grid-6" style={{ marginBottom: '20px' }}>
            <MetricCard
              title="Rows Cleaned"
              value={cleanResult.cleaned_rows}
              subtext={`Original: ${cleanResult.original_rows}`}
              variant="default"
              badgeText={`${cleanResult.comparison.rows.diff} rows`}
            />
            <MetricCard
              title="Columns Retained"
              value={cleanResult.cleaned_cols}
              subtext={`Original: ${cleanResult.original_cols}`}
              variant="default"
            />
            <MetricCard
              title="Missing Cells Remaining"
              value={cleanResult.comparison.missing_cells.after}
              subtext={`Before: ${cleanResult.comparison.missing_cells.before}`}
              variant={cleanResult.comparison.missing_cells.after === 0 ? "success" : "warning"}
              badgeText={`${cleanResult.comparison.missing_cells.diff} cells`}
            />
            <MetricCard
              title="Duplicate Rows"
              value={cleanResult.comparison.duplicate_rows.after}
              subtext={`Before: ${cleanResult.comparison.duplicate_rows.before}`}
              variant="success"
              badgeText="0 Duplicates"
            />
            <MetricCard
              title="Operations Applied"
              value={cleanResult.operations_applied.length}
              subtext="Logged in audit"
              variant="success"
            />
          </div>

          {/* Applied Operations Audit Trail */}
          <div style={{
            padding: '14px 18px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: 'var(--radius-md)',
            marginBottom: '20px'
          }}>
            <h5 style={{ fontSize: '13px', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
              Applied Cleansing Audit Trail:
            </h5>
            <ul style={{ paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              {cleanResult.operations_applied.map((op, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>
                  <strong>{op.operation}:</strong> {op.details}
                </li>
              ))}
            </ul>
          </div>

          {/* Cleaned Dataset Preview Table */}
          <h5 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '10px' }}>
            Cleaned Dataset Preview (First 10 Rows):
          </h5>
          <DataTable
            rows={cleanResult.preview_rows}
          />
        </div>
      )}
    </div>
  );
}
