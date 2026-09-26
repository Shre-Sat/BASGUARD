import { useExperimentStore } from '../../store/useExperimentStore';
import type { AlertEvent } from '../../types';

export const AlertsPanel = () => {
  const { alerts } = useExperimentStore();

  const severityDot = (s: AlertEvent['severity']) => {
    switch (s) {
      case 'CRITICAL': return 'bg-semantic-critical';
      case 'WARNING': return 'bg-semantic-warning';
      case 'SUCCESS': return 'bg-semantic-success';
      default: return 'bg-accent';
    }
  };

  const severityLabel = (s: AlertEvent['severity']) => {
    switch (s) {
      case 'CRITICAL': return 'text-semantic-critical';
      case 'WARNING': return 'text-semantic-warning';
      case 'SUCCESS': return 'text-semantic-success';
      default: return 'text-text-secondary';
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Section label */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <span className="text-label font-medium text-text-secondary">Alert Center</span>
        {alerts.filter(a => a.severity === 'CRITICAL' && !a.acknowledged).length > 0 && (
          <span className="text-meta font-mono text-semantic-critical">
            {alerts.filter(a => a.severity === 'CRITICAL' && !a.acknowledged).length} unacknowledged
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="px-4 py-8 text-sm text-text-muted">
            No alerts
          </div>
        ) : (
          <div className="flex flex-col">
            {alerts.map((alert) => (
              <div key={alert.id} className="px-4 py-3 border-b border-border/50 hover:bg-panel/50 transition-colors">
                <div className="flex items-start gap-2.5">
                  {/* Severity dot */}
                  <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${severityDot(alert.severity)}`} />

                  <div className="flex-1 min-w-0">
                    {/* Header line: severity + time */}
                    <div className="flex items-baseline justify-between gap-2 mb-0.5">
                      <span className={`text-meta font-medium uppercase tracking-wider ${severityLabel(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className="text-meta font-mono text-text-muted">
                        {new Date(alert.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
                      </span>
                    </div>

                    {/* Type */}
                    <p className="text-sm text-text-primary leading-snug">
                      {alert.type.replace(/_/g, ' ').toLowerCase().replace(/^\w/, c => c.toUpperCase())}
                    </p>

                    {/* Message */}
                    <p className="text-meta text-text-tertiary mt-0.5 leading-relaxed">
                      {alert.message}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
