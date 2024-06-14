#!C:/Users/manju/PycharmProjects/aion-prod-auto/venv/Scripts/python.exe
import sys

import pyuac
from PyQt5.QtWidgets import QApplication

from app.gui import BotGui
from config import root_logger


def main():
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
        sys.exit(0)
    else:
        root_logger.info("Start app")
        app = QApplication(sys.argv)
        ex = BotGui()
        ex.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
