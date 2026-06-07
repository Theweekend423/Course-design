import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 模型目录：优先使用 web 项目内 models/，其次尝试桌面端同级目录
_MODEL_CANDIDATES = [
    BASE_DIR / "models",
    BASE_DIR.parent / "models",          # Fish_system/models（桌面端）
    BASE_DIR.parent.parent / "models",
    BASE_DIR.parent / "FishAI" / "models",
]

MODELS_DIR = next((p for p in _MODEL_CANDIDATES if p.is_dir()), BASE_DIR / "models")

OUTPUT_DIR = BASE_DIR / "outputs" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIDENCE = float(os.getenv("FISHAI_CONFIDENCE", "0.5"))

MODEL_REGISTRY = {
    "dead_fish": {
        "file": "dead_fish.pt",
        "name": "死鱼检测",
        "icon": "fish",
        "emoji": "🐟",
        "desc": "识别水面死鱼数量",
        "color": "#ff6b6b",
        "default_enabled": True,
    },
    "pollution": {
        "file": "pollution.pt",
        "name": "污染识别",
        "icon": "factory",
        "emoji": "🏭",
        "desc": "检测水体污染类型",
        "color": "#ffa94d",
        "default_enabled": True,
    },
    "eutrophication": {
        "file": "eutrophication.pt",
        "name": "富营养化",
        "icon": "leaf",
        "emoji": "🌿",
        "desc": "评估水体富营养化程度",
        "color": "#51cf66",
        "default_enabled": True,
    },
    "water_quality": {
        "file": "water_quality.pt",
        "name": "水质评估",
        "icon": "droplet",
        "emoji": "💧",
        "desc": "综合水质等级分类",
        "color": "#339af0",
        "default_enabled": True,
    },
    "water_trash": {
        "file": "water_trash.pt",
        "name": "水面垃圾",
        "icon": "trash",
        "emoji": "🗑️",
        "desc": "检测水面漂浮垃圾",
        "color": "#845ef7",
        "default_enabled": True,
    },
}
