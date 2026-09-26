export interface DetectionResult {
  objectId: string;
  objectName: string;
  confidence: number;
  bbox: [number, number, number, number];
}

export interface HandInteraction {
  handId: string;
  state: 'approaching' | 'touching' | 'grasping' | 'holding' | 'releasing' | 'none';
  objectId: string | null;
  confidence: number;
}

export interface ExperimentState {
  currentStepId: string;
  completedStepIds: string[];
  nextStepId: string | null;
  confidence: number;
  status: 'IDLE' | 'IN_PROGRESS' | 'ERROR' | 'COMPLETED';
}

export interface AlertEvent {
  id: string;
  timestamp: number;
  severity: 'INFO' | 'SUCCESS' | 'WARNING' | 'CRITICAL';
  type: string;
  message: string;
  acknowledged: boolean;
}

export interface SystemHealth {
  fps: number;
  inferenceLatency: number;
  cpu: number;
  gpu: number;
  ram: number;
  power: number;
  storage: number;
  streamStatus: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING';
}

export interface ProtocolStep {
  id: string;
  name: string;
  description: string;
}
