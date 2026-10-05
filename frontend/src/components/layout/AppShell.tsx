import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StatusBar } from './StatusBar';
import { motion, AnimatePresence } from 'framer-motion';
import { OrbitalSpaceBackground } from '../common/OrbitalSpaceBackground';

import { useExperimentStore } from '../../store/useExperimentStore';

export const AppShell = () => {
  const location = useLocation();
  const { themeMode } = useExperimentStore();

  return (
    <div className={`flex w-screen h-screen ${themeMode === 'WHITE_BLUE' ? 'bg-[#F8FAFC] text-slate-900' : 'bg-[#05080E] text-slate-100'} overflow-hidden font-sans select-none tactical-grid relative transition-colors duration-300`}>
      {/* Animated Floating Satellite & Astronaut Background Silhouettes */}
      <OrbitalSpaceBackground />

      {/* Background ambient lighting effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 h-full relative z-10">
        <Header />
        
        {/* Main View Area with Framer Motion transitions */}
        <main className="flex-1 overflow-hidden relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 4, scale: 0.995 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -4, scale: 0.995 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="w-full h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>

        <StatusBar />
      </div>
    </div>
  );
};
