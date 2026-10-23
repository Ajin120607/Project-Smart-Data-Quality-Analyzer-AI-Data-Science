import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles, Check, AlertTriangle } from 'lucide-react';

const SAMPLE_CUSTOMER_CSV = `customer_id,name,age,city,annual_income,signup_date
CUST001,Aarav Sharma,28,Chennai,65000,2023-01-15
CUST002,Priya Patel,34,chennai,72000,2023-02-10
CUST003,Rohan Verma,45,CHENNAI,89000,2023-03-05
CUST004,Ananya Iyer,,Mumbai,54000,2023-04-12
CUST005,Vikram Singh,185,mumbai,98000,2023-05-18
CUST006,Neha Gupta,29,Bengaluru,,2023-06-20
CUST007,Siddharth Reddy,41,bengaluru,115000,2023-07-22
CUST008,Deepika Nair,36,Chennai,78000,2023-08-30
CUST008,Deepika Nair,36,Chennai,78000,2023-08-30
CUST009,Rahul Dravid,52,Bengaluru,14500000,2023-09-14
CUST010,Kavita Krishnan,31,Delhi,62000,2023-10-02
CUST011,Karan Malhotra,-4,delhi,58000,11/15/2023
CUST012,Sneha Rao,26,Delhi,51000,2023-12-01
CUST013,Amitabh Ghosh,48,Kolkata,,2024-01-11
CUST014,Pooja Hegde,27,kolkata,67000,2024-02-14
CUST015,Manoj Bajpayee,55,Kolkata,125000,2024-03-25`;

const SAMPLE_SALES_CSV = `order_id,product,category,quantity,price,order_date,status
ORD-1001,Wireless Mouse,Electronics,2,24.99,2024-01-05,Delivered
ORD-1002,Mechanical Keyboard,electronics,1,89.50,2024-01-06,Delivered
ORD-1003,USB-C Cable,ELECTRONICS,5,9.99,2024-01-07,Delivered
ORD-1004,Office Chair,Furniture,,199.00,2024-01-08,Delivered
ORD-1005,Standing Desk,furniture,1,450.00,2024-01-09,Delivered
ORD-1006,Coffee Mug,Kitchen,4,,2024-01-10,Delivered
ORD-1007,Water Bottle,kitchen,2,15.50,2024-01-11,Delivered
ORD-1008,Desk Lamp,Furniture,1,39.99,2024-01-12,Delivered
ORD-1008,Desk Lamp,Furniture,1,39.99,2024-01-12,Delivered
ORD-1009,Gaming Headset,Electronics,1,120.00,2024-01-13,Delivered
ORD-1010,Monitor 27-inch,ELECTRONICS,1,320.00,2024-01-14,Delivered
ORD-1011,Laptop Stand,Accessories,999,35.00,2024-01-15,Delivered
ORD-1012,HDMI Cable,Electronics,3,12.99,2024-01-16,Delivered
ORD-1013,Air Purifier,Appliances,1,149.99,2024-01-17,Delivered
ORD-1014,Noise Cancelling Earbuds,Electronics,2,79.99,2024-01-18,Delivered
ORD-1015,Electric Kettle,appliances,1,49.99,2024-01-19,Delivered
ORD-1016,Yoga Mat,Fitness,-5,29.99,2024-01-20,Delivered`;

export default function Dropzone({ onFileSelected, isLoading, outlierMethod, setOutlierMethod }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const validateAndProceed = (file) => {
    setErrorMessage('');
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setErrorMessage('Please select a valid CSV (.csv) file.');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 15 MB limit.');
      return;
    }

    onFileSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProceed(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProceed(e.target.files[0]);
    }
  };

  const loadSampleDataset = (name, csvContent) => {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const file = new File([blob], name, { type: 'text/csv' });
    validateAndProceed(file);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div
        className={`dropzone ${isDragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleInputChange}
          disabled={isLoading}
        />

        <div className="dropzone-icon">
          <UploadCloud size={30} />
        </div>

        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Drag and drop your CSV dataset here
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            or click to browse from your computer (Maximum file size: 15 MB)
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="badge badge-info">UTF-8 & Latin-1 supported</span>
          <span className="badge badge-info">Auto delimiter detection</span>
        </div>
      </div>

      {errorMessage && (
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--danger-50)',
          color: 'var(--danger-600)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '13px'
        }}>
          <AlertTriangle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Outlier Method & Sample Datasets Bar */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Outlier Method:
          </span>
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              type="button"
              className={`btn btn-sm ${outlierMethod === 'iqr' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setOutlierMethod('iqr')}
            >
              IQR (Tukey 1.5x)
            </button>
            <button
              type="button"
              className={`btn btn-sm ${outlierMethod === 'zscore' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setOutlierMethod('zscore')}
            >
              Z-Score (|z| &gt; 3)
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Demo Datasets:</span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => loadSampleDataset('customer_data.csv', SAMPLE_CUSTOMER_CSV)}
            disabled={isLoading}
          >
            <Sparkles size={13} />
            Customer Data
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => loadSampleDataset('sales_data.csv', SAMPLE_SALES_CSV)}
            disabled={isLoading}
          >
            <Sparkles size={13} />
            Sales Data
          </button>
        </div>
      </div>
    </div>
  );
}
