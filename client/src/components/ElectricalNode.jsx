/**
 * PwrSysPro Analysis Suite - Custom Electrical Node Component
 * Represents electrical components on the canvas (Sources, Transformers, Motors, etc.)
 */

import React from 'react';
import { Handle, Position } from 'reactflow';

const ElectricalNode = ({ data, selected }) => {
  // Determine node icon based on component type
  const getNodeIcon = (type) => {
    const icons = {
      Source: 'âš¡',
      Transformer: 'ðŸ”„',
      Bus: 'â–¬',
      Breaker: 'âŠ¥âŠ¥',
      Motor: 'M~',
      Cable: 'â€”',
      Load: 'ðŸ’¡',
      Panel: 'â–­',
      Generator: 'G~',
    };
    return icons[type] || 'â—¯';
  };

  // Determine status color
  const getStatusClass = () => {
    if (!data.status) return '';
    
    const statusClasses = {
      PASS: 'node-status-pass',
      WARNING: 'node-status-warning',
      FAIL: 'node-status-fail',
    };
    
    return statusClasses[data.status] || '';
  };

  // Determine if component has results to display
  const hasResults = data.results && Object.keys(data.results).length > 0;

  return (
    <div className={`custom-node ${selected ? 'selected' : ''} ${getStatusClass()}`}>
      {/* Input Handle (Top) */}
      <Handle
        type="target"
        position={Position.Top}
        id="input"
        className="!bg-cad-accent"
      />

      {/* Node Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getNodeIcon(data.type)}</span>
          <span className="font-medium text-sm">{data.type}</span>
        </div>
        
        {/* Status Indicator */}
        {data.status && (
          <span className={`text-xs px-2 py-0.5 rounded 
            ${data.status === 'PASS' ? 'bg-cad-success text-white' : ''}
            ${data.status === 'WARNING' ? 'bg-cad-warning text-white' : ''}
            ${data.status === 'FAIL' ? 'bg-cad-danger text-white' : ''}
          `}>
            {data.status}
          </span>
        )}
      </div>

      {/* Component Tag */}
      {data.tag && (
        <div className="component-tag mb-2">
          {data.tag}
        </div>
      )}

      {/* Component Label */}
      {data.label && (
        <div className="text-xs text-cad-text-secondary mb-2">
          {data.label}
        </div>
      )}

      {/* Calculation Results (if available) */}
      {hasResults && (
        <div className="mt-2 pt-2 border-t border-cad-border space-y-1">
          {data.results.voltage && (
            <div className="text-xs">
              <span className="text-cad-text-secondary">V: </span>
              <span className="text-cad-accent font-mono">{data.results.voltage}V</span>
            </div>
          )}
          {data.results.current && (
            <div className="text-xs">
              <span className="text-cad-text-secondary">I: </span>
              <span className="text-cad-accent font-mono">{data.results.current}A</span>
            </div>
          )}
          {data.results.voltage_drop_percent && (
            <div className="text-xs">
              <span className="text-cad-text-secondary">Î”V: </span>
              <span className={`font-mono ${
                data.results.voltage_drop_percent > 5 ? 'text-cad-danger' : 'text-cad-success'
              }`}>
                {data.results.voltage_drop_percent}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* Output Handle (Bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        className="!bg-cad-accent"
      />
    </div>
  );
};

export default ElectricalNode;
