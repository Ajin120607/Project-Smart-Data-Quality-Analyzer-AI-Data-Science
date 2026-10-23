import React from 'react';

export default function DataTable({ columns, rows, dataTypes = [] }) {
  if (!rows || rows.length === 0) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No records available for preview.
      </div>
    );
  }

  // Type lookup map if available
  const typeMap = {};
  dataTypes.forEach(dt => {
    typeMap[dt.column] = dt.inferred_type || dt.pandas_dtype;
  });

  const cols = columns || Object.keys(rows[0] || {});

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '40px', color: 'var(--text-muted)' }}>#</th>
            {cols.map((col) => (
              <th key={col}>
                <div>{col}</div>
                {typeMap[col] && (
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 400 }}>
                    {typeMap[col]}
                  </div>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              <td style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{idx + 1}</td>
              {cols.map((col) => {
                const val = row[col];
                const isNull = val === null || val === undefined || val === '' || String(val).toLowerCase() === 'nan';
                return (
                  <td key={col}>
                    {isNull ? (
                      <span className="cell-null">null</span>
                    ) : (
                      <span>{String(val)}</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
