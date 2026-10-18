import Card from '../ui/Card';
import Badge from '../ui/Badge';

export default function ExperimentTable({ cropModels, bestModel }) {
  const rows = Object.entries(cropModels || {}).map(([name, m]) => ({
    name,
    accuracy: m.accuracy,
    f1_macro: m.f1_macro,
    f1_weighted: m.f1_weighted,
    cv: m.cv_f1_mean,
    cvStd: m.cv_f1_std,
  }));

  return (
    <Card className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-gray-200 dark:border-white/10">
            <th className="pb-3 pr-4">Model</th>
            <th className="pb-3 pr-4">Accuracy</th>
            <th className="pb-3 pr-4">F1 Macro</th>
            <th className="pb-3 pr-4">F1 Weighted</th>
            <th className="pb-3">CV F1 ± Std</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.name}
              className={
                row.name === bestModel
                  ? 'border-l-4 border-l-brand-500 bg-brand-500/5'
                  : 'border-b border-gray-100 dark:border-white/5'
              }
            >
              <td className="py-3 pr-4 font-medium">
                {row.name}
                {row.name === bestModel && <Badge className="ml-2">Best</Badge>}
              </td>
              <td className="py-3 pr-4 font-mono tabular-nums">{(row.accuracy * 100).toFixed(2)}%</td>
              <td className="py-3 pr-4 font-mono tabular-nums">{(row.f1_macro * 100).toFixed(2)}%</td>
              <td className="py-3 pr-4 font-mono tabular-nums">{(row.f1_weighted * 100).toFixed(2)}%</td>
              <td className="py-3 font-mono tabular-nums text-xs">
                {row.cv?.toFixed(4)} ± {row.cvStd?.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
