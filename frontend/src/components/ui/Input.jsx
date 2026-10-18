import { Check } from 'lucide-react';
import { cn } from '../../utils/cn';

export default function Input({
  label,
  unit,
  hint,
  error,
  value,
  onChange,
  type = 'number',
  min,
  max,
  step = 'any',
  className,
  id,
  ...props
}) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  const filled = value !== '' && value != null;
  const valid = filled && !error;

  return (
    <div className={cn('space-y-1.5', className)}>
      <label htmlFor={inputId} className="flex items-baseline justify-between text-sm font-medium text-gray-700 dark:text-gray-300">
        <span>{label}{unit ? ` (${unit})` : ''}</span>
        {valid && <Check className="w-4 h-4 text-brand-500" aria-hidden />}
      </label>
      <input
        id={inputId}
        type={type}
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(
          'input-field',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
          valid && 'border-brand-500/50'
        )}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
        {...props}
      />
      {hint && !error && (
        <p id={`${inputId}-hint`} className="text-xs text-gray-500 dark:text-gray-500">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${inputId}-error`} className="text-xs text-red-500" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
