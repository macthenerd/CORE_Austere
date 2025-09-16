const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // Opens the native "Browse…" dialog (only .db), returns the chosen path
    selectDbFile: () => ipcRenderer.invoke('dialog:openFile'),

    // Opens the native folder selection dialog
    selectFolder: () => ipcRenderer.invoke('dialog:openFolder'),

    // Called when you drop a file into the Settings drop‐zone
    loadDbFile: (filePath) => ipcRenderer.invoke('file-dropped', filePath),

    exportKml: (table, query, mgrs_col, limit) =>
        ipcRenderer.invoke('export:kml', { table, query, mgrs_col, limit }),

    // Allow renderer to read back the dynamically chosen port
    getApiPort: () => ipcRenderer.invoke('get-api-port'),

    // Existing quit
    quitApp: () => ipcRenderer.send('app:quit')
});
