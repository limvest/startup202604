---
title: SolarFit API
emoji: ☀️
colorFrom: yellow
colorTo: orange
sdk: docker
app_port: 7860
pinned: false
---

# SolarFit

위성 이미지 기반 태양광 발전 입지 자동 분석 플랫폼.

---

## 무엇을 하는가

지도에서 지역을 선택하면 위성 타일을 자동으로 다운로드하고, AI 모델로 태양광 패널을 탐지하여 설치 현황·발전 용량·예상 매출을 즉시 산출한다.

---

## 핵심 기술

### 탐지 파이프라인

| 단계 | 내용 |
|------|------|
| 위성 타일 수집 | VWorld Satellite (한국) / Google Maps (글로벌 폴백) — ZOOM 19 |
| 타일 세분화 | 1장의 ZOOM 19 타일(256px)을 2×2로 분할 → 유효 해상도 ~37m×37m |
| AI 추론 | DeepSolar-3M (ViT-MAE-Large + LoRA 이진 분류기) — 추가 API 호출 없이 4× 정밀도 |
| Region Growing | 고신뢰도 시드 타일에서 BFS로 인접 확장 (ML 확률 게이트 + 시각 유사도) |
| 클러스터링 | 8방향 BFS로 인접 탐지 타일을 단지별로 그룹화 |

### 경제성 산출

```
용량(kW) = 면적(m²) × 80 W/m² ÷ 1000
연간 발전량(kWh) = 용량 × 1200 kWh/kWp
연간 매출(원) = 발전량 × 155 원/kWh  (SMP ~120 + REC ~35)
```

### 주소 조회

VWorld 역지오코딩 API → 탐지 단지 중심 좌표 → 지번 주소 자동 반환

---

## 스택

- **백엔드**: FastAPI + PyTorch (DeepSolar-3M) + Pillow + NumPy
- **프론트엔드**: React + TypeScript + Leaflet (2D) + VWorld WebGL (3D)
- **지도 API**: VWorld WMTS (위성), VWorld 역지오코딩

---

## 주요 API

| 엔드포인트 | 기능 |
|-----------|------|
| `GET /api/analyze` | 단일 좌표 입지 분석 (일사량, 고도, 경사, 규제) |
| `POST /api/scan` | bbox 내 전체 탐지 스캔 → 단지 리스트 반환 |
| `GET /api/search` | 주소·장소명 검색 |

---

## 현재 상태

- 단지 탐지 + 클러스터링 + 경제성 산출: **완료**
- 2D/3D 지도 타일 오버레이: **완료**
- 37m×37m 세밀 탐지 (SPLIT=2): **완료**
- 도메인 갭 (미국 학습 모델 → 한국 대규모 지상형): region growing으로 부분 완화
