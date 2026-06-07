import sys

from PyQt5.QtGui import (
    QIcon,
    QColor,
    QPainter,
    QLinearGradient
)

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect
)

from qfluentwidgets import (
    FluentWindow,
    setTheme,
    Theme,
    FluentIcon
)

from ui.home.home_interface import HomeInterface
from ui.detect.detect_interface import DetectInterface
from ui.evaluate.evaluate_interface import EvaluateInterface
from ui.warning.warning_interface import WarningInterface
from ui.settings.settings_interface import SettingsInterface

from ui.splash.splash_screen import SplashScreen

from core.settings.settings_manager import (
    SettingsManager
)

manager = SettingsManager()


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("慧渔先知")

        desktop = QApplication.desktop()
        screen_width = desktop.width()
        screen_height = desktop.height()

        self.resize(
            int(screen_width * 0.72),
            int(screen_height * 0.72)
        )

        self.setMinimumSize(1280, 820)

        self.navigationInterface.setExpandWidth(320)
        self.navigationInterface.setMinimumWidth(300)

        font = self.font()
        font.setPointSize(13)
        self.setFont(font)

        setTheme(Theme.LIGHT)

        # 页面
        self.homeInterface = HomeInterface(self)
        self.detectInterface = DetectInterface(self)
        self.evaluateInterface = EvaluateInterface(self)
        self.warningInterface = WarningInterface(self)
        self.settingsInterface = SettingsInterface(self)

        # 导航
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "首页")
        self.addSubInterface(self.detectInterface, FluentIcon.CAMERA, "智能检测")
        self.addSubInterface(self.evaluateInterface, FluentIcon.ROBOT, "AI评价")
        self.addSubInterface(self.warningInterface, FluentIcon.INFO, "告警中心")
        self.addSubInterface(self.settingsInterface, FluentIcon.SETTING, "系统设置")

        self.loadQss()
        self.setStyleSheet("""
        FluentWindow{
            background: transparent;
        }
        """)
        # =================================================
        # 主窗口透明度动画
        # =================================================
        self.opacityEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacityEffect)

        self.fadeAnimation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.fadeAnimation.setDuration(1000)
        self.fadeAnimation.setStartValue(0)
        self.fadeAnimation.setEndValue(1)
        self.fadeAnimation.setEasingCurve(QEasingCurve.OutCubic)

        # =================================================
        # 设置窗口图标 (ICO)
        # =================================================
        self.setWindowIcon(QIcon("resources/logo.ico"))
        self.center()

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(
            0,
            QColor("#F5FAFF")
        )

        gradient.setColorAt(
            0.5,
            QColor("#D7ECFF")
        )

        gradient.setColorAt(
            1,
            QColor("#A8D8FF")
        )

        painter.fillRect(
            self.rect(),
            gradient
        )

        super().paintEvent(event)
    def center(self):
        """将窗口移动到屏幕中央"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def showEvent(self, event):
        super().showEvent(event)
        self.fadeAnimation.start()

    def loadQss(self):
        try:
            with open("resources/qss/navigation.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except:
            pass


# =================================================
# 启动程序
# =================================================

if __name__ == '__main__':

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 全局设置应用图标（任务栏、Alt+Tab等也会显示）
    app.setWindowIcon(QIcon("resources/logo.ico"))

    settings = manager.loadSettings()

    splash = None
    if settings["enable_splash"]:
        splash = SplashScreen()
        splash.start()
        app.processEvents()

    # 提前创建窗口
    window = MainWindow()

    # =================================================
    # 平滑切换
    # =================================================
    def showMainWindow():
        if splash:
            splash.finish()
        window.show()

    QTimer.singleShot(2600, showMainWindow)

    sys.exit(app.exec_())