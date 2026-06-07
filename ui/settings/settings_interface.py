import platform
import sys

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QScrollArea,
    QSizePolicy
)
from PyQt5.QtGui import QFont

from qfluentwidgets import (
    CardWidget,
    MessageBox
)

from core.settings.settings_manager import (
    SettingsManager
)

import torch


def get_windows_version_name():
    if platform.system() == "Windows":
        build = sys.getwindowsversion().build
        if build >= 22000:
            return "Windows 11"
        elif build >= 10240:
            return "Windows 10"
        else:
            return f"Windows (Build {build})"
    else:
        return platform.system()


class SettingsInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_interface")
        self.settingsManager = SettingsManager()
        self.settings = self.settingsManager.loadSettings()
        self.initUI()

    # =================================================
    # UI（Emoji 美化）
    # =================================================
    def initUI(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(1)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_widget = QWidget()
        mainLayout = QVBoxLayout(content_widget)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(20)

        # ===== 顶部两列布局 =====
        topLayout = QHBoxLayout()
        topLayout.setSpacing(20)

        # ---------- AI 设置卡片 ----------
        aiCard = CardWidget()
        aiLayout = QVBoxLayout(aiCard)
        aiLayout.setSpacing(12)

        # 标题行
        aiTitleLayout = QHBoxLayout()
        aiEmoji = QLabel("🤖")
        aiEmoji.setFont(QFont("Segoe UI Emoji", 28))
        aiTitleLayout.addWidget(aiEmoji)
        aiTitle = QLabel("AI 模型设置")
        aiTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        aiTitleLayout.addWidget(aiTitle)
        aiTitleLayout.addStretch()
        aiLayout.addLayout(aiTitleLayout)

        # API Key
        aiLayout.addWidget(QLabel("🔑 API Key"))
        self.apiEdit = QLineEdit()
        self.apiEdit.setText(self.settings["api_key"])
        self.apiEdit.setStyleSheet("font-size: 16px; padding: 6px;")
        aiLayout.addWidget(self.apiEdit)

        # Base URL
        aiLayout.addWidget(QLabel("🌐 Base URL"))
        self.urlEdit = QLineEdit()
        self.urlEdit.setText(self.settings["base_url"])
        self.urlEdit.setStyleSheet("font-size: 16px; padding: 6px;")
        aiLayout.addWidget(self.urlEdit)

        # 模型名称
        aiLayout.addWidget(QLabel("📦 模型名称"))
        self.modelEdit = QLineEdit()
        self.modelEdit.setText(self.settings["model_name"])
        self.modelEdit.setStyleSheet("font-size: 16px; padding: 6px;")
        aiLayout.addWidget(self.modelEdit)

        # 超时时间
        aiLayout.addWidget(QLabel("⏱️ AI 请求超时"))
        self.timeoutSpin = QSpinBox()
        self.timeoutSpin.setValue(self.settings["timeout"])
        self.timeoutSpin.setSuffix(" 秒")
        self.timeoutSpin.setStyleSheet("font-size: 16px;")
        aiLayout.addWidget(self.timeoutSpin)

        # Token 消耗
        self.tokenLabel = QLabel(
            f"📊 累计 Token 消耗: {self.settings['token_count']}"
        )
        self.tokenLabel.setStyleSheet("""
            font-size: 18px;
            color: #0078D4;
            font-weight: bold;
        """)
        aiLayout.addWidget(self.tokenLabel)

        # AI 状态（带圆点）
        self.aiStatus = QLabel("🔴 DeepSeek 未连接")
        self.aiStatus.setStyleSheet("""
            font-size: 18px;
            color: red;
            font-weight: bold;
        """)
        aiLayout.addWidget(self.aiStatus)

        # 测试按钮
        self.testBtn = QPushButton("🔌 测试连接")
        self.testBtn.setMinimumHeight(40)
        self.testBtn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #0078D4;
                color: white;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.testBtn.clicked.connect(self.testConnection)
        aiLayout.addWidget(self.testBtn)

        # ---------- YOLO 设置卡片 ----------
        yoloCard = CardWidget()
        yoloLayout = QVBoxLayout(yoloCard)
        yoloLayout.setSpacing(12)

        yoloTitleLayout = QHBoxLayout()
        yoloEmoji = QLabel("🔧")
        yoloEmoji.setFont(QFont("Segoe UI Emoji", 18))
        yoloTitleLayout.addWidget(yoloEmoji)
        yoloTitle = QLabel("YOLO 模型设置")
        yoloTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        yoloTitleLayout.addWidget(yoloTitle)
        yoloTitleLayout.addStretch()
        yoloLayout.addLayout(yoloTitleLayout)

        # 置信度
        conf_label = QLabel("🎚️ 置信度阈值")
        conf_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        yoloLayout.addWidget(conf_label)
        self.confSpin = QDoubleSpinBox()
        self.confSpin.setValue(self.settings["confidence"])
        self.confSpin.setRange(0.1, 1.0)
        self.confSpin.setSingleStep(0.05)
        self.confSpin.setStyleSheet("font-size: 16px;")
        yoloLayout.addWidget(self.confSpin)

        # 模型复选框（每个都带图标）
        self.deadFishCheck = QCheckBox("🐟 启用 dead_fish.pt")
        self.deadFishCheck.setChecked(self.settings["enable_dead_fish"])
        self.deadFishCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        yoloLayout.addWidget(self.deadFishCheck)

        self.pollutionCheck = QCheckBox("🏭 启用 pollution.pt")
        self.pollutionCheck.setChecked(self.settings["enable_pollution"])
        self.pollutionCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        yoloLayout.addWidget(self.pollutionCheck)

        self.eutroCheck = QCheckBox("🌿 启用 eutrophication.pt")
        self.eutroCheck.setChecked(self.settings["enable_eutrophication"])
        self.eutroCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        yoloLayout.addWidget(self.eutroCheck)

        self.waterCheck = QCheckBox("💧 启用 water_quality.pt")
        self.waterCheck.setChecked(self.settings["enable_water_quality"])
        self.waterCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        yoloLayout.addWidget(self.waterCheck)

        self.trashCheck = QCheckBox("🗑️ 启用 water_trash.pt")
        self.trashCheck.setChecked(self.settings["enable_water_trash"])
        self.trashCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        yoloLayout.addWidget(self.trashCheck)

        # GPU 信息
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            deviceText = f"⚡ 当前设备: GPU\n{gpu_name}"
        else:
            deviceText = "💻 当前设备: CPU"

        self.deviceLabel = QLabel(deviceText)
        self.deviceLabel.setStyleSheet("""
            font-size: 18px;
            color: #0078D4;
            font-weight: bold;
        """)
        yoloLayout.addWidget(self.deviceLabel)

        topLayout.addWidget(aiCard, 1)
        topLayout.addWidget(yoloCard, 1)
        mainLayout.addLayout(topLayout)

        # ---------- 系统运行设置卡片 ----------
        systemCard = CardWidget()
        systemLayout = QVBoxLayout(systemCard)
        systemLayout.setSpacing(12)

        systemTitleLayout = QHBoxLayout()
        systemEmoji = QLabel("⚙️")
        systemEmoji.setFont(QFont("Segoe UI Emoji", 28))
        systemTitleLayout.addWidget(systemEmoji)
        systemTitle = QLabel("系统运行设置")
        systemTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        systemTitleLayout.addWidget(systemTitle)
        systemTitleLayout.addStretch()
        systemLayout.addLayout(systemTitleLayout)

        self.splashCheck = QCheckBox("启用开机动画")
        self.splashCheck.setChecked(self.settings["enable_splash"])
        self.splashCheck.setStyleSheet("font-size: 16px; spacing: 8px;")
        systemLayout.addWidget(self.splashCheck)

        mainLayout.addWidget(systemCard)

        # ---------- 关于系统卡片 ----------
        aboutCard = CardWidget()
        aboutLayout = QVBoxLayout(aboutCard)
        aboutLayout.setSpacing(12)

        aboutTitleLayout = QHBoxLayout()
        aboutEmoji = QLabel("ℹ️")
        aboutEmoji.setFont(QFont("Segoe UI Emoji", 28))
        aboutTitleLayout.addWidget(aboutEmoji)
        aboutTitle = QLabel("关于系统")
        aboutTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        aboutTitleLayout.addWidget(aboutTitle)
        aboutTitleLayout.addStretch()
        aboutLayout.addLayout(aboutTitleLayout)

        os_display = get_windows_version_name()
        infoText = f"""
🐟 慧渔先知

智能鱼塘监测平台

作者：TanJun

📦 版本: v1.0

🖥️ 系统: {os_display}

🐍 Python: {sys.version.split()[0]}
"""
        infoLabel = QLabel(infoText)
        infoLabel.setStyleSheet("""
            font-size: 18px;
            line-height: 32px;
        """)
        aboutLayout.addWidget(infoLabel)

        mainLayout.addWidget(aboutCard)

        # ---------- 保存按钮 ----------
        self.saveBtn = QPushButton("💾 保存系统设置")
        self.saveBtn.setMinimumHeight(50)
        self.saveBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #28A745;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.saveBtn.clicked.connect(self.saveSettings)
        mainLayout.addWidget(self.saveBtn)

        mainLayout.addStretch()

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

    # =================================================
    # 测试连接（功能不变，仅美化弹窗图标自动保留）
    # =================================================
    def testConnection(self):
        from core.evaluator.ai_evaluator import AIEvaluator
        self.saveSettings()
        ai = AIEvaluator()
        success, message = ai.testConnection()

        if success:
            self.aiStatus.setText("🟢 ● DeepSeek 在线")
            self.aiStatus.setStyleSheet("""
                font-size: 18px;
                color: green;
                font-weight: bold;
            """)
            MessageBox("连接成功", message, self)
        else:
            self.aiStatus.setText("🔴 DeepSeek 离线")
            self.aiStatus.setStyleSheet("""
                font-size: 18px;
                color: red;
                font-weight: bold;
            """)
            MessageBox("连接失败", message, self)

    # =================================================
    # 保存设置（功能不变）
    # =================================================
    def saveSettings(self):
        settings = {
            "api_key": self.apiEdit.text(),
            "base_url": self.urlEdit.text(),
            "model_name": self.modelEdit.text(),
            "timeout": self.timeoutSpin.value(),
            "token_count": self.settings["token_count"],
            "confidence": self.confSpin.value(),
            "enable_dead_fish": self.deadFishCheck.isChecked(),
            "enable_pollution": self.pollutionCheck.isChecked(),
            "enable_eutrophication": self.eutroCheck.isChecked(),
            "enable_water_quality": self.waterCheck.isChecked(),
            "enable_water_trash": self.trashCheck.isChecked(),
            "enable_splash": self.splashCheck.isChecked()
        }
        self.settingsManager.saveSettings(settings)
        # 更新 token 显示
        self.tokenLabel.setText(f"📊 累计 Token 消耗: {settings['token_count']}")
        MessageBox("保存成功", "系统设置已保存", self)