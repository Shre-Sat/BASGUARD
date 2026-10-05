import { LiveCameraFeed } from '../components/camera/LiveCameraFeed';
import { ExperimentStatus } from '../components/experiment/ExperimentStatus';
import { AlertsPanel } from '../components/alerts/AlertsPanel';
import { LogViewer } from '../components/logs/LogViewer';
import { SystemHealth } from '../components/telemetry/SystemHealth';
import { Viewer3D } from '../components/viewer3d/Viewer3D';

export const MissionControl = () => {
  return (
    <div className="flex h-full w-full overflow-hidden bg-[#04070D]">
      {/* ─── LEFT: Primary Viewports — Perception Feed + 3D Viewport ─── */}
      <div className="flex-[3] flex flex-col min-w-0 border-r border-white/10">
        {/* Live Perception HUD Camera Stream — Dominant Centerpiece */}
        <div className="flex-[3] min-h-0 border-b border-white/10 relative">
          <LiveCameraFeed />
        </div>

        {/* 3D Telemetry Viewer */}
        <div className="flex-[2] min-h-0 relative">
          <Viewer3D />
        </div>
      </div>

      {/* ─── RIGHT: State Machine + Alerts + System Health + Log Stream ─── */}
      <div className="w-[430px] flex flex-col shrink-0 min-h-0 bg-[#050810]">
        {/* FSM State Machine Tracker */}
        <div className="flex-[2.2] min-h-0 border-b border-white/10">
          <ExperimentStatus />
        </div>

        {/* Anomaly & Alert Center */}
        <div className="flex-[1.8] min-h-0 border-b border-white/10">
          <AlertsPanel />
        </div>

        {/* System Health Hardware Meters */}
        <div className="flex-none border-b border-white/10">
          <SystemHealth />
        </div>

        {/* Live Terminal Log Stream */}
        <div className="flex-[1.5] min-h-0">
          <LogViewer />
        </div>
      </div>
    </div>
  );
};
