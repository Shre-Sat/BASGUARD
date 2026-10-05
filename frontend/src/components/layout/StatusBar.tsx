import { useExperimentStore } from '../../store/useExperimentStore';
import { ShieldCheck, Wifi } from 'lucide-react';

export const StatusBar = () => {
  const { experiment } = useExperimentStore();

  const isNominal = experiment.status !== 'ERROR';

  return (
    <footer className="h-7 bg-[#060910] border-t border-white/10 px-4 flex items-center justify-between text-[11px] font-mono text-slate-400 shrink-0 z-20 select-none">
      {/* Left: Overall Health & FSM State */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className={`w-3.5 h-3.5 ${isNominal ? 'text-emerald-400' : 'text-rose-500'}`} />
          <span className={isNominal ? 'text-emerald-300 font-medium' : 'text-rose-400 font-semibold'}>
            {isNominal ? 'NOMINAL OPERATION' : 'ANOMALY DETECTED'}
          </span>
        </div>

        <div className="h-3 w-px bg-white/10" />

        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">STATE:</span>
          <span className="text-slate-200 font-semibold">{experiment.currentStepId}</span>
        </div>
      </div>

      {/* Right: Network WebSocket Ping */}
      <div className="flex items-center gap-2">
        <Wifi className="w-3.5 h-3.5 text-emerald-400" />
        <span className="text-slate-300">WEBSOCKET ONLINE</span>
        <span className="px-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px]">
          100%
        </span>
      </div>
    </footer>
  );
};
