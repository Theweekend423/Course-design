import sys
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import DEFAULT_CONFIDENCE, MODEL_REGISTRY, MODELS_DIR
from backend.detector import detect_image, get_models_status, preload_models

FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(
    title="慧渔先知 Web",
    description="YOLO 水质智能检测网页端",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    preload_models()


@app.get("/api/health")
async def health():
    models = get_models_status()
    available = sum(1 for m in models if m["available"])
    return {
        "status": "ok",
        "app": "慧渔先知 Web",
        "models_dir": str(MODELS_DIR),
        "models_available": available,
        "models_total": len(models),
    }


@app.get("/api/models")
async def list_models():
    return {"models": get_models_status(), "default_confidence": DEFAULT_CONFIDENCE}


@app.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    confidence: float = Form(DEFAULT_CONFIDENCE),
    enabled_models: str = Form(""),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件（jpg/png/webp 等）")

    keys = [k.strip() for k in enabled_models.split(",") if k.strip()]
    valid_keys = set(MODEL_REGISTRY.keys())
    keys = [k for k in keys if k in valid_keys]

    if not keys:
        raise HTTPException(status_code=400, detail="请至少启用一个 YOLO 模型")

    confidence = max(0.1, min(0.99, confidence))
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="图片内容为空")

    try:
        result = detect_image(image_bytes, keys, confidence)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"检测失败: {exc}") from exc

    return result


@app.get("/")
async def index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="前端页面未找到")
    return FileResponse(index_path)


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
