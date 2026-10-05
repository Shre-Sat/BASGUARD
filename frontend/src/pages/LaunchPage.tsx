import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useExperimentStore } from '../store/useExperimentStore';
import { playUiBeep, speakAlert } from '../utils/audioAlert';
import { 
  Rocket, 
  ShieldCheck, 
  Sparkles, 
  Cpu, 
  Activity, 
  Globe, 
  Quote, 
  ChevronRight,
  Palette,
  Volume2,
  VolumeX
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ISRO_QUOTES = [
  {
    quote: "There are some who question the relevance of space activities in a developing nation. To us, there is no ambiguity of purpose. We must be second to none in the application of advanced technologies to the real problems of human society.",
    author: "Dr. Vikram Sarabhai",
    title: "Father of Indian Space Program",
    badge: "ISRO FOUNDER 🚀"
  },
  {
    quote: "You have to dream before your dreams can come true. Courage is taking the first step into the unknown space frontier.",
    author: "Dr. A.P.J. Abdul Kalam",
    title: "Aerospace Scientist & 11th President of India",
    badge: "MISSILE MAN 🇮🇳"
  },
  {
    quote: "The sky is not the limit... it is only the starting line for human curiosity, astronaut safety, and science!",
    author: "ISRO Gaganyaan Mission Team",
    title: "Human Spaceflight Programme",
    badge: "GAGANYAAN 🧑‍🚀"
  }
];

export const LaunchPage = () => {
  const navigate = useNavigate();
  const { themeMode, toggleThemeMode, audioMuted, toggleAudioMuted, setDemoMode } = useExperimentStore();
  const [activeQuoteIndex, setActiveQuoteIndex] = useState(0);
  const [isLaunching, setIsLaunching] = useState(false);

  const handleStartMission = () => {
    setIsLaunching(true);
    playUiBeep(880, 'sine', 0.2);
    setTimeout(() => playUiBeep(1760, 'sine', 0.3), 150);

    if (!audioMuted) {
      speakAlert("Welcome to I S R O BAS Guard. Mission Control system online.");
    }

    setTimeout(() => {
      setDemoMode(true);
      navigate('/mission-control');
    }, 600);
  };

  const nextQuote = () => {
    setActiveQuoteIndex((prev) => (prev + 1) % ISRO_QUOTES.length);
  };

  const currentQuote = ISRO_QUOTES[activeQuoteIndex];

  return (
    <div className={`w-screen h-screen ${themeMode === 'WHITE_BLUE' ? 'bg-[#F8FAFC] text-slate-900' : 'bg-[#04070D] text-slate-100'} overflow-hidden relative font-sans select-none flex flex-col justify-between tactical-grid transition-colors duration-300`}>
      
      {/* Background Radial Glow & Animated Star Field */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none animate-pulse-ring" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[400px] bg-amber-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Top Navigation Bar */}
      <header className="h-14 px-6 flex items-center justify-between z-20 border-b border-white/10 backdrop-blur-md shrink-0">
        <div className="flex items-center gap-3">
          <img 
            src="/basguard-logo.png" 
            alt="BASGUARD Official Emblem" 
            className="h-8 w-auto object-contain drop-shadow-md hover:scale-105 transition-transform" 
          />

          <div className="h-5 w-px bg-white/10" />

          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-600 via-orange-500 to-amber-400 p-[1px] shadow-glow-isro flex items-center justify-center">
            <div className="w-full h-full bg-[#0B101D] rounded-lg flex items-center justify-center">
              <span className="text-[10px] font-black tracking-tighter text-amber-400 font-mono">ISRO</span>
            </div>
          </div>
          <div>
            <h1 className="text-sm font-extrabold tracking-tight font-sans">BASGUARD</h1>
            <p className="text-[10px] font-mono text-slate-400">Space Monitor</p>
          </div>
        </div>

        {/* Top Right Theme & Audio Toggles */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleThemeMode}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono font-semibold transition-all ${
              themeMode === 'WHITE_BLUE'
                ? 'bg-blue-600 text-white border-blue-400 shadow-glow-accent'
                : 'bg-slate-900 text-blue-300 border-blue-500/30 hover:bg-slate-800'
            }`}
          >
            <Palette className="w-3.5 h-3.5" />
            <span>{themeMode === 'WHITE_BLUE' ? 'WHITE & BLUE ☀️' : 'DEEP SPACE 🌌'}</span>
          </button>

          <button
            onClick={toggleAudioMuted}
            className={`p-1.5 rounded-lg transition-all glass-button ${
              audioMuted ? 'text-rose-400 border-rose-500/30' : 'text-emerald-400 border-emerald-500/30'
            }`}
            title={audioMuted ? 'Unmute Audio Copilot' : 'Mute Audio Copilot'}
          >
            {audioMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </header>

      {/* Main Center Content Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 z-20 max-w-4xl mx-auto text-center relative py-2 overflow-hidden">
        
        {/* BASGUARD Official Shield Emblem Hero */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="relative mb-2 shrink-0"
        >
          <div className="absolute inset-0 bg-blue-500/25 rounded-full blur-2xl animate-pulse-ring" />
          <img 
            src="/basguard-logo.png" 
            alt="BASGUARD Official Mission Crest Logo" 
            className="h-20 sm:h-24 w-auto object-contain relative z-10 filter drop-shadow-[0_8px_20px_rgba(37,99,235,0.4)] hover:scale-105 transition-transform duration-300"
          />
        </motion.div>

        {/* Animated ISRO Emblem Badge */}
        <motion.div
          initial={{ opacity: 0, y: -8, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] font-mono mb-2 shadow-glow-isro shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5 animate-spin-slow" />
          <span className="font-semibold">ISRO SPACE EXPERIMENT AI MONITOR</span>
        </motion.div>

        {/* Compact Hero Title */}
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="text-2xl sm:text-3xl font-black tracking-tight leading-tight max-w-2xl mb-2 font-sans shrink-0"
        >
          Precision Space Safety &amp;{' '}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-amber-400 bg-clip-text text-transparent">
            Astronaut Verification
          </span>
        </motion.h1>

        {/* Compact Quote Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-xl mb-4 p-3.5 sm:p-4 rounded-xl glass-panel border border-white/10 relative overflow-hidden shadow-xl text-left shrink-0"
        >
          <div className="absolute top-2.5 right-3 flex items-center gap-1.5">
            <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
              {currentQuote.badge}
            </span>
            <button 
              onClick={nextQuote}
              className="p-0.5 rounded bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Next Aerospace Quote"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-start gap-2.5">
            <Quote className="w-5 h-5 text-blue-400 shrink-0 opacity-60 mt-0.5" />
            <AnimatePresence mode="wait">
              <motion.div
                key={activeQuoteIndex}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.25 }}
                className="flex-1 pr-16"
              >
                <p className="text-xs sm:text-sm italic text-slate-200 font-sans leading-snug mb-1">
                  "{currentQuote.quote}"
                </p>
                <div className="flex items-center gap-1.5 text-[10px]">
                  <span className="font-bold text-amber-400 font-mono">{currentQuote.author}</span>
                  <span className="text-slate-500">·</span>
                  <span className="text-slate-400 font-mono">{currentQuote.title}</span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>

        {/* 🚀 PRIMARY START MISSION BUTTON — HIGHLY VISIBLE & COMPACT 🚀 */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.25 }}
          className="relative group shrink-0 my-1"
        >
          <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-600 via-amber-500 to-indigo-600 blur-md opacity-75 group-hover:opacity-100 transition duration-500 animate-pulse-ring" />
          
          <button
            onClick={handleStartMission}
            disabled={isLaunching}
            className="relative px-8 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white font-bold text-base tracking-wide shadow-2xl flex items-center gap-3 transition-all duration-300 hover:scale-105 active:scale-95 border border-blue-300/40"
          >
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
              <Rocket className={`w-5 h-5 text-amber-300 ${isLaunching ? 'animate-bounce' : 'group-hover:rotate-12 transition-transform'}`} />
            </div>
            <div className="flex flex-col text-left leading-tight">
              <span className="font-extrabold font-mono tracking-wider text-sm sm:text-base">
                {isLaunching ? 'INITIALIZING MISSION CONTROL...' : 'START MISSION DASHBOARD 🚀'}
              </span>
              <span className="text-[10px] text-blue-200 font-sans font-normal">
                Click to launch live ISRO monitor
              </span>
            </div>
            <ChevronRight className="w-5 h-5 text-white group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </main>

      {/* Bottom Operational Pre-Flight Telemetry Badges */}
      <footer className="h-12 px-6 flex items-center justify-between z-20 border-t border-white/10 backdrop-blur-md text-[11px] font-mono text-slate-400 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>ENGINE: <strong className="text-emerald-300">ONLINE (30 FPS)</strong></span>
          </div>

          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span>3D POSE: <strong className="text-blue-300">CALIBRATED</strong></span>
          </div>

          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span>FSM: <strong className="text-amber-300">READY</strong></span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-slate-400">
          <Globe className="w-3.5 h-3.5 text-indigo-400" />
          <span>ISRO GAGANYAAN MONITOR</span>
        </div>
      </footer>
    </div>
  );
};
