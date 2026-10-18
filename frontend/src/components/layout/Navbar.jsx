import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Github, Menu, X } from 'lucide-react';
import Toggle from '../ui/Toggle';
import { cn } from '../../utils/cn';

const links = [
  { to: '/', label: 'Home' },
  { to: '/predict', label: 'Predict' },
  { to: '/dashboard', label: 'Dashboard' },
];

export default function Navbar({ dark, onToggleDark }) {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-white/80 dark:bg-black/60 border-b border-gray-200 dark:border-white/10">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between" aria-label="Main">
        <Link to="/" className="flex items-center gap-2 font-display font-bold text-lg text-gray-900 dark:text-white">
          <span aria-hidden>🌾</span>
          AgroSmart AI
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                cn(
                  'text-sm font-medium transition-colors hover:text-brand-500',
                  isActive
                    ? 'text-brand-600 dark:text-brand-400 underline underline-offset-4 decoration-brand-500'
                    : 'text-gray-600 dark:text-gray-400'
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Toggle dark={dark} onToggle={onToggleDark} />
          <a
            href="https://github.com/MuneebX00/agrosmart-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
            aria-label="GitHub repository"
          >
            <Github className="w-5 h-5" />
          </a>
          <button
            type="button"
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10"
            onClick={() => setOpen(!open)}
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </nav>

      {open && (
        <div className="md:hidden border-t border-gray-200 dark:border-white/10 px-4 py-4 space-y-3 bg-white dark:bg-black/90">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                cn(
                  'block py-2 text-sm font-medium',
                  isActive ? 'text-brand-500' : 'text-gray-600 dark:text-gray-400'
                )
              }
            >
              {label}
            </NavLink>
          ))}
          <a
            href="https://github.com/MuneebX00/agrosmart-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 py-2 text-sm text-gray-600 dark:text-gray-400"
          >
            <Github className="w-4 h-4" /> GitHub
          </a>
        </div>
      )}
    </header>
  );
}
