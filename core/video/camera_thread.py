import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal

from core.detector.result_parser import ResultParser
from core.data.data_manager import DataManager


class CameraThread(QThread):
    changePixmap = pyqtSignal(object)
    changeText = pyqtSignal(str)

    def __init__(self, models, confidence, camera_id=0, frame_skip=3, resize_width=320):
        super().__init__()
        self.models = models
        self.confidence = confidence
        self.camera_id = camera_id
        self.frame_skip = max(1, frame_skip)       # 每隔 N-1 帧检测一次
        self.resize_width = resize_width           # 检测时缩放宽度（像素）
        self.is_running = True
        self.frame_counter = 0
        self.last_display_frame = None
        self.last_result_text = "摄像头已启动，等待检测..."
        self.fps_counter = 0
        self.last_fps_time = time.time()

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            self.changeText.emit("❌ 无法打开摄像头，请检查设备是否可用")
            return

        # 减少 OpenCV 缓冲区延迟
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break

            self.frame_counter += 1
            do_detect = (self.frame_counter % self.frame_skip == 0)

            if do_detect:
                # 1. 缩小图像，加速推理
                h, w = frame.shape[:2]
                new_w = self.resize_width
                new_h = int(h * (new_w / w))
                small_frame = cv2.resize(frame, (new_w, new_h))

                result_lines = ["🔍 ===== 实时检测结果 =====", ""]

                # 2. 依次执行每个模型
                for model_name, model in self.models.items():
                    results = model.predict(
                        source=small_frame,
                        conf=self.confidence,
                        verbose=False
                    )
                    result = results[0]
                    info = ResultParser.parse(result)

                    if info["type"] == "detect":
                        result_lines.append(f"📌 {model_name}: {info['count']}个目标")
                        if model_name == "dead_fish":
                            DataManager.latest_dead_fish = info["count"]
                    elif info["type"] == "classify":
                        result_lines.append(f"🧠 {model_name}: {info['label']} ({info['confidence']:.2%})")

                    small_frame = result.plot()   # 绘制标注

                self.last_result_text = "\n".join(result_lines)

                # 3. 将标注后的小图放大回原始尺寸（用于显示）
                display_frame = cv2.resize(small_frame, (w, h))
                self.last_display_frame = display_frame

                # 可选：计算检测帧率（仅调试）
                self.fps_counter += 1
                now = time.time()
                if now - self.last_fps_time >= 1.0:
                    # 可以打印到控制台，也可以添加到结果文本中
                    # print(f"检测FPS: {self.fps_counter}")
                    self.fps_counter = 0
                    self.last_fps_time = now
            else:
                # 非检测帧：直接复用上一帧的检测结果（不重新推理）
                if self.last_display_frame is not None:
                    display_frame = self.last_display_frame
                else:
                    display_frame = frame

            self.changePixmap.emit(display_frame)
            self.changeText.emit(self.last_result_text)

        cap.release()

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()   # 等待线程完全结束