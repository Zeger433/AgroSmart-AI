import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Share2 } from 'lucide-react';
import ConfidenceMeter from './ConfidenceMeter';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import { cropEmoji } from '../../utils/cropEmojis';

export default function ResultCard({ result, onReset }) {
  const [expanded, setExpanded] = useState(true);
  if (!result?.success) return null;

  const emoji = cropEmoji(result.crop_key || result.crop);
  const conf = result.confidence_pct ?? (result.confidence?.r2_score ? result.confidence.r2_score * 100 : 0);
  const yMin = result.confidence?.min ?? 0;
  const yMax = result.confidence?.max ?? 0;
  const yieldVal = result.yield ?? 0;
  const rangeSpan = Math.max(yMax - yMin, 0.01);
  const barPct = Math.min(100, Math.max(0, ((yieldVal - yMin) / rangeSpan) * 100));

  const handleShare = async () => {
    const text = `AgroSmart AI recommends ${result.crop} (${conf.toFixed?.(1) || conf}% confidence), ~${yieldVal} tons/ha`;
    try {
      await navigator.share?.({ title: 'Crop recommendation', text });
    } catch {
      await navigator.clipboard?.writeText(text);
    }
  };

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="card min-h-[600px] h-full space-y-6 p-8"
    >
      <header className="flex items-start gap-4">
        <span className="text-5xl" aria-hidden>{emoji}</span>
        <div>
          <h2 className="font-display text-3xl font-bold">{result.crop}</h2>
          <p className="text-gray-500 dark:text-gray-400">Recommended crop</p>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex justify-center p-4 rounded-xl bg-gray-50 dark:bg-white/5">
          <ConfidenceMeter value={conf} />
        </div>
        <div className="flex flex-col justify-center p-4 rounded-xl bg-gray-50 dark:bg-white/5">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Model used</p>
          <p className="font-display text-xl font-bold mt-1">{result.crop_model || '—'}</p>
        </div>
      </div>

      <section>
        <p className="text-sm text-gray-500">Expected yield</p>
        <p className="font-mono text-3xl font-bold tabular-nums mt-1">
          {yieldVal} <span className="text-lg font-normal text-gray-500">{result.currency || 'tons/ha'}</span>
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Typical range: {yMin} – {yMax} tons/ha
        </p>
        <div className="mt-3 h-2 rounded-full bg-gray-200 dark:bg-white/10 overflow-hidden">
          <motion.div
            className="h-full bg-brand-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${barPct}%` }}
            transition={{ duration: 0.6 }}
          />
        </div>
      </section>

      <section>
        <button
          type="button"
          className="flex items-center gap-2 text-sm font-medium text-brand-500"
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
        >
          <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
          Why this crop?
        </button>
        {expanded && (
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {result.explanation}
          </p>
        )}
      </section>

      {result.total_production != null && (
        <p className="text-sm text-gray-500">
          Total production estimate: <span className="font-mono font-medium">{result.total_production} tons</span>
        </p>
      )}

      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={onReset}>Try different inputs</Button>
        <Button variant="ghost" onClick={handleShare} className="inline-flex items-center gap-2">
          <Share2 className="w-4 h-4" /> Share
        </Button>
      </div>
    </motion.article>
  );
}
