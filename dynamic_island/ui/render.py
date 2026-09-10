from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen, QPolygonF

from dynamic_island.battery.status import fmt_life
from dynamic_island.ui.theme import GREEN, RED, WHITE
from dynamic_island.utils import clamp


def paint_capsule(p, rect, a, batt, mah, fonts):
    pct = batt.get("pct")
    charging = batt.get("charging")
    low = pct is not None and pct <= 20 and not charging
    acc = QColor(RED if low else GREEN)
    acc.setAlphaF(clamp(a))
    fg = QColor(WHITE)
    fg.setAlphaF(clamp(a) * 0.97)
    dim = QColor(WHITE)
    dim.setAlphaF(clamp(a) * 0.50)

    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    cy = y + h / 2
    p.setPen(Qt.PenStyle.NoPen)

    bs = 22.0
    badge = QRectF(x + 10, cy - bs / 2, bs, bs)
    p.setBrush(QColor(250, 250, 250, int(248 * a)))
    p.drawRoundedRect(badge, 7, 7)
    glyph = QColor(20, 22, 24, int(255 * a))
    p.setBrush(glyph)
    if charging:
        pts = [(1, -8.5), (-7.5, 1.5), (-1, 1.5), (-1.5, 8.5), (7.5, -1.5), (1, -1.5)]
        bolt = QPolygonF([QPointF(badge.center().x() + px * 0.78,
                                  badge.center().y() + py * 0.78)
                          for px, py in pts])
        p.drawPolygon(bolt)
    else:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(glyph, 1.4))
        p.drawRoundedRect(QRectF(badge.center().x() - 5, badge.center().y() - 3,
                                 10, 6), 1.6, 1.6)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glyph)
        p.drawRoundedRect(QRectF(badge.center().x() + 5.5,
                                 badge.center().y() - 1.5, 1.6, 3), 0.8, 0.8)

    cur, design = mah if mah else (None, None)
    big5 = cur is not None and cur >= 10000
    base = cy + 6
    cur_s = f"{cur}" if cur is not None else (f"{pct}" if pct is not None else "—")
    f_cur = fonts.cur5 if big5 else fonts.cur
    f_max = fonts.max5 if big5 else fonts.max
    p.setFont(f_cur)
    p.setPen(QPen(fg, 1))
    p.drawText(QPointF(x + 40, base), cur_s)
    cx = x + 40 + p.fontMetrics().horizontalAdvance(cur_s)
    if design is not None:
        p.setFont(f_max)
        p.setPen(QPen(dim, 1))
        p.drawText(QPointF(cx + 2, base), f"/{design}")
        cx += 2 + p.fontMetrics().horizontalAdvance(f"/{design}")
    p.setFont(f_max)
    p.setPen(QPen(dim, 1))
    p.drawText(QPointF(cx + 3, base), "mAh")

    p.setFont(fonts.pct)
    pct_s = f"{pct}" if pct is not None else "—"
    pw = p.fontMetrics().horizontalAdvance(pct_s)
    sym_w = p.fontMetrics().horizontalAdvance("%")
    pct_right = x + w - 40
    base2 = cy + 5.5
    p.setPen(QPen(fg, 1))
    p.drawText(QPointF(pct_right - sym_w - 4 - pw, base2), pct_s)
    p.setFont(f_max)
    p.setPen(QPen(dim, 1))
    p.drawText(QPointF(pct_right - sym_w, base2), "%")

    rc = QPointF(x + w - 21, cy)
    ro = 10.5
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(255, 255, 255, int(90 * a)), 2.2,
                  Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
    p.drawEllipse(rc, ro, ro)
    if pct is not None:
        p.setPen(QPen(acc, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        p.drawArc(QRectF(rc.x() - ro, rc.y() - ro, ro * 2, ro * 2),
                  90 * 16, -int(3.6 * pct * 16))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(acc)
    p.drawEllipse(rc, 5.5, 5.5)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(255, 255, 255, int(240 * a)), 1.0))
    p.drawRoundedRect(QRectF(rc.x() - 2.8, rc.y() - 1.7, 5.6, 3.4), 0.9, 0.9)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(255, 255, 255, int(240 * a)))
    p.drawRoundedRect(QRectF(rc.x() + 2.9, rc.y() - 0.8, 1.1, 1.6), 0.5, 0.5)


def paint_panel(p, rect, a, batt, fonts):
    pct = batt.get("pct")
    charging = batt.get("charging")
    low = pct is not None and pct <= 20 and not charging
    accent = QColor(GREEN if charging else (RED if low else WHITE))
    fg = QColor(WHITE)
    fg.setAlphaF(clamp(a) * 0.95)
    gray = QColor(WHITE)
    gray.setAlphaF(clamp(a) * 0.55)
    dim = QColor(WHITE)
    dim.setAlphaF(clamp(a) * 0.18)
    ac = QColor(accent)
    ac.setAlphaF(clamp(a))

    rr = 42.0
    center = QPointF(rect.x() + 92, rect.y() + 85)
    box = QRectF(center.x() - rr, center.y() - rr, rr * 2, rr * 2)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(dim, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawArc(box, 0, 360 * 16)
    p.setPen(QPen(ac, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawArc(box, 90 * 16, -int(3.6 * (pct or 0) * 16))

    p.setPen(QPen(ac if (charging or low) else fg, 1))
    p.setFont(fonts.big)
    p.drawText(QRectF(center.x() - rr, center.y() - 20, rr * 2, 40),
               Qt.AlignmentFlag.AlignCenter,
               f"{pct}%" if pct is not None else "—")

    rx = rect.right() - 32
    if charging:
        status = "正在充电"
    elif batt.get("ac"):
        status = "已接通电源"
    elif pct is None:
        status = "未检测到电池"
    elif pct <= 20:
        status = "电量偏低"
    elif pct < 50:
        status = "电量中等"
    else:
        status = "电量充足"

    p.setPen(QPen(gray, 1))
    p.setFont(fonts.eyebrow)
    p.drawText(QPointF(rx - p.fontMetrics().horizontalAdvance("电池"), rect.y() + 34), "电池")

    p.setPen(QPen(fg, 1))
    p.setFont(fonts.status)
    p.drawText(QPointF(rx - p.fontMetrics().horizontalAdvance(status), rect.y() + 64), status)

    life = batt.get("life")
    if life and not batt.get("ac"):
        sub = fmt_life(life)
        p.setPen(QPen(gray, 1))
        p.setFont(fonts.sub)
        p.drawText(QPointF(rx - p.fontMetrics().horizontalAdvance(sub), rect.y() + 90), sub)
