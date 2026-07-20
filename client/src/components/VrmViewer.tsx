import React, { Suspense, useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { VRM, VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

export interface VrmState {
  expression: 'joy' | 'sorrow' | 'angry' | 'surprised' | 'neutral';
  mouth_open: number;
  look_at: [number, number, number];
  is_speaking: boolean;
}

const EXPRESSION_MAP: Record<VrmState['expression'], string> = {
  joy: 'happy',
  sorrow: 'sad',
  angry: 'angry',
  surprised: 'surprised',
  neutral: 'neutral',
};

interface VrmModelProps {
  modelUrl: string;
  vrmState: VrmState | null;
  analyser: AnalyserNode | null;
  onLoadError: () => void;
}

const VrmModel: React.FC<VrmModelProps> = ({ modelUrl, vrmState, analyser, onLoadError }) => {
  const [vrm, setVrm] = useState<VRM | null>(null);

  useEffect(() => {
    let cancelled = false;
    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      modelUrl,
      (gltf) => {
        if (cancelled) return;
        const loadedVrm = gltf.userData.vrm as VRM | undefined;
        if (!loadedVrm) {
          onLoadError();
          return;
        }
        VRMUtils.rotateVRM0(loadedVrm);
        setVrm(loadedVrm);
      },
      undefined,
      () => {
        if (!cancelled) onLoadError();
      }
    );

    return () => {
      cancelled = true;
    };
  }, [modelUrl, onLoadError]);

  const amplitudeBufferRef = useRef<Uint8Array | null>(null);

  useFrame((_, delta) => {
    if (!vrm) return;
    vrm.update(delta);

    const em = vrm.expressionManager;
    if (!em) return;

    if (vrmState) {
      em.resetValues();
      em.setValue(EXPRESSION_MAP[vrmState.expression] ?? 'neutral', 1.0);

      let mouth = 0;
      if (vrmState.is_speaking && analyser) {
        if (!amplitudeBufferRef.current || amplitudeBufferRef.current.length !== analyser.frequencyBinCount) {
          amplitudeBufferRef.current = new Uint8Array(analyser.frequencyBinCount);
        }
        const data = amplitudeBufferRef.current;
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) sum += Math.abs(data[i] - 128);
        mouth = Math.min(1, (sum / data.length) / 30);
      }
      em.setValue('aa', mouth);
    }
  });

  return vrm ? <primitive object={vrm.scene} /> : null;
};

interface VrmViewerProps {
  modelUrl: string;
  vrmState: VrmState | null;
  audioElement: HTMLAudioElement | null;
  fallback: React.ReactNode;
}

const VrmViewer: React.FC<VrmViewerProps> = ({ modelUrl, vrmState, audioElement, fallback }) => {
  const [failed, setFailed] = useState(false);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);

  useEffect(() => {
    if (!audioElement || sourceRef.current) return;
    try {
      const ctx = audioCtxRef.current ?? new AudioContext();
      audioCtxRef.current = ctx;
      const source = ctx.createMediaElementSource(audioElement);
      const node = ctx.createAnalyser();
      node.fftSize = 256;
      source.connect(node);
      node.connect(ctx.destination);
      sourceRef.current = source;
      setAnalyser(node);
    } catch (err) {
      // Analyser is a nice-to-have for lip-sync amplitude; failing to attach
      // it should never block audio playback or the rest of the UI.
      console.warn('VrmViewer: failed to attach audio analyser', err);
    }
  }, [audioElement]);

  if (failed) return <>{fallback}</>;

  return (
    <Canvas camera={{ position: [0, 1.3, 1.5], fov: 30 }}>
      <ambientLight intensity={1.0} />
      <directionalLight position={[1, 1, 1]} />
      <Suspense fallback={null}>
        <VrmModel
          modelUrl={modelUrl}
          vrmState={vrmState}
          analyser={analyser}
          onLoadError={() => setFailed(true)}
        />
      </Suspense>
    </Canvas>
  );
};

export default VrmViewer;
