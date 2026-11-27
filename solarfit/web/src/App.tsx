import { useState } from 'react';
import type { AnalysisResult, ScanResult, ScanDetection, ScanTile } from './types';
import { analyzeLocation, scanRegion } from './api';
import SearchBar from './components/SearchBar';
import Map2D from './components/Map2D';
import Map3D from './components/Map3D';
import AnalysisPanel from './components/AnalysisPanel';
import ScanControl from './components/ScanControl';
import ScanResultPanel from './components/ScanResultPanel';
import AppHeader from './components/AppHeader';
import SolarDashboardPage from './components/SolarDashboardPage';
import SolarExplorePage from './components/SolarExplorePage';

type Bbox = { lat_min: number; lat_max: number; lon_min: number; lon_max: number };

type View = 'home' | 'dashboard' | 'explore';

function HomePage() {
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'2d' | '3d' | 'solar'>('2d');

  const [drawMode, setDrawMode] = useState(false);
  const [bbox, setBbox] = useState<Bbox | null>(null);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [scanDetections, setScanDetections] = useState<ScanDetection[]>([]);
  const [scanTiles, setScanTiles] = useState<ScanTile[]>([]);
  const [scanError, setScanError] = useState<string | null>(null);

  async function handleSelect(lat: number, lon: number) {
    setCoords({ lat, lon });
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeLocation(lat, lon);
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function handleToggleDraw() {
    setDrawMode(d => !d);
    setBbox(null);
  }

  async function handleBboxDrawn(b: Bbox) {
    setBbox(b);
    setDrawMode(false);
    setScanning(true);
    setScanError(null);
    setScanResult(null);
    setScanDetections([]);
    setScanTiles([]);
    try {
      const res = await scanRegion(b);
      setScanResult(res);
      setScanDetections(res.detections);
      setScanTiles(res.tiles);
    } catch (e) {
      setScanError((e as Error).message);
    } finally {
      setScanning(false);
    }
  }

  async function handleScan() {
    if (!bbox) return;
    setScanning(true);
    setScanError(null);
    try {
      const res = await scanRegion(bbox);
      setScanResult(res);
      setScanDetections(res.detections);
      setScanTiles(res.tiles);
    } catch (e) {
      setScanError((e as Error).message);
    } finally {
      setScanning(false);
    }
  }

  function handleClearScan() {
    setScanResult(null);
    setScanDetections([]);
    setScanTiles([]);
    setBbox(null);
  }

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-950 text-white overflow-hidden">

      {/* ── 지도 영역 ── */}
      <div className="relative flex-1 min-h-0">

        {/* 검색바 — 모바일: 우측에 모드버튼 공간 확보, 데스크톱: w-80 고정 */}
        {mode !== 'solar' && <SearchBar onSelect={handleSelect} />}

        {/* 모드 전환 버튼 */}
        <div className="absolute top-4 right-4 z-[1000] flex bg-gray-900 rounded-lg overflow-hidden shadow-lg">
          <button
            onClick={() => setMode('2d')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${mode === '2d' ? 'bg-yellow-400 text-gray-900' : 'text-gray-300 hover:text-white'}`}
          >2D</button>
          <button
            onClick={() => setMode('3d')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${mode === '3d' ? 'bg-yellow-400 text-gray-900' : 'text-gray-300 hover:text-white'}`}
          >3D</button>
          <button
            onClick={() => setMode('solar')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${mode === 'solar' ? 'bg-yellow-400 text-gray-900' : 'text-gray-300 hover:text-white'}`}
          >
            <span className="hidden md:inline">햇빛지도</span>
            <span className="md:hidden">☀</span>
          </button>
        </div>

        {/* 지도 컨텐츠 */}
        {mode === '2d' && (
          <Map2D
            onMapClick={handleSelect}
            selectedCoords={coords}
            drawMode={drawMode}
            onBboxDrawn={handleBboxDrawn}
            scanDetections={scanDetections}
            scanTiles={scanTiles}
            scanBbox={bbox}
            onDetectionClick={handleSelect}
          />
        )}
        {mode === '3d' && (
          coords
            ? <Map3D
                lat={coords.lat}
                lon={coords.lon}
                drawMode={drawMode}
                onBboxDrawn={handleBboxDrawn}
                scanTiles={scanTiles}
              />
            : <div className="flex items-center justify-center h-full text-gray-500 text-sm">먼저 위치를 선택하세요</div>
        )}
        {mode === 'solar' && (
          <div className="w-full h-full overflow-hidden relative">
            <iframe
              src="https://energyinfo.seoul.go.kr/solarmap#"
              className="solar-iframe"
              style={{ position: 'absolute', left: 0, width: '100%', border: 'none' }}
              title="서울 햇빛지도"
              allow="fullscreen"
            />
          </div>
        )}

        {/* 3D 미니 프리뷰 — 데스크톱 전용 */}
        {mode === '2d' && coords && (
          <div className="hidden md:block absolute top-16 right-4 z-[1000] w-72 h-48 rounded-xl overflow-hidden shadow-2xl border border-gray-700">
            <Map3D lat={coords.lat} lon={coords.lon} />
          </div>
        )}

        {mode !== 'solar' && (
          <ScanControl
            drawMode={drawMode}
            scanning={scanning}
            result={scanResult}
            bbox={bbox}
            onToggleDraw={handleToggleDraw}
            onScan={handleScan}
            onClear={handleClearScan}
          />
        )}
      </div>

      {/* ── 분석 패널 — solar 모드 모바일에서는 숨김, 데스크톱: 우측 w-96 ── */}
      <div className={`flex-shrink-0 md:h-auto md:w-96 bg-gray-900 overflow-y-auto border-t border-gray-800 md:border-t-0 md:border-l flex flex-col ${mode === 'solar' ? 'hidden md:flex' : 'h-60'}`}>
        {/* 모바일 드래그 핸들 */}
        <div className="flex justify-center pt-2 pb-1 md:hidden">
          <div className="w-10 h-1 rounded-full bg-gray-600" />
        </div>

        {scanResult ? (
          <ScanResultPanel
            result={scanResult}
            onInstallationClick={handleSelect}
            onClear={handleClearScan}
          />
        ) : (
          <>
            {loading && (
              <div className="p-8 text-center text-gray-400">
                <div className="animate-spin text-4xl mb-4">⚡</div>
                분석 중...
              </div>
            )}
            {scanning && (
              <div className="p-8 text-center text-gray-400">
                <div className="animate-spin text-4xl mb-4">🛰️</div>
                위성 타일 스캔 중...
              </div>
            )}
            {error && <div className="p-6 text-red-400 text-sm">오류: {error}</div>}
            {scanError && <div className="p-6 text-red-400 text-sm">스캔 오류: {scanError}</div>}
            {result && !loading && <AnalysisPanel result={result} />}
            {!result && !loading && !scanning && !error && (
              <div className="p-6 text-center text-gray-500">
                <div className="text-4xl mb-3">📍</div>
                <div className="text-sm">지도를 클릭하거나 주소를 검색해 입지를 분석하세요</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<View>('home');

  return (
    <div className="flex h-screen flex-col bg-gray-950">
      <AppHeader activeView={view} onChange={setView} />
      {view === 'home' && <HomePage />}
      {view === 'dashboard' && <SolarDashboardPage />}
      {view === 'explore' && <SolarExplorePage />}
    </div>
  );
}
