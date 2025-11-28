/**
 * Custom hook for API calls with loading, error states
 * Industry-level pattern
 */

import { useState, useCallback } from 'react';
import { apiService } from '@/services/api.service';

export const useApi = (apiFunc) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...params) => {
      try {
        setLoading(true);
        setError(null);

        const response = await apiFunc(...params);
        setData(response);

        return { success: true, data: response };
      } catch (err) {
        setError(err.message || 'An error occurred');
        return { success: false, error: err };
      } finally {
        setLoading(false);
      }
    },
    [apiFunc]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
};
