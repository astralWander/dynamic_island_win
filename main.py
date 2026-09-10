# Copyright (c) 2026 LZY. All Rights Reserved.
# Author: LZY
# Date: 2026-09-10
# Description: 仿 macOS 灵动岛风格的 Windows 电量悬浮窗，常驻屏幕顶部，
#              实时显示电池电量、毫安容量与充电状态，支持展开面板、
#              拖动定位与低电量警示。
import sys

from dynamic_island.app import run

if __name__ == "__main__":
    sys.exit(run())
