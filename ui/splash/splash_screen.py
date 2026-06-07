import os

from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve
)

from PyQt5.QtGui import (
    QPixmap
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QApplication,
    QGraphicsOpacityEffect
)


class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.resize(900, 520)

        desktop = QApplication.desktop()

        self.move(
            (desktop.width() - self.width()) // 2,
            (desktop.height() - self.height()) // 2
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.imageLabel = QLabel()

        self.imageLabel.setAlignment(
            Qt.AlignCenter
        )

        splash_path = os.path.join(
            "resources",
            "splash.png"
        )

        if os.path.exists(splash_path):

            pixmap = QPixmap(splash_path)

            self.imageLabel.setPixmap(
                pixmap.scaled(
                    900,
                    520,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        else:

            self.imageLabel.setText(
                "慧渔先知"
            )

            self.imageLabel.setStyleSheet("""
                font-size: 48px;
                color: white;
                background-color: #0078D4;
                border-radius: 24px;
            """)

        layout.addWidget(
            self.imageLabel
        )

        # =================================================
        # 透明度效果
        # =================================================

        self.opacityEffect = (
            QGraphicsOpacityEffect()
        )

        self.setGraphicsEffect(
            self.opacityEffect
        )

        # =================================================
        # 淡入动画
        # =================================================

        self.fadeInAnimation = (
            QPropertyAnimation(
                self.opacityEffect,
                b"opacity"
            )
        )

        self.fadeInAnimation.setDuration(
            1200
        )

        self.fadeInAnimation.setStartValue(
            0
        )

        self.fadeInAnimation.setEndValue(
            1
        )

        self.fadeInAnimation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # =================================================
        # 淡出动画
        # =================================================

        self.fadeOutAnimation = (
            QPropertyAnimation(
                self.opacityEffect,
                b"opacity"
            )
        )

        self.fadeOutAnimation.setDuration(
            800
        )

        self.fadeOutAnimation.setStartValue(
            1
        )

        self.fadeOutAnimation.setEndValue(
            0
        )

        self.fadeOutAnimation.setEasingCurve(
            QEasingCurve.InCubic
        )

        self.fadeOutAnimation.finished.connect(
            self.close
        )

    # =================================================
    # 显示启动页
    # =================================================

    def start(self):

        self.show()

        self.fadeInAnimation.start()

    # =================================================
    # 关闭启动页
    # =================================================

    def finish(self):

        self.fadeOutAnimation.start()
