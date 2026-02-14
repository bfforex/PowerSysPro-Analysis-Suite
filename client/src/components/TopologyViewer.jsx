/**
 * PwrSysPro Analysis Suite - Topology Viewer (Phase 2)
 * Displays network topology analysis results including:
 * - Network levels
 * - Bus identification
 * - Loop detection
 * - Validation issues
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TopologyViewer = ({ projectId }) => {
  const [topology, setTopology] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const fetchTopology = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/projects/${projectId}/topology`);
      setTopology(response.data);
    } catch (error) {
      console.error('Error fetching topology:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && projectId) {
      fetchTopology();
    }
  }, [isOpen, projectId]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-secondary text-sm"
      >
        ðŸ” Analyze Topology
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-cad-panel border border-cad-border rounded-lg w-3/4 max-w-4xl max-h-3/4 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cad-border">
          <h2 className="text-lg font-semibold text-cad-text-primary">
            ðŸ”— Network Topology Analysis
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchTopology}
              disabled={loading}
              className="btn btn-primary text-sm"
            >
              {loading ? 'ðŸ”„ Analyzing...' : 'ðŸ”„ Refresh'}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="btn btn-secondary text-sm"
            >
              âœ• Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="spinner w-8 h-8"></div>
            </div>
          ) : topology ? (
            <>
              {/* Statistics */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                  <div className="text-2xl font-bold text-cad-accent">
                    {topology.statistics.total_nodes}
                  </div>
                  <div className="text-sm text-cad-text-secondary">Components</div>
                </div>
                <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                  <div className="text-2xl font-bold text-cad-accent">
                    {topology.statistics.total_edges}
                  </div>
                  <div className="text-sm text-cad-text-secondary">Connections</div>
                </div>
                <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                  <div className="text-2xl font-bold text-cad-success">
                    {topology.statistics.sources}
                  </div>
                  <div className="text-sm text-cad-text-secondary">Sources</div>
                </div>
                <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                  <div className="text-2xl font-bold text-cad-warning">
                    {topology.statistics.buses}
                  </div>
                  <div className="text-sm text-cad-text-secondary">Buses</div>
                </div>
              </div>

              {/* Buses */}
              {Object.keys(topology.topology.buses).length > 0 && (
                <div>
                  <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                    ðŸšŒ Identified Buses
                  </h3>
                  <div className="space-y-2">
                    {Object.entries(topology.topology.buses).map(([busName, nodeIds]) => (
                      <div
                        key={busName}
                        className="bg-cad-dark p-3 rounded-lg border border-cad-border"
                      >
                        <div className="font-medium text-cad-accent">{busName}</div>
                        <div className="text-sm text-cad-text-secondary">
                          {nodeIds.length} node{nodeIds.length !== 1 ? 's' : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Loops */}
              {topology.loops && topology.loops.length > 0 && (
                <div>
                  <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                    ðŸ”„ Detected Loops
                  </h3>
                  <div className="space-y-2">
                    {topology.loops.map((loop, index) => (
                      <div
                        key={index}
                        className="bg-cad-dark p-3 rounded-lg border border-cad-warning"
                      >
                        <div className="text-cad-warning font-medium">Loop {index + 1}</div>
                        <div className="text-sm text-cad-text-secondary">
                          {loop.length} nodes in loop
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Validation Issues */}
              {topology.validation_issues && topology.validation_issues.length > 0 ? (
                <div>
                  <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                    âš ï¸ Validation Issues
                  </h3>
                  <div className="space-y-2">
                    {topology.validation_issues.map((issue, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${
                          issue.startsWith('Error')
                            ? 'bg-cad-danger bg-opacity-10 border-cad-danger'
                            : 'bg-cad-warning bg-opacity-10 border-cad-warning'
                        }`}
                      >
                        <div className="text-sm">{issue}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="bg-cad-success bg-opacity-10 border border-cad-success rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">âœ…</span>
                    <div>
                      <div className="font-medium text-cad-success">No Issues Found</div>
                      <div className="text-sm text-cad-text-secondary">
                        Network topology is valid
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Node Levels */}
              {topology.topology.nodes && (
                <div>
                  <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                    ðŸ“Š Network Levels
                  </h3>
                  <div className="bg-cad-dark p-4 rounded-lg border border-cad-border max-h-60 overflow-y-auto">
                    <div className="space-y-1 font-mono text-sm">
                      {Object.values(topology.topology.nodes).map((node) => (
                        <div key={node.id} className="flex items-center justify-between">
                          <span className="text-cad-text-primary">{node.tag}</span>
                          <span className="text-cad-accent">Level {node.level}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-cad-text-secondary py-8">
              Click "Refresh" to analyze topology
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopologyViewer;
