/**
 * API Service - Handles all API calls to the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Analyze a wallet address
 * @param {string} address - Ethereum wallet address
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeAddress(address) {
  const response = await fetch(`${API_BASE_URL}/predict/address/${address}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze address');
  }
  
  return response.json();
}

/**
 * Upload CSV for analysis
 * @param {File} file - CSV file with on-chain features
 * @returns {Promise<Object>} Analysis results
 */
export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/predict/csv`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process CSV');
  }
  
  return response.json();
}

/**
 * Get list of available addresses
 * @param {string} search - Optional search filter
 * @param {number} limit - Maximum results to return
 * @returns {Promise<Object>} List of addresses
 */
export async function getAddresses(search = '', limit = 100) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  params.append('limit', limit.toString());
  
  const response = await fetch(`${API_BASE_URL}/predict/addresses?${params}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch addresses');
  }
  
  return response.json();
}

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  const response = await fetch('http://localhost:8000/health');
  return response.json();
}
