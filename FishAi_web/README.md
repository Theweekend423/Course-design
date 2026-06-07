# 慧渔先知 · Web 拓展端

桌面端「慧渔先知」的轻量网页备用端，支持 5 个 YOLO 模型的图片综合检测。

## 功能

- 图片上传 / 拖拽检测
- 5 模型独立开关：死鱼、污染、富营养化、水质、水面垃圾
- 置信度调节
- 标注结果图展示与本地保存
- 蓝紫渐变呼吸流动背景 UI

## 目录结构

```
FishAi_web/
├── backend/          # FastAPI 后端
├── frontend/         # 网页前端
├── models/           # 放置 .pt 模型（见下方）
├── outputs/images/   # 检测结果自动保存
├── run.py            # 启动入口
└── requirements.txt
```

## 模型文件

将以下 5 个模型放入 `models/` 目录（或桌面端项目的 `models/` 目录，程序会自动查找）：

| 文件名 | 说明 |
|--------|------|
| `dead_fish.pt` | 死鱼检测 |
| `pollution.pt` | 污染识别 |
| `eutrophication.pt` | 富营养化 |
| `water_quality.pt` | 水质评估 |
| `water_trash.pt` | 水面垃圾 |

## 快速启动

```bash
cd FishAi_web
pip install -r requirements.txt
python run.py
```

浏览器访问：**http://localhost:8080**

## 说明

- 本项目为独立网页端，**不会修改**原有桌面端代码
- 检测逻辑参考桌面端 `ResultParser` 与多模型串联推理方式
- 网页端暂不支持视频/摄像头（可作为后续扩展）
