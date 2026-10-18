export const CROP_EMOJIS = {
  rice: '🍚',
  wheat: '🌾',
  maize: '🌽',
  corn: '🌽',
  coffee: '☕',
  banana: '🍌',
  mango: '🥭',
  apple: '🍎',
  grapes: '🍇',
  orange: '🍊',
  coconut: '🥥',
  watermelon: '🍉',
  cotton: '🤍',
};

export function cropEmoji(cropKey) {
  if (!cropKey) return '🌿';
  const key = String(cropKey).toLowerCase().replace(/\s+/g, '');
  return CROP_EMOJIS[key] || '🌿';
}
