import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useExperimentStore } from '../../store/useExperimentStore';
import { LanguageSelector } from '../common/LanguageSelector';
import { 
  Clock, 
  Volume2, 
  VolumeX, 
  Zap, 
  RotateCcw, 
  Play, 
  AlertOctagon, 
  CheckCircle2, 
  Sparkles,
  Radio,
  Sun,
  Moon,
  Palette
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const Header = () => {
  const { 
    audioMuted, 
    toggleAudioMuted,
    themeMode,
    toggleThemeMode,
    orbitalPhase,
    toggleOrbitalPhase,
    triggerNormalSequence,
    triggerOutOfSequence,
    triggerLowConfidence,
    resetExperiment,
    completeExperiment
  } = useExperimentStore();

  const [time, setTime] = useState(new Date());
  const [showSimMenu, setShowSimMenu] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatIST = (d: Date) => {
    return d.toLocaleTimeString('en-IN', {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false, timeZone: 'Asia/Kolkata',
    });
  };

  const formatUTC = (d: Date) => {
    return d.toISOString().substring(11, 19);
  };

  return (
    <header className="h-12 flex items-center justify-between px-4 bg-[#0A0E17]/90 backdrop-blur-md border-b border-white/10 shrink-0 z-30 select-none">
      {/* Left: Branding & ISRO Mission Mark */}
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2.5 hover:opacity-80 transition-opacity">
          <img src="/basguard-logo.png" alt="BASGUARD Logo" className="h-7 w-auto object-contain drop-shadow-sm" />
          <div className="relative flex items-center justify-center w-6 h-6 rounded bg-gradient-to-tr from-amber-600 via-orange-500 to-amber-400 p-[1px] shadow-glow-isro">
            <div className="w-full h-full bg-[#0B101D] rounded flex items-center justify-center">
              <span className="text-[10px] font-black tracking-tighter text-amber-400 font-mono">ISRO</span>
            </div>
          </div>
          <span className="text-base font-extrabold tracking-tight text-slate-100 font-sans">BASGUARD</span>
        </Link>
      </div>

      {/* Center: Dual Orbital Day/Night Telemetry Display */}
      <div className="flex items-center gap-2.5">
        {/* Orbital Solar Cycle Telemetry Display (Sunlit vs Eclipse) */}
        <button
          onClick={toggleOrbitalPhase}
          title="Click to toggle Orbital Day (Sunlit ☀️) / Orbital Night (Eclipse 🌙)"
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-mono transition-all ${
            orbitalPhase === 'DAY'
              ? 'bg-amber-500/15 text-amber-300 border-amber-500/40 shadow-glow-isro'
              : 'bg-indigo-950/60 text-indigo-300 border-indigo-500/40 shadow-glow-accent'
          }`}
        >
          {orbitalPhase === 'DAY' ? (
            <Sun className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
          ) : (
            <Moon className="w-3.5 h-3.5 text-indigo-400" />
          )}
          <span className="text-[10px] font-bold tracking-wider">
            {orbitalPhase === 'DAY' ? 'ORBITAL DAY ☀️' : 'ORBITAL NIGHT 🌙'}
          </span>
        </button>

        {/* Language Selector Dropdown Choice */}
        <LanguageSelector />

        {/* UI Theme Switcher: White & Electric Blue vs Deep Space Night */}
        <button
          onClick={toggleThemeMode}
          title={`Switch Theme to ${themeMode === 'NIGHT' ? 'Clean White & Electric Blue 🎨' : 'Deep Space Night 🌌'} Mode`}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-mono font-semibold transition-all ${
            themeMode === 'WHITE_BLUE'
              ? 'bg-blue-600 text-white border-blue-400 shadow-glow-accent'
              : 'bg-slate-900 text-blue-300 border-blue-500/30 hover:bg-slate-800'
          }`}
        >
          <Palette className="w-3.5 h-3.5" />
          <span>{themeMode === 'WHITE_BLUE' ? 'WHITE & BLUE ☀️' : 'DEEP SPACE 🌌'}</span>
        </button>
      </div>

      {/* Right: Controls, Voice Toggle, Clock */}
      <div className="flex items-center gap-3">
        {/* Voice Audio Toggle */}
        <button
          onClick={toggleAudioMuted}
          title={audioMuted ? 'Unmute Voice Copilot 🗣️' : 'Mute Voice Copilot 🤫'}
          className={`p-1.5 rounded transition-all glass-button ${
            audioMuted ? 'text-rose-400 border-rose-500/30' : 'text-emerald-400 border-emerald-500/30'
          }`}
        >
          {audioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>

        {/* Demo Controller Button */}
        <div className="relative">
          <button
            onClick={() => setShowSimMenu(!showSimMenu)}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-medium rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition-all shadow-glow-isro"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>SIMULATOR 🎮</span>
          </button>

          <AnimatePresence>
            {showSimMenu && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 6, scale: 0.96 }}
                className="absolute right-0 mt-2 w-64 p-3 rounded-lg glass-panel border border-amber-500/20 shadow-2xl z-50 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between pb-2 border-b border-white/10 text-xs font-mono font-semibold text-amber-400">
                  <span className="flex items-center gap-1.5"><Radio className="w-3.5 h-3.5" /> EASY SIMULATOR CONTROLS</span>
                  <button onClick={() => setShowSimMenu(false)} className="text-slate-400 hover:text-white">✕</button>
                </div>

                <div className="flex flex-col gap-1.5 pt-1 text-xs font-mono">
                  <button
                    onClick={() => { triggerNormalSequence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/20 text-left transition-colors"
                  >
                    <Play className="w-3.5 h-3.5 shrink-0" />
                    <span>Advance Next Step (Good Job! 👍)</span>
                  </button>

                  <button
                    onClick={() => { triggerOutOfSequence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/20 text-left transition-colors"
                  >
                    <AlertOctagon className="w-3.5 h-3.5 shrink-0" />
                    <span>Trigger Out-of-Sequence (Oops! 🚨)</span>
                  </button>

                  <button
                    onClick={() => { triggerLowConfidence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/20 text-left transition-colors"
                  >
                    <Zap className="w-3.5 h-3.5 shrink-0" />
                    <span>Trigger Blurry Vision (Squint! 🧐)</span>
                  </button>

                  <button
                    onClick={() => { completeExperiment(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 hover:bg-blue-500/20 text-left transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    <span>Complete Full Mission (High Five! 🎉)</span>
                  </button>

                  <div className="h-px bg-white/10 my-1" />

                  <button
                    onClick={() => { resetExperiment(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-left transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5 shrink-0" />
                    <span>Reset Protocol to Start 🔄</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Live Clock Display */}
        <div className="flex items-center gap-2 px-3 py-1 rounded bg-slate-950/80 border border-white/10 text-xs font-mono text-slate-200 shadow-inner">
          <Clock className="w-3.5 h-3.5 text-blue-400" />
          <div className="flex flex-col text-[10px] leading-tight font-mono">
            <span className="text-slate-100 font-semibold">{formatIST(time)} IST</span>
            <span className="text-slate-400">{formatUTC(time)} UTC</span>
          </div>
        </div>
      </div>
    </header>
  );
};
