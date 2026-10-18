import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Brain,
  CheckCircle,
  BarChart3,
  FlaskConical,
  Plug,
  TestTube,
  Cpu,
  Leaf,
} from 'lucide-react';
import Button from '../components/ui/Button';

/** Static marketing stats — never fetched from API */
const STATS = [
  { value: 99.3, suffix: '%', label: 'Crop Accuracy', decimals: 1 },
  { value: 0.9734, suffix: '', label: 'Yield R²', decimals: 4 },
  { value: 10, suffix: '', label: 'Models Benchmarked', decimals: 0 },
  { value: 18, suffix: '/18', label: 'Tests Passing', decimals: 0 },
];

function formatStat(stat, n) {
  const rounded = stat.decimals > 0 ? n.toFixed(stat.decimals) : String(Math.round(n));
  if (stat.suffix === '/18') return `${Math.round(n)}${stat.suffix}`;
  return `${rounded}${stat.suffix}`;
}

function StatItem({ label, display }) {
  return (
    <div className="text-center px-4 py-6">
      <p className="font-mono text-3xl md:text-4xl font-bold tabular-nums text-white">
        {display}
      </p>
      <p className="text-sm text-gray-400 mt-2">{label}</p>
    </div>
  );
}

function StatsBar() {
  const ref = useRef(null);
  const animatedRef = useRef(false);
  const [displayValues, setDisplayValues] = useState(() => STATS.map(() => 0));

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    let frameId = 0;

    const obs = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting || animatedRef.current) return;
        animatedRef.current = true;

        const duration = 800;
        const start = performance.now();

        const tick = (now) => {
          const t = Math.min(1, (now - start) / duration);
          setDisplayValues(STATS.map((s) => s.value * t));
          if (t < 1) {
            frameId = requestAnimationFrame(tick);
          } else {
            setDisplayValues(STATS.map((s) => s.value));
          }
        };

        frameId = requestAnimationFrame(tick);
      },
      { threshold: 0.2 }
    );

    obs.observe(el);
    return () => {
      obs.disconnect();
      cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <section ref={ref} className="bg-[#0a0a0a] border-y border-white/10">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4">
        {STATS.map((stat, i) => (
          <StatItem
            key={stat.label}
            label={stat.label}
            display={formatStat(stat, displayValues[i])}
          />
        ))}
      </div>
    </section>
  );
}

const features = [
  { icon: Brain, title: 'Multi-Model Intelligence', desc: '5 classifiers and 5 regressors trained, compared, and the best auto-selected. No black box.' },
  { icon: CheckCircle, title: 'Input Validation', desc: 'Agronomic range checks on all inputs — N, P, K, pH, temperature, humidity, rainfall — before any prediction is made.' },
  { icon: BarChart3, title: 'Full Transparency', desc: 'Every prediction shows which model was used, confidence score, yield range, and feature importance breakdown.' },
  { icon: FlaskConical, title: 'Experiment Suite', desc: 'Includes a class-imbalance study: raw merged data vs SMOTE — showing real-world ML challenges and solutions.' },
  { icon: Plug, title: 'REST API', desc: 'Clean endpoints: /predict, /model-info, /health, /get_defaults. Integrate with any system.' },
  { icon: TestTube, title: '18 Automated Tests', desc: 'Full pytest suite covering API routes, model loading, preprocessing, and input validators.' },
];

const steps = [
  { icon: TestTube, title: 'Enter Field Data', desc: "Input your soil's N, P, K, pH and local climate — or auto-fill from your country's averages." },
  { icon: Cpu, title: '5 Models Analyse', desc: 'RandomForest, XGBoost, SVM, KNN, and GradientBoosting all evaluate your inputs. The best model\'s result is returned.' },
  { icon: Leaf, title: 'Get Your Recommendation', desc: 'See which crop to grow, expected yield in tons/ha, confidence score, and why the model made that choice.' },
];

const floatCards = [
  { text: '🌾 Wheat — 92.3% confident', className: 'top-24 left-[8%] animate-float', delay: 0 },
  { text: 'R² = 0.97  RandomForest', className: 'top-40 right-[10%] animate-float-slow', delay: 0.5 },
  { text: '18 / 18 tests ✓', className: 'bottom-32 left-[15%] animate-float', delay: 1 },
];

export default function Landing() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-[#0c0c0c] text-white hero-mesh grid-pattern">
        {floatCards.map((card, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: card.delay + 0.3 }}
            className={`absolute hidden lg:block glass-card px-4 py-3 text-sm font-mono ${card.className}`}
          >
            {card.text}
          </motion.div>
        ))}

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center py-20">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-brand-500/20 text-brand-400 border border-brand-500/30 mb-6">
            🌾 Final Year Project 2026
          </span>
          <h1 className="font-display text-4xl sm:text-5xl md:text-7xl font-bold tracking-tight leading-tight">
            Smarter Farming
            <br />
            Starts With Data
          </h1>
          <p className="mt-6 text-lg md:text-xl text-gray-400 max-w-2xl mx-auto">
            Predict the optimal crop and expected yield from soil chemistry and climate data — powered by 5 ML models benchmarked for accuracy.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/predict"><Button>Try the Predictor →</Button></Link>
            <Link to="/dashboard"><Button variant="ghost">View Model Results</Button></Link>
          </div>
          <p className="mt-8 text-xs font-mono text-gray-500">
            99.3% accuracy · 5 classifiers · 18 tests passing
          </p>
        </div>
      </section>

      <StatsBar />

      <section className="py-20 px-4 max-w-7xl mx-auto">
        <h2 className="section-heading text-center">Everything you need for precision agriculture</h2>
        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <motion.div
              key={title}
              whileHover={{ y: -4 }}
              className="card p-6 hover:border-brand-500/40 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-brand-500/20 flex items-center justify-center mb-4">
                <Icon className="w-5 h-5 text-brand-500" aria-hidden />
              </div>
              <h3 className="font-medium text-lg">{title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="py-20 px-4 bg-gray-50 dark:bg-white/[0.02]">
        <div className="max-w-5xl mx-auto">
          <h2 className="section-heading text-center">From soil sample to crop recommendation in seconds</h2>
          <div className="mt-16 flex flex-col md:flex-row gap-8 md:gap-4 relative">
            <div className="hidden md:block absolute top-8 left-[16%] right-[16%] h-0.5 bg-brand-500/30" aria-hidden />
            {steps.map(({ icon: Icon, title, desc }, i) => (
              <div key={title} className="flex-1 relative md:text-center pl-6 md:pl-0 border-l-2 md:border-l-0 border-brand-500/40 md:border-0">
                <div className="md:mx-auto w-12 h-12 rounded-xl bg-brand-500/20 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-brand-500" />
                </div>
                <h3 className="font-medium">{title}</h3>
                <p className="text-sm text-gray-500 mt-2">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-brand-600">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <h2 className="font-display text-2xl md:text-3xl font-bold text-white">Ready to predict your crop?</h2>
          <Link to="/predict">
            <Button className="bg-white text-brand-700 hover:bg-gray-100">Open Predictor →</Button>
          </Link>
        </div>
      </section>
    </motion.div>
  );
}
