import { useCallback, useEffect, useRef, useState } from 'react';
import type { ScanTile, IndustrialArea } from '../types';

type Bbox = { lat_min: number; lat_max: number; lon_min: number; lon_max: number };

interface Props {
  lat: number;
  lon: number;
  drawMode?: boolean;
  onBboxDrawn?: (bbox: Bbox) => void;
  scanTiles?: ScanTile[];
  areas?: IndustrialArea[];
  selectedArea?: IndustrialArea;
  onAreaSelect?: (area: IndustrialArea) => void;
  onAreaBoundaryChange?: (boundary: [number, number][]) => void;
}

const KEY = import.meta.env.VITE_VWORLD_KEY ?? '';

export default function Map3D({ lat, lon, drawMode, onBboxDrawn, scanTiles, areas = [], selectedArea, onAreaSelect, onAreaBoundaryChange }: Props) {
  const iframeRef  = useRef<HTMLIFrameElement>(null);
  const readyRef   = useRef(false);
  const pendingRef = useRef<{ lat: number; lon: number } | null>(null);
  const areasRef   = useRef<IndustrialArea[]>(areas);
  const [src] = useState(
    () => `/vworld3d.html?key=${encodeURIComponent(KEY)}&lat=${lat}&lon=${lon}`
  );

  const onBboxDrawnRef = useRef(onBboxDrawn);
  useEffect(() => { onBboxDrawnRef.current = onBboxDrawn; }, [onBboxDrawn]);

  useEffect(() => {
    areasRef.current = areas;
  }, [areas]);

  const postOverlay = useCallback(() => {
    iframeRef.current?.contentWindow?.postMessage({
      type: 'renderIndustrialAreas',
      areas,
      selectedAreaId: selectedArea?.id ?? null,
    }, '*');
  }, [areas, selectedArea?.id]);

  /* ── iframe 메시지 수신 ── */
  useEffect(() => {
    function onMessage(e: MessageEvent) {
      if (e.source !== iframeRef.current?.contentWindow) return;

      if (e.data?.type === 'vworld3d:areaSelected') {
        const area = areasRef.current.find((item) => item.id === e.data.areaId);
        if (area) onAreaSelect?.(area);
        return;
      }
      if (e.data?.type === 'vworld3d:areaBoundaryChanged') {
        onAreaBoundaryChange?.(e.data.boundary);
        return;
      }
      if (e.data?.type === 'vworld3d:bbox') {
        onBboxDrawnRef.current?.(e.data.bbox);
        return;
      }
      if (e.data?.type !== 'vworld3d:ready') return;

      readyRef.current = true;
      if (pendingRef.current) {
        iframeRef.current?.contentWindow?.postMessage(
          { type: 'flyTo', ...pendingRef.current }, '*'
        );
        pendingRef.current = null;
      }
      if (scanTiles && scanTiles.length > 0) {
        iframeRef.current?.contentWindow?.postMessage(
          { type: 'showTiles', tiles: scanTiles }, '*'
        );
      }
      postOverlay();
    }
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, [onAreaBoundaryChange, onAreaSelect, postOverlay, scanTiles]);

  /* ── scanTiles 변경 시 iframe에 전송 ── */
  useEffect(() => {
    if (!readyRef.current) return;
    iframeRef.current?.contentWindow?.postMessage(
      { type: 'showTiles', tiles: scanTiles ?? [] }, '*'
    );
  }, [scanTiles]);

  /* ── drawMode 변경 시 iframe에 메시지 ── */
  useEffect(() => {
    if (!readyRef.current) return;
    iframeRef.current?.contentWindow?.postMessage(
      { type: drawMode ? 'startDraw' : 'cancelDraw' }, '*'
    );
  }, [drawMode]);

  /* ── 좌표 변경 시 카메라 이동 ── */
  useEffect(() => {
    if (readyRef.current) {
      iframeRef.current?.contentWindow?.postMessage({ type: 'flyTo', lat, lon }, '*');
    } else {
      pendingRef.current = { lat, lon };
    }
  }, [lat, lon]);

  useEffect(() => {
    if (readyRef.current) postOverlay();
  }, [postOverlay]);

  if (!KEY || KEY === 'your_vworld_key_here') {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 text-red-400 text-sm">
        VITE_VWORLD_KEY가 설정되지 않았습니다
      </div>
    );
  }

  return (
    <iframe
      ref={iframeRef}
      src={src}
      className="w-full h-full border-0"
      title="VWorld 3D"
    />
  );
}
