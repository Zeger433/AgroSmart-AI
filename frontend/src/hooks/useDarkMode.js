import { useEffect, useState } from 'react';

export function useDarkMode() {
  const [dark, setDark] = useState(() =>
    localStorage.getItem('theme') === 'light' ? false : true
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);

  const toggle = () => setDark((d) => !d);

  return { dark, setDark, toggle };
}
