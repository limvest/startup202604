"""Tile-grid scanner: downloads satellite tiles, runs DeepSolar-3M, clusters installations.

Tile source priority:
  1. VWorld Satellite (VWORLD_API_KEY set) — Korean gov imagery, fresher for Korea
  2. Google Maps satellite — global fallback

Revenue estimates use 2025 Korean market rates:
  - Capacity: 80 W/m² effective (panels + row spacing)
  - Generation: 1200 kWh/kWp/year (Korea avg, CF ~13.7%)
  - Price: SMP ~120 + REC ~35 = 155 KRW/kWh
"""
import math
import os
import time
import numpy as np
import requests
from collections import deque
from PIL import Image
from io import BytesIO
from api.models import ScanDetection, ScanTile, SolarInstallation, ScanResult
from api.config import VWORLD_API_KEY, VWORLD_GEOCODER_URL

ZOOM = 19          # 타일 다운로드 줌
SPLIT = 2          # 각 타일을 SPLIT×SPLIT으로 세분화 (다운로드 추가 없음)
EFFECTIVE_ZOOM = ZOOM + 1   # log2(SPLIT)=1 → 유효 줌 (37m×37m 해상도)
# Configurable via env so HF Space can use a smaller cap (CPU-only, slower)
MAX_BASE_TILES = int(os.environ.get("MAX_BASE_TILES", "150"))
_HEADERS = {"User-Agent": "Mozilla/5.0"}

# Economics constants
_W_PER_M2 = 80          # 실효 설치 밀도 (W/m²)
_KWH_PER_KWP = 1200     # 연간 발전량 (kWh/kWp)
_KRW_PER_KWH = 155      # SMP + REC 단가 (원/kWh)


def _ll_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    n = 2 ** zoom
    x = int((lon + 180) / 360 * n)
    y = int(
        (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi)
        / 2 * n
    )
    return x, y


def tile_center_latlon(x: int, y: int, zoom: int) -> tuple[float, float]:
    n = 2 ** zoom
    lon = (x + 0.5) / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 0.5) / n))))
    return lat, lon


def tile_bounds(x: int, y: int, zoom: int) -> tuple[float, float, float, float]:
    """타일의 위경도 경계 반환: (lat_min, lat_max, lon_min, lon_max)."""
    n = 2 ** zoom
    lon_min = x / n * 360 - 180
    lon_max = (x + 1) / n * 360 - 180
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lat_min, lat_max, lon_min, lon_max


def tile_area_m2(lat: float, zoom: int) -> float:
    """Mercator 타일 실제 면적 (위도에 따라 경도 방향 보정)."""
    tile_m = 40075016.686 / (2 ** zoom)   # 적도 기준 타일 너비
    width = tile_m * math.cos(math.radians(lat))
    return width * tile_m                  # height는 위도 무관


def bbox_to_tiles(
    lat_min: float, lat_max: float, lon_min: float, lon_max: float, zoom: int = ZOOM
) -> list[tuple[int, int]]:
    x0, y1 = _ll_to_tile(lat_min, lon_min, zoom)
    x1, y0 = _ll_to_tile(lat_max, lon_max, zoom)
    tiles = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    if len(tiles) > MAX_BASE_TILES:
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        tiles.sort(key=lambda t: abs(t[0] - mx) + abs(t[1] - my))
        tiles = tiles[:MAX_BASE_TILES]
    return tiles


def _get_tile(x: int, y: int) -> Image.Image | None:
    urls = []
    if VWORLD_API_KEY:
        urls.append(
            f"https://api.vworld.kr/req/wmts/1.0.0/{VWORLD_API_KEY}/Satellite/{ZOOM}/{y}/{x}.jpeg"
        )
    urls.append(f"https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={ZOOM}")
    for url in urls:
        try:
            r = requests.get(url, headers=_HEADERS, timeout=8)
            if r.status_code == 200 and len(r.content) > 1000:
                return Image.open(BytesIO(r.content)).convert("RGB")
        except Exception:
            continue
    return None


def _cluster_tiles(
    positives: list[tuple[int, int, float]]
) -> list[list[tuple[int, int, float]]]:
    """8-방향 BFS로 인접 타일을 단지별로 묶는다."""
    coord_map: dict[tuple[int, int], float] = {(x, y): p for x, y, p in positives}
    visited: set[tuple[int, int]] = set()
    clusters: list[list[tuple[int, int, float]]] = []

    for x, y, _ in positives:
        if (x, y) in visited:
            continue
        cluster: list[tuple[int, int, float]] = []
        queue: deque[tuple[int, int]] = deque([(x, y)])
        visited.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            cluster.append((cx, cy, coord_map[(cx, cy)]))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nb = (cx + dx, cy + dy)
                    if nb in coord_map and nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
        clusters.append(cluster)

    return clusters


def _reverse_geocode(lat: float, lon: float) -> str | None:
    """VWorld 역지오코딩 → 지번 주소."""
    if not VWORLD_API_KEY:
        return None
    try:
        r = requests.get(
            VWORLD_GEOCODER_URL,
            params={
                "service": "address",
                "request": "getAddress",
                "version": "2.0",
                "crs": "epsg:4326",
                "point": f"{lon},{lat}",
                "type": "parcel",
                "key": VWORLD_API_KEY,
                "format": "json",
            },
            timeout=6,
        )
        data = r.json()
        results = data.get("response", {}).get("result", [])
        if results:
            return results[0].get("text")
    except Exception:
        pass
    return None


def _make_installation(
    cluster: list[tuple[int, int, float]]
) -> SolarInstallation:
    """타일 클러스터 → SolarInstallation 계산."""
    lats = [tile_center_latlon(x, y, ZOOM)[0] for x, y, _ in cluster]
    lons = [tile_center_latlon(x, y, ZOOM)[1] for x, y, _ in cluster]
    probs = [p for _, _, p in cluster]

    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # 면적: 각 타일 실면적 합산
    area = sum(tile_area_m2(lat, ZOOM) for lat in lats)

    capacity_kw = area * _W_PER_M2 / 1000
    annual_kwh = capacity_kw * _KWH_PER_KWP
    revenue_krw = int(annual_kwh * _KRW_PER_KWH)

    address = _reverse_geocode(center_lat, center_lon)

    return SolarInstallation(
        lat=round(center_lat, 6),
        lon=round(center_lon, 6),
        tile_count=len(cluster),
        area_m2=round(area),
        capacity_kw=round(capacity_kw, 1),
        annual_kwh=round(annual_kwh),
        revenue_krw=revenue_krw,
        max_prob=round(max(probs), 3),
        address=address,
    )


def _img_features(img: Image.Image) -> dict:
    arr = np.array(img, dtype=np.float32)
    return {
        'brightness': float(arr.mean()),
        'variance':   float(arr.var()),
        'mean_r':     float(arr[:, :, 0].mean()),
        'mean_g':     float(arr[:, :, 1].mean()),
        'mean_b':     float(arr[:, :, 2].mean()),
    }


def _is_solar_like(feat: dict, seed_feats: list[dict]) -> bool:
    """씨앗 타일과 시각적으로 유사한지.

    절대 색상 비율 대신 씨앗 상대 비교 사용.
    (위성 이미지 조건에 따라 패널 색이 달라질 수 있음)
    """
    # 너무 밝으면 도로·건물
    if feat['brightness'] > 125:
        return False
    # 분산이 크면 복잡한 지형·나무
    if feat['variance'] > 2500:
        return False
    # 씨앗 대비 밝기·색상 유사도
    for sf in seed_feats:
        if abs(feat['brightness'] - sf['brightness']) > 40:
            continue
        if abs(feat['mean_r'] - sf['mean_r']) > 30:
            continue
        if abs(feat['mean_g'] - sf['mean_g']) > 30:
            continue
        if abs(feat['mean_b'] - sf['mean_b']) > 30:
            continue
        return True
    return False


# 태양광 내부 타일 최소 확률 (0.004~0.02) vs 농지·일반지형 (~0.001~0.003)
_GROW_MIN_PROB = 0.004


def _region_grow(
    tile_data: dict[tuple[int, int], tuple[float, dict]],
    seed_threshold: float,
) -> set[tuple[int, int]]:
    """고신뢰도 씨앗 → ML 확률 게이트 + 시각 유사도로 BFS 확장."""
    seeds = {(x, y) for (x, y), (p, _) in tile_data.items() if p >= seed_threshold}
    if not seeds:
        return seeds

    seed_feats = [tile_data[xy][1] for xy in seeds]
    detected: set[tuple[int, int]] = set(seeds)
    queue: deque[tuple[int, int]] = deque(seeds)

    while queue:
        cx, cy = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nb = (cx + dx, cy + dy)
                if nb in detected or nb not in tile_data:
                    continue
                nb_prob, nb_feat = tile_data[nb]
                # ML 확률 최소값 + 시각 유사도 동시 충족
                if nb_prob >= _GROW_MIN_PROB and _is_solar_like(nb_feat, seed_feats):
                    detected.add(nb)
                    queue.append(nb)

    return detected


def scan_region(
    lat_min: float, lat_max: float, lon_min: float, lon_max: float, threshold: float = 0.12
) -> ScanResult:
    """
    1. ZOOM=19 타일 다운로드 (MAX_BASE_TILES개)
    2. 각 타일을 SPLIT×SPLIT으로 세분화 → 유효 해상도 EFFECTIVE_ZOOM
    3. 세분 타일별 DeepSolar 추론
    4. region growing (씨앗 + ML 확률 게이트 + 시각 유사도)
    5. 클러스터링 → 단지 분석
    """
    from api.clients.deepsolar import infer_batch

    base_coords = bbox_to_tiles(lat_min, lat_max, lon_min, lon_max, zoom=ZOOM)

    # 가상 타일 좌표: (vx, vy) at EFFECTIVE_ZOOM
    # base tile (x,y) → sub-tiles (x*SPLIT+j, y*SPLIT+i) for i,j in [0, SPLIT)
    tile_data: dict[tuple[int, int], tuple[float, dict]] = {}

    # Collect all sub-tile images, then infer in one batch for speed
    batch_imgs: list = []
    batch_keys: list[tuple[int, int]] = []
    batch_feats: list[dict] = []

    for bx, by in base_coords:
        img = _get_tile(bx, by)
        if img is None:
            continue
        iw, ih = img.size
        sw, sh = iw // SPLIT, ih // SPLIT

        for si in range(SPLIT):     # row: 0=top
            for sj in range(SPLIT): # col: 0=left
                crop = img.crop((sj * sw, si * sh, (sj + 1) * sw, (si + 1) * sh))
                crop_256 = crop.resize((256, 256), Image.LANCZOS)
                vx = bx * SPLIT + sj
                vy = by * SPLIT + si
                batch_imgs.append(crop_256)
                batch_keys.append((vx, vy))
                batch_feats.append(_img_features(crop_256))

    # 시간 예산 50s: 초과 시 남은 타일은 prob=0으로 처리 (타임아웃 방지)
    _BUDGET_S = 50.0
    _t0 = time.monotonic()
    if batch_imgs:
        probs: list[float] = []
        mini = 8
        for i in range(0, len(batch_imgs), mini):
            if time.monotonic() - _t0 > _BUDGET_S:
                probs.extend([0.0] * (len(batch_imgs) - len(probs)))
                break
            probs.extend(infer_batch(batch_imgs[i : i + mini]))
        for (vx, vy), prob, feat in zip(batch_keys, probs, batch_feats):
            tile_data[(vx, vy)] = (prob, feat)

    # region growing (EFFECTIVE_ZOOM 가상 좌표계)
    detected_xy = _region_grow(tile_data, seed_threshold=threshold)

    # 결과 조립
    positives: list[tuple[int, int, float]] = []
    scan_tiles: list[ScanTile] = []

    for (vx, vy), (prob, _) in tile_data.items():
        detected = (vx, vy) in detected_xy
        bmin_lat, bmax_lat, bmin_lon, bmax_lon = tile_bounds(vx, vy, EFFECTIVE_ZOOM)
        scan_tiles.append(ScanTile(
            lat_min=round(bmin_lat, 7),
            lat_max=round(bmax_lat, 7),
            lon_min=round(bmin_lon, 7),
            lon_max=round(bmax_lon, 7),
            prob=round(prob, 3),
            detected=detected,
        ))
        if detected:
            positives.append((vx, vy, prob))

    detections = [
        ScanDetection(
            lat=tile_center_latlon(vx, vy, EFFECTIVE_ZOOM)[0],
            lon=tile_center_latlon(vx, vy, EFFECTIVE_ZOOM)[1],
            prob=round(p, 3),
        )
        for vx, vy, p in positives
    ]

    clusters = _cluster_tiles(positives)
    installations = [_make_installation(c) for c in clusters]

    total_area = sum(inst.area_m2 for inst in installations)
    total_cap = sum(inst.capacity_kw for inst in installations)
    total_rev = sum(inst.revenue_krw for inst in installations)

    return ScanResult(
        detections=detections,
        installations=installations,
        tiles=scan_tiles,
        tiles_scanned=len(tile_data),
        tiles_positive=len(positives),
        total_area_m2=round(total_area),
        total_capacity_kw=round(total_cap, 1),
        total_revenue_krw=total_rev,
    )
