from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QTextEdit
)

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

from qfluentwidgets import CardWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

from core.history.history_manager import HistoryManager
from core.report.report_generator import ReportGenerator
from core.data.data_manager import DataManager


# =========================
# 趋势图（带 Emoji 标题）
# =========================
class StatsChart(CardWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 标题行：Emoji + 文字
        title_layout = QHBoxLayout()
        title_emoji = QLabel("📊")
        title_emoji.setFont(QFont("Segoe UI Emoji", 28))
        title_layout.addWidget(title_emoji)

        title = QLabel("AI评分趋势图")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.updateChart([0])

    def updateChart(self, scores):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if len(scores) == 0:
            scores = [0]
        x = list(range(1, len(scores) + 1))
        ax.plot(x, scores, linewidth=3, marker='o', color='#0078D4')
        ax.set_title("AI评分趋势")
        ax.set_xlabel("检测次数")
        ax.set_ylabel("评分")
        ax.set_xticks(x)
        ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas.draw()


# =========================
# 主页面
# =========================
class EvaluateInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("evaluate_interface")
        self.historyManager = HistoryManager()
        self.reportGenerator = ReportGenerator()
        self.currentReport = ""
        self.initUI()
        self.loadHistory()

        # 实时刷新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateRealData)
        self.timer.start(2000)

    # =========================
    # UI 构建（Emoji 美化）
    # =========================
    def initUI(self):
        mainLayout = QHBoxLayout(self)
        mainLayout.setSpacing(20)

        # ===== 左侧区域 =====
        leftLayout = QVBoxLayout()
        leftLayout.setSpacing(20)

        # 趋势图卡片
        self.chart = StatsChart()
        leftLayout.addWidget(self.chart)

        # AI 结果卡片
        resultCard = CardWidget()
        resultLayout = QVBoxLayout(resultCard)
        resultLayout.setSpacing(15)

        # 标题行（Emoji + 文字）
        resultTitleLayout = QHBoxLayout()
        resultEmoji = QLabel("🤖")
        resultEmoji.setFont(QFont("Segoe UI Emoji", 32))
        resultTitleLayout.addWidget(resultEmoji)

        resultTitle = QLabel("AI综合评价")
        resultTitle.setStyleSheet("font-size: 26px; font-weight: bold;")
        resultTitleLayout.addWidget(resultTitle)
        resultTitleLayout.addStretch()
        resultLayout.addLayout(resultTitleLayout)

        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        self.resultText.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            border: none;
            background-color: #f8f9fa;
        """)
        resultLayout.addWidget(self.resultText)

        # 导出按钮（带 Emoji）
        self.exportBtn = QPushButton("📄 导出PDF报告")
        self.exportBtn.setMinimumHeight(45)
        self.exportBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #0078D4;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.exportBtn.clicked.connect(self.exportReport)
        resultLayout.addWidget(self.exportBtn)

        leftLayout.addWidget(resultCard)

        # ===== 右侧历史记录卡片 =====
        historyCard = CardWidget()
        historyLayout = QVBoxLayout(historyCard)
        historyLayout.setSpacing(15)

        # 标题行（Emoji + 文字）
        historyTitleLayout = QHBoxLayout()
        historyEmoji = QLabel("📜")
        historyEmoji.setFont(QFont("Segoe UI Emoji", 28))
        historyTitleLayout.addWidget(historyEmoji)

        historyTitle = QLabel("最近5次历史报告")
        historyTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        historyTitleLayout.addWidget(historyTitle)
        historyTitleLayout.addStretch()
        historyLayout.addLayout(historyTitleLayout)

        self.historyList = QListWidget()
        self.historyList.setStyleSheet("""
            QListWidget {
                font-size: 18px;
                padding: 10px;
                border: none;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #0078D4;
                color: white;
            }
        """)
        self.historyList.itemClicked.connect(self.showHistoryReport)
        historyLayout.addWidget(self.historyList)

        mainLayout.addLayout(leftLayout, 3)
        mainLayout.addWidget(historyCard, 1)

    # =========================
    # 实时更新（功能不变）
    # =========================
    def updateRealData(self):
        # 更新 AI 报告
        if DataManager.latest_report:
            self.currentReport = DataManager.latest_report
            self.resultText.setText(self.currentReport)

            # 保存历史（仅当报告变化时）
            self.historyManager.saveRecord(
                self.currentReport,
                DataManager.latest_score
            )
            self.loadHistory()

        # 更新趋势图
        scores = DataManager.score_history
        if not scores:
            scores = [0]
        self.chart.updateChart(scores)

    # =========================
    # 加载历史（功能不变）
    # =========================
    def loadHistory(self):
        self.historyList.clear()
        history = self.historyManager.loadHistory()
        for i, item in enumerate(history):
            title = f"📄 报告{i+1}  评分: {item['score']}"
            self.historyList.addItem(title)

    # =========================
    # 查看历史报告（功能不变）
    # =========================
    def showHistoryReport(self, item):
        history = self.historyManager.loadHistory()
        index = self.historyList.row(item)
        report = history[index]["content"]
        self.currentReport = report
        self.resultText.setText(report)

    # =========================
    # 导出PDF（功能不变）
    # =========================
    def exportReport(self):
        filePath = self.reportGenerator.exportPdf(self.currentReport)
        self.resultText.append(f"\n\n📄 PDF已导出:\n{filePath}")