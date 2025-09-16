import React, { useState, useCallback } from 'react';
import '../styles/SettingsComponent.css';

export default function SettingsComponent() {
  const [status, setStatus] = useState('No database loaded.');

  // Drag & drop handler
  const onDrop = useCallback(async (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    
    // Check if we're running in Electron (has electronAPI) or browser
    if (!window.electronAPI) {
      setStatus('⛔ File upload only works in the Electron app, not in browser mode.');
      return;
    }
    
    if (!file || !file.name.toLowerCase().endsWith('.db')) {
      setStatus('⛔ Please drop a valid .db file.');
      return;
    }
    
    try {
      // In Electron, file.path exists; in browser it doesn't
      const filePath = file.path || file.name;
      const returned = await window.electronAPI.loadDbFile(filePath);
      if (returned) {
        setStatus(`✅ Loaded database: ${returned}`);
      } else {
        setStatus('⛔ Load cancelled or invalid .db file.');
      }
    } catch (err) {
      setStatus(`❗ Error: ${err.message}`);
    }
  }, []);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  // Browse… button & box click both call this
  const handleBrowse = useCallback(async () => {
    // Check if we're running in Electron (has electronAPI) or browser
    if (!window.electronAPI) {
      setStatus('⛔ File selection only works in the Electron app, not in browser mode.');
      return;
    }
    
    try {
      const returned = await window.electronAPI.selectDbFile();
      if (returned && returned.toLowerCase().endsWith('.db')) {
        setStatus(`✅ Loaded database: ${returned}`);
      } else {
        setStatus('⛔ Please select a valid .db file. ⛔');
      }
    } catch (err) {
      setStatus(`❗ Error: ${err.message}`);
    }
  }, []);

  return (
    <div className="settings-container">
      <h2>Load SQLite Database</h2>

      <div
        className="upload-box"
        onDrop={onDrop}
        onDragOver={onDragOver}
        onClick={handleBrowse}
      >
        <p>Drag &amp; drop a <code>.db</code> here</p>
        <p>or click to browse …</p>
      </div>

      <button className="select-db-button" onClick={handleBrowse}>
        Browse…
      </button>

      <p className="status-text">{status}</p>
    </div>
  );
}
