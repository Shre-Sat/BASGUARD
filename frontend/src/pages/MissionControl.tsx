import { LiveCameraFeed } from '../components/camera/LiveCameraFeed';
import { ExperimentStatus } from '../components/experiment/ExperimentStatus';
import { AlertsPanel } from '../components/alerts/AlertsPanel';
import { LogViewer } from '../components/logs/LogViewer';
import { SystemHealth } from '../components/telemetry/SystemHealth';
import { Viewer3D } from '../components/viewer3d/Viewer3D';

export const MissionControl = () => {
  return (
    <div className="flex h-full w-full overflow-hidden">

      {/* ─── LEFT: Primary — Live Perception + 3D ─── */}
      <div className="flex-[3] flex flex-col min-w-0 border-r border-border">
        {/* Perception feed — dominant */}
        <div className="flex-[3] min-h-0">
          <LiveCameraFeed />
        </div>

        <div className="divider-h" />

        {/* 3D Scene — tertiary */}
        <div className="flex-[1] min-h-0">
          <Viewer3D />
        </div>
      </div>

      {/* ─── RIGHT: Secondary — State + Alerts + Health ─── */}
      <div className="w-[420px] flex flex-col shrink-0 min-h-0">
        {/* Experiment state — secondary importance */}
        <div className="flex-[2] min-h-0 border-b border-border">
          <ExperimentStatus />
        </div>

        {/* Alerts — tertiary */}
        <div className="flex-[2] min-h-0 border-b border-border">
          <AlertsPanel />
        </div>

        {/* System Health — tertiary */}
        <div className="flex-none border-b border-border">
          <SystemHealth />
        </div>

        {/* Event Log — bottom */}
        <div className="flex-[1] min-h-0">
          <LogViewer />
        </div>
      </div>
    </div>
  );
};
