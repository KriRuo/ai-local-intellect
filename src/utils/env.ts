// Utility to get the API URL in Vite environments
export const getApiUrl = () => {
  return import.meta.env.VITE_API_URL || 'http://localhost:8081/api';
}; 