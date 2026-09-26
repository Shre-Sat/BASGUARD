import { useState } from 'react';
import { LogViewer } from '../components/logs/LogViewer';
import { AlertsPanel } from '../components/alerts/AlertsPanel';
import { Download, Search } from 'lucide-react';
import { useExperimentStore } from '../store/useExperimentStore';

export const Logs = () => {
  const { alerts } = useExperimentStore();
  const [searchQuery, setSearchQuery] = useState<string>('');

  const exportAuditLogs = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(alerts, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `BASGuard_AuditLogs_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-bg-dark">
      {/* Action Header */}
      <div className="h-12 border-b border-border bg-bg-panel px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-xs font-semibold text-text-primary uppercase tracking-wider">
            Audit Logs & Real-Time Event Telemetry
          </h1>
          <span className="text-border">|</span>
          <span className="text-meta text-text-tertiary font-mono">TOTAL EVENTS: {alerts.length + 142}</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Search bar */}
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 absolute left-2.5 text-text-tertiary" />
            <input
              type="text"
              placeholder="Search logs or error codes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-bg-dark border border-border rounded text-xs pl-8 pr-3 py-1 text-text-primary focus:outline-none focus:border-accent w-56 font-mono"
            />
          </div>

          {/* Export Button */}
          <button
            onClick={exportAuditLogs}
            className="px-3 py-1 rounded bg-accent/20 text-accent border border-accent/30 text-xs font-mono flex items-center gap-1.5 hover:bg-accent/30 transition-colors"
          >
            <Download className="w-3.5 h-3.5" /> Export Audit Bundle
          </button>
        </div>
      </div>

      {/* Main Content split */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Alert Stream */}
        <div className="w-[420px] border-r border-border shrink-0 flex flex-col h-full bg-bg-panel/40">
          <AlertsPanel />
        </div>

        {/* Right Log Console Stream */}
        <div className="flex-1 flex flex-col h-full bg-bg-dark">
          <LogViewer />
        </div>
      </div>
    </div>
  );
};
