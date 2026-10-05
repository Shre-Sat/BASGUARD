import { LogViewer } from '../components/logs/LogViewer';
import { AlertsPanel } from '../components/alerts/AlertsPanel';
import { Download, Terminal } from 'lucide-react';
import { useExperimentStore } from '../store/useExperimentStore';

export const Logs = () => {
  const { alerts } = useExperimentStore();

  const exportAuditLogs = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(alerts, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `ISRO_BASGuard_AuditLogs_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-[#04070D] font-sans select-none">
      <div className="h-12 border-b border-white/10 bg-[#090D18]/90 px-6 flex items-center justify-between shrink-0 font-mono">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-100 uppercase tracking-wider">
            <Terminal className="w-4 h-4 text-emerald-400" /> AUDIT LOGS & TELEMETRY ARCHIVE
          </div>
          <span className="text-white/20">|</span>
          <span className="text-xs text-slate-400">TOTAL EVENTS RECORDED: {alerts.length + 184}</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exportAuditLogs}
            className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono flex items-center gap-1.5 transition-all shadow-glow-accent"
          >
            <Download className="w-3.5 h-3.5" /> EXPORT AUDIT BUNDLE (JSON)
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-[440px] border-r border-white/10 shrink-0 flex flex-col h-full bg-[#050810]">
          <AlertsPanel />
        </div>

        <div className="flex-1 flex flex-col h-full bg-[#04070D]">
          <LogViewer />
        </div>
      </div>
    </div>
  );
};
