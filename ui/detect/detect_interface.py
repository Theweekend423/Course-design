import os
import cv2
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QLineEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont

from qfluentwidgets import CardWidget
from ultralytics import YOLO

from core.video.video_thread import VideoDetectThread
from core.video.camera_thread import CameraThread          # 新增导入
from core.evaluator.ai_thread import AIThread
from core.settings.settings_manager import SettingsManager
from core.detector.result_parser import ResultParser
from core.data.data_manager import DataManager


class DetectInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detect_interface")
        self.settingsManager = SettingsManager()
        self.models = {}
        self.videoThread = None
        self.cameraThread = None           # 摄像头线程
        self.loadModels()
        self.initUI()

    # =================================================
    # 加载模型（功能不变）
    # =================================================
    def loadModels(self):
        settings = self.settingsManager.loadSettings()
        self.models = {}
        if settings["enable_dead_fish"]:
            self.models["dead_fish"] = YOLO("models/dead_fish.pt")
        if settings["enable_pollution"]:
            self.models["pollution"] = YOLO("models/pollution.pt")
        if settings["enable_eutrophication"]:
            self.models["eutrophication"] = YOLO("models/eutrophication.pt")
        if settings["enable_water_quality"]:
            self.models["water_quality"] = YOLO("models/water_quality.pt")
        if settings["enable_water_trash"]:
            self.models["water_trash"] = YOLO("models/water_trash.pt")

    # =================================================
    # UI 构建（添加摄像头按钮）
    # =================================================
    def initUI(self):
        mainLayout = QHBoxLayout(self)
        mainLayout.setSpacing(20)

        # ---------- 左侧卡片（图像显示区域） ----------
        leftCard = CardWidget()
        leftLayout = QVBoxLayout(leftCard)
        leftLayout.setSpacing(15)

        self.imageLabel = QLabel("🖼️ 等待上传图片或视频")
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setMinimumSize(500, 350)
        self.imageLabel.setMaximumHeight(600)
        self.imageLabel.setScaledContents(False)
        self.imageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.imageLabel.setStyleSheet("""
            font-size: 18px;
            color: #888;
            background-color: #f5f5f5;
            border-radius: 10px;
        """)
        leftLayout.addWidget(self.imageLabel)

        # 按钮布局（第一行：图片检测、视频检测）
        btnLayout = QHBoxLayout()
        btnLayout.setSpacing(15)

        self.imageBtn = QPushButton("📷 图片检测")
        self.videoBtn = QPushButton("🎥 视频检测")
        self.imageBtn.setMinimumHeight(45)
        self.videoBtn.setMinimumHeight(45)
        self.imageBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #0078D4;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.videoBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #28A745;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.imageBtn.clicked.connect(self.loadImage)
        self.videoBtn.clicked.connect(self.loadVideo)

        btnLayout.addWidget(self.imageBtn)
        btnLayout.addWidget(self.videoBtn)
        leftLayout.addLayout(btnLayout)

        # 新增：摄像头按钮布局（第二行）
        cameraLayout = QHBoxLayout()
        cameraLayout.setSpacing(15)

        self.cameraOpenBtn = QPushButton("📸 打开摄像头")
        self.cameraCloseBtn = QPushButton("🔴 关闭摄像头")
        self.cameraOpenBtn.setMinimumHeight(45)
        self.cameraCloseBtn.setMinimumHeight(45)
        # 摄像头打开按钮样式
        self.cameraOpenBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #FF8C00;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #E07C00;
            }
        """)
        # 摄像头关闭按钮样式
        self.cameraCloseBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #DC3545;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        self.cameraOpenBtn.clicked.connect(self.openCamera)
        self.cameraCloseBtn.clicked.connect(self.closeCamera)

        cameraLayout.addWidget(self.cameraOpenBtn)
        cameraLayout.addWidget(self.cameraCloseBtn)
        leftLayout.addLayout(cameraLayout)

        # ---------- 右侧卡片（参数输入 + 检测结果） ----------
        rightCard = CardWidget()
        rightLayout = QVBoxLayout(rightCard)
        rightLayout.setSpacing(15)

        # 输入框（带 Emoji 占位符）
        self.tempInput = QLineEdit()
        self.tempInput.setPlaceholderText("🌡️ 输入水温 (℃)")
        self.tempInput.setStyleSheet("font-size: 16px; padding: 8px;")

        self.phInput = QLineEdit()
        self.phInput.setPlaceholderText("🧪 输入 pH 值")
        self.phInput.setStyleSheet("font-size: 16px; padding: 8px;")

        self.levelInput = QLineEdit()
        self.levelInput.setPlaceholderText("💧 输入水位 (cm)")
        self.levelInput.setStyleSheet("font-size: 16px; padding: 8px;")

        rightLayout.addWidget(self.tempInput)
        rightLayout.addWidget(self.phInput)
        rightLayout.addWidget(self.levelInput)

        # 检测结果显示区域
        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        self.resultText.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                padding: 12px;
                background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
            }
        """)
        rightLayout.addWidget(self.resultText)

        mainLayout.addWidget(leftCard, 5)
        mainLayout.addWidget(rightCard, 2)

    # =================================================
    # 图片检测（不变）
    # =================================================
    def loadImage(self):
        # 停止视频或摄像头检测
        self.stopAllDetection()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not filePath:
            return
        self.detectImage(filePath)

    def detectImage(self, imagePath):
        self.loadModels()
        settings = self.settingsManager.loadSettings()
        image = cv2.imread(imagePath)
        resultText = "🔍 ===== AI 综合检测结果 =====\n\n"

        for modelName, model in self.models.items():
            results = model.predict(
                source=image,
                conf=settings["confidence"],
                verbose=False
            )
            result = results[0]
            info = ResultParser.parse(result)

            if info["type"] == "detect":
                resultText += f"📌 {modelName}: {info['count']}个目标\n"
                if modelName == "dead_fish":
                    DataManager.latest_dead_fish = info["count"]
            elif info["type"] == "classify":
                resultText += f"🧠 {modelName}: {info['label']} ({info['confidence']:.2%})\n"

            image = result.plot()

        # 显示检测结果图片
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        qtImage = QImage(rgbImage.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qtImage)
        self.imageLabel.setPixmap(
            pixmap.scaled(
                self.imageLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self.resultText.setText(resultText)

        # 保存检测结果图片
        os.makedirs("outputs/images", exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join("outputs", "images", f"detect_{now}.jpg")
        cv2.imwrite(save_path, image)
        self.resultText.append(f"\n💾 检测图片已保存:\n{save_path}")

        # 启动 AI 分析线程
        self.aiThread = AIThread(
            detect_result=resultText,
            water_temp=self.tempInput.text(),
            ph_value=self.phInput.text(),
            water_level=self.levelInput.text()
        )
        self.aiThread.resultSignal.connect(self.showAIResult)
        self.aiThread.start()

    # =================================================
    # 视频检测（不变，但需要先停止摄像头）
    # =================================================
    def loadVideo(self):
        self.stopAllDetection()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "", "Videos (*.mp4 *.avi)"
        )
        if not filePath:
            return
        self.videoThread = VideoDetectThread(filePath)
        self.videoThread.changePixmap.connect(self.updateVideoFrame)
        self.videoThread.changeText.connect(self.resultText.setText)
        self.videoThread.start()

    def updateVideoFrame(self, frame):
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        qtImage = QImage(rgbImage.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qtImage)
        self.imageLabel.setPixmap(
            pixmap.scaled(
                self.imageLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # =================================================
    # 摄像头检测（新增）
    # =================================================
    def openCamera(self):
        self.stopAllDetection()
        self.loadModels()
        if not self.models:
            self.resultText.setText("⚠️ 没有启用的YOLO模型，请先在系统设置中打开至少一个模型开关。")
            return

        settings = self.settingsManager.loadSettings()
        confidence = settings["confidence"]

        # 根据启用的模型数量动态调整跳帧和分辨率
        model_count = len(self.models)
        if model_count >= 5:
            frame_skip = 5  # 每5帧检测一次
            resize_width = 320
        elif model_count >= 3:
            frame_skip = 4
            resize_width = 480
        else:
            frame_skip = 2
            resize_width = 640

        self.cameraThread = CameraThread(
            models=self.models,
            confidence=confidence,
            camera_id=0,
            frame_skip=frame_skip,
            resize_width=resize_width
        )
        self.cameraThread.changePixmap.connect(self.updateCameraFrame)
        self.cameraThread.changeText.connect(self.updateCameraText)
        self.cameraThread.start()

        self.resultText.append(
            f"📹 摄像头已打开（模型数:{model_count}, 检测间隔:{frame_skip}帧, 分辨率:{resize_width}px）")

    def closeCamera(self):
        if self.cameraThread is not None:
            # 断开信号，避免残留数据覆盖重置
            try:
                self.cameraThread.changePixmap.disconnect(self.updateCameraFrame)
            except TypeError:
                pass
            try:
                self.cameraThread.changeText.disconnect(self.updateCameraText)
            except TypeError:
                pass

            self.cameraThread.stop()
            self.cameraThread = None

            # 重置显示区域为初始状态
            self.imageLabel.setText("🖼️ 等待上传图片或视频")
            self.imageLabel.setPixmap(QPixmap())  # 清空图片
            self.resultText.append("🔴 摄像头检测已停止")

    def updateCameraFrame(self, frame):
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        qtImage = QImage(rgbImage.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qtImage)
        self.imageLabel.setPixmap(
            pixmap.scaled(
                self.imageLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def updateCameraText(self, text):
        self.resultText.setText(text)   # 实时覆盖显示最新检测结果

    # =================================================
    # AI 结果回调（不变）
    # =================================================
    def showAIResult(self, aiResult):
        try:
            data = json.loads(aiResult)
            score = int(data.get("score", 0))
            report = (
                f"🤖 DeepSeek AI 分析结果\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 评分：{score}\n\n"
                f"⚠️ 风险等级：{data.get('risk_level', '未知')}\n\n"
                f"📋 风险原因：\n{data.get('reason', '')}\n\n"
                f"💡 处理建议：\n{data.get('suggestion', '')}\n\n"
                f"🔔 是否告警：{data.get('warning', '否')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            DataManager.latest_report = report
            DataManager.latest_score = score
            DataManager.score_history.append(score)
            if len(DataManager.score_history) > 20:
                DataManager.score_history = DataManager.score_history[-20:]

            self.resultText.append(f"\n\n{report}")

        except Exception as e:
            self.resultText.append(f"\n❌ AI 结果解析失败:\n{e}")

    # =================================================
    # 辅助：停止所有检测线程
    # =================================================
    def stopAllDetection(self):
        if self.videoThread is not None:
            self.videoThread.stop()
            self.videoThread = None
        if self.cameraThread is not None:
            self.cameraThread.stop()
            self.cameraThread = None