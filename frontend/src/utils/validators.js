import { RANGES, FIELD_LABELS } from '../constants/ranges';

export function validateField(field, value) {
  if (value === '' || value === null || value === undefined) {
    return null;
  }
  const num = Number(value);
  if (Number.isNaN(num)) {
    return `Invalid value for ${FIELD_LABELS[field] || field}`;
  }
  const [lo, hi] = RANGES[field] || [0, Infinity];
  if (num < lo || num > hi) {
    return `${FIELD_LABELS[field] || field} must be between ${lo} and ${hi}`;
  }
  return null;
}

export function validateForm(values) {
  const errors = {};
  const required = ['N', 'P', 'K', 'ph', 'temperature', 'humidity', 'rainfall', 'pesticides'];
  for (const field of required) {
    if (values[field] === '' || values[field] == null) {
      errors[field] = 'Required';
      continue;
    }
    const err = validateField(field, values[field]);
    if (err) errors[field] = err;
  }
  if (!values.country?.trim()) errors.country = 'Select a country';
  if (!values.soil_type?.trim()) errors.soil_type = 'Select soil type';
  return errors;
}

export function isFormValid(errors) {
  return Object.keys(errors).length === 0;
}
