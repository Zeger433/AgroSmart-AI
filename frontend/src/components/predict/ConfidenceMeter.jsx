import { useEffect, useState } from 'react';

export function arcColor(pct) {
  if (pct >= 75) return '#22c55e';
  if (pct >= 50) return '#f59e0b';
  return '#ef4444';
}

export default function ConfidenceMeter({ value = 0, size = 120 }) {
  const [display, setDisplay] = useState(0);
  const pct = Math.min(100, Math.max(0, Number(value) || 0));
  const r = (size - 16) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = Math.PI * r;
  const offset = circumference - (display / 100) * circumference;

  useEffect(() => {
    const start = performance.now();
    const duration = 800;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      setDisplay(pct * t);
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [pct]);

  return (
    <div className="flex flex-col items-center" role="img" aria-label={`Confidence ${pct.toFixed(1)} percent`}>
      <svg width={size} height={size / 2 + 8} viewBox={`0 0 ${size} ${size / 2 + 8}`}>
        <path
          d={`M ${16} ${cy} A ${r} ${r} 0 0 1 ${size - 16} ${cy}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-gray-200 dark:text-white/10"
        />
        <path
          d={`M ${16} ${cy} A ${r} ${r} 0 0 1 ${size - 16} ${cy}`}
          fill="none"
          stroke={arcColor(display)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke 0.3s' }}
        />
      </svg>
      <span
        className="font-mono text-2xl font-bold tabular-nums -mt-6 transition-colors duration-300"
        style={{ color: arcColor(display) }}
      >
        {display.toFixed(1)}%
      </span>
      <span className="text-xs text-gray-500 dark:text-gray-400">Confidence</span>
    </div>
  );
}
