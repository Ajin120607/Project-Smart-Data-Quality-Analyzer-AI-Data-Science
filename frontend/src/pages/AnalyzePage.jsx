import React, { useState } from 'react';
import { 
  FileSpreadsheet, 
  Sparkles, 
  Check, 
  RotateCcw, 
  ArrowRight, 
  Sliders, 
  Filter 
} from 'lucide-react';
import Dropzone from '../components/Dropzone';
import DataTable from '../components/DataTable';

export default function AnalyzePage({ 
  report, 
  onAnalyzeFile, 
  isLoading, 
  outlierMethod, 
  setOutlierMethod, 
  onNavigate 
}) {
  const [selectedCols, setSelectedCols] = useState([]);
  const [currentFile, setCurrentFile] = useState(null);

  const handleFilePicked = (file) => {
    setCurrentFile(file);
    onAnalyzeFile(file, outlierMethod);
  };

  const toggleColumn = (col) => {
    if (selectedCols.includes(col)) {
      setSelectedCols(selectedCols.filter(c => c !== col));
    } else {
      setSelectedCols([...selectedCols, col]);
    }
  };

  const selectAllCols = () => {
    if (report) {
      setSelectedCols([...report.summary.column_names]);
    }
  };

  const deselectAllCols = () => {
    setSelectedCols([]);
  };

  const handleReanalyzeWithSelection = () => {
    if (currentFile && selectedCols.length > 0) {
      onAnalyzeFile(currentFile, outlierMethod, selectedCols);
    }
  };

  return (
    <div className="page-container">
      {/* Upload Header Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <FileSpreadsheet size={20} color="var(--primary-600)" />
              Dataset Ingestion & Inspection
            </div>
            <div className="card-subtitle">
              Upload any standard CSV file to trigger instant data-quality verification.
            </div>
          </div>
        </div>

        <Dropzone
          onFileSelected={handleFilePicked}
          isLoading={isLoading}
          outlierMethod={outlierMethod}
          setOutlierMethod={setOutlierMethod}
        />

        {isLoading && (
          <div style={{
            marginTop: '20px',
            padding: '24px',
            backgroundColor: 'var(--primary-50)',
            borderRadius: 'var(--radius-md)',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              border: '3px solid var(--primary-100)',
              borderTopColor: 'var(--primary-600)',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite'
            }} />
            <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--primary-700)' }}>
              Executing automated quality checks...
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Calculating missingness, duplicates, Tukey IQR bounds, and casing clusters
            </div>
          </div>
        )}
      </div>

      {/* Dataset Preview & Column Filter Card */}
      {report && (
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                First 10 Rows Preview & Column Selection
              </div>
              <div className="card-subtitle">
                Select specific columns to narrow down the analytical scope, or proceed to cleaning.
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                className="btn btn-primary btn-sm"
                onClick={() => onNavigate('cleaning')}
              >
                <Sparkles size={14} />
                Open Cleaning Engine
              </button>
            </div>
          </div>

          {/* Column Toggles */}
          <div style={{
            padding: '14px 18px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Filter size={14} />
                Filter Columns for Analysis:
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button 
                  type="button" 
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '3px 8px', fontSize: '11px' }}
                  onClick={selectAllCols}
                >
                  Select All
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '3px 8px', fontSize: '11px' }}
                  onClick={deselectAllCols}
                >
                  Clear
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {report.summary.column_names.map((col) => {
                const isSelected = selectedCols.length === 0 || selectedCols.includes(col);
                return (
                  <button
                    key={col}
                    type="button"
                    onClick={() => toggleColumn(col)}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      border: '1px solid',
                      borderColor: isSelected ? 'var(--primary-500)' : 'var(--border-subtle)',
                      backgroundColor: isSelected ? 'var(--primary-50)' : 'var(--bg-card)',
                      color: isSelected ? 'var(--primary-700)' : 'var(--text-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    {isSelected && <Check size={12} />}
                    {col}
                  </button>
                );
              })}
            </div>

            {selectedCols.length > 0 && selectedCols.length !== report.summary.column_names.length && currentFile && (
              <div style={{ marginTop: '12px' }}>
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={handleReanalyzeWithSelection}
                  disabled={isLoading}
                >
                  <RotateCcw size={13} />
                  Re-analyze with Selected ({selectedCols.length}) Columns
                </button>
              </div>
            )}
          </div>

          {/* Table Preview */}
          <DataTable
            rows={report.preview_rows}
            dataTypes={report.data_types}
          />
        </div>
      )}
    </div>
  );
}
