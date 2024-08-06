"""
主程序入口
"""

import os
import CLI


def cls():
    """
    os.system快捷使用
    """
    os.system("cls")


print("Music163 网易云音乐下载")


input("确认并继续 请回车\n>>")

cls()
if not os.path.exists(os.path.abspath("./config.json")):
    choice = CLI.SclectBox(
        "选择你使用的浏览器...",
        "########\n建议将你的浏览器升级到最新版本",
        (
            (
                "Mircosoft Edge浏览器",
                (
                    "https://msedgedriver.azureedge.net/{version}/edgedriver_win64.zip",
                    "https://msedgedriver.azureedge.net/{version}/edgedriver_win32.zip",
                    "https://msedgedriver.azureedge.net/129.0.2759.0/edgedriver_arm64.zip",
                ),
            ),
        ),
    )
