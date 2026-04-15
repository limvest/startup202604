# Processed Data Summary

## 1) 요약

- 기준 시점: `process_all_raw.py` 최신 실행 결과
- `processed_dataset_manifest.csv` 기준 데이터셋 수: **18개**
- 모든 데이터셋 상태: **processed (18/18)**
- raw 파일 처리 상태(`raw_processing_status.csv`):
  - `processed`: **24개**
  - `ignored`: **1개** (`기억장치관리전략-0408.ini`, 설정 파일)
  - `blocked`: **0개**

## 2) 처리 커버리지

현재 `data/raw`의 분석 대상 파일은 모두 처리 완료되었고, 비분석 파일(`.ini`) 1개만 의도적으로 제외되었다.

상세 상태표:
- `data/processed/raw_processing_status.csv`
- `data/processed/raw_processing_status.parquet`

## 3) 주요 산출물(핵심 테이블)

- `analysis_hourly` (통합 마스터): `87,672` rows
- `load_hourly_all_sources` (전국 시간별 수요 통합): `131,544` rows
- `smp_hourly`: `52,608` rows
- `weather_daily`: `18,992` rows
- `dr_hourly`: `17,544` rows
- `supply_daily`: `2,202` rows
- `renewable_utilization_monthly`: `2,828` rows
- `regional_energy_usage_2024`: `2,904` rows
- `smp_weighted_monthly`: `72` rows
- `kepco_api_catalog_20250630`: `23` rows

산출물 위치:
- CSV: `data/processed/*.csv`
- Parquet: `data/processed/*.parquet`

## 4) 전력시장통계 워크북 처리

연도별 워크북(`2022~2025`)의 시트를 개별 파일로 추출 완료.

- 경로: `data/processed/market_statistics_sheets`
- 시트 파일 수:
  - CSV: `126`
  - Parquet: `126`
- 시트 인덱스:
  - `data/processed/market_statistics_sheet_index.csv`
  - `data/processed/market_statistics_sheet_index.parquet`

## 5) Legacy Plus DR(.xls) 처리 결과

기존에 `blocked`였던 3개 `.xls`는 `xlrd` 기반으로 읽어 **메타데이터(컬럼정의서) 테이블**로 처리 완료.

- `plus_dr_economic_schema` (`4` rows)
- `plus_dr_resource_market_schema` (`0` rows, 원본 정의행 없음)
- `plus_dr_jeju_schema` (`13` rows)

## 6) 매니페스트(권장 참조 순서)

1. `data/processed/processed_dataset_manifest.csv`
2. `data/processed/raw_processing_status.csv`
3. `data/processed/market_statistics_sheet_index.csv`

## 7) 재실행 방법

```bash
python3 scripts/process_all_raw.py
```

위 명령을 실행하면 요약 매니페스트와 상태표가 최신으로 갱신된다.
