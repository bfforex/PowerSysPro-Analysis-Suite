import React, { useState } from 'react';
import axios from 'axios';

const RXDiagram = ({ projectId, projectName }) => {
  const [loading, setLoading] = useState(false);
  const [diagramData, setDiagramData] = useState(null);
  const [imageData, setImageData] = useState(null);
  const [showStats, setShowStats] = useState(true);

  const generateDiagram = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/rx-diagram`
      );
      
      setDiagramData(response.data.plot_data);
      setImageData(response.data.image_base64);
    } catch (error) {
      console.error('R-X diagram generation failed:', error);
      alert('Failed to generate R-X diagram. Please check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const downloadPNG = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/rx-diagram/export/png`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${projectName}_RX_Diagram.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const downloadSVG = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/rx-diagram/export/svg`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${projectName}_RX_Diagram.svg`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <div className="rx-diagram-container">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">ðŸ“Š R-X Impedance Diagram</h3>
        
        <div className="flex gap-2">
          <button
            onClick={generateDiagram}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">â³</span>
                Generating...
              </>
            ) : (
              <>
                ðŸ“Š Generate Diagram
              </>
            )}
          </button>
        </div>
      </div>

      {diagramData && (
        <>
          {/* Diagram Image */}
          <div className="bg-white rounded-lg shadow-lg p-4 mb-4">
            <div className="flex justify-center">
              <img
                src={`data:image/png;base64,${imageData}`}
                alt="R-X Impedance Diagram"
                className="max-w-full h-auto"
              />
            </div>
            
            {/* Action Buttons */}
            <div className="flex justify-center gap-2 mt-4">
              <button
                onClick={downloadPNG}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-2"
              >
                ðŸ“¥ Download PNG
              </button>
              <button
                onClick={downloadSVG}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-2"
              >
                ðŸ“¥ Download SVG
              </button>
              <button
                onClick={() => setShowStats(!showStats)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                {showStats ? 'ðŸ“Š Hide Stats' : 'ðŸ“Š Show Stats'}
              </button>
            </div>
          </div>

          {/* Statistics */}
          {showStats && diagramData.statistics && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h4 className="text-lg font-bold mb-4">ðŸ“ˆ Impedance Statistics</h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Total Components</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {diagramData.statistics.total_components}
                  </div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Max Impedance</div>
                  <div className="text-2xl font-bold text-green-600">
                    {diagramData.statistics.max_impedance?.toFixed(3)} pu
                  </div>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Min Impedance</div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {diagramData.statistics.min_impedance?.toFixed(3)} pu
                  </div>
                </div>
                
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">Avg X/R Ratio</div>
                  <div className="text-2xl font-bold text-purple-600">
                    {diagramData.statistics.avg_x_r_ratio?.toFixed(2)}
                  </div>
                </div>
              </div>

              {/* Component Details Table */}
              <div className="mt-6">
                <h5 className="font-bold mb-2">Component Details</h5>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tag</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">R (pu)</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">X (pu)</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Z (pu)</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Angle (Â°)</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {diagramData.components?.map((comp, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-3 text-sm font-medium">{comp.tag}</td>
                          <td className="px-4 py-3 text-sm">{comp.type}</td>
                          <td className="px-4 py-3 text-sm">{comp.r?.toFixed(4)}</td>
                          <td className="px-4 py-3 text-sm">{comp.x?.toFixed(4)}</td>
                          <td className="px-4 py-3 text-sm">{comp.z?.toFixed(4)}</td>
                          <td className="px-4 py-3 text-sm">{comp.angle?.toFixed(1)}Â°</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Help Text */}
          <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 p-4">
            <h5 className="font-bold text-blue-900 mb-2">ðŸ“– About R-X Diagrams</h5>
            <p className="text-sm text-blue-800">
              The R-X diagram plots component impedances on the Resistance-Reactance plane.
              This visualization helps in:
            </p>
            <ul className="text-sm text-blue-800 list-disc ml-6 mt-2">
              <li>Protection relay coordination</li>
              <li>Understanding system impedance characteristics</li>
              <li>Identifying dominant impedance components (resistive vs. inductive)</li>
              <li>Comparing component impedances at different voltage levels</li>
            </ul>
            <p className="text-sm text-blue-800 mt-2">
              <strong>Standards:</strong> IEEE C37.113 (Protection and Coordination)
            </p>
          </div>
        </>
      )}

      {!diagramData && !loading && (
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">ðŸ“Š</div>
          <h4 className="text-xl font-bold text-gray-700 mb-2">No Diagram Generated</h4>
          <p className="text-gray-600 mb-4">
            Click "Generate Diagram" to create an R-X impedance diagram for this project.
          </p>
        </div>
      )}
    </div>
  );
};

export default RXDiagram;
