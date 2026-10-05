import { useState } from 'react';
import { useExperimentStore } from '../store/useExperimentStore';
import { Settings as SettingsIcon, Sliders, Volume2, Sparkles } from 'lucide-react';

export const Settings = () => {
  const {
    demoMode, 
    setDemoMode,
    audioMuted,
    toggleAudioMuted,
    triggerNormalSequence, 
    triggerOutOfSequence, 
    triggerLowConfidence,
    simulateCameraLoss, 
    completeExperiment, 
    resetExperiment,
  } = useExperimentStore();

  const [yoloThreshold, setYoloThreshold] = useState(0.85);
  const [fsmTimeout, setFsmTimeout] = useState(15);

  const demoActions = [
    { label: 'Advance Next Step (Normal)', desc: 'Validates perception criteria and progresses Petri-Net state', fn: triggerNormalSequence },
    { label: 'Trigger Out-of-Sequence Anomaly', desc: 'Simulates astronaut executing out-of-order action', fn: triggerOutOfSequence },
    { label: 'Trigger Low Confidence Anomaly', desc: 'Simulates occlusion or poor lighting condition', fn: triggerLowConfidence },
    { label: 'Simulate Camera Feed Disconnection', desc: 'Tests fallback edge recovery mechanism', fn: simulateCameraLoss },
    { label: 'Complete Full Protocol Sequence', desc: 'Marks all ISRO BAS experiment steps complete', fn: completeExperiment },
    { label: 'Reset Protocol State to Standby', desc: 'Clears active FSM tokens and active alerts', fn: resetExperiment },
  ];

  return (
    <div className="flex flex-col h-full w-full overflow-y-auto bg-[#04070D] font-sans select-none p-6">
      <div className="max-w-3xl w-full mx-auto flex flex-col gap-8">
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <SettingsIcon className="w-5 h-5 text-blue-400" /> MISSION CONTROL SYSTEM CONFIGURATION
            </h1>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Configure YOLOv8 perception thresholds, Petri-Net timeout guards, and Voice Alert parameters
            </p>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-white/10 flex flex-col gap-5 shadow-xl">
          <h2 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider pb-3 border-b border-white/10 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-400" /> AI PERCEPTION & VOICE ALERT SETTINGS
          </h2>

          <div className="flex flex-col gap-4 font-mono text-xs">
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <div>
                <span className="text-slate-100 font-semibold flex items-center gap-2">
                  <Volume2 className="w-4 h-4 text-emerald-400" /> Neural Text-to-Speech (Piper TTS) Voice Alerts
                </span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  Plays priority-queued audio alerts when anomalies or protocol violations occur.
                </p>
              </div>
              <button
                onClick={toggleAudioMuted}
                className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all border ${
                  !audioMuted ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-glow-success' : 'bg-slate-800 text-slate-400 border-white/10'
                }`}
              >
                {!audioMuted ? 'ACTIVE (UNMUTED)' : 'MUTED'}
              </button>
            </div>

            <div className="flex flex-col gap-2 py-2 border-b border-white/5">
              <div className="flex justify-between items-center">
                <span className="text-slate-300 font-semibold">YOLOv8 Minimum Confidence Cutoff:</span>
                <span className="text-blue-400 font-bold">{(yoloThreshold * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={yoloThreshold}
                onChange={(e) => setYoloThreshold(parseFloat(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
            </div>

            <div className="flex flex-col gap-2 py-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-300 font-semibold">Petri-Net Anomaly Duration Limit:</span>
                <span className="text-amber-400 font-bold">{fsmTimeout} Seconds</span>
              </div>
              <input
                type="range"
                min="5"
                max="60"
                step="5"
                value={fsmTimeout}
                onChange={(e) => setFsmTimeout(parseInt(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-white/10 flex flex-col gap-5 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div>
              <h2 className="text-xs font-semibold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" /> DEMO SIMULATOR SUITE
              </h2>
              <p className="text-[11px] font-sans text-slate-400 mt-0.5">
                Simulate ISRO BAS experiment events for evaluation and demonstration.
              </p>
            </div>

            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all border ${
                demoMode ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-glow-isro' : 'bg-slate-800 text-slate-400 border-white/10'
              }`}
            >
              {demoMode ? 'DEMO MODE ACTIVE' : 'REAL HARDWARE MODE'}
            </button>
          </div>

          {demoMode && (
            <div className="grid grid-cols-1 gap-2 font-mono text-xs">
              {demoActions.map((action) => (
                <div key={action.label} className="p-3 rounded-lg bg-slate-900/60 border border-white/5 flex items-center justify-between hover:bg-slate-800/60 transition-colors">
                  <div>
                    <span className="text-slate-200 font-bold font-sans">{action.label}</span>
                    <p className="text-[11px] text-slate-400 font-sans mt-0.5">{action.desc}</p>
                  </div>
                  <button
                    onClick={action.fn}
                    className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs font-semibold transition-all shadow-md active:scale-95"
                  >
                    TRIGGER
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
