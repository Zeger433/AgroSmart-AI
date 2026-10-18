import { useState } from 'react';
import { predictCrop } from '../utils/api';

export function usePrediction() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictCrop(formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Check inputs.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { result, loading, error, predict, reset };
}
