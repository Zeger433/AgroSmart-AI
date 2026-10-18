import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '../../utils/cn';

export default function Toast({ message, type = 'error', onClose, duration = 5000 }) {
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(onClose, duration);
    return () => clearTimeout(t);
  }, [message, duration, onClose]);

  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className={cn(
            'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border max-w-md',
            type === 'success'
              ? 'bg-brand-950 border-brand-700 text-brand-100'
              : 'bg-red-950 border-red-800 text-red-100'
          )}
          role="alert"
        >
          {type === 'success' ? (
            <CheckCircle className="w-5 h-5 shrink-0" aria-hidden />
          ) : (
            <AlertCircle className="w-5 h-5 shrink-0" aria-hidden />
          )}
          <p className="text-sm flex-1">{message}</p>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:opacity-70"
            aria-label="Dismiss notification"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
