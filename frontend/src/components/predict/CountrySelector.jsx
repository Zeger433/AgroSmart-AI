import { useEffect, useMemo, useRef, useState } from 'react';
import { Search } from 'lucide-react';
import { cn } from '../../utils/cn';

const COUNTRIES = [
  'Afghanistan', 'Albania', 'Algeria', 'Angola', 'Argentina',
  'Australia', 'Bangladesh', 'Belarus', 'Belgium', 'Bolivia',
  'Brazil', 'Bulgaria', 'Burkina Faso', 'Cambodia', 'Cameroon',
  'Canada', 'Chile', 'China', 'Colombia', 'Congo',
  'Costa Rica', 'Cuba', 'Czech Republic', 'Denmark', 'Ecuador',
  'Egypt', 'El Salvador', 'Ethiopia', 'Finland', 'France',
  'Germany', 'Ghana', 'Greece', 'Guatemala', 'Guinea',
  'Honduras', 'Hungary', 'India', 'Indonesia', 'Iran',
  'Iraq', 'Ireland', 'Italy', 'Japan', 'Jordan',
  'Kazakhstan', 'Kenya', 'Madagascar', 'Malawi', 'Malaysia',
  'Mali', 'Mexico', 'Morocco', 'Mozambique', 'Myanmar',
  'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger',
  'Nigeria', 'Norway', 'Pakistan', 'Paraguay', 'Peru',
  'Philippines', 'Poland', 'Portugal', 'Romania', 'Russia',
  'Rwanda', 'Saudi Arabia', 'Senegal', 'Sierra Leone', 'Somalia',
  'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Sweden',
  'Switzerland', 'Syria', 'Tanzania', 'Thailand', 'Togo',
  'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'United Kingdom',
  'United States of America', 'Uruguay', 'Venezuela',
  'Vietnam', 'Zambia', 'Zimbabwe',
];

export default function CountrySelector({ value, onChange, onSelect, error, loading }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return COUNTRIES;
    return COUNTRIES.filter((c) => c.toLowerCase().includes(q));
  }, [query]);

  useEffect(() => {
    const onDocClick = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) {
        setOpen(false);
        setQuery('');
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const handlePick = (country) => {
    onChange(country);
    setQuery('');
    setOpen(false);
    onSelect?.(country);
  };

  const displayValue = open ? query : value;

  return (
    <div ref={rootRef} className="space-y-1.5 relative">
      <label htmlFor="country" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Country / Region
      </label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" aria-hidden />
        <input
          id="country"
          type="text"
          value={displayValue}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => {
            setOpen(true);
            setQuery('');
          }}
          placeholder="Search countries..."
          className={cn('input-field pl-10', error && 'border-red-500')}
          aria-invalid={!!error}
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls="country-listbox"
        />
        {loading && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-brand-500 animate-pulse">
            Loading…
          </span>
        )}
      </div>
      {open && (
        <ul
          id="country-listbox"
          className="absolute z-30 mt-1 w-full max-h-[200px] overflow-y-auto rounded-lg border border-white/10 bg-[#141414] backdrop-blur-md shadow-xl"
          role="listbox"
        >
          {filtered.length === 0 ? (
            <li className="px-4 py-3 text-sm text-gray-500">No countries found</li>
          ) : (
            filtered.map((c) => (
              <li key={c}>
                <button
                  type="button"
                  className={cn(
                    'w-full text-left px-4 py-2.5 text-sm text-gray-200 transition-colors',
                    'hover:bg-brand-500/20 hover:text-brand-300',
                    c === value && 'bg-brand-500/15 text-brand-400'
                  )}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handlePick(c)}
                  role="option"
                  aria-selected={c === value}
                >
                  {c}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
      {error && <p className="text-xs text-red-500" role="alert">{error}</p>}
    </div>
  );
}
