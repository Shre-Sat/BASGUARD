import { create } from 'zustand';
import type { 
  ExperimentState, 
  AlertEvent, 
  SystemHealth, 
  ProtocolStep 
} from '../types';

interface AppState {
  // Mode
  demoMode: boolean;
  setDemoMode: (enabled: boolean) => void;
  
  // Protocol Definition
  protocol: ProtocolStep[];
  
  // Real-time State
  experiment: ExperimentState;
  alerts: AlertEvent[];
  health: SystemHealth;
  detections: any[];
  
  // Actions for Demo/Backend
  updateExperiment: (update: Partial<ExperimentState>) => void;
  addAlert: (alert: Omit<AlertEvent, 'id' | 'timestamp'>) => void;
  updateHealth: (update: Partial<SystemHealth>) => void;
  
  // Real backend connection
  connectWebSocket: (url: string) => void;
  
  // Demo Controls
  triggerNormalSequence: () => void;
  triggerOutOfSequence: () => void;
  triggerLowConfidence: () => void;
  simulateCameraLoss: () => void;
  completeExperiment: () => void;
  resetExperiment: () => void;
}

const DEFAULT_PROTOCOL: ProtocolStep[] = [
  { id: 'IDLE', name: 'Wait', description: 'System ready.' },
  { id: 'DETECT_OUTER', name: 'Detect Outer Box', description: 'Ensure outer box is visible.' },
  { id: 'OPEN_OUTER', name: 'Open Outer Box', description: 'Open the lid of the outer box.' },
  { id: 'IDENTIFY_RED', name: 'Identify Red Box', description: 'Locate the red inner box.' },
  { id: 'IDENTIFY_YELLOW', name: 'Identify Yellow Box', description: 'Locate the yellow inner box.' },
  { id: 'PICK_YELLOW', name: 'Pick Yellow Box', description: 'Grasp the yellow box.' },
  { id: 'PLACE_YELLOW', name: 'Place Yellow Box', description: 'Place the yellow box down.' },
  { id: 'COMPLETE', name: 'Complete', description: 'Experiment finished.' },
];

const INITIAL_HEALTH: SystemHealth = {
  fps: 0,
  inferenceLatency: 0,
  cpu: 0,
  gpu: 0,
  ram: 0,
  power: 0,
  storage: 0,
  streamStatus: 'DISCONNECTED',
};

const INITIAL_EXPERIMENT: ExperimentState = {
  currentStepId: 'IDLE',
  completedStepIds: [],
  nextStepId: 'DETECT_OUTER',
  confidence: 0,
  status: 'IDLE'
};

export const useExperimentStore = create<AppState>((set, get) => ({
  demoMode: false, // Default to false to use real backend
  setDemoMode: (enabled) => set({ demoMode: enabled }),
  
  protocol: DEFAULT_PROTOCOL,
  experiment: { ...INITIAL_EXPERIMENT },
  alerts: [],
  health: { ...INITIAL_HEALTH },
  detections: [],
  
  updateExperiment: (update) => set((state) => ({ 
    experiment: { ...state.experiment, ...update } 
  })),
  
  addAlert: (alert) => set((state) => ({
    alerts: [
      { ...alert, id: Math.random().toString(36).substring(7), timestamp: Date.now() },
      ...state.alerts
    ].slice(0, 50) // Keep last 50
  })),
  
  updateHealth: (update) => set((state) => ({
    health: { ...state.health, ...update }
  })),

  connectWebSocket: (url: string) => {
    let ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log('Connected to BASGuard Backend WebSocket');
      set((state) => ({
        health: { ...state.health, streamStatus: 'CONNECTED' }
      }));
    };
    
    ws.onmessage = (event) => {
      if (get().demoMode) return; // Ignore backend if in demo mode
      try {
        const data = JSON.parse(event.data);
        
        set((state) => {
          const newState = { ...state };
          
          if (data.health) {
            newState.health = { ...state.health, ...data.health, streamStatus: 'CONNECTED' };
          }
          if (data.experiment) {
            newState.experiment = { ...state.experiment, ...data.experiment };
          }
          if (data.alerts && Array.isArray(data.alerts)) {
            // Append new alerts that don't already exist (simple dedup by timestamp/message)
            const newAlerts = data.alerts.filter((a: any) => 
              !state.alerts.some(existing => existing.timestamp === a.timestamp && existing.message === a.message)
            ).map((a: any) => ({
              id: Math.random().toString(36).substring(7),
              severity: a.severity,
              type: 'SYSTEM',
              message: a.message,
              timestamp: a.timestamp * 1000,
              acknowledged: false
            }));
            
            if (newAlerts.length > 0) {
              newState.alerts = [...newAlerts.reverse(), ...state.alerts].slice(0, 50);
            }
          }
          if (data.detections && Array.isArray(data.detections)) {
            newState.detections = data.detections;
          }
          
          return newState;
        });
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected. Reconnecting in 3s...');
      set((state) => ({
        health: { ...state.health, streamStatus: 'DISCONNECTED', fps: 0 }
      }));
      setTimeout(() => get().connectWebSocket(url), 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      ws.close();
    };
  },
  
  // --- DEMO ACTIONS ---
  triggerNormalSequence: () => {
    const { experiment, protocol, addAlert } = get();
    const currentIndex = protocol.findIndex(s => s.id === experiment.currentStepId);
    
    if (currentIndex < protocol.length - 1) {
      const nextStep = protocol[currentIndex + 1];
      const futureStep = protocol[currentIndex + 2];
      
      addAlert({
        severity: 'SUCCESS',
        type: 'STEP_COMPLETED',
        message: `Step ${currentIndex} completed successfully`,
        acknowledged: false
      });
      
      set((state) => ({
        experiment: {
          ...state.experiment,
          status: 'IN_PROGRESS',
          completedStepIds: [...state.experiment.completedStepIds, state.experiment.currentStepId],
          currentStepId: nextStep.id,
          nextStepId: futureStep ? futureStep.id : null,
          confidence: 94 + Math.random() * 5
        }
      }));
    }
  },
  
  triggerOutOfSequence: () => {
    const { addAlert, experiment } = get();
    addAlert({
      severity: 'CRITICAL',
      type: 'OUT_OF_SEQUENCE',
      message: `Expected: ${experiment.nextStepId}. Detected: CLOSE_OUTER_BOX`,
      acknowledged: false
    });
    set((state) => ({
      experiment: { ...state.experiment, status: 'ERROR', confidence: 45.2 }
    }));
  },
  
  triggerLowConfidence: () => {
    get().addAlert({
      severity: 'WARNING',
      type: 'LOW_CONFIDENCE',
      message: 'Unable to confidently identify hand-object interaction',
      acknowledged: false
    });
    set((state) => ({
      experiment: { ...state.experiment, confidence: 32.4 }
    }));
  },
  
  simulateCameraLoss: () => {
    get().addAlert({
      severity: 'CRITICAL',
      type: 'STREAM_LOST',
      message: 'Connection to CAM-01 lost. Attempting reconnect...',
      acknowledged: false
    });
    set((state) => ({
      health: { ...state.health, streamStatus: 'DISCONNECTED', fps: 0 }
    }));
  },
  
  completeExperiment: () => {
    const { protocol, addAlert } = get();
    const allIds = protocol.map(p => p.id);
    addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: 'Experiment sequence successfully completed.',
      acknowledged: false
    });
    set({
      experiment: {
        currentStepId: 'COMPLETE',
        completedStepIds: allIds.slice(0, -1),
        nextStepId: null,
        confidence: 99.9,
        status: 'COMPLETED'
      }
    });
  },
  
  resetExperiment: () => {
    get().addAlert({
      severity: 'INFO',
      type: 'SYSTEM',
      message: 'Experiment monitoring reset',
      acknowledged: false
    });
    set({
      experiment: { ...INITIAL_EXPERIMENT },
      alerts: [],
      health: { ...INITIAL_HEALTH }
    });
  }
}));
