import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Stars, PerspectiveCamera } from '@react-three/drei';
import { Group, Mesh } from 'three';
import { useExperimentStore } from '../../store/useExperimentStore';
import { Move3D } from 'lucide-react';

const AnimatedRackScene = ({ currentStep }: { currentStep: string }) => {
  const handGroupRef = useRef<Group>(null);
  const yellowBoxRef = useRef<Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (handGroupRef.current) {
      if (currentStep === 'PICK_YELLOW' || currentStep === 'PLACE_YELLOW') {
        handGroupRef.current.position.y = Math.sin(t * 1.5) * 0.15 + 0.6;
        handGroupRef.current.position.x = Math.cos(t * 1.5) * 0.2 + 0.3;
      } else {
        handGroupRef.current.position.y = Math.sin(t * 0.8) * 0.08 + 1.1;
        handGroupRef.current.position.x = Math.cos(t * 0.6) * 0.1;
      }
    }

    if (yellowBoxRef.current && (currentStep === 'PICK_YELLOW' || currentStep === 'PLACE_YELLOW')) {
      yellowBoxRef.current.position.y = Math.sin(t * 1.5) * 0.15 + 0.6;
      yellowBoxRef.current.position.x = Math.cos(t * 1.5) * 0.2 + 0.3;
    }
  });

  return (
    <group>
      <mesh position={[0, 0.6, 0]}>
        <boxGeometry args={[2.2, 1.4, 1.5]} />
        <meshBasicMaterial color="#3B82F6" wireframe transparent opacity={0.3} />
      </mesh>

      <mesh position={[-0.4, 0.2, 0.2]}>
        <boxGeometry args={[0.35, 0.35, 0.35]} />
        <meshStandardMaterial color="#EF4444" roughness={0.3} metalness={0.4} emissive="#EF4444" emissiveIntensity={0.2} />
      </mesh>

      <mesh ref={yellowBoxRef} position={[0.4, 0.2, 0.2]}>
        <boxGeometry args={[0.35, 0.35, 0.35]} />
        <meshStandardMaterial color="#F59E0B" roughness={0.3} metalness={0.4} emissive="#F59E0B" emissiveIntensity={0.2} />
      </mesh>

      <group ref={handGroupRef} position={[0, 1.1, 0]}>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.6} />
        </mesh>

        {[-0.08, -0.04, 0, 0.04, 0.08].map((x, i) => (
          <mesh key={i} position={[x, -0.12, 0.06]}>
            <sphereGeometry args={[0.03, 12, 12]} />
            <meshStandardMaterial color="#6EE7B7" emissive="#6EE7B7" emissiveIntensity={0.8} />
          </mesh>
        ))}
      </group>

      <group>
        <mesh position={[0.8, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.006, 0.006, 1.6]} />
          <meshBasicMaterial color="#EF4444" transparent opacity={0.6} />
        </mesh>
        <mesh position={[0, 0.8, 0]}>
          <cylinderGeometry args={[0, 0.006, 1.6]} />
          <meshBasicMaterial color="#10B981" transparent opacity={0.6} />
        </mesh>
        <mesh position={[0, 0, 0.8]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.006, 0.006, 1.6]} />
          <meshBasicMaterial color="#3B82F6" transparent opacity={0.6} />
        </mesh>
      </group>
    </group>
  );
};

export const Viewer3D = () => {
  const { experiment, health } = useExperimentStore();
  const [cameraPreset, setCameraPreset] = useState<'ISO' | 'TOP' | 'FRONT'>('ISO');

  const isOnline = health.streamStatus === 'CONNECTED' || true;

  const cameraPositions: Record<string, [number, number, number]> = {
    ISO: [2.8, 2.2, 2.8],
    TOP: [0.01, 4.5, 0.01],
    FRONT: [0, 1.2, 4.0],
  };

  return (
    <div className="relative w-full h-full flex flex-col bg-[#05080F] overflow-hidden select-none border border-white/5">
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#090D18]/90 border-b border-white/10 shrink-0 z-20">
        <div className="flex items-center gap-2">
          <Move3D className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold font-mono text-slate-200">3D SPATIAL TELEMETRY</span>
        </div>

        <div className="flex items-center gap-1">
          {(['ISO', 'TOP', 'FRONT'] as const).map((preset) => (
            <button
              key={preset}
              onClick={() => setCameraPreset(preset)}
              className={`px-2 py-0.5 text-[10px] font-mono rounded border transition-all ${
                cameraPreset === preset
                  ? 'bg-blue-500/20 text-blue-300 border-blue-500/40 font-semibold'
                  : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
              }`}
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 relative cursor-grab active:cursor-grabbing bg-[#03050A]">
        {isOnline ? (
          <Canvas>
            <PerspectiveCamera makeDefault position={cameraPositions[cameraPreset]} fov={42} />
            <color attach="background" args={['#03050A']} />
            <ambientLight intensity={0.5} />
            <directionalLight position={[6, 10, 6]} intensity={0.8} />
            <pointLight position={[-4, 4, -4]} intensity={0.4} color="#3B82F6" />

            <AnimatedRackScene currentStep={experiment.currentStepId} />

            <Stars radius={50} depth={20} count={500} factor={3} saturation={0} fade speed={1} />

            <Grid
              infiniteGrid
              cellSize={0.4}
              sectionSize={1.6}
              cellColor="#1E293B"
              sectionColor="#334155"
              fadeDistance={10}
              fadeStrength={1.5}
            />
            <OrbitControls enablePan enableZoom enableRotate />
          </Canvas>
        ) : (
          <div className="flex items-center justify-center h-full">
            <span className="text-xs font-mono text-slate-500">WAITING FOR POSE TELEMETRY</span>
          </div>
        )}

        <div className="absolute bottom-2 left-2 z-20 flex items-center gap-3 px-2.5 py-1 rounded bg-slate-950/80 border border-white/10 font-mono text-[10px] text-slate-300 backdrop-blur-md">
          <span className="text-rose-400">X: +0.42m</span>
          <span className="text-emerald-400">Y: +0.18m</span>
          <span className="text-blue-400">Z: +0.84m</span>
        </div>
      </div>
    </div>
  );
};
