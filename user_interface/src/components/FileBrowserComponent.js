// src/components/FileBrowserComponent.js
import React, { useState, useEffect } from 'react';
import { apiGet } from '../api';
import '../styles/FileBrowserComponent.css';

export default function FileBrowserComponent({ onFileSelect }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('processed');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch files from backend
  const fetchFiles = async () => {
    console.log('FileBrowser: fetchFiles called');
    setLoading(true);
    setError(null);
    
    try {
      console.log('FileBrowser: Making API call to /files');
      const response = await apiGet('/files');
      console.log('FileBrowser: API response:', response.data);
      setFiles(response.data.files || []);
    } catch (err) {
      console.error('FileBrowser: Error fetching files:', err);
      setError('Failed to load files from database');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('FileBrowser: useEffect called, calling fetchFiles');
    fetchFiles();
  }, []);

  // Listen for database changes
  useEffect(() => {
    const handleDatabaseChange = () => {
      console.log('Database changed, refreshing files...');
      fetchFiles();
    };

    window.addEventListener('databaseChanged', handleDatabaseChange);
    return () => {
      window.removeEventListener('databaseChanged', handleDatabaseChange);
    };
  }, []);

  // Get file type icon
  const getFileIcon = (type, extension) => {
    switch (type) {
      case 'pdf':
        return '📄';
      case 'document':
        return '📝';
      case 'text':
        return '📃';
      case 'geographic':
        return '🗺️';
      case 'image':
        return '🖼️';
      default:
        return '📁';
    }
  };

  // Filter and sort files
  const getFilteredAndSortedFiles = () => {
    let filtered = files;

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(file => file.type === filterType);
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(file =>
        file.name.toLowerCase().includes(term) ||
        file.subject.toLowerCase().includes(term) ||
        file.topic.toLowerCase().includes(term) ||
        file.keywords.toLowerCase().includes(term)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (sortBy === 'processed') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  };

  const filteredFiles = getFilteredAndSortedFiles();

  // Get unique file types for filter dropdown
  const fileTypes = [...new Set(files.map(file => file.type))];

  const handleFileClick = (file) => {
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const formatFileSize = (path) => {
    // This is a placeholder - in a real implementation you'd get file size from the backend
    return 'N/A';
  };

  console.log('FileBrowserComponent render - loading:', loading, 'files:', files.length, 'error:', error);

  if (loading) {
    return (
      <div className="file-browser-container">
        <div className="loading-message">Loading files...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="file-browser-container">
        <div className="error-message">
          {error}
          <button onClick={fetchFiles} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="file-browser-container" style={{border: '2px solid red', padding: '10px', margin: '10px'}}>
      <div style={{background: '#27ae60', padding: '5px', borderRadius: '5px'}}>
        <h3 style={{color: 'white', margin: '0'}}>FILE BROWSER TEST - Database Files ({files.length})</h3>
      </div>
      <div className="file-browser-header">
        <h3>Database Files ({files.length})</h3>
        
        <div className="file-browser-controls">
          {/* Search */}
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="file-search-input"
          />

          {/* Type filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="file-filter-select"
          >
            <option value="all">All Types</option>
            {fileTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>

          {/* Sort options */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field);
              setSortOrder(order);
            }}
            className="file-sort-select"
          >
            <option value="processed-desc">Newest First</option>
            <option value="processed-asc">Oldest First</option>
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="type-asc">Type A-Z</option>
            <option value="topic-asc">Topic A-Z</option>
          </select>

          <button onClick={fetchFiles} className="refresh-files-button" title="Refresh files">
            🔄
          </button>
        </div>
      </div>

      <div className="file-list">
        {filteredFiles.length === 0 ? (
          <div className="no-files-message">
            {searchTerm || filterType !== 'all' 
              ? 'No files match your filters' 
              : 'No files in database'}
          </div>
        ) : (
          filteredFiles.map((file) => (
            <div
              key={file.id}
              className="file-item"
              onClick={() => handleFileClick(file)}
            >
              <div className="file-icon">
                {getFileIcon(file.type, file.extension)}
              </div>
              
              <div className="file-info">
                <div className="file-name">
                  {file.name}
                  <span className="file-extension">{file.extension}</span>
                </div>
                
                <div className="file-metadata">
                  <span className="file-topic">{file.topic}</span>
                  {file.coordinates && (
                    <span className="file-coordinates" title="Has coordinates">
                      📍
                    </span>
                  )}
                  <span className="file-classification">{file.classification}</span>
                </div>
                
                <div className="file-subject">{file.subject}</div>
                
                {file.keywords && (
                  <div className="file-keywords">
                    {file.keywords.split(' ').slice(0, 5).map((keyword, idx) => (
                      <span key={idx} className="keyword-tag">
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
                
                <div className="file-date">
                  Processed: {formatDate(file.processed)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
