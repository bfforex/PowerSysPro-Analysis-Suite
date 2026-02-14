/**
 * PwrSysPro Analysis Suite - Property Inspector
 * Displays and allows editing of selected component properties
 */

import React, { useState, useEffect } from 'react';
import { calculateVoltageDrop } from '../services/api';

const PropertyInspector = ({ selectedNode }) => {
  const [calculationResults, setCalculationResults] = useState(null);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    // Reset when selection changes
    setCalculationResults(null);
  }, [selectedNode]);

  const handleCalculate = async () => {
    if (!selectedNode || !selectedNode.data.component) {
      return;
    }

    setCalculating(true);
    
    try {
      // Example calculation - voltage drop
      // In a real implementation, this would use actual circuit topology
      const result = await calculateVoltageDrop({
        resistance_per_km: selectedNode.data.component.impedance_r || 0.161,
        reactance_per_km: selectedNode.data.component.impedance_x || 0.086,
        length_km: 0.050, // 50m default
        ampacity_base: selectedNode.data.component.ampacity_base || 285,
        load_current: 200, // Default load current
        power_factor: 0.85,
        voltage_nominal: 400,
        ambient_temp: 30,
        num_cables_grouped: 1,
        installation_method: 'E',
        phases: 3,
      });
      
      setCalculationResults(result);
    } catch (error) {
      console.error('Calculation error:', error);
    } finally {
      setCalculating(false);
    }
  };

  if (!selectedNode) {
    return (
      <div className="property-inspector w-80 h-full p-4">
        <div className="text-center text-cad-text-secondary py-8">
          <div className="text-4xl mb-3">â—¯</div>
          <p className="text-sm">Select a component to view properties</p>
        </div>
      </div>
    );
  }

  const { data } = selectedNode;

  return (
    <div className="property-inspector w-80 h-full overflow-y-auto p-4">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <span className="text-3xl">
            {data.type === 'Source' && 'âš¡'}
            {data.type === 'Transformer' && 'ðŸ”„'}
            {data.type === 'Motor' && 'M~'}
            {data.type === 'Bus' && 'â–¬'}
            {data.type === 'Breaker' && 'âŠ¥âŠ¥'}
            {data.type === 'Load' && 'ðŸ’¡'}
          </span>
          <div>
            <h2 className="text-lg font-semibold text-cad-text-primary">
              {data.type}
            </h2>
            <p className="text-xs text-cad-text-secondary">{data.label}</p>
          </div>
        </div>
        
        {/* Tag Display */}
        {data.tag && (
          <div className="component-tag inline-block">
            {data.tag}
          </div>
        )}
      </div>

      {/* Component Library Info */}
      {data.component && (
        <div className="property-group">
          <h3 className="text-sm font-medium text-cad-text-primary mb-3 border-b border-cad-border pb-2">
            Component Specifications
          </h3>
          
          <div className="space-y-3">
            <div>
              <label className="property-label">Manufacturer</label>
              <div className="property-value bg-opacity-50">
                {data.component.manufacturer}
              </div>
            </div>

            <div>
              <label className="property-label">Model</label>
              <div className="property-value bg-opacity-50">
                {data.component.model}
              </div>
            </div>

            <div>
              <label className="property-label">Voltage Rating</label>
              <div className="property-value bg-opacity-50">
                {data.component.voltage_rating} kV
              </div>
            </div>

            {data.component.ampacity_base && (
              <div>
                <label className="property-label">Base Ampacity</label>
                <div className="property-value bg-opacity-50">
                  {data.component.ampacity_base} A
                </div>
              </div>
            )}

            {data.component.impedance_r && (
              <div>
                <label className="property-label">Resistance (R)</label>
                <div className="property-value bg-opacity-50">
                  {data.component.impedance_r} Î©/km
                </div>
              </div>
            )}

            {data.component.impedance_x && (
              <div>
                <label className="property-label">Reactance (X)</label>
                <div className="property-value bg-opacity-50">
                  {data.component.impedance_x} Î©/km
                </div>
              </div>
            )}

            {data.component.short_circuit_rating && (
              <div>
                <label className="property-label">Short Circuit Rating</label>
                <div className="property-value bg-opacity-50">
                  {data.component.short_circuit_rating} kA
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Calculation Section */}
      <div className="property-group mt-6">
        <h3 className="text-sm font-medium text-cad-text-primary mb-3 border-b border-cad-border pb-2">
          Analysis
        </h3>
        
        <button
          onClick={handleCalculate}
          disabled={calculating || !data.component}
          className="btn btn-primary w-full mb-4"
        >
          {calculating ? (
            <span className="flex items-center justify-center">
              <div className="spinner w-4 h-4 mr-2"></div>
              Calculating...
            </span>
          ) : (
            'âš¡ Calculate Voltage Drop'
          )}
        </button>

        {calculationResults && (
          <div className="space-y-3">
            <div>
              <label className="property-label">Voltage Drop</label>
              <div className={`property-value ${
                calculationResults.voltage_drop.voltage_drop_percent > 5 
                  ? 'border-cad-danger' 
                  : 'border-cad-success'
              }`}>
                {calculationResults.voltage_drop.voltage_drop_volts}V 
                ({calculationResults.voltage_drop.voltage_drop_percent}%)
              </div>
            </div>

            <div>
              <label className="property-label">Status</label>
              <div className={`result-badge ${
                calculationResults.voltage_drop.status === 'PASS'
                  ? 'result-badge-pass'
                  : 'result-badge-fail'
              }`}>
                {calculationResults.voltage_drop.status}
              </div>
            </div>

            <div>
              <label className="property-label">Power Loss</label>
              <div className="property-value">
                {calculationResults.voltage_drop.power_loss_watts}W
              </div>
            </div>

            <div>
              <label className="property-label">Cable Utilization</label>
              <div className="property-value">
                {calculationResults.cable_sizing.utilization_percent}%
              </div>
            </div>

            <div>
              <label className="property-label">Effective Ampacity</label>
              <div className="property-value">
                {calculationResults.cable_sizing.cable_ampacity_effective}A
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Position Info (for debugging) */}
      <div className="property-group mt-6">
        <h3 className="text-sm font-medium text-cad-text-secondary mb-3 border-b border-cad-border pb-2">
          Position
        </h3>
        <div className="text-xs text-cad-text-secondary space-y-1">
          <div>X: {Math.round(selectedNode.position.x)}</div>
          <div>Y: {Math.round(selectedNode.position.y)}</div>
          <div>ID: {selectedNode.id}</div>
        </div>
      </div>
    </div>
  );
};

export default PropertyInspector;
