/**
 * PwrSysPro Analysis Suite - API Service
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Component Library API
// ============================================================================

export const getComponents = async (type = null) => {
  const params = type ? { type } : {};
  const response = await api.get('/components', { params });
  return response.data;
};

export const getComponent = async (componentId) => {
  const response = await api.get(`/components/${componentId}`);
  return response.data;
};

// ============================================================================
// Projects API
// ============================================================================

export const getProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};

export const getProject = async (projectId) => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

// ============================================================================
// Nodes API (Canvas Elements)
// ============================================================================

export const createNode = async (nodeData) => {
  const response = await api.post('/nodes', nodeData);
  return response.data;
};

export const getProjectNodes = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/nodes`);
  return response.data;
};

export const updateNodePosition = async (nodeId, position_x, position_y) => {
  const response = await api.put(`/nodes/${nodeId}/position`, {
    position_x,
    position_y,
  });
  return response.data;
};

export const deleteNode = async (nodeId) => {
  const response = await api.delete(`/nodes/${nodeId}`);
  return response.data;
};

// ============================================================================
// Connections API (Cables/Wires)
// ============================================================================

export const createConnection = async (connectionData) => {
  const response = await api.post('/connections', connectionData);
  return response.data;
};

export const getProjectConnections = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/connections`);
  return response.data;
};

// ============================================================================
// Calculations API
// ============================================================================

export const calculateVoltageDrop = async (calculationData) => {
  const response = await api.post('/calculate/voltage-drop', calculationData);
  return response.data;
};

export const generateTag = async (componentType, voltageKv, fromBus, toBus, sequence = 1) => {
  const response = await api.post('/calculate/tag', null, {
    params: {
      component_type: componentType,
      voltage_kv: voltageKv,
      from_bus: fromBus,
      to_bus: toBus,
      sequence,
    },
  });
  return response.data;
};

// ============================================================================
// Error Handling
// ============================================================================

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
