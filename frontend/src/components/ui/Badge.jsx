import { cn } from '../../utils/cn';

const styles = {
  default: 'bg-brand-500/15 text-brand-600 dark:text-brand-400 border-brand-500/30',
  gold: 'bg-gold-500/15 text-gold-600 dark:text-gold-400 border-gold-500/30',
  danger: 'bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30',
  muted: 'bg-gray-500/15 text-gray-600 dark:text-gray-400 border-gray-500/30',
};

export default function Badge({ children, variant = 'default', className }) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        styles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
