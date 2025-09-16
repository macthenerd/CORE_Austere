// src/components/SearchComponent.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet } from '../api';
import FileBrowserComponent from './FileBrowserComponent';
import '../styles/SearchComponent.css';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [loadingTables, setLoadingTables] = useState(true);
  const [tableError, setTableError] = useState(null);

  const navigate = useNavigate();

  // Function to fetch tables
  const fetchTables = () => {
    setLoadingTables(true);
    setTableError(null);
    apiGet('/tables')
      .then(res => {
        setTables(res.data);
        if (res.data.length > 0) {
          setSelectedTable(res.data[0]);
        }
      })
      .catch(err => {
        console.error('Error fetching tables:', err);
        setTableError('Unable to load tables');
      })
      .finally(() => {
        setLoadingTables(false);
      });
  };

  // Fetch available tables from the backend on mount
  useEffect(() => {
    fetchTables();
  }, []);

  // Listen for database changes (when user creates new DB)
  useEffect(() => {
    const handleDatabaseChange = () => {
      console.log('Database changed, refreshing tables...');
      fetchTables();
    };

    // Listen for custom event
    window.addEventListener('databaseChanged', handleDatabaseChange);
    
    return () => {
      window.removeEventListener('databaseChanged', handleDatabaseChange);
    };
  }, []);

  const handleSearch = () => {
    if (!selectedTable) {
      setTableError('Please select a table');
      return;
    }
    if (!query.trim()) {
      return;
    }
    navigate('/results', { state: { query, table: selectedTable } });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle file selection from browser
  const handleFileSelect = (file) => {
    // Auto-fill search with file name or keywords
    const searchTerms = file.keywords ? file.keywords.split(' ')[0] : file.name.split('.')[0];
    setQuery(searchTerms);
  };

  return (
    <div className="page-content">
      <div className="search-container">
        <h2>Search</h2>

        {loadingTables ? (
          <p>Loading tables…</p>
        ) : tableError ? (
          <div className="error-section">
            <p className="error">{tableError}</p>
            <button onClick={fetchTables} className="refresh-button">
              Refresh Tables
            </button>
          </div>
        ) : (
          <div className="table-select">
            <label htmlFor="table-dropdown">Table:</label>
            <div className="table-select-row">
              <select
                id="table-dropdown"
                value={selectedTable}
                onChange={e => setSelectedTable(e.target.value)}
              >
                {tables.map(tbl => (
                  <option key={tbl} value={tbl}>{tbl}</option>
                ))}
              </select>
              <button onClick={fetchTables} className="refresh-button" title="Refresh tables">
                🔄
              </button>
            </div>
          </div>
        )}

        <div className="search-box">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="search-input"
            placeholder="Enter search terms..."
            disabled={loadingTables || !!tableError}
          />
          <button
            onClick={handleSearch}
            className="search-button"
            disabled={loadingTables || !!tableError}
          >
            Search
          </button>
        </div>

        {/* File Browser */}
        {console.log('SearchComponent: About to render FileBrowserComponent')}
        <FileBrowserComponent onFileSelect={handleFileSelect} />
      </div>
    </div>
  );
}

export default SearchComponent;
