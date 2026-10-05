import { useState, useEffect } from 'react';
import { useExperimentStore } from '../../store/useExperimentStore';
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
  Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const Header = () => {
  const { 
    health, 
    demoMode, 
    audioMuted, 
    toggleAudioMuted,
    triggerNormalSequence,
    triggerOutOfSequence,
    triggerLowConfidence,
    resetExperiment,
    completeExperiment
  } = useExperimentStore();

  const [time, setTime] = useState(new Date());
  const [showSimMenu, setShowSimMenu] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 200);
    return () => clearInterval(timer);
  }, []);

  const isOnline = health.streamStatus === 'CONNECTED' || demoMode;

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
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center justify-center w-7 h-7 rounded bg-gradient-to-tr from-amber-600 via-orange-500 to-amber-400 p-[1px] shadow-glow-isro">
            <div className="w-full h-full bg-[#0B101D] rounded flex items-center justify-center">
              <span className="text-[11px] font-black tracking-tighter text-amber-400 font-mono">ISRO</span>
            </div>
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-100 tracking-tight font-sans">BASGUARD</span>
              <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v2.4.1
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">Biological Activity Space Monitor</span>
          </div>
        </div>

        <div className="h-4 w-px bg-white/10" />

        <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900/60 border border-white/5">
          <div className="relative flex items-center justify-center">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            {isOnline && <div className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-75" />}
          </div>
          <span className="text-xs font-mono font-medium text-slate-300">
            {demoMode ? 'SIMULATED EDGE AI' : isOnline ? 'HARDWARE ONLINE' : 'STREAM DISCONNECTED'}
          </span>
        </div>
      </div>

      <div className="hidden md:flex items-center gap-6 text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-500">PAYLOAD:</span>
          <span className="text-amber-400 font-semibold">ISRO-BAS-01</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">ORBIT:</span>
          <span className="text-slate-200">LEO 400 KM</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">FPS:</span>
          <span className="text-emerald-400 font-semibold">{health.fps.toFixed(1)}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">LATENCY:</span>
          <span className="text-blue-400">{health.inferenceLatency.toFixed(0)} ms</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleAudioMuted}
          title={audioMuted ? 'Unmute Neural Voice Alerts' : 'Mute Voice Alerts'}
          className={`p-1.5 rounded transition-all glass-button ${
            audioMuted ? 'text-rose-400 border-rose-500/30' : 'text-emerald-400 border-emerald-500/30'
          }`}
        >
          {audioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>

        <div className="relative">
          <button
            onClick={() => setShowSimMenu(!showSimMenu)}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-medium rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition-all shadow-glow-isro"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>SIMULATOR</span>
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
                  <span className="flex items-center gap-1.5"><Radio className="w-3.5 h-3.5" /> TELEMETRY SIMULATOR</span>
                  <button onClick={() => setShowSimMenu(false)} className="text-slate-400 hover:text-white">✕</button>
                </div>

                <div className="flex flex-col gap-1.5 pt-1 text-xs font-mono">
                  <button
                    onClick={() => { triggerNormalSequence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/20 text-left transition-colors"
                  >
                    <Play className="w-3.5 h-3.5 shrink-0" />
                    <span>Advance Next Step (Normal)</span>
                  </button>

                  <button
                    onClick={() => { triggerOutOfSequence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/20 text-left transition-colors"
                  >
                    <AlertOctagon className="w-3.5 h-3.5 shrink-0" />
                    <span>Trigger Out-of-Sequence Anomaly</span>
                  </button>

                  <button
                    onClick={() => { triggerLowConfidence(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/20 text-left transition-colors"
                  >
                    <Zap className="w-3.5 h-3.5 shrink-0" />
                    <span>Trigger Low Confidence</span>
                  </button>

                  <button
                    onClick={() => { completeExperiment(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 hover:bg-blue-500/20 text-left transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    <span>Complete Full Sequence</span>
                  </button>

                  <div className="h-px bg-white/10 my-1" />

                  <button
                    onClick={() => { resetExperiment(); setShowSimMenu(false); }}
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-left transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5 shrink-0" />
                    <span>Reset Protocol to Standby</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

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
