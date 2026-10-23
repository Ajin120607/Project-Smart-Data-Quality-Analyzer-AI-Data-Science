/**
 * API communication service for Smart Data Quality Analyzer.
 * Supports configurable VITE_API_URL or defaults to local /api proxy.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    console.error('API health check error:', err);
    return { status: 'down', error: err.message };
  }
}

export async function analyzeDataset(file, outlierMethod = 'iqr', selectedColumns = null) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('outlier_method', outlierMethod);
  if (selectedColumns && selectedColumns.length > 0) {
    formData.append('selected_columns', JSON.stringify(selectedColumns));
  }

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || `Upload failed with HTTP status ${res.status}`);
  }

  return await res.json();
}

export async function cleanDataset(cleanPayload) {
  const res = await fetch(`${API_BASE}/clean`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(cleanPayload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Cleaning failed' }));
    throw new Error(errorData.detail || `Cleaning failed with HTTP status ${res.status}`);
  }

  return await res.json();
}

export async function getReportById(reportId) {
  const res = await fetch(`${API_BASE}/report/${reportId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Report not found' }));
    throw new Error(errorData.detail || 'Could not retrieve quality report');
  }
  return await res.json();
}

export async function triggerDownload(fileId, filename = 'cleaned_dataset.csv') {
  const res = await fetch(`${API_BASE}/download/${fileId}`);
  if (!res.ok) {
    throw new Error('Failed to download cleaned file artifact.');
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
