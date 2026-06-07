import json

from openai import OpenAI

from core.settings.settings_manager import SettingsManager


class AIEvaluator:

    def __init__(self):

        self.settingsManager = SettingsManager()

    # =================================================
    # 创建客户端
    # =================================================
    def createClient(self):

        settings = self.settingsManager.loadSettings()

        client = OpenAI(
            api_key=settings["api_key"],
            base_url=settings["base_url"],
            timeout=settings["timeout"]
        )

        return client

    # =================================================
    # AI 分析
    # =================================================
    def analyze(
            self,
            detect_result,
            water_temp,
            ph_value,
            water_level
    ):

        settings = self.settingsManager.loadSettings()

        if settings["api_key"] == "":

            return json.dumps({
                "score": 0,
                "risk_level": "未配置",
                "reason": "未配置 DeepSeek API Key",
                "suggestion": "请前往系统设置配置 API",
                "warning": "是"
            }, ensure_ascii=False)

        prompt = f"""
你现在是专业水产养殖 AI 专家。

请根据以下信息，
生成鱼池风险分析。

【检测结果】
{detect_result}

【环境参数】
水温：{water_temp}
pH 值：{ph_value}
水位：{water_level}

你必须严格按照以下 JSON 格式输出。

不要输出任何额外内容。
不要解释。
不要 Markdown。
不要```json。

直接输出：

{{
"score": 0,
"risk_level": "",
"reason": "",
"suggestion": "",
"warning": ""
}}

其中：

score:
0-100 整数。

risk_level:
安全/低风险/中风险/高风险。

warning:
是/否。
"""

        try:

            client = self.createClient()

            response = client.chat.completions.create(
                model=settings["model_name"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                timeout=settings["timeout"]
            )

            # =========================
            # Token统计
            # =========================
            try:

                total_tokens = response.usage.total_tokens

                self.settingsManager.addToken(total_tokens)

            except Exception:
                pass

            return response.choices[0].message.content

        except Exception as e:

            return json.dumps({
                "score": 0,
                "risk_level": "AI连接失败",
                "reason": str(e),
                "suggestion": "检查 API 配置 / 网络 / 模型名",
                "warning": "是"
            }, ensure_ascii=False)

    # =================================================
    # 测试连接
    # =================================================
    def testConnection(self):

        settings = self.settingsManager.loadSettings()

        try:

            client = self.createClient()

            response = client.chat.completions.create(
                model=settings["model_name"],
                messages=[
                    {
                        "role": "user",
                        "content": "你好"
                    }
                ],
                timeout=settings["timeout"]
            )

            return True, "DeepSeek 连接成功"

        except Exception as e:

            return False, str(e)