/**
 * PwrSysPro Analysis Suite - File Operations (Phase 2)
 * Save and load .psp project files
 */

import React, { useState } from 'react';
import axios from 'axios';

const FileOperations = ({ projectId, currentProject }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);

  const handleExport = async () => {
    if (!projectId) {
      alert('No project selected');
      return;
    }

    setIsExporting(true);
    try {
      const response = await axios.post(`http://localhost:8000/api/projects/${projectId}/export`);
      
      if (response.data.status === 'success') {
        // Download the file
        const pspData = response.data.psp_data;
        const blob = new Blob([JSON.stringify(pspData, null, 2)], {
          type: 'application/json'
        });
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${response.data.project_name.replace(/[^a-z0-9]/gi, '_')}.psp`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        alert('âœ… Project exported successfully!');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('âŒ Export failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsExporting(false);
    }
  };

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsImporting(true);
    try {
      const text = await file.text();
      const pspData = JSON.parse(text);

      const response = await axios.post('http://localhost:8000/api/projects/import', pspData);

      if (response.data.status === 'success') {
        alert(
          `âœ… Project imported successfully!\n\n` +
          `Project: ${response.data.project_name}\n` +
          `Nodes: ${response.data.nodes_imported}\n` +
          `Connections: ${response.data.connections_imported}\n\n` +
          `Reload the page to see the imported project.`
        );
        setShowImportDialog(false);
      }
    } catch (error) {
      console.error('Import error:', error);
      alert('âŒ Import failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsImporting(false);
      event.target.value = ''; // Reset input
    }
  };

  return (
    <>
      {/* Export Button */}
      <button
        onClick={handleExport}
        disabled={isExporting || !projectId}
        className="btn btn-secondary text-sm"
        title="Export project to .psp file"
      >
        {isExporting ? (
          <span className="flex items-center">
            <div className="spinner w-4 h-4 mr-2"></div>
            Exporting...
          </span>
        ) : (
          'ðŸ’¾ Export Project'
        )}
      </button>

      {/* Import Button */}
      <button
        onClick={() => setShowImportDialog(true)}
        disabled={isImporting}
        className="btn btn-secondary text-sm"
        title="Import project from .psp file"
      >
        ðŸ“‚ Import Project
      </button>

      {/* Import Dialog */}
      {showImportDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-cad-panel border border-cad-border rounded-lg w-96 p-6">
            <h2 className="text-lg font-semibold text-cad-text-primary mb-4">
              ðŸ“‚ Import Project
            </h2>

            <div className="mb-4 text-sm text-cad-text-secondary">
              <p className="mb-2">Select a .psp file to import:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Creates a new project</li>
                <li>Imports all nodes and connections</li>
                <li>Preserves component references</li>
              </ul>
            </div>

            <input
              type="file"
              accept=".psp,.json"
              onChange={handleFileSelect}
              disabled={isImporting}
              className="w-full mb-4 text-sm text-cad-text-primary
                       file:mr-4 file:py-2 file:px-4
                       file:rounded-lg file:border-0
                       file:text-sm file:font-semibold
                       file:bg-cad-accent file:text-white
                       file:cursor-pointer
                       hover:file:bg-blue-600"
            />

            {isImporting && (
              <div className="mb-4 text-center">
                <div className="spinner w-6 h-6 mx-auto"></div>
                <p className="text-sm text-cad-text-secondary mt-2">
                  Importing project...
                </p>
              </div>
            )}

            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowImportDialog(false)}
                disabled={isImporting}
                className="btn btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FileOperations;
