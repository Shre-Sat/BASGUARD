import { useExperimentStore } from '../../store/useExperimentStore';
import { Activity, ShieldCheck, Cpu, HardDrive, Wifi } from 'lucide-react';

export const StatusBar = () => {
  const { health, experiment } = useExperimentStore();

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

      {/* Center: Live Telemetry Ticker */}
      <div className="hidden lg:flex items-center gap-6 text-[10px]">
        <div className="flex items-center gap-1.5">
          <Cpu className="w-3 h-3 text-blue-400" />
          <span>CPU {health.cpu.toFixed(0)}%</span>
        </div>

        <div className="flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-emerald-400" />
          <span>GPU {health.gpu.toFixed(0)}%</span>
        </div>

        <div className="flex items-center gap-1.5">
          <HardDrive className="w-3 h-3 text-amber-400" />
          <span>VRAM {health.ram.toFixed(1)} GB</span>
        </div>
      </div>

      {/* Right: Network WebSocket Ping */}
      <div className="flex items-center gap-2">
        <Wifi className="w-3 h-3 text-emerald-400" />
        <span className="text-slate-300">WEBSOCKET 127.0.0.1:8000</span>
        <span className="px-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px]">
          ACTIVE
        </span>
      </div>
    </footer>
  );
};
