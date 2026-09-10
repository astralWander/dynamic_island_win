import sys

from PySide6.QtWidgets import QApplication

from dynamic_island.battery import read_battery, read_mah
from dynamic_island.ui.island import DynamicIsland


def run(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--check" in argv:
        print(read_battery())
        print("mAh:", read_mah())
        return 0
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    island = DynamicIsland()
    island.show()
    return app.exec()
