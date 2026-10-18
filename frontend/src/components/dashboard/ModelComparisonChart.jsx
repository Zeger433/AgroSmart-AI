import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import Card from '../ui/Card';

const SHORT = {
  RandomForest: 'RF',
  XGBoost: 'XGB',
  GradientBoosting: 'GB',
  SVM: 'SVM',
  KNN: 'KNN',
};

export default function ModelComparisonChart({ models, bestModel }) {
  const data = Object.entries(models || {}).map(([name, m]) => ({
    name: SHORT[name] || name,
    fullName: name,
    accuracy: m.accuracy,
    f1_macro: m.f1_macro,
    cv_f1: m.cv_f1_mean,
  }));

  return (
    <Card>
      <h3 className="font-display text-lg font-bold mb-6">
        Crop classifiers — Experiment 1 (balanced dataset)
      </h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-white/10" />
          <XAxis dataKey="name" tick={{ fill: 'currentColor', fontSize: 12 }} />
          <YAxis domain={[0.95, 1]} tick={{ fill: 'currentColor', fontSize: 11 }} tickFormatter={(v) => v.toFixed(2)} />
          <Tooltip
            contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 8 }}
            formatter={(v) => [Number(v).toFixed(4), '']}
          />
          <Legend />
          <Bar dataKey="accuracy" name="Accuracy" fill="#22c55e" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.fullName} fill={entry.fullName === bestModel ? '#4ade80' : '#16a34a'} />
            ))}
          </Bar>
          <Bar dataKey="f1_macro" name="F1 Macro" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          <Bar dataKey="cv_f1" name="CV F1" fill="#86efac" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      {bestModel && (
        <p className="text-center text-sm text-gray-500 mt-2">
          👑 Best: {bestModel}
        </p>
      )}
    </Card>
  );
}
