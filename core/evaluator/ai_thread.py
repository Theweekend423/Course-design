from PyQt5.QtCore import QThread, pyqtSignal

from core.evaluator.ai_evaluator import AIEvaluator


class AIThread(QThread):

    resultSignal = pyqtSignal(str)

    def __init__(
            self,
            detect_result,
            water_temp,
            ph_value,
            water_level
    ):

        super().__init__()

        self.detect_result = detect_result
        self.water_temp = water_temp
        self.ph_value = ph_value
        self.water_level = water_level

        self.aiEvaluator = AIEvaluator()

    def run(self):

        result = self.aiEvaluator.analyze(
            detect_result=self.detect_result,
            water_temp=self.water_temp,
            ph_value=self.ph_value,
            water_level=self.water_level
        )

        self.resultSignal.emit(result)