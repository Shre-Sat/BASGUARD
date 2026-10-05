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
      <header className="h-16 px-8 flex items-center justify-between z-20 border-b border-white/10 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 via-orange-500 to-amber-400 p-[1px] shadow-glow-isro flex items-center justify-center">
            <div className="w-full h-full bg-[#0B101D] rounded-xl flex items-center justify-center">
              <span className="text-xs font-black tracking-tighter text-amber-400 font-mono">ISRO</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight font-sans">BASGUARD</h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                PS26174
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">Biological Activity Space Experiment Monitor</p>
          </div>
        </div>

        {/* Top Right Theme & Audio Toggles */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleThemeMode}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold transition-all ${
              themeMode === 'WHITE_BLUE'
                ? 'bg-blue-600 text-white border-blue-400 shadow-glow-accent'
                : 'bg-slate-900 text-blue-300 border-blue-500/30 hover:bg-slate-800'
            }`}
          >
            <Palette className="w-4 h-4" />
            <span>{themeMode === 'WHITE_BLUE' ? 'WHITE & BLUE ☀️' : 'DEEP SPACE 🌌'}</span>
          </button>

          <button
            onClick={toggleAudioMuted}
            className={`p-2 rounded-lg transition-all glass-button ${
              audioMuted ? 'text-rose-400 border-rose-500/30' : 'text-emerald-400 border-emerald-500/30'
            }`}
            title={audioMuted ? 'Unmute Audio Copilot' : 'Mute Audio Copilot'}
          >
            {audioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Main Center Content Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 z-20 max-w-5xl mx-auto text-center relative">
        
        {/* Animated ISRO Emblem Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono mb-6 shadow-glow-isro"
        >
          <Sparkles className="w-4 h-4 animate-spin-slow" />
          <span className="font-semibold">ISRO SPACE EXPERIMENT AUDIT AI SYSTEM</span>
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
        </motion.div>

        {/* Hero Title */}
        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl font-black tracking-tight leading-tight max-w-3xl mb-4 font-sans"
        >
          Precision Space Safety &amp; <br />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-amber-400 bg-clip-text text-transparent">
            Astronaut Protocol Verification
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-sm sm:text-base text-slate-400 max-w-2xl mb-8 leading-relaxed font-sans"
        >
          Real-time 30 FPS OpenCV perception, MediaPipe 21-point hand tracking, and asynchronous VLM multimodal reasoning for biological payload operations.
        </motion.p>

        {/* Dynamic ISRO / Aerospace Quote Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="w-full max-w-2xl mb-10 p-6 rounded-2xl glass-panel border border-white/10 relative overflow-hidden shadow-2xl text-left"
        >
          <div className="absolute top-3 right-4 flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
              {currentQuote.badge}
            </span>
            <button 
              onClick={nextQuote}
              className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Next Aerospace Quote"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-start gap-4">
            <Quote className="w-8 h-8 text-blue-400 shrink-0 opacity-60 mt-1" />
            <AnimatePresence mode="wait">
              <motion.div
                key={activeQuoteIndex}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.3 }}
                className="flex-1"
              >
                <p className="text-sm sm:text-base italic text-slate-200 font-sans leading-relaxed mb-3">
                  "{currentQuote.quote}"
                </p>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-400 font-mono">{currentQuote.author}</span>
                  <span className="text-slate-500 text-xs">·</span>
                  <span className="text-xs text-slate-400 font-mono">{currentQuote.title}</span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>

        {/* 🚀 PRIMARY START MISSION BUTTON 🚀 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="relative group"
        >
          <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-blue-600 via-amber-500 to-indigo-600 blur-lg opacity-70 group-hover:opacity-100 transition duration-500 animate-pulse-ring" />
          
          <button
            onClick={handleStartMission}
            disabled={isLaunching}
            className="relative px-10 py-5 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white font-bold text-lg tracking-wide shadow-2xl flex items-center gap-4 transition-all duration-300 hover:scale-105 active:scale-95 border border-blue-300/40"
          >
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
              <Rocket className={`w-6 h-6 text-amber-300 ${isLaunching ? 'animate-bounce' : 'group-hover:rotate-12 transition-transform'}`} />
            </div>
            <div className="flex flex-col text-left leading-tight">
              <span className="font-extrabold font-mono tracking-wider text-base">
                {isLaunching ? 'INITIALIZING MISSION CONTROL...' : 'START MISSION DASHBOARD 🚀'}
              </span>
              <span className="text-xs text-blue-200 font-sans font-normal">
                Click to enter live ISRO experiment monitor
              </span>
            </div>
            <ChevronRight className="w-6 h-6 text-white group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </main>

      {/* Bottom Operational Pre-Flight Telemetry Badges */}
      <footer className="h-16 px-8 flex items-center justify-between z-20 border-t border-white/10 backdrop-blur-md text-xs font-mono text-slate-400">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>PERCEPTION ENGINE: <strong className="text-emerald-300">ONLINE (30 FPS)</strong></span>
          </div>

          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>MEDIAPIPE 3D: <strong className="text-blue-300">CALIBRATED</strong></span>
          </div>

          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-amber-400" />
            <span>PETRI-NET STATE: <strong className="text-amber-300">STANDBY</strong></span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <Globe className="w-4 h-4 text-indigo-400" />
          <span>ISRO GAGANYAAN PS26174 ARCHITECTURE</span>
        </div>
      </footer>
    </div>
  );
};
