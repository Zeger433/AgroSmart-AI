import Card from '../ui/Card';

export default function MetricCard({ title, value, subtitle, highlight }) {
  return (
    <Card className={highlight ? 'border-l-4 border-l-brand-500' : ''}>
      <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
      <p className="font-display text-2xl font-bold mt-2 tabular-nums">{value}</p>
      {subtitle && <p className="text-sm text-brand-600 dark:text-brand-400 mt-1 font-mono">{subtitle}</p>}
    </Card>
  );
}
