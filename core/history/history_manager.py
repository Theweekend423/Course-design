import json
import os


class HistoryManager:

    def __init__(self):

        self.historyFile = "outputs/history/history.json"

        if not os.path.exists("outputs/history"):
            os.makedirs("outputs/history")

        if not os.path.exists(self.historyFile):

            with open(
                    self.historyFile,
                    "w",
                    encoding="utf-8"
            ) as f:

                json.dump([], f)

    # =========================
    # 保存历史
    # =========================

    def saveRecord(self, report, score):

        with open(
                self.historyFile,
                "r",
                encoding="utf-8"
        ) as f:

            data = json.load(f)

        # 防止重复保存
        if len(data) > 0:

            if data[0]["content"] == report:
                return

        data.insert(0, {
            "score": score,
            "content": report
        })

        # 只保留最近5次
        data = data[:5]

        with open(
                self.historyFile,
                "w",
                encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    # =========================
    # 读取历史
    # =========================

    def loadHistory(self):

        with open(
                self.historyFile,
                "r",
                encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data