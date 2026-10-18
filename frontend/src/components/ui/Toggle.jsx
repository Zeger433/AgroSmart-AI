import { Sun, Moon } from 'lucide-react';
import { cn } from '../../utils/cn';

export default function Toggle({ dark, onToggle, className }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn(
        'p-2 rounded-lg border border-white/10 hover:bg-white/10 transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-brand-500',
        className
      )}
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {dark ? <Sun className="w-5 h-5 text-gold-400" /> : <Moon className="w-5 h-5 text-gray-600" />}
    </button>
  );
}
