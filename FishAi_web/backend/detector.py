import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import cv2
import numpy as np
from PIL import Image

from backend.config import DEFAULT_CONFIDENCE, MODEL_REGISTRY, MODELS_DIR, OUTPUT_DIR
from backend.result_parser import ResultParser

_models_cache: dict = {}


def _model_path(key: str) -> Path:
    return MODELS_DIR / MODEL_REGISTRY[key]["file"]


def get_models_status() -> List[Dict]:
    status = []
    for key, meta in MODEL_REGISTRY.items():
        path = _model_path(key)
        status.append({
            "id": key,
            "name": meta["name"],
            "icon": meta["icon"],
            "emoji": meta["emoji"],
            "desc": meta["desc"],
            "color": meta["color"],
            "default_enabled": meta["default_enabled"],
            "available": path.is_file(),
            "path": str(path),
        })
    return status


def _load_model(key: str):
    if key not in _models_cache:
        from ultralytics import YOLO

        path = _model_path(key)
        if not path.is_file():
            raise FileNotFoundError(f"模型文件不存在: {path}")
        _models_cache[key] = YOLO(str(path))
    return _models_cache[key]


def preload_models(keys: Optional[List[str]] = None):
    keys = keys or list(MODEL_REGISTRY.keys())
    loaded, failed = [], []
    for key in keys:
        try:
            _load_model(key)
            loaded.append(key)
        except Exception as exc:
            failed.append({"id": key, "error": str(exc)})
    return loaded, failed


def _decode_image(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return image


def _encode_image_b64(image: np.ndarray) -> str:
    _, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return base64.b64encode(buf).decode("utf-8")


def detect_image(
    image_bytes: bytes,
    enabled_models: List[str],
    confidence: float = DEFAULT_CONFIDENCE,
) -> dict:
    image = _decode_image(image_bytes)
    results_detail = []
    summary_lines = []

    for key in enabled_models:
        if key not in MODEL_REGISTRY:
            continue
        meta = MODEL_REGISTRY[key]
        try:
            model = _load_model(key)
            pred = model.predict(source=image, conf=confidence, verbose=False)
            result = pred[0]
            info = ResultParser.parse(result)
            image = result.plot()

            if info["type"] == "detect":
                text = f"{meta['emoji']} {meta['name']}: {info['count']} 个目标"
                summary_lines.append(text)
                results_detail.append({
                    "model_id": key,
                    "model_name": meta["name"],
                    "emoji": meta["emoji"],
                    "type": "detect",
                    "count": info["count"],
                    "label": None,
                    "confidence": None,
                    "text": text,
                })
            elif info["type"] == "classify":
                conf_pct = f"{info['confidence']:.1%}"
                text = f"{meta['emoji']} {meta['name']}: {info['label']} ({conf_pct})"
                summary_lines.append(text)
                results_detail.append({
                    "model_id": key,
                    "model_name": meta["name"],
                    "emoji": meta["emoji"],
                    "type": "classify",
                    "count": 1,
                    "label": info["label"],
                    "confidence": info["confidence"],
                    "text": text,
                })
            else:
                text = f"{meta['emoji']} {meta['name']}: 未识别到有效结果"
                summary_lines.append(text)
                results_detail.append({
                    "model_id": key,
                    "model_name": meta["name"],
                    "emoji": meta["emoji"],
                    "type": "unknown",
                    "count": 0,
                    "label": None,
                    "confidence": None,
                    "text": text,
                })
        except FileNotFoundError as exc:
            text = f"⚠️ {meta['name']}: 模型文件缺失"
            summary_lines.append(text)
            results_detail.append({
                "model_id": key,
                "model_name": meta["name"],
                "emoji": meta["emoji"],
                "type": "error",
                "error": str(exc),
                "text": text,
            })
        except Exception as exc:
            text = f"❌ {meta['name']}: {exc}"
            summary_lines.append(text)
            results_detail.append({
                "model_id": key,
                "model_name": meta["name"],
                "emoji": meta["emoji"],
                "type": "error",
                "error": str(exc),
                "text": text,
            })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = OUTPUT_DIR / f"detect_{timestamp}.jpg"
    cv2.imwrite(str(save_path), image)

    return {
        "summary": "\n".join(summary_lines) if summary_lines else "未执行任何检测",
        "results": results_detail,
        "image_base64": _encode_image_b64(image),
        "saved_path": str(save_path),
        "model_count": len(enabled_models),
    }
