import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import Card from '../ui/Card';

function r2Color(r2) {
  if (r2 > 0.9) return '#22c55e';
  if (r2 >= 0.7) return '#f59e0b';
  if (r2 >= 0.5) return '#fbbf24';
  return '#ef4444';
}

export default function YieldRegressorChart({ models, bestModel }) {
  const data = Object.entries(models || {})
    .map(([name, m]) => ({ name, r2: m.r2, mae: m.mae, rmse: m.rmse, cv: m.cv_r2_mean, cvStd: m.cv_r2_std }))
    .sort((a, b) => b.r2 - a.r2);

  return (
    <Card>
      <h3 className="font-display text-lg font-bold mb-6">Yield regressors — R² comparison</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart layout="vertical" data={data} margin={{ left: 8, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-white/10" />
          <XAxis type="number" domain={[-0.3, 1]} tick={{ fill: 'currentColor', fontSize: 11 }} />
          <YAxis type="category" dataKey="name" width={100} tick={{ fill: 'currentColor', fontSize: 11 }} />
          <Tooltip formatter={(v) => [Number(v).toFixed(4), 'R²']} />
          <Bar dataKey="r2" name="R²" radius={[0, 4, 4, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={r2Color(entry.r2)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2">Best: {bestModel}</p>
    </Card>
  );
}
