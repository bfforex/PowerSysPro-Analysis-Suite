/**
 * PwrSysPro Analysis Suite - Main Application Component
 * Phase 1: Foundation with Canvas, Component Library, and Property Inspector
 */

import React, { useState, useEffect } from 'react';
import Canvas from './components/Canvas';
import ComponentLibrary from './components/ComponentLibrary';
import PropertyInspector from './components/PropertyInspector';
import TopologyViewer from './components/TopologyViewer';
import FileOperations from './components/FileOperations';
import NetworkAnalysis from './components/NetworkAnalysis';
import ReportGenerator from './components/ReportGenerator';
import { getProjects } from './services/api';
import axios from 'axios';

function App() {
  const [currentProject, setCurrentProject] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const projectList = await getProjects();
      if (projectList.length > 0) {
        setProjects(projectList);
        setCurrentProject(projectList[0]);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const handleNodeSelect = (node) => {
    setSelectedNode(node);
  };

  const handleUpdateTags = async () => {
    if (!currentProject) return;
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/projects/${currentProject.id}/update-tags`
      );
      
      if (response.data.status === 'success') {
        alert(
          `âœ… Tags Updated!\n\n` +
          `${response.data.updated_count} component(s) updated`
        );
        // Reload would be needed to see updated tags
        window.location.reload();
      }
    } catch (error) {
      console.error('Error updating tags:', error);
      alert('âŒ Failed to update tags');
    }
  };

  return (
    <div className="app h-screen w-screen flex flex-col bg-cad-dark">
      {/* Toolbar */}
      <div className="toolbar">
        <div className="toolbar-group">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-cad-accent">âš¡ PwrSysPro</h1>
            <span className="text-sm text-cad-text-secondary">Analysis Suite</span>
            <span className="text-xs bg-cad-success px-2 py-1 rounded text-white font-medium">
              Phase 4
            </span>
          </div>
        </div>

        <div className="toolbar-group ml-auto">
          {currentProject && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-cad-text-secondary">Project:</span>
              <span className="text-sm font-medium text-cad-text-primary">
                {currentProject.name}
              </span>
            </div>
          )}
        </div>

        <div className="toolbar-group space-x-2">
          {/* Phase 2 Features */}
          <FileOperations 
            projectId={currentProject?.id} 
            currentProject={currentProject}
          />
          
          <TopologyViewer projectId={currentProject?.id} />
          
          <button 
            onClick={handleUpdateTags}
            className="btn btn-secondary text-sm"
            title="Update all component tags based on topology"
          >
            ðŸ·ï¸ Update Tags
          </button>
          
          {/* Phase 3 & 4 Features - Network Analysis */}
          <NetworkAnalysis
            projectId={currentProject?.id}
            currentProject={currentProject}
          />
          
          {/* Phase 4 - Professional Report */}
          <ReportGenerator
            projectId={currentProject?.id}
            currentProject={currentProject}
          />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Component Library */}
        <ComponentLibrary />

        {/* Center - Canvas */}
        <div className="flex-1 relative">
          {currentProject ? (
            <Canvas 
              projectId={currentProject.id} 
              onNodeSelect={handleNodeSelect}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-6xl mb-4">âš¡</div>
                <h2 className="text-xl font-semibold text-cad-text-primary mb-2">
                  Welcome to PwrSysPro
                </h2>
                <p className="text-cad-text-secondary">
                  Loading project...
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar - Property Inspector */}
        <PropertyInspector selectedNode={selectedNode} />
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1">
            <span className="w-2 h-2 bg-cad-success rounded-full"></span>
            <span>Ready</span>
          </span>
          {currentProject && (
            <>
              <span>â€¢</span>
              <span>Standards: {currentProject.standard_short_circuit}</span>
              <span>â€¢</span>
              <span>Base MVA: {currentProject.base_mva}</span>
              <span>â€¢</span>
              <span>Frequency: {currentProject.system_frequency} Hz</span>
            </>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <span className="text-cad-success font-medium">Phase 4: Professional Reports</span>
          <span>â€¢</span>
          <span>IEEE 1584 â€¢ PDF Reports</span>
          <span>â€¢</span>
          <span>v4.0.0</span>
        </div>
      </div>
    </div>
  );
}

export default App;
