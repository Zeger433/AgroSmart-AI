import { useState } from 'react';
import { motion } from 'framer-motion';
import InputForm from '../components/predict/InputForm';
import ResultCard from '../components/predict/ResultCard';
import Toast from '../components/ui/Toast';
import { usePrediction } from '../hooks/usePrediction';

function EmptyState() {
  return (
    <div className="card flex flex-col items-center justify-center min-h-[600px] h-full text-center p-8">
      <svg className="w-24 h-24 text-brand-500/40 mb-6" viewBox="0 0 80 120" aria-hidden>
        <path d="M40 10 Q50 40 40 70 Q30 40 40 10" fill="currentColor" opacity="0.5" />
        <path d="M40 70 L40 110" stroke="currentColor" strokeWidth="3" />
        <ellipse cx="40" cy="75" rx="20" ry="6" fill="currentColor" opacity="0.3" />
      </svg>
      <p className="font-medium text-gray-700 dark:text-gray-300">Submit your field data to get a crop recommendation</p>
      <p className="text-sm text-gray-500 mt-2">Results will appear here</p>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="card min-h-[600px] h-full space-y-4 animate-pulse p-8" aria-busy="true" aria-label="Loading results">
      <div className="h-8 bg-gray-200 dark:bg-white/10 rounded w-1/2" />
      <div className="h-24 bg-gray-200 dark:bg-white/10 rounded" />
      <div className="h-4 bg-gray-200 dark:bg-white/10 rounded w-3/4" />
      <div className="h-4 bg-gray-200 dark:bg-white/10 rounded w-1/2" />
    </div>
  );
}

export default function Predict() {
  const { result, loading, error, predict, reset } = usePrediction();
  const [toastDismissed, setToastDismissed] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10"
    >
      <header className="mb-10">
        <h1 className="section-heading">Crop &amp; Yield Predictor</h1>
        <p className="section-subtext">Enter soil and climate data for an ML-powered recommendation.</p>
      </header>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="w-full lg:min-w-[480px] lg:max-w-[560px] lg:shrink-0">
          <InputForm onSubmit={predict} loading={loading} />
        </div>
        <section className="flex-1 min-w-0 lg:min-w-[400px] min-h-[600px] flex flex-col" aria-label="Prediction insights">
          <h2 className="sr-only">Insights</h2>
          {loading && <Skeleton />}
          {!loading && result && <ResultCard result={result} onReset={reset} />}
          {!loading && !result && <EmptyState />}
        </section>
      </div>

      <Toast
        message={error && !toastDismissed ? error : null}
        type="error"
        onClose={() => setToastDismissed(true)}
      />
    </motion.div>
  );
}
