import type { AnalysisResult, SearchResult, ScanResult } from './types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

export async function analyzeLocation(lat: number, lon: number): Promise<AnalysisResult> {
  const res = await fetch(`${BASE}/analyze?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`분석 실패: ${res.status}`);
  return res.json() as Promise<AnalysisResult>;
}

export async function searchAddress(query: string): Promise<SearchResult[]> {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`검색 실패: ${res.status}`);
  const data = await res.json() as { results: SearchResult[] };
  return data.results;
}

export interface ScanRequest {
  lat_min: number;
  lat_max: number;
  lon_min: number;
  lon_max: number;
  threshold?: number;
}

export async function scanRegion(req: ScanRequest): Promise<ScanResult> {
  const res = await fetch(`${BASE}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`스캔 실패: ${res.status}`);
  return res.json();
}
