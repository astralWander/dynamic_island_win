import ctypes
from ctypes import wintypes

GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE = 0x2
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

_kernel32 = ctypes.windll.kernel32
_kernel32.CreateFileW.restype = wintypes.HANDLE
_kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
_kernel32.DeviceIoControl.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID,
                                      wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                                      ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def _ctl(dev, func):
    return (dev << 16) | (1 << 14) | (func << 2)


IOCTL_BATTERY_QUERY_TAG = _ctl(0x2A, 0x00)
IOCTL_BATTERY_QUERY_INFORMATION = _ctl(0x2A, 0x01)
IOCTL_BATTERY_QUERY_STATUS = _ctl(0x2A, 0x03)


class BATTERY_WAIT_FOR_TAG(ctypes.Structure):
    _fields_ = [("BatteryTag", wintypes.ULONG), ("Timeout", wintypes.ULONG)]


class BATTERY_QUERY_INFORMATION(ctypes.Structure):
    _fields_ = [("BatteryTag", wintypes.ULONG), ("InformationLevel", wintypes.ULONG),
                ("AtRate", ctypes.c_long)]


class BATTERY_INFORMATION(ctypes.Structure):
    _fields_ = [("Capabilities", wintypes.ULONG), ("Technology", ctypes.c_ubyte),
                ("Reserved", ctypes.c_ubyte * 3), ("Chemistry", ctypes.c_ubyte * 4),
                ("DesignedCapacity", wintypes.ULONG), ("FullChargedCapacity", wintypes.ULONG),
                ("DefaultAlert1", wintypes.ULONG), ("DefaultAlert2", wintypes.ULONG),
                ("CriticalBias", wintypes.ULONG), ("CycleCount", wintypes.ULONG)]


class BATTERY_QUERY_STATUS(ctypes.Structure):
    _fields_ = [("BatteryTag", wintypes.ULONG), ("Timeout", wintypes.ULONG),
                ("PowerState", wintypes.ULONG)]


class BATTERY_STATUS(ctypes.Structure):
    _fields_ = [("PowerState", wintypes.ULONG), ("Capacity", wintypes.ULONG),
                ("Voltage", wintypes.ULONG), ("Rate", ctypes.c_long)]


def read_mah():
    try:
        h = _kernel32.CreateFileW("\\\\.\\Battery0", GENERIC_READ,
                                  FILE_SHARE_READ | FILE_SHARE_WRITE, None,
                                  OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
        if h not in (None, INVALID_HANDLE_VALUE):
            try:
                ret = wintypes.ULONG(0)
                wait = BATTERY_WAIT_FOR_TAG(0, 0)
                tag = wintypes.ULONG(0)
                if _kernel32.DeviceIoControl(h, IOCTL_BATTERY_QUERY_TAG,
                                             ctypes.byref(wait), ctypes.sizeof(wait),
                                             ctypes.byref(tag), ctypes.sizeof(tag),
                                             ctypes.byref(ret), None) and tag.value:
                    info = BATTERY_QUERY_INFORMATION(tag.value, 0, 0)
                    buf = ctypes.create_string_buffer(64)
                    qs = BATTERY_QUERY_STATUS(tag.value, 0, 0)
                    sbuf = ctypes.create_string_buffer(32)
                    if (_kernel32.DeviceIoControl(h, IOCTL_BATTERY_QUERY_INFORMATION,
                                                  ctypes.byref(info), ctypes.sizeof(info),
                                                  buf, 64, ctypes.byref(ret), None)
                            and _kernel32.DeviceIoControl(h, IOCTL_BATTERY_QUERY_STATUS,
                                                          ctypes.byref(qs), ctypes.sizeof(qs),
                                                          sbuf, 32, ctypes.byref(ret), None)):
                        bi = BATTERY_INFORMATION.from_buffer_copy(buf)
                        bs = BATTERY_STATUS.from_buffer_copy(sbuf)
                        design = bi.DesignedCapacity or bi.FullChargedCapacity
                        if design and bs.Capacity:
                            return int(bs.Capacity), int(design)
            finally:
                _kernel32.CloseHandle(h)
    except Exception:
        pass
    try:
        import wmi
        w = wmi.WMI(namespace="root\\wmi")
        design = w.BatteryStaticData()[0].DesignedCapacity
        try:
            design = w.BatteryFullChargedCapacity()[0].FullChargedCapacity or design
        except Exception:
            pass
        cur = w.BatteryStatus()[0].RemainingCapacity
        if design and cur:
            return int(cur), int(design)
    except Exception:
        pass
    return None
