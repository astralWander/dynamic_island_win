import time

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QWidget

from dynamic_island.battery import read_battery, read_mah
from dynamic_island.config import (CX, CY, ISLAND_H, ISLAND_TOP, ISLAND_W,
                                   PANEL_H, PANEL_W, REFRESH_INTERVAL_MS,
                                   WIN_H, WIN_W)
from dynamic_island.ui.render import paint_capsule, paint_panel
from dynamic_island.ui.theme import ISLAND, Fonts
from dynamic_island.utils import clamp, lerp


class DynamicIsland(QWidget):
    def __init__(self):
        super().__init__()
        self.reveal = 0.0
        self.expand = 0.0
        self.hover = 0.0
        self.expanded = False
        self.ready = False
        self.batt = read_battery()
        self.mah = read_mah()
        self.fonts = Fonts()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(WIN_W, WIN_H)
        self.setMouseTracking(True)

        ag = QApplication.primaryScreen().availableGeometry()
        self.move(ag.x() + (ag.width() - WIN_W) // 2, ag.top())

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(REFRESH_INTERVAL_MS)

        QTimer.singleShot(120, self._enter)

    def _animate(self, attr, to, dur, ease, done=None):
        anim = QVariantAnimation(self)
        anim.setStartValue(getattr(self, attr))
        anim.setEndValue(to)
        anim.setDuration(dur)
        anim.setEasingCurve(ease)
        anim.valueChanged.connect(lambda v: (setattr(self, attr, v), self.update()))
        if done:
            anim.finished.connect(done)
        anim.finished.connect(anim.deleteLater)
        anim.start()

    def _enter(self):
        self._animate("reveal", 1.0, 800, QEasingCurve.Type.OutQuint)
        QTimer.singleShot(820, lambda: setattr(self, "ready", True))

    def toggle(self):
        self.expanded = not self.expanded
        self._animate("expand", 1.0 if self.expanded else 0.0, 480,
                      QEasingCurve.Type.OutBack if self.expanded
                      else QEasingCurve.Type.OutQuint)

    def _refresh(self):
        self.batt = read_battery()
        self.mah = read_mah()
        self.update()

    def enterEvent(self, e):
        self._animate("hover", 1.0, 180, QEasingCurve.Type.OutCubic)

    def leaveEvent(self, e):
        self._animate("hover", 0.0, 220, QEasingCurve.Type.OutCubic)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            now = time.monotonic()
            if now - getattr(self, "last_right", -9.0) < 0.6:
                QApplication.quit()
            self.last_right = now
            return
        self.press = e.globalPosition().toPoint() - self.pos()
        self.moved = False

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton:
            delta = e.globalPosition().toPoint() - self.pos() - self.press
            if self.moved or abs(delta.x()) + abs(delta.y()) > 4:
                self.moved = True
                self.move(e.globalPosition().toPoint() - self.press)

    def mouseReleaseEvent(self, e):
        if self.ready and not self.moved and e.button() == Qt.MouseButton.LeftButton:
            self.toggle()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        e_ = self.expand
        s_eff = 1 + 0.045 * self.hover * (1 - e_)

        w = lerp(ISLAND_W, PANEL_W, e_) * s_eff
        h = lerp(ISLAND_H, PANEL_H, e_) * s_eff
        y0 = lerp(CY - h / 2, ISLAND_TOP, e_)
        x0 = CX - w / 2
        rect = QRectF(x0, y0, w, h)
        radius = lerp(h / 2, 26, e_)

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ISLAND)
        p.drawPath(path)

        if e_ > 0.03:
            p.save()
            p.setClipPath(path)
            grad = QLinearGradient(0, y0, 0, y0 + h * 0.55)
            grad.setColorAt(0.0, QColor(255, 255, 255, 26))
            grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.setBrush(QColor(0, 0, 0, 0))
            p.setPen(QPen(grad, 1.2))
            inner = QPainterPath()
            inner.addRoundedRect(rect.adjusted(1, 1, -1, -1), radius - 1, radius - 1)
            p.drawPath(inner)
            p.restore()

        p.setPen(QPen(QColor(255, 255, 255, 16), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        a_cap = clamp(1 - e_ * 2.2)
        a_pan = clamp((e_ - 0.5) * 2.4)
        if a_cap > 0.02:
            paint_capsule(p, rect, a_cap, self.batt or {}, self.mah, self.fonts)
        if a_pan > 0.02:
            paint_panel(p, rect, a_pan, self.batt or {}, self.fonts)

        if self.reveal < 1.0:
            rv = self.reveal
            band = 90.0
            fade = 1.0 - max(0.0, (rv - 0.55) / 0.45)
            x_pos = lerp(x0 - band, x0 + w + band, rv)
            grad = QLinearGradient(x_pos - band / 2, 0, x_pos + band / 2, 0)
            grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.15, QColor(0, 0, 0, int(240 * fade)))
            grad.setColorAt(0.85, QColor(0, 0, 0, int(240 * fade)))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.save()
            p.setClipPath(path)
            p.setPen(QPen(grad, band))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(QPointF(x_pos - 14, y0 - band), QPointF(x_pos + 14, y0 + h + band))
            p.restore()
