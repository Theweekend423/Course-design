import json
import os


class SettingsManager:

    def __init__(self):

        self.config_dir = "config"

        self.config_file = os.path.join(
            self.config_dir,
            "settings.json"
        )

        self.default_settings = {

            # =========================
            # AI 设置
            # =========================

            "api_key": "",

            "base_url":
                "https://api.deepseek.com",

            "model_name":
                "deepseek-chat",

            "timeout": 30,

            "token_count": 0,

            # =========================
            # YOLO 设置
            # =========================

            "confidence": 0.5,

            "enable_dead_fish": True,

            "enable_pollution": True,

            "enable_eutrophication": True,

            "enable_water_quality": True,

            "enable_water_trash": True,

            # =========================
            # 系统设置
            # =========================

            "enable_splash": True
        }

        self.initConfig()

    # =================================================
    # 初始化配置
    # =================================================

    def initConfig(self):

        os.makedirs(
            self.config_dir,
            exist_ok=True
        )

        if not os.path.exists(
            self.config_file
        ):

            self.saveSettings(
                self.default_settings
            )

    # =================================================
    # 保存配置
    # =================================================

    def saveSettings(self, settings):

        with open(
            self.config_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                settings,
                f,
                ensure_ascii=False,
                indent=4
            )

    # =================================================
    # 读取配置
    # =================================================

    def loadSettings(self):

        try:

            with open(
                self.config_file,
                "r",
                encoding="utf-8"
            ) as f:

                settings = json.load(f)

            updated = False

            for key, value in self.default_settings.items():

                if key not in settings:

                    settings[key] = value

                    updated = True

            if updated:
                self.saveSettings(settings)

            return settings

        except Exception:

            self.saveSettings(
                self.default_settings
            )

            return self.default_settings

    # =================================================
    # 获取单个配置
    # =================================================

    def get(self, key):

        settings = self.loadSettings()

        return settings.get(key)

    # =================================================
    # 修改单个配置
    # =================================================

    def set(self, key, value):

        settings = self.loadSettings()

        settings[key] = value

        self.saveSettings(settings)

    # =================================================
    # Token 增加
    # =================================================

    def addToken(self, token):

        settings = self.loadSettings()

        settings["token_count"] += int(token)

        self.saveSettings(settings)