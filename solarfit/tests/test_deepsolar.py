import numpy as np
from PIL import Image


def test_infer_returns_float():
    from api.clients.deepsolar import infer_tile
    img = Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))
    prob = infer_tile(img)
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0


def test_infer_blank_is_valid():
    from api.clients.deepsolar import infer_tile
    img = Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))
    prob = infer_tile(img)
    assert 0.0 <= prob <= 1.0
