/**
 * PwrSysPro Analysis Suite - Main Canvas Component
 * Interactive Single Line Diagram (SLD) canvas using ReactFlow
 */

import React, { useState, useCallback, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

import ElectricalNode from './ElectricalNode';
import { createNode, createConnection, updateNodePosition } from '../services/api';

const nodeTypes = {
  electrical: ElectricalNode,
};

let nodeId = 0;
const getNodeId = () => `node_${nodeId++}`;

const Canvas = ({ projectId, onNodeSelect }) => {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  // Handle connection creation
  const onConnect = useCallback(
    async (params) => {
      // Create edge in UI
      setEdges((eds) => addEdge({
        ...params,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      }, eds));

      // Save connection to backend
      try {
        await createConnection({
          project_id: projectId,
          source_node_id: params.source,
          target_node_id: params.target,
          length: 50, // Default length in meters
        });
        console.log('Connection saved to backend');
      } catch (error) {
        console.error('Error saving connection:', error);
      }
    },
    [projectId]
  );

  // Handle drag over event for drop zone
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Handle drop event - create new node
  const onDrop = useCallback(
    async (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const data = JSON.parse(
        event.dataTransfer.getData('application/reactflow')
      );

      // Calculate position relative to ReactFlow canvas
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNodeId = getNodeId();
      
      // Generate tag (simplified for now)
      const tag = `${data.type}-${newNodeId}`;

      // Create node data
      const newNode = {
        id: newNodeId,
        type: 'electrical',
        position,
        data: {
          type: data.type,
          label: data.component?.model || data.type,
          tag: tag,
          component: data.component,
          results: {},
        },
      };

      // Add node to canvas
      setNodes((nds) => nds.concat(newNode));

      // Save to backend
      try {
        await createNode({
          project_id: projectId,
          type: data.type,
          position_x: position.x,
          position_y: position.y,
          component_library_id: data.component?.id || null,
          properties: { tag },
        });
        console.log('Node saved to backend');
      } catch (error) {
        console.error('Error saving node:', error);
      }
    },
    [reactFlowInstance, projectId]
  );

  // Handle node drag end - save position
  const onNodeDragStop = useCallback(
    async (event, node) => {
      try {
        await updateNodePosition(node.id, node.position.x, node.position.y);
        console.log('Node position updated');
      } catch (error) {
        console.error('Error updating node position:', error);
      }
    },
    []
  );

  // Handle node selection
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
    if (onNodeSelect) {
      onNodeSelect(node);
    }
  }, [onNodeSelect]);

  // Handle canvas click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    if (onNodeSelect) {
      onNodeSelect(null);
    }
  }, [onNodeSelect]);

  return (
    <div className="w-full h-full" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeDragStop={onNodeDragStop}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        snapToGrid
        snapGrid={[15, 15]}
      >
        {/* Grid Background - CAD style */}
        <Background 
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#1e2942"
        />
        
        {/* Controls */}
        <Controls className="!bg-cad-panel !border-cad-border" />
        
        {/* MiniMap */}
        <MiniMap
          className="!bg-cad-panel !border-cad-border"
          nodeColor={(node) => {
            switch (node.data.status) {
              case 'PASS': return '#10b981';
              case 'WARNING': return '#f59e0b';
              case 'FAIL': return '#ef4444';
              default: return '#2563eb';
            }
          }}
          maskColor="rgba(10, 14, 26, 0.7)"
        />
      </ReactFlow>
    </div>
  );
};

export default Canvas;
