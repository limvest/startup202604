import type { ScanResult, SolarInstallation } from '../types';

function fmt_area(m2: number): string {
  if (m2 >= 10000) return `${(m2 / 10000).toFixed(1)}ha`;
  return `${m2.toLocaleString()}m²`;
}

function fmt_kw(kw: number): string {
  if (kw >= 1000) return `${(kw / 1000).toFixed(1)}MW`;
  return `${kw.toFixed(0)}kW`;
}

function fmt_revenue(krw: number): string {
  if (krw >= 100_000_000) return `${(krw / 100_000_000).toFixed(1)}억원/년`;
  if (krw >= 10_000) return `${(krw / 10_000).toFixed(0)}만원/년`;
  return `${krw.toLocaleString()}원/년`;
}

interface InstallationCardProps {
  inst: SolarInstallation;
  index: number;
  onClick: (lat: number, lon: number) => void;
}

function InstallationCard({ inst, index, onClick }: InstallationCardProps) {
  const confColor = inst.max_prob >= 0.6 ? '#4ade80' : inst.max_prob >= 0.3 ? '#facc15' : '#f87171';

  return (
    <div
      className="p-3 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-750 border border-gray-700 hover:border-yellow-400/40 transition-colors"
      onClick={() => onClick(inst.lat, inst.lon)}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-gray-400">#{index + 1}</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-700" style={{ color: confColor }}>
          신뢰도 {Math.round(inst.max_prob * 100)}%
        </span>
      </div>

      {inst.address && (
        <p className="text-xs text-gray-300 mb-2 leading-tight">{inst.address}</p>
      )}

      <div className="grid grid-cols-2 gap-1.5 text-xs">
        <div className="bg-gray-900 rounded p-1.5">
          <div className="text-gray-500 text-[10px]">면적</div>
          <div className="text-white font-medium">{fmt_area(inst.area_m2)}</div>
        </div>
        <div className="bg-gray-900 rounded p-1.5">
          <div className="text-gray-500 text-[10px]">용량</div>
          <div className="text-white font-medium">{fmt_kw(inst.capacity_kw)}</div>
        </div>
        <div className="bg-gray-900 rounded p-1.5 col-span-2">
          <div className="text-gray-500 text-[10px]">예상 연간 매출</div>
          <div className="text-yellow-400 font-bold">{fmt_revenue(inst.revenue_krw)}</div>
          <div className="text-gray-600 text-[10px] mt-0.5">{inst.annual_kwh.toLocaleString()} kWh 발전</div>
        </div>
      </div>
    </div>
  );
}

interface Props {
  result: ScanResult;
  onInstallationClick: (lat: number, lon: number) => void;
  onClear: () => void;
}

export default function ScanResultPanel({ result, onInstallationClick, onClear }: Props) {
  const { installations, tiles_scanned, tiles_positive, total_area_m2, total_capacity_kw, total_revenue_krw } = result;

  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-white">스캔 결과</h2>
          <p className="text-xs text-gray-500 mt-0.5">{tiles_scanned}타일 스캔 → {tiles_positive}개 감지</p>
        </div>
        <button onClick={onClear} className="text-gray-500 hover:text-gray-300 text-xs">✕ 초기화</button>
      </div>

      {/* 요약 */}
      <div className="p-4 border-b border-gray-700">
        <p className="text-xs text-gray-500 mb-2">총 {installations.length}개 단지 추정</p>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-gray-800 rounded-lg p-2">
            <div className="text-[10px] text-gray-500">총 면적</div>
            <div className="text-sm font-bold text-white">{fmt_area(total_area_m2)}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-2">
            <div className="text-[10px] text-gray-500">총 용량</div>
            <div className="text-sm font-bold text-white">{fmt_kw(total_capacity_kw)}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-2">
            <div className="text-[10px] text-gray-500">연간 매출</div>
            <div className="text-sm font-bold text-yellow-400">{fmt_revenue(total_revenue_krw)}</div>
          </div>
        </div>
        <p className="text-[10px] text-gray-600 mt-2">
          ※ SMP 120원 + REC 35원/kWh, 용량계수 13.7% 기준 추정치
        </p>
      </div>

      {/* 단지 목록 */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {installations.length === 0 ? (
          <p className="text-xs text-gray-500 text-center py-4">감지된 단지 없음</p>
        ) : (
          installations
            .slice()
            .sort((a, b) => b.revenue_krw - a.revenue_krw)
            .map((inst, i) => (
              <InstallationCard
                key={`${inst.lat}-${inst.lon}`}
                inst={inst}
                index={i}
                onClick={onInstallationClick}
              />
            ))
        )}
      </div>
    </div>
  );
}
