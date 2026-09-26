import { useExperimentStore } from '../../store/useExperimentStore';
import { Clock } from 'lucide-react';

export const Header = () => {
  const { health } = useExperimentStore();

  const isOnline = health.streamStatus === 'CONNECTED';
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-IN', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false, timeZone: 'Asia/Kolkata',
  });

  return (
    <header className="h-11 flex items-center justify-between px-5 bg-base-50 border-b border-border shrink-0">
      {/* Left: Branding */}
      <div className="flex items-center gap-6">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-semibold text-text-primary tracking-tight">BASGuard</span>
          <span className="text-meta text-text-muted">ISRO BAS Experiment Monitor</span>
        </div>
        <div className="divider-v h-4" />
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-semantic-success' : 'bg-semantic-critical'}`} />
          <span className="text-meta text-text-tertiary">
            {isOnline ? 'Offline Edge AI' : 'System Offline'}
          </span>
        </div>
      </div>

      {/* Center: Experiment info */}
      <div className="flex items-center gap-6">
        <div className="flex items-baseline gap-2">
          <span className="text-label text-text-secondary">BAS Experiment</span>
          <span className="text-label font-mono text-text-primary">EXP-001</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-label text-text-secondary">Session</span>
          <span className="text-label font-mono text-text-primary">0042</span>
        </div>
      </div>

      {/* Right: System status & Time */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-semantic-success' : 'bg-semantic-critical'}`} />
          <span className="text-meta text-text-secondary">
            {isOnline ? 'System Nominal' : 'System Fault'}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-meta text-text-tertiary font-mono">
          <Clock className="w-3 h-3" strokeWidth={1.5} />
          <span>{timeStr} IST</span>
        </div>
      </div>
    </header>
  );
};
