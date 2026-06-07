import os
import cv2

from PyQt5.QtCore import (
    QThread,
    pyqtSignal
)

from ultralytics import YOLO

from core.settings.settings_manager import (
    SettingsManager
)

from core.detector.result_parser import ResultParser

class VideoDetectThread(QThread):

    changePixmap = pyqtSignal(object)

    changeText = pyqtSignal(str)

    def __init__(self, videoPath):

        super().__init__()

        self.videoPath = videoPath

        self.isRunning = True

        self.settingsManager = SettingsManager()

        self.models = {}

        self.loadModels()

    # =================================================
    # 加载模型
    # =================================================

    def loadModels(self):

        settings = self.settingsManager.loadSettings()

        self.models = {}

        if settings["enable_dead_fish"]:

            self.models["dead_fish"] = YOLO(
                "models/dead_fish.pt"
            )

        if settings["enable_pollution"]:

            self.models["pollution"] = YOLO(
                "models/pollution.pt"
            )

        if settings["enable_eutrophication"]:

            self.models["eutrophication"] = YOLO(
                "models/eutrophication.pt"
            )

        if settings["enable_water_quality"]:

            self.models["water_quality"] = YOLO(
                "models/water_quality.pt"
            )

        if settings["enable_water_trash"]:

            self.models["water_trash"] = YOLO(
                "models/water_trash.pt"
            )

    def run(self):

        settings = self.settingsManager.loadSettings()

        cap = cv2.VideoCapture(self.videoPath)

        fps = cap.get(cv2.CAP_PROP_FPS)

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        os.makedirs(
            "outputs/videos",
            exist_ok=True
        )

        output_path = os.path.join(
            "outputs",
            "videos",
            "detect_result.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (width, height)
        )

        while self.isRunning:

            ret, frame = cap.read()

            if not ret:
                break

            resultText = "===== 实时检测结果 =====\n\n"

            for modelName, model in self.models.items():

                results = model.predict(
                    source=frame,
                    conf=settings["confidence"],
                    verbose=False
                )

                result = results[0]

                info = ResultParser.parse(result)

                if info["type"] == "detect":

                    resultText += (
                        f"{modelName}: "
                        f"{info['count']}个目标\n"
                    )

                    if modelName == "dead_fish":
                        from core.data.data_manager import DataManager

                        DataManager.latest_dead_fish = (
                            info["count"]
                        )

                elif info["type"] == "classify":

                    resultText += (
                        f"{modelName}: "
                        f"{info['label']} "
                        f"({info['confidence']:.2%})\n"
                    )

                frame = result.plot()

            out.write(frame)

            self.changeText.emit(resultText)

            self.changePixmap.emit(frame)

        out.release()

        cap.release()

    def stop(self):

        self.isRunning = False

        self.quit()