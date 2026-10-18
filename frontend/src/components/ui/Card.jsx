import { cn } from '../../utils/cn';

export default function Card({ children, className, ...props }) {
  return (
    <div className={cn('card p-6', className)} {...props}>
      {children}
    </div>
  );
}
