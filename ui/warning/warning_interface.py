from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout
)

from PyQt5.QtCore import (
    QTimer,
    QDateTime
)
from PyQt5.QtGui import QFont

from qfluentwidgets import CardWidget

from core.data.data_manager import (
    DataManager
)

from core.alarm.alarm_manager import (
    AlarmManager
)


class WarningInterface(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("warning_interface")
        self.lastAlarmTime = None
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkRealtimeAlarm)
        self.timer.start(10000)

    # =========================
    # UI（Emoji 美化）
    # =========================
    def initUI(self):
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(20)

        # =================================================
        # 左侧参数设置卡片
        # =================================================
        settingCard = CardWidget()
        settingCard.setMinimumWidth(340)
        settingLayout = QVBoxLayout(settingCard)
        settingLayout.setSpacing(15)

        # 标题行
        titleLayout = QHBoxLayout()
        titleEmoji = QLabel("⚙️")
        titleEmoji.setFont(QFont("Segoe UI Emoji", 28))
        titleLayout.addWidget(titleEmoji)
        title = QLabel("报警参数设置")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        titleLayout.addWidget(title)
        titleLayout.addStretch()
        settingLayout.addLayout(titleLayout)

        # 网格布局（添加 Emoji 标签）
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(15)

        # 死鱼阈值
        deadLabel = QLabel("🐟 死鱼阈值")
        deadLabel.setStyleSheet("font-size:18px;")
        self.deadFishSpin = QSpinBox()
        self.deadFishSpin.setValue(2)
        self.deadFishSpin.setMinimumHeight(38)
        self.deadFishSpin.setStyleSheet("font-size:16px;")
        grid.addWidget(deadLabel, 0, 0)
        grid.addWidget(self.deadFishSpin, 0, 1)

        # 水温阈值
        tempLabel = QLabel("🌡️ 最高水温")
        tempLabel.setStyleSheet("font-size:18px;")
        self.tempSpin = QDoubleSpinBox()
        self.tempSpin.setValue(30)
        self.tempSpin.setSuffix(" ℃")
        self.tempSpin.setMinimumHeight(38)
        self.tempSpin.setStyleSheet("font-size:16px;")
        grid.addWidget(tempLabel, 1, 0)
        grid.addWidget(self.tempSpin, 1, 1)

        # pH 阈值
        phLabel = QLabel("🧪 最低pH")
        phLabel.setStyleSheet("font-size:18px;")
        self.phSpin = QDoubleSpinBox()
        self.phSpin.setValue(6.5)
        self.phSpin.setMinimumHeight(38)
        self.phSpin.setStyleSheet("font-size:16px;")
        grid.addWidget(phLabel, 2, 0)
        grid.addWidget(self.phSpin, 2, 1)

        # 水位阈值
        levelLabel = QLabel("💧 最低水位")
        levelLabel.setStyleSheet("font-size:18px;")
        self.levelSpin = QDoubleSpinBox()
        self.levelSpin.setValue(30)
        self.levelSpin.setSuffix(" cm")
        self.levelSpin.setMinimumHeight(38)
        self.levelSpin.setStyleSheet("font-size:16px;")
        grid.addWidget(levelLabel, 3, 0)
        grid.addWidget(self.levelSpin, 3, 1)

        # 静默时间
        muteLabel = QLabel("⏰ 静默时间")
        muteLabel.setStyleSheet("font-size:18px;")
        self.muteSpin = QSpinBox()
        self.muteSpin.setValue(30)
        self.muteSpin.setSuffix(" 分钟")
        self.muteSpin.setMinimum(1)
        self.muteSpin.setMinimumHeight(38)
        self.muteSpin.setStyleSheet("font-size:16px;")
        grid.addWidget(muteLabel, 4, 0)
        grid.addWidget(self.muteSpin, 4, 1)

        settingLayout.addLayout(grid)
        settingLayout.addStretch()

        # =================================================
        # 中间状态卡片
        # =================================================
        statusCard = CardWidget()
        statusCard.setMinimumWidth(300)
        statusLayout = QVBoxLayout(statusCard)
        statusLayout.setSpacing(25)

        statusTitleLayout = QHBoxLayout()
        statusEmoji = QLabel("📡")
        statusEmoji.setFont(QFont("Segoe UI Emoji", 28))
        statusTitleLayout.addWidget(statusEmoji)
        statusTitle = QLabel("系统实时状态")
        statusTitle.setStyleSheet("font-size: 26px; font-weight: bold;")
        statusTitleLayout.addWidget(statusTitle)
        statusTitleLayout.addStretch()
        statusLayout.addLayout(statusTitleLayout)

        self.statusLabel = QLabel("🟢 正常")
        self.statusLabel.setStyleSheet("""
            font-size: 42px;
            color: green;
            font-weight: bold;
        """)
        statusLayout.addWidget(self.statusLabel)

        self.statusInfo = QLabel("当前鱼池状态稳定")
        self.statusInfo.setStyleSheet("""
            font-size: 20px;
            color: #555;
        """)
        statusLayout.addWidget(self.statusInfo)
        statusLayout.addStretch()

        # =================================================
        # 右侧日志卡片
        # =================================================
        logCard = CardWidget()
        logLayout = QVBoxLayout(logCard)

        logTitleLayout = QHBoxLayout()
        logEmoji = QLabel("📋")
        logEmoji.setFont(QFont("Segoe UI Emoji", 28))
        logTitleLayout.addWidget(logEmoji)
        logTitle = QLabel("报警日志")
        logTitle.setStyleSheet("font-size: 26px; font-weight: bold;")
        logTitleLayout.addWidget(logTitle)
        logTitleLayout.addStretch()
        logLayout.addLayout(logTitleLayout)

        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        self.logText.setStyleSheet("""
            font-size: 16px;
            padding: 12px;
            background-color: #f8f9fa;
            border: none;
        """)
        logLayout.addWidget(self.logText)

        # 主布局比例（保持不变）
        mainLayout.addWidget(settingCard, 2)
        mainLayout.addWidget(statusCard, 2)
        mainLayout.addWidget(logCard, 4)

    # =================================================
    # 实时报警检测（功能完全不变）
    # =================================================
    def checkRealtimeAlarm(self):
        settings = {
            "dead_fish": self.deadFishSpin.value(),
            "water_temp": self.tempSpin.value(),
            "ph_value": self.phSpin.value(),
            "water_level": self.levelSpin.value()
        }

        # 模拟实时数据（保持不变）
        dead_fish = DataManager.latest_dead_fish
        water_temp = 32          # 模拟值
        ph_value = 5.8          # 模拟值
        water_level = 20        # 模拟值

        alarm, message = AlarmManager.checkAlarm(
            dead_fish, water_temp, ph_value, water_level, settings
        )

        now = QDateTime.currentDateTime()
        muteMinutes = self.muteSpin.value()
        canAlarm = True
        if self.lastAlarmTime:
            seconds = self.lastAlarmTime.secsTo(now)
            if seconds < muteMinutes * 60:
                canAlarm = False

        if alarm:
            # 更新状态显示（带 Emoji）
            self.statusLabel.setText("🔴 危险")
            self.statusLabel.setStyleSheet("""
                font-size: 42px;
                color: red;
                font-weight: bold;
            """)
            self.statusInfo.setText("检测到风险指标异常")

            currentTime = now.toString("yyyy-MM-dd hh:mm:ss")
            self.logText.append(f"[{currentTime}]\n⚠️ {message}\n")

            if canAlarm:
                AlarmManager.showAlarm(message)
                self.lastAlarmTime = now
        else:
            self.statusLabel.setText("🟢 正常")
            self.statusLabel.setStyleSheet("""
                font-size: 42px;
                color: green;
                font-weight: bold;
            """)
            self.statusInfo.setText("当前鱼池状态稳定")