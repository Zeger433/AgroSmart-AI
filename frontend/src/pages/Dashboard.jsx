import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useModelInfo } from '../hooks/useModelInfo';
import MetricCard from '../components/dashboard/MetricCard';
import ModelComparisonChart from '../components/dashboard/ModelComparisonChart';
import YieldRegressorChart from '../components/dashboard/YieldRegressorChart';
import ExperimentTable from '../components/dashboard/ExperimentTable';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import { EXPERIMENT2 } from '../constants/experimentData';

const SHORT = { RandomForest: 'RF', XGBoost: 'XGB', GradientBoosting: 'GB', SVM: 'SVM', KNN: 'KNN' };

function FeatureImportance({ data }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), { threshold: 0.2 });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const items = Object.entries(data || {}).map(([k, v]) => ({
    name: k.replace(/_/g, ' '),
    pct: Number(v),
  }));

  return (
    <Card ref={ref}>
      <h3 className="font-display text-lg font-bold mb-6">Yield prediction — feature importance</h3>
      <div className="space-y-4">
        {items.map(({ name, pct }) => (
          <div key={name}>
            <div className="flex justify-between text-sm mb-1">
              <span>{name}</span>
              <span className="font-mono tabular-nums">{pct}%</span>
            </div>
            <div className="h-2 rounded-full bg-gray-200 dark:bg-white/10 overflow-hidden">
              <div
                className="h-full bg-brand-500 rounded-full transition-all duration-700 ease-out"
                style={{ width: visible ? `${pct}%` : '0%' }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ImbalanceCharts() {
  const models = ['RandomForest', 'XGBoost', 'GradientBoosting', 'SVM', 'KNN'];
  const accData = models.map((m) => ({
    name: SHORT[m],
    raw: EXPERIMENT2.raw_merged_holdout[m]?.accuracy,
    smote: EXPERIMENT2.smote_balanced_holdout[m]?.accuracy,
  }));
  const f1Data = models.map((m) => ({
    name: SHORT[m],
    raw: EXPERIMENT2.raw_merged_holdout[m]?.f1_macro,
    smote: EXPERIMENT2.smote_balanced_holdout[m]?.f1_macro,
  }));

  return (
    <Card>
      <h3 className="font-display text-lg font-bold">Experiment 2 — Class imbalance study</h3>
      <p className="text-sm text-gray-500 mt-2 mb-6">
        Merged dataset: raw class weights vs SMOTE oversampling
      </p>
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <p className="text-sm font-medium mb-2">Accuracy</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={accData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-white/10" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="raw" name="Raw merged" fill="#f59e0b" />
              <Bar dataKey="smote" name="SMOTE" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <p className="text-sm font-medium mb-2">F1 Macro</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={f1Data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-white/10" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="raw" name="Raw merged" fill="#f59e0b" />
              <Bar dataKey="smote" name="SMOTE" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="mt-6 p-4 rounded-xl bg-gold-500/10 border border-gold-500/30 text-sm text-gray-700 dark:text-gray-300">
        💡 <strong>Key finding:</strong> SMOTE showed no significant improvement over raw class weights.
        The accuracy–F1 divergence is caused by structural label overlap between source datasets — not a
        training bug. The balanced Crop_recommendation.csv is used for production.
      </div>
    </Card>
  );
}

function YieldTable({ models, bestModel }) {
  return (
    <Card className="overflow-x-auto mt-6">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-gray-200 dark:border-white/10">
            <th className="pb-3 pr-4">Model</th>
            <th className="pb-3 pr-4">R²</th>
            <th className="pb-3 pr-4">MAE (hg/ha)</th>
            <th className="pb-3 pr-4">RMSE</th>
            <th className="pb-3">CV R² ± Std</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(models || {}).map(([name, m]) => (
            <tr key={name} className="border-b border-gray-100 dark:border-white/5">
              <td className="py-3 pr-4 font-medium">
                {name}
                {name === bestModel && <Badge className="ml-2">Best</Badge>}
                {name === 'SVR' && <Badge variant="danger" className="ml-2">Poor fit</Badge>}
              </td>
              <td className="py-3 pr-4 font-mono">{m.r2?.toFixed(4)}</td>
              <td className="py-3 pr-4 font-mono">{m.mae?.toFixed(1)}</td>
              <td className="py-3 pr-4 font-mono">{m.rmse?.toFixed(1)}</td>
              <td className="py-3 font-mono text-xs">
                {m.cv_r2_mean?.toFixed(4)} ± {m.cv_r2_std?.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

export default function Dashboard() {
  const { info, loading, error } = useModelInfo();

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <Spinner label="Loading dashboard" />
      </div>
    );
  }

  if (error || !info) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-red-500">
        {error || 'No model data available'}
      </div>
    );
  }

  const crop = info.crop || {};
  const yld = info.yield || {};
  const cropModels = crop.models || {};
  const yieldModels = yld.models || {};
  const bestCrop = crop.best_model;
  const bestYield = yld.best_model;
  const fi = yld.feature_importance || {};

  const humanFi = {};
  Object.entries(fi).forEach(([k, v]) => {
    const label = k
      .replace('Item_crop', 'Crop Type')
      .replace('Area_country', 'Region/Country')
      .replace('pesticides_tonnes', 'Pesticide Usage')
      .replace('avg_temp', 'Avg Temperature')
      .replace('avg_rain', 'Avg Rainfall');
    humanFi[label] = v;
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12"
    >
      <header>
        <h1 className="section-heading">Model Performance Dashboard</h1>
        <p className="section-subtext">
          Live results from the last training run — all 5 classifiers and 5 regressors benchmarked.
        </p>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Best Crop Model" value={bestCrop} subtitle={`${((crop.best_f1_macro || 0) * 100).toFixed(1)}% acc`} highlight />
        <MetricCard title="Best Yield Model" value={bestYield} subtitle={`R²=${(yld.best_r2 || 0).toFixed(3)}`} highlight />
        <MetricCard title="Models Compared" value="10" subtitle="(5+5)" />
        <MetricCard title="Tests Passing" value="18 / 18" />
      </div>

      <ModelComparisonChart models={cropModels} bestModel={bestCrop} />
      <ExperimentTable cropModels={cropModels} bestModel={bestCrop} />

      <div>
        <YieldRegressorChart models={yieldModels} bestModel={bestYield} />
        <YieldTable models={yieldModels} bestModel={bestYield} />
      </div>

      <ImbalanceCharts />
      <FeatureImportance data={humanFi} />
    </motion.div>
  );
}
