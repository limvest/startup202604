interface Props {
  drawMode: boolean;
  scanning: boolean;
  result: { tiles_scanned: number; tiles_positive: number } | null;
  bbox: { lat_min: number; lat_max: number; lon_min: number; lon_max: number } | null;
  onToggleDraw: () => void;
  onScan: () => void;
  onClear: () => void;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default function ScanControl({ drawMode, scanning, result, bbox, onToggleDraw, onScan, onClear: _onClear }: Props) {
  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-2 bg-gray-900/90 backdrop-blur rounded-xl px-3 py-2 shadow-xl border border-gray-700">
      <button
        onClick={onToggleDraw}
        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
          drawMode ? 'bg-yellow-400 text-gray-900' : 'bg-gray-700 text-gray-200 hover:bg-gray-600'
        }`}
      >
        {drawMode ? '📐 선택 중...' : '📐 지역 선택'}
      </button>

      {bbox && !drawMode && (
        <button
          onClick={onScan}
          disabled={scanning}
          className="px-3 py-1.5 rounded-lg text-sm font-medium bg-yellow-400 text-gray-900 hover:bg-yellow-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {scanning ? '⚡ 스캔 중...' : '🔍 스캔'}
        </button>
      )}

      {result && (
        <span className="text-xs text-yellow-400 font-medium">
          {result.tiles_positive}개 감지 — 오른쪽 패널 확인
        </span>
      )}
    </div>
  );
}
