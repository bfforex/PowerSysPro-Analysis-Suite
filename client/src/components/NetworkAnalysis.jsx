/**
 * PwrSysPro Analysis Suite - Network Analysis (Phase 3)
 * Displays comprehensive power system analysis results:
 * - Short Circuit Analysis (IEC 60909)
 * - Load Flow Analysis (Newton-Raphson)
 * - Breaker Validation
 * - Per-Unit System
 */

import React, { useState } from 'react';
import axios from 'axios';

const NetworkAnalysis = ({ projectId, currentProject }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [analysisType, setAnalysisType] = useState('complete');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runAnalysis = async (type) => {
    if (!projectId) {
      alert('No project selected');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysisType(type);

    try {
      let endpoint;
      switch (type) {
        case 'short-circuit':
          endpoint = `/api/projects/${projectId}/analyze/short-circuit`;
          break;
        case 'load-flow':
          endpoint = `/api/projects/${projectId}/analyze/load-flow`;
          break;
        case 'arc-flash':
          endpoint = `/api/projects/${projectId}/analyze/arc-flash`;
          break;
        case 'complete':
          endpoint = `/api/projects/${projectId}/analyze/complete`;
          break;
        default:
          endpoint = `/api/projects/${projectId}/analyze/complete`;
      }

      const response = await axios.post(`http://localhost:8000${endpoint}`);
      setResults(response.data);
      setIsOpen(true);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || err.message);
      alert(`âŒ Analysis failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const AnalysisButtons = () => (
    <div className="flex space-x-2">
      <button
        onClick={() => runAnalysis('short-circuit')}
        disabled={loading || !projectId}
        className="btn btn-primary text-sm"
        title="IEC 60909 Short Circuit Analysis"
      >
        {loading && analysisType === 'short-circuit' ? (
          <span className="flex items-center">
            <div className="spinner w-4 h-4 mr-2"></div>
            Analyzing...
          </span>
        ) : (
          'âš¡ Short Circuit'
        )}
      </button>

      <button
        onClick={() => runAnalysis('load-flow')}
        disabled={loading || !projectId}
        className="btn btn-primary text-sm"
        title="Newton-Raphson Load Flow"
      >
        {loading && analysisType === 'load-flow' ? (
          <span className="flex items-center">
            <div className="spinner w-4 h-4 mr-2"></div>
            Analyzing...
          </span>
        ) : (
          'ðŸ“ˆ Load Flow'
        )}
      </button>

      <button
        onClick={() => runAnalysis('arc-flash')}
        disabled={loading || !projectId}
        className="btn btn-danger text-sm"
        title="IEEE 1584 Arc Flash Analysis"
      >
        {loading && analysisType === 'arc-flash' ? (
          <span className="flex items-center">
            <div className="spinner w-4 h-4 mr-2"></div>
            Analyzing...
          </span>
        ) : (
          'ðŸ”¥ Arc Flash'
        )}
      </button>

      <button
        onClick={() => runAnalysis('complete')}
        disabled={loading || !projectId}
        className="btn btn-success text-sm"
        title="Complete Network Analysis"
      >
        {loading && analysisType === 'complete' ? (
          <span className="flex items-center">
            <div className="spinner w-4 h-4 mr-2"></div>
            Analyzing...
          </span>
        ) : (
          'ðŸŽ¯ Complete Analysis'
        )}
      </button>
    </div>
  );

  if (!isOpen || !results) {
    return <AnalysisButtons />;
  }

  return (
    <>
      <AnalysisButtons />
      
      {/* Results Modal */}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-cad-panel border border-cad-border rounded-lg w-11/12 max-w-6xl max-h-5/6 overflow-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-cad-border sticky top-0 bg-cad-panel">
            <div>
              <h2 className="text-lg font-semibold text-cad-text-primary">
                {results.analysis_type}
              </h2>
              <p className="text-sm text-cad-text-secondary">
                {currentProject?.name || 'Project Analysis'}
              </p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="btn btn-secondary text-sm"
            >
              âœ• Close
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Complete Analysis Results */}
            {analysisType === 'complete' && results.project && (
              <>
                {/* Project Info */}
                <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                  <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                    ðŸ“‹ Project Information
                  </h3>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-cad-text-secondary">Base MVA</div>
                      <div className="text-cad-accent font-medium">{results.project.base_mva}</div>
                    </div>
                    <div>
                      <div className="text-cad-text-secondary">Frequency</div>
                      <div className="text-cad-accent font-medium">{results.project.frequency_hz} Hz</div>
                    </div>
                    <div>
                      <div className="text-cad-text-secondary">Standard</div>
                      <div className="text-cad-accent font-medium">{results.project.standard}</div>
                    </div>
                    <div>
                      <div className="text-cad-text-secondary">Status</div>
                      <div className={`font-medium ${
                        results.overall_status === 'PASS' ? 'text-cad-success' : 'text-cad-warning'
                      }`}>
                        {results.overall_status}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Short Circuit Summary */}
                {results.short_circuit_summary && (
                  <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                    <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                      âš¡ Short Circuit Summary
                    </h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-2xl font-bold text-cad-danger">
                          {results.short_circuit_summary.max_fault_current_ka} kA
                        </div>
                        <div className="text-sm text-cad-text-secondary">Max Fault Current</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-2xl font-bold text-cad-accent">
                          {results.short_circuit_summary.buses_analyzed}
                        </div>
                        <div className="text-sm text-cad-text-secondary">Buses Analyzed</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-sm text-cad-text-secondary mb-1">Critical Bus</div>
                        <div className="text-lg font-medium text-cad-warning">
                          {results.short_circuit_summary.max_fault_bus || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Load Flow Summary */}
                {results.load_flow_summary && (
                  <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                    <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                      ðŸ“ˆ Load Flow Summary
                    </h3>
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-success">
                          {results.load_flow_summary.converged ? 'âœ…' : 'âŒ'}
                        </div>
                        <div className="text-sm text-cad-text-secondary">
                          {results.load_flow_summary.converged ? 'Converged' : 'Not Converged'}
                        </div>
                        <div className="text-xs text-cad-text-secondary mt-1">
                          {results.load_flow_summary.iterations} iterations
                        </div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-accent">
                          {results.load_flow_summary.total_load_mw} MW
                        </div>
                        <div className="text-sm text-cad-text-secondary">Total Load</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-warning">
                          {results.load_flow_summary.total_losses_mw} MW
                        </div>
                        <div className="text-sm text-cad-text-secondary">Total Losses</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-text-primary">
                          {results.load_flow_summary.loss_percent}%
                        </div>
                        <div className="text-sm text-cad-text-secondary">Loss Percentage</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Breaker Summary */}
                {results.breaker_summary && (
                  <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                    <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                      ðŸ”’ Breaker Validation Summary
                    </h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-accent">
                          {results.breaker_summary.total}
                        </div>
                        <div className="text-sm text-cad-text-secondary">Total Breakers</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-success">
                          {results.breaker_summary.pass} âœ…
                        </div>
                        <div className="text-sm text-cad-text-secondary">Pass</div>
                      </div>
                      <div className="text-center p-3 bg-cad-panel rounded-lg">
                        <div className="text-xl font-bold text-cad-danger">
                          {results.breaker_summary.fail} âŒ
                        </div>
                        <div className="text-sm text-cad-text-secondary">Fail</div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Arc Flash Detailed Results */}
            {analysisType === 'arc-flash' && results.results && Object.keys(results.results).length > 0 && (
              <div className="bg-cad-dark p-4 rounded-lg border border-cad-danger">
                <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                  ðŸ”¥ Arc Flash Analysis Results (IEEE 1584-2018)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-cad-border">
                        <th className="text-left p-2 text-cad-text-secondary">Bus</th>
                        <th className="text-right p-2 text-cad-text-secondary">IE (cal/cmÂ²)</th>
                        <th className="text-right p-2 text-cad-text-secondary">AFB (ft)</th>
                        <th className="text-center p-2 text-cad-text-secondary">PPE Cat</th>
                        <th className="text-center p-2 text-cad-text-secondary">Hazard</th>
                        <th className="text-center p-2 text-cad-text-secondary">Safe</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(results.results).map(([busId, data]) => (
                        <tr key={busId} className="border-b border-cad-border hover:bg-cad-panel">
                          <td className="p-2 font-mono text-cad-accent">{data.node_tag}</td>
                          <td className={`p-2 text-right font-medium ${
                            data.incident_energy > 40 ? 'text-cad-danger' :
                            data.incident_energy > 25 ? 'text-cad-warning' :
                            data.incident_energy > 8 ? 'text-orange-500' :
                            'text-cad-success'
                          }`}>
                            {data.incident_energy}
                          </td>
                          <td className="p-2 text-right">{data.afb_ft}</td>
                          <td className="p-2 text-center">
                            <span className={`px-2 py-1 rounded text-xs ${
                              data.ppe_category.includes('4') ? 'bg-cad-danger text-white' :
                              data.ppe_category.includes('3') ? 'bg-orange-600 text-white' :
                              data.ppe_category.includes('2') ? 'bg-cad-warning text-black' :
                              'bg-cad-success text-white'
                            }`}>
                              {data.ppe_category}
                            </span>
                          </td>
                          <td className="p-2 text-center text-xs">{data.hazard_level}</td>
                          <td className="p-2 text-center">{data.is_safe ? 'âœ…' : 'âš ï¸'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Safety Warning */}
                <div className="mt-4 p-3 bg-cad-danger bg-opacity-10 border border-cad-danger rounded-lg">
                  <div className="flex items-start space-x-2">
                    <span className="text-xl">âš ï¸</span>
                    <div className="text-sm">
                      <div className="font-medium text-cad-danger mb-1">Safety Notice</div>
                      <div className="text-cad-text-secondary">
                        All personnel must wear appropriate PPE as indicated above when working on energized equipment.
                        Consider de-energizing equipment when incident energy exceeds 40 cal/cmÂ².
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Short Circuit Detailed Results */}
            {results.results && Object.keys(results.results).length > 0 && (
              <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                  âš¡ Short Circuit Detailed Results
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-cad-border">
                        <th className="text-left p-2 text-cad-text-secondary">Bus</th>
                        <th className="text-right p-2 text-cad-text-secondary">I"k3 (kA)</th>
                        <th className="text-right p-2 text-cad-text-secondary">ip (kA)</th>
                        <th className="text-right p-2 text-cad-text-secondary">Ib (kA)</th>
                        <th className="text-right p-2 text-cad-text-secondary">Sk (MVA)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(results.results).map(([busId, data]) => (
                        <tr key={busId} className="border-b border-cad-border hover:bg-cad-panel">
                          <td className="p-2 font-mono text-cad-accent">{data.node_tag}</td>
                          <td className="p-2 text-right font-medium">{data.i_k3_initial_ka}</td>
                          <td className="p-2 text-right">{data.i_k3_peak_ka}</td>
                          <td className="p-2 text-right">{data.i_k3_breaking_ka}</td>
                          <td className="p-2 text-right">{data.s_k3_mva}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Load Flow Detailed Results */}
            {results.bus_results && Object.keys(results.bus_results).length > 0 && (
              <div className="bg-cad-dark p-4 rounded-lg border border-cad-border">
                <h3 className="text-md font-semibold text-cad-text-primary mb-3">
                  ðŸ“ˆ Load Flow Detailed Results
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-cad-border">
                        <th className="text-left p-2 text-cad-text-secondary">Bus</th>
                        <th className="text-right p-2 text-cad-text-secondary">V (pu)</th>
                        <th className="text-right p-2 text-cad-text-secondary">Î¸ (deg)</th>
                        <th className="text-right p-2 text-cad-text-secondary">P (MW)</th>
                        <th className="text-right p-2 text-cad-text-secondary">Q (MVAR)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(results.bus_results).map(([busId, data]) => (
                        <tr key={busId} className="border-b border-cad-border hover:bg-cad-panel">
                          <td className="p-2 font-mono text-cad-accent">{data.node_tag}</td>
                          <td className={`p-2 text-right font-medium ${
                            data.v_magnitude_pu < 0.95 ? 'text-cad-danger' : 
                            data.v_magnitude_pu > 1.05 ? 'text-cad-warning' :
                            'text-cad-success'
                          }`}>
                            {data.v_magnitude_pu}
                          </td>
                          <td className="p-2 text-right">{data.v_angle_deg}Â°</td>
                          <td className="p-2 text-right">{data.p_mw}</td>
                          <td className="p-2 text-right">{data.q_mvar}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default NetworkAnalysis;
