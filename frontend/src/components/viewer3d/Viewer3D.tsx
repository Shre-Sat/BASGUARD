import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { Mesh } from 'three';
import { useExperimentStore } from '../../store/useExperimentStore';

const RackScene = () => {
  const handRef = useRef<Mesh>(null);

  useFrame((state) => {
    if (handRef.current) {
      handRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.8) * 0.3 + 1.2;
      handRef.current.position.x = Math.cos(state.clock.elapsedTime * 0.5) * 0.3;
    }
  });

  return (
    <group>
      {/* Rack wireframe */}
      <mesh position={[0, 1, 0]}>
        <boxGeometry args={[2.4, 1.8, 1.6]} />
        <meshBasicMaterial color="#253242" wireframe transparent opacity={0.25} />
      </mesh>

      {/* Yellow box */}
      <mesh position={[0.4, 0.25, 0.3]}>
        <boxGeometry args={[0.3, 0.3, 0.3]} />
        <meshStandardMaterial color="#B8860B" roughness={0.7} />
      </mesh>

      {/* Red box */}
      <mesh position={[-0.3, 0.25, 0.3]}>
        <boxGeometry args={[0.3, 0.3, 0.3]} />
        <meshStandardMaterial color="#8B2020" roughness={0.7} />
      </mesh>

      {/* Hand position indicator */}
      <mesh ref={handRef} position={[0, 1.2, 0]}>
        <sphereGeometry args={[0.06, 12, 12]} />
        <meshStandardMaterial color="#22C55E" emissive="#22C55E" emissiveIntensity={0.5} />
      </mesh>

      {/* Coordinate axes — subtle */}
      <group>
        {/* X axis */}
        <mesh position={[0.75, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.005, 0.005, 1.5]} />
          <meshBasicMaterial color="#EF4444" opacity={0.3} transparent />
        </mesh>
        {/* Y axis */}
        <mesh position={[0, 0.75, 0]}>
          <cylinderGeometry args={[0.005, 0.005, 1.5]} />
          <meshBasicMaterial color="#22C55E" opacity={0.3} transparent />
        </mesh>
        {/* Z axis */}
        <mesh position={[0, 0, 0.75]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.005, 0.005, 1.5]} />
          <meshBasicMaterial color="#3B82F6" opacity={0.3} transparent />
        </mesh>
      </group>
    </group>
  );
};

export const Viewer3D = () => {
  const { health } = useExperimentStore();
  const isOnline = health.streamStatus === 'CONNECTED';

  return (
    <div className="flex flex-col h-full w-full">
      {/* Section label */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-baseline gap-3">
          <span className="text-label font-medium text-text-secondary">3D Scene</span>
          <span className="text-meta font-mono text-text-muted">Rack-Relative Frame</span>
        </div>
        <div className="flex gap-4 text-meta font-mono text-text-muted">
          <span>X +0.42 m</span>
          <span>Y −0.17 m</span>
          <span>Z +0.86 m</span>
        </div>
      </div>

      <div className="flex-1 cursor-grab active:cursor-grabbing">
        {isOnline ? (
          <Canvas camera={{ position: [3, 2.5, 3], fov: 40 }}>
            <color attach="background" args={['#050810']} />
            <ambientLight intensity={0.4} />
            <directionalLight position={[5, 8, 5]} intensity={0.6} />

            <RackScene />

            <Grid
              infiniteGrid
              cellSize={0.5}
              sectionSize={2}
              cellColor="#1E2A38"
              sectionColor="#253242"
              fadeDistance={12}
              fadeStrength={1.5}
            />
            <OrbitControls enablePan enableZoom enableRotate />
          </Canvas>
        ) : (
          <div className="flex items-center justify-center h-full">
            <span className="text-sm text-text-muted">Waiting for pose data</span>
          </div>
        )}
      </div>
    </div>
  );
};
