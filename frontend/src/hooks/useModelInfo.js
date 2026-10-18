import { useState, useEffect } from 'react';
import { getModelInfo } from '../utils/api';

export function useModelInfo() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getModelInfo()
      .then(setInfo)
      .catch(() => setError('Could not load model info'))
      .finally(() => setLoading(false));
  }, []);

  return { info, loading, error };
}
