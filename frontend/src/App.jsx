import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import AnalyzePage from './pages/AnalyzePage';
import CleaningPage from './pages/CleaningPage';
import ReportsPage from './pages/ReportsPage';
import AboutPage from './pages/AboutPage';
import { checkHealth, analyzeDataset } from './services/api';

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('sdqa_theme') || 'dark';
  });
  const [activePage, setActivePage] = useState('dashboard');
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [outlierMethod, setOutlierMethod] = useState('iqr');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [toast, setToast] = useState(null);

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('sdqa_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Check backend health on initial mount
  useEffect(() => {
    async function verifyBackend() {
      const res = await checkHealth();
      setBackendStatus(res.status === 'healthy' ? 'healthy' : 'down');
    }
    verifyBackend();
  }, []);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleAnalyzeFile = async (file, method = outlierMethod, selectedCols = null) => {
    setIsLoading(true);
    try {
      const result = await analyzeDataset(file, method, selectedCols);
      setReport(result);
      showToast(`Dataset '${file.name}' analyzed successfully! Quality Score: ${result.quality_score.overall_score}/100`, 'success');
      setActivePage('dashboard');
    } catch (err) {
      showToast(err.message || 'Dataset analysis failed. Please verify file format.', 'danger');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toast && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '24px',
          zIndex: 100,
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: toast.type === 'danger' ? 'var(--danger-500)' : toast.type === 'success' ? 'var(--success-600)' : 'var(--primary-600)',
          color: '#ffffff',
          boxShadow: 'var(--shadow-lg)',
          fontSize: '13px',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          animation: 'slideIn 0.3s ease'
        }}>
          {toast.message}
        </div>
      )}

      {/* Sidebar */}
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        hasData={!!report}
      />

      {/* Main Wrapper */}
      <div className="main-wrapper">
        <Navbar
          activePage={activePage}
          theme={theme}
          toggleTheme={toggleTheme}
          backendStatus={backendStatus}
          currentFileName={report?.summary?.file_name}
        />

        <main style={{ flex: 1 }}>
          {activePage === 'dashboard' && (
            <DashboardPage
              report={report}
              onNavigate={setActivePage}
            />
          )}

          {activePage === 'analyze' && (
            <AnalyzePage
              report={report}
              onAnalyzeFile={handleAnalyzeFile}
              isLoading={isLoading}
              outlierMethod={outlierMethod}
              setOutlierMethod={setOutlierMethod}
              onNavigate={setActivePage}
            />
          )}

          {activePage === 'cleaning' && (
            <CleaningPage
              report={report}
              onNavigate={setActivePage}
            />
          )}

          {activePage === 'reports' && (
            <ReportsPage
              report={report}
              onNavigate={setActivePage}
            />
          )}

          {activePage === 'about' && (
            <AboutPage />
          )}
        </main>
      </div>
    </div>
  );
}
