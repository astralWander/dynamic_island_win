import ctypes


class POWER_STATUS(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_byte),
                ("BatteryFlag", ctypes.c_byte),
                ("BatteryLifePercent", ctypes.c_byte),
                ("Reserved1", ctypes.c_byte),
                ("BatteryLifeTime", ctypes.c_uint32),
                ("BatteryFullLifeTime", ctypes.c_uint32)]


def read_battery():
    ps = POWER_STATUS()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(ps)):
        return None
    pct = ps.BatteryLifePercent
    life = ps.BatteryLifeTime
    return {
        "pct": None if pct in (0, 255) or ps.BatteryFlag & 128 else pct,
        "ac": ps.ACLineStatus == 1,
        "charging": bool(ps.BatteryFlag & 8),
        "life": life if 0 < life < 10 ** 8 else None,
    }


def fmt_life(sec):
    h, m = sec // 3600, sec % 3600 // 60
    if h:
        return f"约 {h} 小时 {m} 分"
    return f"约 {m} 分钟"
