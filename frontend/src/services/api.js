/**
 * API Service - Handles all API calls to the FastAPI backend
 */

import { API_URL } from '../config';

const API_BASE_URL = API_URL;

/**
 * Analyze a wallet address
 * @param {string} address - Ethereum wallet address
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeAddress(address) {
  const response = await fetch(`${API_BASE_URL}/risk/analyze/${address}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze address');
  }

  return response.json();
}

/**
 * Upload CSV for batch analysis
 * @param {File} file - CSV file with addresses
 * @returns {Promise<Object>} Analysis results
 */
export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/risk/analyze-batch`, {
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
 * Health check
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  const response = await fetch('http://localhost:8000/health');
  return response.json();
}
