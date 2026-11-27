from api.scanner import bbox_to_tiles, tile_center_latlon
import math


def test_bbox_to_tiles_nonempty():
    tiles = bbox_to_tiles(35.05, 35.06, 126.22, 126.23, zoom=18)
    assert len(tiles) > 0
    assert all(isinstance(t, tuple) and len(t) == 2 for t in tiles)


def test_bbox_to_tiles_respects_max():
    from api.scanner import MAX_TILES
    tiles = bbox_to_tiles(34.0, 35.0, 126.0, 127.0, zoom=19)
    assert len(tiles) <= MAX_TILES


def test_tile_center_roundtrip():
    lat, lon, zoom = 35.0558, 126.2292, 19
    n = 2 ** zoom
    x = int((lon + 180) / 360 * n)
    y = int(
        (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi)
        / 2 * n
    )
    clat, clon = tile_center_latlon(x, y, zoom)
    assert abs(clat - lat) < 0.01
    assert abs(clon - lon) < 0.01
