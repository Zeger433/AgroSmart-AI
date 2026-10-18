import { useState, useCallback } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';
import Spinner from '../ui/Spinner';
import CountrySelector from './CountrySelector';
import { SOIL_TYPES } from '../../constants/countries';
import { RANGES } from '../../constants/ranges';
import { validateField, validateForm } from '../../utils/validators';
import { getDefaults } from '../../utils/api';

const SECTION_LABEL = 'text-xs font-semibold tracking-widest text-brand-400 uppercase mb-3 mt-6 first:mt-0';

const INITIAL = {
  country: 'India',
  soil_type: 'loam',
  N: '90',
  P: '42',
  K: '43',
  ph: '6.5',
  temperature: '25',
  humidity: '82',
  rainfall: '120',
  pesticides: '50000',
  land_area: '',
};

function hint(field) {
  const [lo, hi] = RANGES[field];
  return `Valid range: ${lo}–${hi}`;
}

export default function InputForm({ onSubmit, loading }) {
  const [values, setValues] = useState(INITIAL);
  const [errors, setErrors] = useState({});
  const [defaultsLoading, setDefaultsLoading] = useState(false);

  const set = (field) => (v) => {
    setValues((prev) => ({ ...prev, [field]: v }));
    const err = validateField(field, v);
    setErrors((prev) => {
      const next = { ...prev };
      if (err) next[field] = err;
      else delete next[field];
      return next;
    });
  };

  const handleCountrySelect = useCallback(async (country) => {
    setDefaultsLoading(true);
    try {
      const d = await getDefaults(country);
      if (d.success) {
        setValues((prev) => ({
          ...prev,
          country,
          rainfall: String(d.rainfall),
          temperature: String(d.temperature),
          pesticides: String(d.pesticides),
        }));
        ['rainfall', 'temperature', 'pesticides'].forEach((f) => {
          setErrors((prev) => {
            const next = { ...prev };
            delete next[f];
            return next;
          });
        });
      }
    } catch {
      /* keep manual values */
    } finally {
      setDefaultsLoading(false);
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validateForm(values);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;
    onSubmit({
      N: Number(values.N),
      P: Number(values.P),
      K: Number(values.K),
      ph: Number(values.ph),
      temperature: Number(values.temperature),
      humidity: Number(values.humidity),
      rainfall: Number(values.rainfall),
      pesticides: Number(values.pesticides),
      soil_type: values.soil_type,
      country: values.country,
      land_area: values.land_area ? Number(values.land_area) : 0,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-8 space-y-2" noValidate>
      <div>
        <h2 className="font-display text-xl font-bold">Field Inputs</h2>
        <p className="text-sm text-gray-500 mt-1">Soil chemistry and local climate</p>
      </div>

      <section>
        <h3 className={SECTION_LABEL}>Location</h3>
        <div className="space-y-4">
        <CountrySelector
          value={values.country}
          onChange={(c) => set('country')(c)}
          onSelect={handleCountrySelect}
          error={errors.country}
          loading={defaultsLoading}
        />
        <div className="space-y-1.5">
          <label htmlFor="soil_type" className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Soil type
          </label>
          <select
            id="soil_type"
            value={values.soil_type}
            onChange={(e) => set('soil_type')(e.target.value)}
            className="input-field"
          >
            {SOIL_TYPES.map(({ value, label }) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        </div>
      </section>

      <section>
        <h3 className={SECTION_LABEL}>Soil chemistry</h3>
        <div className="grid grid-cols-2 gap-4">
          {['N', 'P', 'K', 'ph'].map((field) => (
            <Input
              key={field}
              label={field === 'ph' ? 'pH level' : field === 'N' ? 'Nitrogen (N)' : field === 'P' ? 'Phosphorus (P)' : 'Potassium (K)'}
              unit={field === 'ph' ? '' : 'kg/ha'}
              hint={hint(field)}
              min={RANGES[field][0]}
              max={RANGES[field][1]}
              value={values[field]}
              onChange={set(field)}
              error={errors[field]}
            />
          ))}
        </div>
      </section>

      <section>
        <h3 className={SECTION_LABEL}>Climate</h3>
        <div className="grid grid-cols-2 gap-4">
          <Input label="Temperature" unit="°C" hint={hint('temperature')} min={8} max={43} value={values.temperature} onChange={set('temperature')} error={errors.temperature} />
          <Input label="Humidity" unit="%" hint={hint('humidity')} min={14} max={100} value={values.humidity} onChange={set('humidity')} error={errors.humidity} />
          <Input label="Rainfall" unit="mm" hint={hint('rainfall')} min={20} max={300} value={values.rainfall} onChange={set('rainfall')} error={errors.rainfall} />
          <Input label="Pesticides" unit="tonnes" hint={hint('pesticides')} min={0} max={1000000} value={values.pesticides} onChange={set('pesticides')} error={errors.pesticides} />
        </div>
      </section>

      <section>
        <Input
          label="Land area"
          unit="ha"
          hint="Optional"
          type="number"
          min={0}
          value={values.land_area}
          onChange={set('land_area')}
          className="opacity-80"
        />
      </section>

      <Button
        type="submit"
        disabled={loading}
        className="w-full h-12 text-base font-semibold flex items-center justify-center gap-2 mt-4"
      >
        {loading ? (
          <>
            <Spinner /> Analysing your field...
          </>
        ) : (
          'Predict crop & yield →'
        )}
      </Button>
    </form>
  );
}
