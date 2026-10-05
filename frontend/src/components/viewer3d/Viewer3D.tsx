import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Stars, PerspectiveCamera, Text } from '@react-three/drei';
import { Group, Mesh, Vector3 } from 'three';
import { useExperimentStore } from '../../store/useExperimentStore';
import { Move3D, Eye, Layers, Zap } from 'lucide-react';

const TrajectoryTrail = ({ points }: { points: Vector3[] }) => {
  if (points.length < 2) return null;
  return (
    <group>
      {points.map((pt, i) => (
        <mesh key={i} position={pt.toArray()}>
          <sphereGeometry args={[0.015, 8, 8]} />
          <meshBasicMaterial color="#3B82F6" transparent opacity={0.3 + (i / points.length) * 0.7} />
        </mesh>
      ))}
    </group>
  );
};

const AnimatedRackScene = ({ 
  currentStep, 
  renderMode, 
  showTrail 
}: { 
  currentStep: string; 
  renderMode: 'SOLID' | 'WIREFRAME' | 'XRAY';
  showTrail: boolean;
}) => {
  const handGroupRef = useRef<Group>(null);
  const yellowBoxRef = useRef<Mesh>(null);
  const trailPointsRef = useRef<Vector3[]>([]);
  const [trail, setTrail] = useState<Vector3[]>([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    let handX = 0;
    let handY = 1.1;
    let handZ = 0;

    if (handGroupRef.current) {
      if (currentStep === 'PICK_YELLOW' || currentStep === 'PLACE_YELLOW') {
        handY = Math.sin(t * 1.5) * 0.15 + 0.6;
        handX = Math.cos(t * 1.5) * 0.2 + 0.3;
      } else {
        handY = Math.sin(t * 0.8) * 0.08 + 1.1;
        handX = Math.cos(t * 0.6) * 0.1;
      }
      handGroupRef.current.position.set(handX, handY, handZ);

      if (showTrail) {
        const newPt = new Vector3(handX, handY, handZ);
        trailPointsRef.current = [...trailPointsRef.current.slice(-30), newPt];
        setTrail([...trailPointsRef.current]);
      }
    }

    if (yellowBoxRef.current && (currentStep === 'PICK_YELLOW' || currentStep === 'PLACE_YELLOW')) {
      yellowBoxRef.current.position.y = handY;
      yellowBoxRef.current.position.x = handX;
    }
  });

  const isWireframe = renderMode === 'WIREFRAME';
  const isXray = renderMode === 'XRAY';

  return (
    <group>
      {/* Main ISRO Payload Outer Containment Rack Frame */}
      <mesh position={[0, 0.6, 0]}>
        <boxGeometry args={[2.2, 1.4, 1.5]} />
        <meshBasicMaterial 
          color="#3B82F6" 
          wireframe={isWireframe || isXray} 
          transparent 
          opacity={isXray ? 0.15 : isWireframe ? 0.6 : 0.25} 
        />
      </mesh>

      {/* 3D Label text for Containment Rack */}
      <Text
        position={[0, 1.4, 0]}
        fontSize={0.12}
        color="#3B82F6"
        anchorX="center"
        anchorY="middle"
      >
        ISRO BIO-CONTAINMENT WORKBENCH
      </Text>

      {/* Red Specimen Box A (Spicy Sample) */}
      <mesh position={[-0.4, 0.2, 0.2]}>
        <boxGeometry args={[0.35, 0.35, 0.35]} />
        <meshStandardMaterial 
          color="#EF4444" 
          wireframe={isWireframe}
          roughness={0.3} 
          metalness={0.4} 
          emissive="#EF4444" 
          emissiveIntensity={isXray ? 0.6 : 0.2} 
        />
      </mesh>
      <Text position={[-0.4, 0.45, 0.2]} fontSize={0.08} color="#EF4444" anchorX="center">
        SPECIMEN-A (RED)
      </Text>

      {/* Yellow Specimen Box B (Banana Mold) */}
      <mesh ref={yellowBoxRef} position={[0.4, 0.2, 0.2]}>
        <boxGeometry args={[0.35, 0.35, 0.35]} />
        <meshStandardMaterial 
          color="#F59E0B" 
          wireframe={isWireframe}
          roughness={0.3} 
          metalness={0.4} 
          emissive="#F59E0B" 
          emissiveIntensity={isXray ? 0.7 : 0.3} 
        />
      </mesh>
      <Text position={[0.4, 0.45, 0.2]} fontSize={0.08} color="#F59E0B" anchorX="center">
        SPECIMEN-B (YELLOW)
      </Text>

      {/* Astronaut Glove 21-Keypoint 3D Model */}
      <group ref={handGroupRef} position={[0, 1.1, 0]}>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.8} />
        </mesh>

        {[-0.08, -0.04, 0, 0.04, 0.08].map((x, i) => (
          <mesh key={i} position={[x, -0.12, 0.06]}>
            <sphereGeometry args={[0.03, 12, 12]} />
            <meshStandardMaterial color="#6EE7B7" emissive="#6EE7B7" emissiveIntensity={0.9} />
          </mesh>
        ))}

        <Text position={[0, 0.15, 0]} fontSize={0.08} color="#10B981" anchorX="center">
          ASTRONAUT GLOVE (3D POSE)
        </Text>
      </group>

      {/* Motion Trajectory Particle Ribbon Trail */}
      {showTrail && <TrajectoryTrail points={trail} />}

      {/* 3D Coordinate Axis Vectors (X = Red, Y = Green, Z = Blue) */}
      <group position={[-1.0, 0, -0.8]}>
        <mesh position={[0.4, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.008, 0.008, 0.8]} />
          <meshBasicMaterial color="#EF4444" />
        </mesh>
        <Text position={[0.85, 0, 0]} fontSize={0.08} color="#EF4444">X</Text>

        <mesh position={[0, 0.4, 0]}>
          <cylinderGeometry args={[0.008, 0.008, 0.8]} />
          <meshBasicMaterial color="#10B981" />
        </mesh>
        <Text position={[0, 0.85, 0]} fontSize={0.08} color="#10B981">Y</Text>

        <mesh position={[0, 0, 0.4]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.008, 0.008, 0.8]} />
          <meshBasicMaterial color="#3B82F6" />
        </mesh>
        <Text position={[0, 0, 0.85]} fontSize={0.08} color="#3B82F6">Z</Text>
      </group>
    </group>
  );
};

export const Viewer3D = () => {
  const { experiment, themeMode } = useExperimentStore();
  const [cameraPreset, setCameraPreset] = useState<'ISO' | 'TOP' | 'FRONT' | 'SIDE'>('ISO');
  const [renderMode, setRenderMode] = useState<'SOLID' | 'WIREFRAME' | 'XRAY'>('SOLID');
  const [showTrail, setShowTrail] = useState(true);

  const isWhiteBlue = themeMode === 'WHITE_BLUE';

  const cameraPositions: Record<string, [number, number, number]> = {
    ISO: [2.8, 2.2, 2.8],
    TOP: [0.01, 4.5, 0.01],
    FRONT: [0, 1.2, 4.0],
    SIDE: [4.0, 1.2, 0],
  };

  const bgCanvasColor = isWhiteBlue ? '#F8FAFC' : '#03050A';
  const gridCellColor = isWhiteBlue ? '#CBD5E1' : '#1E293B';
  const gridSectionColor = isWhiteBlue ? '#94A3B8' : '#334155';

  return (
    <div className={`relative w-full h-full flex flex-col ${isWhiteBlue ? 'bg-[#F8FAFC] text-slate-900' : 'bg-[#05080F] text-slate-100'} overflow-hidden select-none border border-white/5`}>
      {/* Header Bar with Controls */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#090D18]/90 border-b border-white/10 shrink-0 z-20 font-mono">
        <div className="flex items-center gap-2">
          <Move3D className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200">3D SPATIAL TELEMETRY</span>
        </div>

        {/* Control Buttons for Presets, Render Mode, and Trail */}
        <div className="flex items-center gap-1.5 text-[10px]">
          {/* Camera Angles */}
          <div className="flex items-center gap-0.5 bg-slate-900 p-0.5 rounded border border-white/10">
            {(['ISO', 'TOP', 'FRONT', 'SIDE'] as const).map((preset) => (
              <button
                key={preset}
                onClick={() => setCameraPreset(preset)}
                className={`px-1.5 py-0.5 rounded transition-all ${
                  cameraPreset === preset
                    ? 'bg-blue-600 text-white font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Render Mode Toggle (Solid vs Wireframe vs X-Ray) */}
          <button
            onClick={() => {
              const modes: ('SOLID' | 'WIREFRAME' | 'XRAY')[] = ['SOLID', 'WIREFRAME', 'XRAY'];
              const next = modes[(modes.indexOf(renderMode) + 1) % modes.length];
              setRenderMode(next);
            }}
            className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 text-blue-300 border border-blue-500/30 hover:bg-slate-800 transition-colors"
            title="Toggle 3D Shading Mode (Solid / Wireframe / X-Ray)"
          >
            <Layers className="w-3 h-3 text-blue-400" />
            <span>{renderMode}</span>
          </button>

          {/* Trajectory Trail Toggle */}
          <button
            onClick={() => setShowTrail(!showTrail)}
            className={`flex items-center gap-1 px-2 py-0.5 rounded border transition-colors ${
              showTrail
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : 'bg-slate-900 text-slate-400 border-white/10 hover:text-white'
            }`}
            title="Toggle Astronaut Hand Motion Trajectory Trail"
          >
            <Zap className="w-3 h-3 text-emerald-400" />
            <span>TRAIL {showTrail ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      {/* 3D WebGL Canvas */}
      <div className="flex-1 relative cursor-grab active:cursor-grabbing">
        <Canvas>
          <PerspectiveCamera makeDefault position={cameraPositions[cameraPreset]} fov={42} />
          <color attach="background" args={[bgCanvasColor]} />
          <ambientLight intensity={isWhiteBlue ? 0.8 : 0.5} />
          <directionalLight position={[6, 10, 6]} intensity={1.0} />
          <pointLight position={[-4, 4, -4]} intensity={0.5} color="#3B82F6" />

          <AnimatedRackScene 
            currentStep={experiment.currentStepId} 
            renderMode={renderMode}
            showTrail={showTrail}
          />

          {!isWhiteBlue && <Stars radius={50} depth={20} count={600} factor={3} saturation={0} fade speed={1} />}

          <Grid
            infiniteGrid
            cellSize={0.4}
            sectionSize={1.6}
            cellColor={gridCellColor}
            sectionColor={gridSectionColor}
            fadeDistance={10}
            fadeStrength={1.5}
          />
          <OrbitControls enablePan enableZoom enableRotate />
        </Canvas>

        {/* Live Vector Coordinates Overlay HUD */}
        <div className="absolute bottom-2 left-2 z-20 flex items-center gap-3 px-3 py-1 rounded-lg bg-slate-950/80 border border-white/15 font-mono text-[10px] text-slate-300 backdrop-blur-md shadow-lg">
          <div className="flex items-center gap-1">
            <span className="text-rose-400 font-bold">X:</span>
            <span>+0.42m</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-emerald-400 font-bold">Y:</span>
            <span>+0.18m</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-blue-400 font-bold">Z:</span>
            <span>+0.84m</span>
          </div>
          <div className="h-3 w-px bg-white/20" />
          <span className="text-amber-400 font-semibold">STATE: {experiment.currentStepId}</span>
        </div>

        {/* Top-Right Preset Angle Label */}
        <div className="absolute top-2 left-2 z-20 px-2 py-0.5 rounded bg-slate-900/80 border border-white/10 text-[9px] font-mono text-slate-400 flex items-center gap-1.5 backdrop-blur-md">
          <Eye className="w-3 h-3 text-blue-400" />
          <span>VIEW: {cameraPreset} ({renderMode})</span>
        </div>
      </div>
    </div>
  );
};

