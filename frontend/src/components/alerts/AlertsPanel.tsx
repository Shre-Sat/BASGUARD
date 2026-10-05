import { useState } from 'react';
import { useExperimentStore } from '../../store/useExperimentStore';
import { 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  Bell, 
  Check, 
  Trash2,
  Volume2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const AlertsPanel = () => {
  const { alerts, acknowledgeAlert, clearAllAlerts, audioMuted } = useExperimentStore();
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'WARNING'>('ALL');

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'CRITICAL') return a.severity === 'CRITICAL';
    if (filter === 'WARNING') return a.severity === 'WARNING';
    return true;
  });

  const unacknowledgedCount = alerts.filter(a => !a.acknowledged).length;

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />;
      case 'WARNING': return <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />;
      case 'SUCCESS': return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />;
      default: return <Info className="w-4 h-4 text-blue-400 shrink-0" />;
    }
  };

  const getBorderColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'border-rose-500/30 bg-rose-500/5';
      case 'WARNING': return 'border-amber-500/30 bg-amber-500/5';
      case 'SUCCESS': return 'border-emerald-500/30 bg-emerald-500/5';
      default: return 'border-white/5 bg-slate-900/40';
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#05080F] border border-white/5 select-none overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-[#090D18]/90 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold font-mono text-slate-200">ANOMALY & ALERT CENTER</span>
          {unacknowledgedCount > 0 && (
            <span className="px-1.5 py-0.2 rounded-full bg-rose-500 text-white font-mono text-[10px] font-bold animate-pulse">
              {unacknowledgedCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Audio Alert Status Badge */}
          <div className={`flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded border ${
            audioMuted ? 'bg-slate-900 text-slate-500 border-white/10' : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
          }`}>
            <Volume2 className="w-3 h-3" />
            <span>{audioMuted ? 'MUTED' : 'VOICE ACTIVE'}</span>
          </div>

          <button
            onClick={clearAllAlerts}
            className="p-1 rounded text-slate-400 hover:text-rose-400 transition-colors"
            title="Clear All Alerts"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1 px-3 py-1.5 bg-[#070B14] border-b border-white/5 text-[10px] font-mono">
        {(['ALL', 'CRITICAL', 'WARNING'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2.5 py-0.5 rounded transition-all ${
              filter === f 
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        <AnimatePresence mode="popLayout">
          {filteredAlerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 font-mono text-xs gap-2 py-8">
              <CheckCircle2 className="w-8 h-8 text-emerald-500/40" />
              <span>NO ACTIVE ANOMALIES</span>
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, height: 0, y: -10 }}
                animate={{ opacity: 1, height: 'auto', y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                className={`p-2.5 rounded-lg border flex items-start gap-2.5 ${getBorderColor(alert.severity)} ${
                  !alert.acknowledged ? 'ring-1 ring-white/10' : 'opacity-70'
                }`}
              >
                {getIcon(alert.severity)}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-semibold text-slate-200 uppercase">
                      {alert.type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 mt-0.5 leading-snug font-sans">
                    {alert.message}
                  </p>
                </div>

                {!alert.acknowledged && (
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono flex items-center gap-1 transition-colors"
                    title="Acknowledge Alert"
                  >
                    <Check className="w-3 h-3 text-emerald-400" />
                  </button>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
