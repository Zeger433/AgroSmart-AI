import { Link } from 'react-router-dom';
import { Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-black/40 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <p className="font-display font-bold text-lg">🌾 AgroSmart AI</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              ML-powered precision agriculture
            </p>
          </div>
          <div>
            <p className="text-sm font-medium mb-3">Quick links</p>
            <div className="flex flex-col gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Link to="/" className="hover:text-brand-500">Home</Link>
              <Link to="/predict" className="hover:text-brand-500">Predict</Link>
              <Link to="/dashboard" className="hover:text-brand-500">Dashboard</Link>
            </div>
          </div>
          <div>
            <a
              href="https://github.com/MuneebX00/agrosmart-ai"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-brand-500"
            >
              <Github className="w-4 h-4" /> GitHub
            </a>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">Final Year Project · 2026</p>
            <p className="text-xs text-gray-400 mt-1">Built with Flask + React + scikit-learn</p>
          </div>
        </div>
        <p className="text-center text-xs text-gray-400 mt-10 border-t border-gray-200 dark:border-white/10 pt-6">
          MIT License · 18 tests passing · RandomForest 99.3% accuracy
        </p>
      </div>
    </footer>
  );
}
