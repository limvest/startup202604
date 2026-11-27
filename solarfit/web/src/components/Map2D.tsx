import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { ScanTile } from '../types';

type Bbox = { lat_min: number; lat_max: number; lon_min: number; lon_max: number };

interface Props {
  onMapClick: (lat: number, lon: number) => void;
  selectedCoords: { lat: number; lon: number } | null;
  drawMode: boolean;
  onBboxDrawn: (bbox: Bbox) => void;
  scanDetections: { lat: number; lon: number; prob: number }[];
  scanTiles?: ScanTile[];
  scanBbox?: Bbox | null;
  onDetectionClick: (lat: number, lon: number) => void;
}

export default function Map2D({ onMapClick, selectedCoords, drawMode, onBboxDrawn, scanDetections, scanTiles = [], scanBbox, onDetectionClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const detectionLayerRef = useRef<L.Marker[]>([]);
  const firstClickRef = useRef<L.LatLng | null>(null);
  const rectPreviewRef = useRef<L.Rectangle | null>(null);
  const tileLayerRef = useRef<L.Rectangle[]>([]);

  // Refs keep event handlers up-to-date without re-registering them
  const drawModeRef = useRef(drawMode);
  const onBboxDrawnRef = useRef(onBboxDrawn);
  const onMapClickRef = useRef(onMapClick);
  const onDetectionClickRef = useRef(onDetectionClick);
  useEffect(() => { drawModeRef.current = drawMode; }, [drawMode]);
  useEffect(() => { onBboxDrawnRef.current = onBboxDrawn; }, [onBboxDrawn]);
  useEffect(() => { onMapClickRef.current = onMapClick; }, [onMapClick]);
  useEffect(() => { onDetectionClickRef.current = onDetectionClick; }, [onDetectionClick]);

  // One-time map init
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current).setView([34.57, 126.60], 11);

    const vworldKey = import.meta.env.VITE_VWORLD_KEY;
    if (vworldKey && vworldKey !== 'your_vworld_key_here') {
      L.tileLayer(
        `https://api.vworld.kr/req/wmts/1.0.0/${vworldKey}/Base/{z}/{y}/{x}.png`,
        { attribution: '© VWorld', maxZoom: 19 }
      ).addTo(map);
    } else {
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);
    }

    // click-click 방식: 첫 클릭 = 시작점, 두 번째 클릭 = 완성
    map.on('click', (e: L.LeafletMouseEvent) => {
      if (!drawModeRef.current) {
        onMapClickRef.current(e.latlng.lat, e.latlng.lng);
        return;
      }
      if (!firstClickRef.current) {
        firstClickRef.current = e.latlng;
      } else {
        if (rectPreviewRef.current) { map.removeLayer(rectPreviewRef.current); rectPreviewRef.current = null; }
        const bounds = L.latLngBounds(firstClickRef.current, e.latlng);
        firstClickRef.current = null;
        onBboxDrawnRef.current({
          lat_min: bounds.getSouth(), lat_max: bounds.getNorth(),
          lon_min: bounds.getWest(), lon_max: bounds.getEast(),
        });
      }
    });

    map.on('mousemove', (e: L.LeafletMouseEvent) => {
      if (!drawModeRef.current || !firstClickRef.current) return;
      if (rectPreviewRef.current) map.removeLayer(rectPreviewRef.current);
      rectPreviewRef.current = L.rectangle(L.latLngBounds(firstClickRef.current, e.latlng), {
        color: '#facc15', weight: 2, fillOpacity: 0.1, dashArray: '4',
      }).addTo(map);
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // drawMode 해제 시 상태 초기화
  useEffect(() => {
    if (!mapRef.current) return;
    mapRef.current.getContainer().style.cursor = drawMode ? 'crosshair' : '';
    if (!drawMode) {
      firstClickRef.current = null;
      if (rectPreviewRef.current) {
        mapRef.current.removeLayer(rectPreviewRef.current);
        rectPreviewRef.current = null;
      }
    }
  }, [drawMode]);

  // Selected-point marker
  useEffect(() => {
    if (!mapRef.current || !selectedCoords) return;
    if (markerRef.current) markerRef.current.remove();
    markerRef.current = L.marker([selectedCoords.lat, selectedCoords.lon], {
      icon: L.divIcon({
        className: '',
        html: '<div style="background:#FBBF24;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>',
        iconAnchor: [8, 8],
      }),
    }).addTo(mapRef.current);
  }, [selectedCoords]);

  // Tile grid overlay + bbox에 자동 fitBounds
  useEffect(() => {
    if (!mapRef.current) return;
    tileLayerRef.current.forEach(r => mapRef.current!.removeLayer(r));
    tileLayerRef.current = [];

    if (scanTiles.length === 0) return;

    // 탐지 타일 → 그쪽으로 줌. 없으면 전체 bbox
    const detected = scanTiles.filter(t => t.detected);
    const zoomTarget = detected.length > 0 ? detected : scanTiles;
    const fitLats = zoomTarget.flatMap(t => [t.lat_min, t.lat_max]);
    const fitLons = zoomTarget.flatMap(t => [t.lon_min, t.lon_max]);
    mapRef.current.fitBounds(
      [[Math.min(...fitLats), Math.min(...fitLons)], [Math.max(...fitLats), Math.max(...fitLons)]],
      { padding: [60, 60], maxZoom: 17, animate: true },
    );

    scanTiles.forEach(tile => {
      const bounds = L.latLngBounds(
        [tile.lat_min, tile.lon_min],
        [tile.lat_max, tile.lon_max],
      );
      if (tile.detected) {
        const fillOpacity = 0.45 + tile.prob * 0.45;
        const rect = L.rectangle(bounds, {
          color: '#fbbf24',
          weight: 2,
          fillColor: '#fbbf24',
          fillOpacity,
        }).addTo(mapRef.current!);
        tileLayerRef.current.push(rect);
      } else {
        const rect = L.rectangle(bounds, {
          color: '#ffffff',
          weight: 1,
          fillColor: '#ffffff',
          fillOpacity: 0.08,
          dashArray: '3 3',
        }).addTo(mapRef.current!);
        tileLayerRef.current.push(rect);
      }
    });
  }, [scanTiles, scanBbox]);

  // Detection markers
  useEffect(() => {
    if (!mapRef.current) return;
    detectionLayerRef.current.forEach(m => mapRef.current!.removeLayer(m));
    detectionLayerRef.current = [];
    scanDetections.forEach(d => {
      const hue = Math.round(d.prob * 120);
      const icon = L.divIcon({
        className: '',
        html: `<div style="width:12px;height:12px;border-radius:50%;background:hsl(${hue},90%,50%);border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5)"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6],
      });
      const m = L.marker([d.lat, d.lon], { icon })
        .addTo(mapRef.current!)
        .on('click', () => onDetectionClickRef.current(d.lat, d.lon));
      detectionLayerRef.current.push(m);
    });
  }, [scanDetections]);

  return <div ref={containerRef} className="w-full h-full" />;
}
