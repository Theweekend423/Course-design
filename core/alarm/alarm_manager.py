from PyQt5.QtWidgets import QMessageBox

import winsound


class AlarmManager:

    @staticmethod
    def checkAlarm(
            dead_fish,
            water_temp,
            ph_value,
            water_level,
            settings
    ):

        messages = []

        # 死鱼
        if dead_fish >= settings["dead_fish"]:

            messages.append(
                f"死鱼数量超标: {dead_fish}"
            )

        # 水温
        if water_temp >= settings["water_temp"]:

            messages.append(
                f"水温过高: {water_temp}℃"
            )

        # pH
        if ph_value <= settings["ph_value"]:

            messages.append(
                f"pH过低: {ph_value}"
            )

        # 水位
        if water_level <= settings["water_level"]:

            messages.append(
                f"水位过低: {water_level}cm"
            )

        if len(messages) > 0:

            text = "\n".join(messages)

            return True, text

        return False, "正常"

    # =================================================
    # 真正报警
    # =================================================

    @staticmethod
    def showAlarm(message):

        # 声音报警
        winsound.PlaySound(
            "resources/sound/alarm.wav",
            winsound.SND_FILENAME |
            winsound.SND_ASYNC
        )

        # 弹窗
        QMessageBox.warning(
            None,
            "FishAI危险报警",
            message
        )