import platform
import sys
import subprocess
import os
import signal
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QPushButton, QTextEdit
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
        self.webProcess = None
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

        # =================================================
        # 网页端备用路线控制卡片
        # =================================================
        webCard = CardWidget()
        webLayout = QVBoxLayout(webCard)
        webLayout.setSpacing(15)

        # 标题行
        webTitle_layout = QHBoxLayout()
        web_icon = QLabel("🌐")
        web_icon.setFont(QFont("Segoe UI Emoji", 32))
        webTitle_layout.addWidget(web_icon)
        webTitle = QLabel("网页端备用路线")
        webTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        webTitle_layout.addWidget(webTitle)
        webTitle_layout.addStretch()
        webLayout.addLayout(webTitle_layout)

        # 状态与说明
        self.webStatusLabel = QLabel("🔴 网页端服务未启动")
        self.webStatusLabel.setStyleSheet("font-size: 18px; color: #D83B01; font-weight: bold;")
        webLayout.addWidget(self.webStatusLabel)

        self.webInfoLabel = QLabel(
            "💡 轻量网页备用端，支持图片综合检测，无需安装额外软件即可通过浏览器访问。"
        )
        self.webInfoLabel.setWordWrap(True)
        self.webInfoLabel.setStyleSheet("font-size: 16px; color: #555; line-height: 26px;")
        webLayout.addWidget(self.webInfoLabel)

        # 链接显示区域
        self.webLinkText = QTextEdit()
        self.webLinkText.setReadOnly(True)
        self.webLinkText.setMaximumHeight(60)
        self.webLinkText.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                padding: 10px;
                background-color: #f0f4ff;
                border: 2px dashed #4facfe;
                border-radius: 10px;
                color: #2d1b69;
            }
        """)
        self.webLinkText.setText("🔗 链接将在启动后显示于此处...")
        self.webLinkText.setVisible(False)
        webLayout.addWidget(self.webLinkText)

        # 按钮布局
        webBtnLayout = QHBoxLayout()
        webBtnLayout.setSpacing(15)

        self.startWebBtn = QPushButton("▶️ 启动备用网页界面")
        self.startWebBtn.setMinimumHeight(50)
        self.startWebBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #28A745;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.startWebBtn.clicked.connect(self.startWebServer)

        self.stopWebBtn = QPushButton("⏹️ 关闭网页端")
        self.stopWebBtn.setMinimumHeight(50)
        self.stopWebBtn.setEnabled(False)
        self.stopWebBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #DC3545;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stopWebBtn.clicked.connect(self.stopWebServer)

        self.openBrowserBtn = QPushButton("⏏️ 在浏览器中打开")
        self.openBrowserBtn.setMinimumHeight(50)
        self.openBrowserBtn.setEnabled(False)
        self.openBrowserBtn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #0078D4;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.openBrowserBtn.clicked.connect(self.openBrowser)

        webBtnLayout.addWidget(self.startWebBtn)
        webBtnLayout.addWidget(self.stopWebBtn)
        webBtnLayout.addWidget(self.openBrowserBtn)
        webLayout.addLayout(webBtnLayout)

        mainLayout.addWidget(webCard)

        mainLayout.addStretch()

    # =================================================
    # 网页端服务控制方法
    # =================================================
    def startWebServer(self):
        """启动 Web 后端服务"""
        try:
            possible_paths = []

            # 当前文件所在目录: ui/home/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 桌面端根目录: ui/ 的父目录
            desktop_dir = os.path.dirname(current_dir)

            # 方案1: FishAi_web 与 Fish_system 同级（常见布局）
            parent_of_desktop = os.path.dirname(desktop_dir)
            possible_paths.append(os.path.join(parent_of_desktop, "FishAi_web"))

            # 方案2: FishAi_web 在 Fish_system 内部
            possible_paths.append(os.path.join(desktop_dir, "FishAi_web"))

            # 方案3: 从当前工作目录查找
            possible_paths.append(os.path.join(os.getcwd(), "FishAi_web"))

            # 方案4: 绝对路径（硬编码备用）
            possible_paths.append(r"E:\YOLO11\Fish_system\FishAi_web")

            web_dir = None
            run_script = None
            for p in possible_paths:
                candidate = os.path.join(p, "run.py")
                if os.path.exists(candidate):
                    web_dir = p
                    run_script = candidate
                    break

            if web_dir is None:
                # 最后一次尝试：直接搜索 run.py
                search_roots = [
                    parent_of_desktop,
                    desktop_dir,
                    os.getcwd(),
                    r"E:\YOLO11\Fish_system",
                ]
                for root in search_roots:
                    for dirpath, dirnames, filenames in os.walk(root):
                        if "run.py" in filenames:
                            # 确认是 FishAi_web 的 run.py（检查同级是否有 backend/app.py）
                            if os.path.exists(os.path.join(dirpath, "backend", "app.py")):
                                web_dir = dirpath
                                run_script = os.path.join(dirpath, "run.py")
                                break
                        # 限制搜索深度，避免太慢
                        if dirpath.count(os.sep) > root.count(os.sep) + 2:
                            del dirnames[:]
                    if web_dir:
                        break

            if web_dir is None or not os.path.exists(run_script):
                self.webStatusLabel.setText("❌ 未找到 run.py\n已尝试路径: " + "; ".join(possible_paths[:3]))
                self.webStatusLabel.setStyleSheet("font-size: 18px; color: #DC3545; font-weight: bold;")
                return

            # 启动子进程运行 run.py
            if sys.platform == "win32":
                self.webProcess = subprocess.Popen(
                    [sys.executable, run_script],
                    cwd=web_dir,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.webProcess = subprocess.Popen(
                    [sys.executable, run_script],
                    cwd=web_dir,
                    preexec_fn=os.setsid
                )

            # 更新 UI 状态
            self.webStatusLabel.setText("🟢 网页端服务运行中")
            self.webStatusLabel.setStyleSheet("font-size: 18px; color: #28A745; font-weight: bold;")
            self.webInfoLabel.setText("✅ 服务已启动！点击下方按钮在浏览器中打开网页端。")

            self.webLinkText.setText("🔗 http://localhost:8081")
            self.webLinkText.setVisible(True)

            self.startWebBtn.setEnabled(False)
            self.stopWebBtn.setEnabled(True)
            self.openBrowserBtn.setEnabled(True)

        except Exception as e:
            self.webStatusLabel.setText(f"❌ 启动失败: {str(e)}")
            self.webStatusLabel.setStyleSheet("font-size: 18px; color: #DC3545; font-weight: bold;")

    def stopWebServer(self):
        """停止 Web 后端服务"""
        if self.webProcess is not None:
            try:
                if sys.platform == "win32":
                    # Windows: 终止进程组
                    self.webProcess.send_signal(signal.CTRL_BREAK_EVENT)
                    self.webProcess.kill()
                else:
                    # Linux/Mac: 终止进程组
                    os.killpg(os.getpgid(self.webProcess.pid), signal.SIGTERM)
                    self.webProcess.kill()
            except Exception:
                pass
            finally:
                self.webProcess = None

        # 更新 UI 状态
        self.webStatusLabel.setText("🔴 网页端服务已停止")
        self.webStatusLabel.setStyleSheet("font-size: 18px; color: #D83B01; font-weight: bold;")
        self.webInfoLabel.setText("💡 轻量网页备用端，支持图片综合检测，无需安装额外软件即可通过浏览器访问。")

        self.webLinkText.setVisible(False)
        self.webLinkText.setText("🔗 链接将在启动后显示于此处...")

        self.startWebBtn.setEnabled(True)
        self.stopWebBtn.setEnabled(False)
        self.openBrowserBtn.setEnabled(False)

    def openBrowser(self):
        """在默认浏览器中打开网页端"""
        import webbrowser
        webbrowser.open("http://localhost:8081")

    def closeEvent(self, event):
        """窗口关闭时确保停止 Web 服务"""
        self.stopWebServer()
        event.accept()

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