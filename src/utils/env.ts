// Utility to get the API URL in both Vite and Jest environments
export const getApiUrl = () => {
  // This dynamic function prevents Jest/Babel from parsing import.meta
  try {
    // eslint-disable-next-line no-new-func
    return new Function('return typeof importMeta !== "undefined" && importMeta.env && importMeta.env.VITE_API_URL ? importMeta.env.VITE_API_URL : (typeof import !== "undefined" && import.meta && import.meta.env && import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL : undefined);')();
  } catch {
    // ignore
  }
  return process.env.VITE_API_URL || 'http://localhost:8001/api';
}; 