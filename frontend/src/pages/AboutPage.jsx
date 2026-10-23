import React from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Cpu, 
  HelpCircle, 
  Code2, 
  BookOpen, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="page-container">
      {/* Intro Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <ShieldCheck size={20} color="var(--primary-600)" />
              Smart Data Quality Analyzer — Project Architecture & Methodology
            </div>
            <div className="card-subtitle">
              Artificial Intelligence & Data Science (AIDS) Engineering Portfolio Project
            </div>
          </div>
        </div>

        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <strong>Smart Data Quality Analyzer</strong> is a full-stack data auditing and interactive cleansing platform
          designed to eliminate the tedious manual work of inspecting tabular CSV datasets before exploratory data analysis (EDA)
          and machine learning model training.
        </p>
      </div>

      {/* Scoring Methodology Card */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <BookOpen size={18} color="var(--primary-600)" />
            Transparent Data Quality Scoring Formula
          </div>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
          Rather than presenting an uninterpretable black-box percentage, the quality index begins at a baseline of <strong>100 points</strong>
          and deducts explainable, bounded penalties across 6 essential dataset hygiene dimensions:
        </p>

        <div style={{
          padding: '16px 20px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderRadius: 'var(--radius-md)',
          fontFamily: 'var(--font-mono)',
          fontSize: '13px',
          color: 'var(--primary-600)',
          marginBottom: '16px'
        }}>
          Score = 100 - [P_missing (max 25) + P_duplicates (max 20) + P_outliers (max 15) + P_types (max 15) + P_constants (max 15) + P_categories (max 10)]
        </div>

        <div className="grid-2" style={{ gap: '14px' }}>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>1. Missing Values (Max 25 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Scaled directly by the proportion of missing cells across all rows and columns.
            </p>
          </div>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>2. Duplicate Records (Max 20 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Scaled by the percentage of fully identical rows. Repeated rows artificially skew statistical distributions.
            </p>
          </div>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>3. Numerical Outliers (Max 15 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Evaluated using Tukey's Interquartile Range (IQR = Q3 - Q1) or standard Z-scores (|z| &gt; 3.0).
            </p>
          </div>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>4. Inconsistent Data Types (Max 15 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Flags numeric values or timestamp strings trapped as text, and columns with mixed heterogeneous content.
            </p>
          </div>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>5. Zero / Low-Variance Columns (Max 15 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Identifies constant columns (100% same value) or quasi-constant columns (&gt;=90% same value) with zero analytical entropy.
            </p>
          </div>
          <div style={{ padding: '12px 16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>6. Inconsistent Category Casing (Max 10 pts)</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Clusters variations like "Chennai", "chennai", and "CHENNAI" into canonical suggestions.
            </p>
          </div>
        </div>

        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          backgroundColor: 'var(--warning-50)',
          color: 'var(--warning-600)',
          borderRadius: 'var(--radius-md)',
          fontSize: '12px',
          display: 'flex',
          gap: '8px',
          alignItems: 'center'
        }}>
          <AlertTriangle size={16} />
          <span>
            <strong>Academic Transparency Disclaimer:</strong> This score is a heuristic hygiene index designed for automated exploratory screening. It does not represent an industry standard or a guarantee of ground-truth factual correctness.
          </span>
        </div>
      </div>

      {/* Tech Stack Card */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Cpu size={18} color="var(--primary-600)" />
            Technology Stack
          </div>
        </div>

        <div className="grid-3">
          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '14px', color: 'var(--primary-600)' }}>Backend</strong>
            <ul style={{ paddingLeft: '18px', marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <li>Python 3.14</li>
              <li>FastAPI & Uvicorn</li>
              <li>Pandas & NumPy</li>
              <li>Scikit-Learn (Isolation Forest)</li>
              <li>Pydantic v2 validation</li>
              <li>Pytest test suite</li>
            </ul>
          </div>

          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '14px', color: 'var(--primary-600)' }}>Frontend</strong>
            <ul style={{ paddingLeft: '18px', marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <li>React 18 & Vite</li>
              <li>JavaScript (ES Modules)</li>
              <li>Recharts interactive charts</li>
              <li>Lucide React icons</li>
              <li>CSS3 design system (Light/Dark)</li>
              <li>Fetch API with proxy</li>
            </ul>
          </div>

          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ fontSize: '14px', color: 'var(--primary-600)' }}>Security & Storage</strong>
            <ul style={{ paddingLeft: '18px', marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <li>In-memory session processing</li>
              <li>15 MB payload guardrails</li>
              <li>Path traversal sanitization</li>
              <li>Zero persistent file storage</li>
              <li>1-hour TTL cache expiration</li>
              <li>No arbitrary code execution</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
