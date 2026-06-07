import platform
import sys
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QColor,
    QFont,
    QPixmap
)

from qfluentwidgets import CardWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

from core.data.data_manager import DataManager
from core.settings.settings_manager import SettingsManager
import torch


# =========================
# 数据卡片（使用 Emoji 图标）
# =========================
class InfoCard(CardWidget):
    def __init__(self, title, value_func, emoji, color="#0078D4", format_str="{}"):
        super().__init__()
        self.value_func = value_func
        self.format_str = format_str
        self.setFixedHeight(140)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Emoji 图标作为 QLabel
        icon_label = QLabel(emoji)
        icon_label.setFont(QFont("Segoe UI Emoji", 36))
        icon_label.setStyleSheet(f"color: {color};")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #6c6c6c;")
        text_layout.addWidget(title_label)

        self.value_label = QLabel()
        self.value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        text_layout.addWidget(self.value_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        self.updateValue()

    def updateValue(self):
        val = self.value_func()
        self.value_label.setText(self.format_str.format(val))


# =========================
# 状态指示灯（Emoji 图标 + 圆点）
# =========================
class StatusLight(QWidget):
    def __init__(self, text, emoji, color_func):
        super().__init__()
        self.color_func = color_func
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        icon_label = QLabel(emoji)
        icon_label.setFont(QFont("Segoe UI Emoji", 18))
        layout.addWidget(icon_label)

        self.dot = QLabel()
        self.dot.setFixedSize(14, 14)
        self.label = QLabel(text)
        self.label.setStyleSheet("font-size: 16px; color: #2c3e50;")

        layout.addWidget(self.dot)
        layout.addWidget(self.label)
        layout.addStretch()

        self.updateColor()

    def updateColor(self):
        color = self.color_func()
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 7px;")


# =========================
# AI 评分趋势图（Emoji 标题）
# =========================
class ScoreTrendChart(CardWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        title_emoji = QLabel("📈")
        title_emoji.setFont(QFont("Segoe UI Emoji", 24))
        title_layout.addWidget(title_emoji)

        title_label = QLabel("AI 评分趋势 (最近10次)")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #202020;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        self.figure = Figure(figsize=(5, 2.5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

    def updateChart(self, scores):
        self.figure.clear()
        if not scores:
            scores = [0]
        ax = self.figure.add_subplot(111)
        x = list(range(1, len(scores) + 1))
        ax.plot(x, scores, marker='o', linewidth=2, color='#0078D4')
        ax.set_xlabel("检测次数")
        ax.set_ylabel("评分")
        ax.set_ylim(0, 105)
        ax.set_xticks(x)
        ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas.draw()


# =========================
# 主页面
# =========================
class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("home_interface")
        self.settingsManager = SettingsManager()
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshAll)
        self.timer.start(2000)
        self.refreshAll()

    def initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(20)

        # 标题栏（Emoji）
        title_layout = QHBoxLayout()

        logo_label = QLabel()

        pixmap = QPixmap("resources/image.png")

        pixmap = pixmap.scaled(
            64,
            64,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        logo_label.setPixmap(pixmap)

        title_layout.addWidget(logo_label)

        title = QLabel("慧渔先知 · 智能监测平台")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #202020;
        """)

        title_layout.addWidget(title)

        title_layout.addStretch()

        mainLayout.addLayout(title_layout)

        # 顶部数据卡片
        cardLayout = QHBoxLayout()
        cardLayout.setSpacing(20)

        self.detectCountCard = InfoCard(
            "AI 分析次数",
            lambda: len(DataManager.score_history),
            "🤖",
            "#0078D4", "{} 次"
        )
        self.scoreCard = InfoCard(
            "最新 AI 评分",
            lambda: DataManager.latest_score if DataManager.latest_score else 0,
            "⭐",
            "#886CE4", "{} 分"
        )
        self.deadFishCard = InfoCard(
            "最新死鱼数量",
            lambda: DataManager.latest_dead_fish,
            "🐟",
            "#D83B01", "{} 条"
        )
        self.apiCard = InfoCard(
            "DeepSeek API",
            self.getApiStatusText,
            "☁️",
            "#107C10", "{}"
        )

        cardLayout.addWidget(self.detectCountCard)
        cardLayout.addWidget(self.scoreCard)
        cardLayout.addWidget(self.deadFishCard)
        cardLayout.addWidget(self.apiCard)
        mainLayout.addLayout(cardLayout)

        # 中间区域：系统状态 + 趋势图
        middleLayout = QHBoxLayout()
        middleLayout.setSpacing(20)

        # 左侧系统状态
        statusCard = CardWidget()
        statusLayout = QVBoxLayout(statusCard)
        statusTitle_layout = QHBoxLayout()
        status_icon = QLabel("⚙️")
        status_icon.setFont(QFont("Segoe UI Emoji", 24))
        statusTitle_layout.addWidget(status_icon)
        statusTitle = QLabel("系统运行状态")
        statusTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        statusTitle_layout.addWidget(statusTitle)
        statusTitle_layout.addStretch()
        statusLayout.addLayout(statusTitle_layout)
        statusLayout.addSpacing(10)

        self.modelLight = StatusLight("YOLO 模型", "🎥", self.getModelColor)
        self.aiLight = StatusLight("AI 服务", "💬", self.getAIColor)
        self.gpuLight = StatusLight("计算设备", "⚡", self.getGPUColor)
        self.dataLight = StatusLight("数据同步", "🔄", lambda: "#107C10" if DataManager.latest_report else "#D83B01")

        statusLayout.addWidget(self.modelLight)
        statusLayout.addWidget(self.aiLight)
        statusLayout.addWidget(self.gpuLight)
        statusLayout.addWidget(self.dataLight)
        statusLayout.addStretch()
        middleLayout.addWidget(statusCard, 1)

        # 右侧趋势图
        self.trendChart = ScoreTrendChart()
        middleLayout.addWidget(self.trendChart, 2)
        mainLayout.addLayout(middleLayout)

        # AI 综合评价区域
        aiCard = CardWidget()
        aiLayout = QVBoxLayout(aiCard)
        aiTitle_layout = QHBoxLayout()
        ai_icon = QLabel("🧠")
        ai_icon.setFont(QFont("Segoe UI Emoji", 32))
        aiTitle_layout.addWidget(ai_icon)
        aiTitle = QLabel("DeepSeek AI 综合评价")
        aiTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        aiTitle_layout.addWidget(aiTitle)
        aiTitle_layout.addStretch()
        aiLayout.addLayout(aiTitle_layout)
        aiLayout.addSpacing(10)

        self.aiReportLabel = QLabel()
        self.aiReportLabel.setWordWrap(True)
        self.aiReportLabel.setStyleSheet("font-size: 18px; line-height: 32px; color: #2c3e50;")
        self.aiReportLabel.setText("等待首次检测...")
        aiLayout.addWidget(self.aiReportLabel)
        mainLayout.addWidget(aiCard)

        mainLayout.addStretch()

    # 辅助方法
    def getModelColor(self):
        settings = self.settingsManager.loadSettings()
        enabled = any([
            settings.get("enable_dead_fish", False),
            settings.get("enable_pollution", False),
            settings.get("enable_eutrophication", False),
            settings.get("enable_water_quality", False),
            settings.get("enable_water_trash", False)
        ])
        return "#107C10" if enabled else "#D83B01"

    def getAIColor(self):
        api_key = self.settingsManager.get("api_key")
        return "#107C10" if api_key and api_key.strip() != "" else "#D83B01"

    def getApiStatusText(self):
        api_key = self.settingsManager.get("api_key")
        if api_key and api_key.strip():
            return "● 已配置"
        return "● 未配置"

    def getGPUColor(self):
        return "#107C10" if torch.cuda.is_available() else "#666666"

    def refreshAll(self):
        self.detectCountCard.updateValue()
        self.scoreCard.updateValue()
        self.deadFishCard.updateValue()
        self.apiCard.updateValue()

        scores = DataManager.score_history[-10:] if DataManager.score_history else [0]
        self.trendChart.updateChart(scores)

        self.modelLight.updateColor()
        self.aiLight.updateColor()
        self.gpuLight.updateColor()
        self.dataLight.updateColor()

        if DataManager.latest_report:
            report = DataManager.latest_report
            if report.strip().startswith("{") and "score" in report:
                try:
                    import json
                    data = json.loads(report)
                    text = f"【评分】{data.get('score', '?')}分  |  【风险等级】{data.get('risk_level', '未知')}\n"
                    text += f"【原因】{data.get('reason', '无')}\n"
                    text += f"【建议】{data.get('suggestion', '无')}"
                    self.aiReportLabel.setText(text)
                except:
                    self.aiReportLabel.setText(report[:400] + ("..." if len(report) > 400 else ""))
            else:
                self.aiReportLabel.setText(report[:400] + ("..." if len(report) > 400 else ""))
        else:
            self.aiReportLabel.setText("暂无 AI 分析结果，请前往「智能检测」上传图片进行分析。")