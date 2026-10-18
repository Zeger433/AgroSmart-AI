import { cn } from '../../utils/cn';

export default function Spinner({ className, label = 'Loading' }) {
  return (
    <div className={cn('flex items-center gap-2', className)} role="status" aria-label={label}>
      <svg
        className="animate-spin h-5 w-5 text-brand-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
}
