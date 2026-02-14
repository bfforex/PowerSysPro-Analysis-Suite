/**
 * PwrSysPro Analysis Suite - Component Library Sidebar
 * Displays available electrical components that can be dragged onto the canvas
 */

import React, { useEffect, useState } from 'react';
import { getComponents } from '../services/api';

const ComponentLibrary = () => {
  const [components, setComponents] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);

  // Component categories for filtering
  const categories = ['All', 'Cable', 'Breaker', 'Transformer', 'Motor', 'Bus', 'Source'];

  useEffect(() => {
    loadComponents();
  }, []);

  const loadComponents = async () => {
    try {
      const data = await getComponents();
      setComponents(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading components:', error);
      setLoading(false);
    }
  };

  // Handle drag start - sets data for drop event
  const onDragStart = (event, nodeType, component = null) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({
      type: nodeType,
      component: component,
    }));
    event.dataTransfer.effectAllowed = 'move';
  };

  // Filter components by category
  const filteredComponents = selectedCategory === 'All' 
    ? components 
    : components.filter(c => c.type === selectedCategory);

  // Group basic components (not from library)
  const basicComponents = [
    { type: 'Source', icon: 'âš¡', label: 'Power Source', color: 'text-yellow-500' },
    { type: 'Bus', icon: 'â–¬', label: 'Busbar', color: 'text-blue-500' },
    { type: 'Transformer', icon: 'ðŸ”„', label: 'Transformer', color: 'text-purple-500' },
    { type: 'Motor', icon: 'M~', label: 'Motor', color: 'text-green-500' },
    { type: 'Load', icon: 'ðŸ’¡', label: 'Load', color: 'text-orange-500' },
    { type: 'Breaker', icon: 'âŠ¥âŠ¥', label: 'Circuit Breaker', color: 'text-red-500' },
  ];

  return (
    <div className="component-library w-80 h-full overflow-y-auto p-4">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-cad-text-primary mb-2">
          Component Library
        </h2>
        <p className="text-xs text-cad-text-secondary">
          Drag components onto the canvas
        </p>
      </div>

      {/* Category Filter */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-1">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`text-xs px-3 py-1 rounded-lg transition-colors ${
                selectedCategory === category
                  ? 'bg-cad-accent text-white'
                  : 'bg-cad-dark text-cad-text-secondary hover:bg-cad-panel'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Basic Components Section */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-cad-text-secondary mb-3">
          Basic Components
        </h3>
        <div className="space-y-2">
          {basicComponents.map((comp) => (
            <div
              key={comp.type}
              className="component-item"
              draggable
              onDragStart={(e) => onDragStart(e, comp.type)}
            >
              <div className="flex items-center space-x-3">
                <span className={`text-2xl ${comp.color}`}>{comp.icon}</span>
                <div className="flex-1">
                  <div className="text-sm font-medium text-cad-text-primary">
                    {comp.label}
                  </div>
                  <div className="text-xs text-cad-text-secondary">
                    {comp.type}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Manufacturer Components Section */}
      {!loading && filteredComponents.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-cad-text-secondary mb-3">
            Manufacturer Library
          </h3>
          
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="spinner w-8 h-8"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredComponents.map((component) => (
                <div
                  key={component.id}
                  className="component-item"
                  draggable
                  onDragStart={(e) => onDragStart(e, component.type, component)}
                >
                  <div className="flex flex-col space-y-1">
                    <div className="text-sm font-medium text-cad-text-primary">
                      {component.manufacturer} {component.model}
                    </div>
                    <div className="text-xs text-cad-text-secondary">
                      {component.type} â€¢ {component.voltage_rating}kV
                    </div>
                    {component.ampacity_base && (
                      <div className="text-xs text-cad-accent">
                        {component.ampacity_base}A
                      </div>
                    )}
                    {component.short_circuit_rating && (
                      <div className="text-xs text-cad-accent">
                        {component.short_circuit_rating}kA
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-6 p-3 bg-cad-dark rounded-lg border border-cad-border">
        <h4 className="text-xs font-medium text-cad-text-primary mb-2">
          ðŸ’¡ Quick Tips
        </h4>
        <ul className="text-xs text-cad-text-secondary space-y-1">
          <li>â€¢ Drag components to canvas</li>
          <li>â€¢ Connect by dragging handles</li>
          <li>â€¢ Click to edit properties</li>
          <li>â€¢ Auto-tag updates on connection</li>
        </ul>
      </div>
    </div>
  );
};

export default ComponentLibrary;
