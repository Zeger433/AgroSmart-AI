import { cn } from '../../utils/cn';

const variants = {
  primary: 'btn-primary',
  secondary:
    'bg-gray-100 dark:bg-white/10 hover:bg-gray-200 dark:hover:bg-white/15 text-gray-900 dark:text-white font-medium px-6 py-3 rounded-lg transition-all active:scale-95',
  ghost: 'btn-ghost',
};

export default function Button({
  children,
  variant = 'primary',
  className,
  disabled,
  type = 'button',
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={cn(
        variants[variant],
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
