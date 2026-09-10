from PySide6.QtGui import QColor, QFont

from dynamic_island.config import FONT_STACK

ISLAND = QColor(34, 36, 38, 222)
WHITE = QColor(245, 245, 247)
GREEN = QColor(48, 209, 88)
RED = QColor(255, 69, 58)


def font(size, weight=QFont.Weight.Normal, px=False):
    f = QFont()
    f.setFamilies(FONT_STACK)
    if px:
        f.setPixelSize(size)
    else:
        f.setPointSizeF(size)
    f.setWeight(weight)
    return f


class Fonts:
    def __init__(self):
        self.pct = font(16, QFont.Weight.Bold, px=True)
        self.cur = font(18, QFont.Weight.Bold, px=True)
        self.cur5 = font(16, QFont.Weight.Bold, px=True)
        self.max = font(11, QFont.Weight.Normal, px=True)
        self.max5 = font(10, QFont.Weight.Normal, px=True)
        self.big = font(20, QFont.Weight.Bold)
        self.eyebrow = font(9.5)
        self.status = font(14, QFont.Weight.DemiBold)
        self.sub = font(9.5)
