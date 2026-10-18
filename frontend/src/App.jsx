import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Landing from './pages/Landing';
import Predict from './pages/Predict';
import Dashboard from './pages/Dashboard';
import { useDarkMode } from './hooks/useDarkMode';

export default function App() {
  const location = useLocation();
  const { dark, toggle } = useDarkMode();

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-[#0c0c0c]">
      <Navbar dark={dark} onToggleDark={toggle} />
      <main className="flex-1">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Landing />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </AnimatePresence>
      </main>
      <Footer />
    </div>
  );
}
