"""DeepSolar-3M — ViT-MAE-Large + LoRA (Stanford ICLR 2025). Lazy-loaded singleton."""
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification, ViTImageProcessor

_HF_REPO = os.getenv("DEEPSOLAR_HF_REPO", "")
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "deepsolar3m", "detection_model")
_WEIGHTS = os.path.join(_MODEL_DIR, "pytorch_model.bin")

_model = None
_transform = None
_device = None


class _LoRA(nn.Module):
    """LoRA adapter matching the peft-style naming used in the DeepSolar-3M checkpoint.

    Checkpoint convention:
        lora_A  shape [out_features, rank]   — scaling matrix
        lora_B  shape [in_features,  rank]   — projection matrix
        base_module.*                         — original nn.Linear weights

    Forward: y = base_module(x) + x @ lora_B @ lora_A.T
    """

    def __init__(self, base: nn.Module, rank: int = 4):
        super().__init__()
        self.base_module = base
        out_f = base.weight.shape[0]   # [out, in]
        in_f  = base.weight.shape[1]
        # Use peft-matching names so load_state_dict works without key remapping.
        self.lora_A = nn.Parameter(torch.empty(out_f, rank))
        self.lora_B = nn.Parameter(torch.zeros(in_f, rank))
        nn.init.normal_(self.lora_A)

    def forward(self, x):
        # x: [..., in_features]
        # lora_B: [in_features, rank], lora_A: [out_features, rank]
        return self.base_module(x) + x @ self.lora_B @ self.lora_A.t()


def _download():
    if os.path.exists(_WEIGHTS):
        return
    if not _HF_REPO:
        raise RuntimeError(
            "DeepSolar-3M weights not found. Set DEEPSOLAR_HF_REPO to the Hugging Face repo "
            "that hosts them, or place the files under models/deepsolar3m/detection_model/."
        )
    from huggingface_hub import hf_hub_download
    os.makedirs(_MODEL_DIR, exist_ok=True)
    print("DeepSolar-3M weights downloading from HuggingFace Hub...")
    for fname in ["config.json", "preprocessor_config.json", "pytorch_model.bin", "training_args.bin"]:
        hf_hub_download(repo_id=_HF_REPO, filename=fname, local_dir=_MODEL_DIR)
    print("Download complete.")


def _load():
    global _model, _transform, _device
    if _model is not None:
        return
    _download()
    _device = (
        torch.device("mps") if torch.backends.mps.is_available()
        else torch.device("cuda") if torch.cuda.is_available()
        else torch.device("cpu")
    )
    proc = ViTImageProcessor.from_pretrained("facebook/vit-mae-large")
    m = ViTForImageClassification.from_pretrained(
        "facebook/vit-mae-large", num_labels=2, ignore_mismatched_sizes=True
    )
    enc = getattr(m.vit, 'encoder', m.vit)
    vit_layers = getattr(enc, 'layer', None) or getattr(enc, 'layers', None)
    if vit_layers is None:
        raise RuntimeError(f"Cannot locate ViT transformer layers. vit attrs: {[a for a in dir(m.vit) if not a.startswith('_')]}")
    for layer in vit_layers:
        layer.output.dense = _LoRA(layer.output.dense)
        layer.intermediate.dense = _LoRA(layer.intermediate.dense)
    state = torch.load(_WEIGHTS, map_location=_device)
    m.load_state_dict(state, strict=True)
    m.to(_device).eval()
    _model = m
    _transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=proc.image_mean, std=proc.image_std),
    ])


def infer_tile(img: Image.Image) -> float:
    """Return probability 0-1 that the tile contains solar panels."""
    _load()
    t = _transform(img.convert("RGB")).unsqueeze(0).to(_device)
    with torch.no_grad():
        prob = F.softmax(_model(t).logits, dim=1)[0][1].item()
    return float(prob)


def infer_batch(imgs: list, mini_batch: int = 8) -> list:
    """Mini-batch inference — avoids OOM and keeps CPU time predictable."""
    _load()
    results: list[float] = []
    for i in range(0, len(imgs), mini_batch):
        chunk = imgs[i : i + mini_batch]
        tensors = torch.stack([_transform(img.convert("RGB")) for img in chunk]).to(_device)
        with torch.no_grad():
            probs = F.softmax(_model(tensors).logits, dim=1)[:, 1].tolist()
        results.extend(float(p) for p in probs)
    return results
