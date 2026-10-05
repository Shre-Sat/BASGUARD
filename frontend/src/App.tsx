import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { LaunchPage } from './pages/LaunchPage';
import { MissionControl } from './pages/MissionControl';
import { Experiment } from './pages/Experiment';
import { Scene } from './pages/Scene';
import { Logs } from './pages/Logs';
import { System } from './pages/System';
import { Settings } from './pages/Settings';
import { useExperimentStore } from './store/useExperimentStore';

function App() {
  const { connectWebSocket, demoMode } = useExperimentStore();

  useEffect(() => {
    if (!demoMode) {
      connectWebSocket(import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws');
    }
  }, [connectWebSocket, demoMode]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LaunchPage />} />
        <Route element={<AppShell />}>
          <Route path="mission-control" element={<MissionControl />} />
          <Route path="experiment" element={<Experiment />} />
          <Route path="scene" element={<Scene />} />
          <Route path="logs" element={<Logs />} />
          <Route path="system" element={<System />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
