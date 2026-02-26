import ctypes
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor

class WindowBlurService:
    @staticmethod
    def enable_acrylic(window: QWidget, color: QColor = QColor(255, 255, 255, 128)):
        """
        Enables the Acrylic blur effect on Windows 10/11.
        """
        if not window.isWindow():
            return

        hwnd = int(window.winId())
        
        # Windows 10/11 Window Composition Attribute
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint)
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t)
            ]

        accent = ACCENT_POLICY()
        accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
        
        # Acrylic effect (AccentState = 4) requires a gradient color
        # Format: 0xAABBGGRR
        rgba = (color.alpha() << 24) | (color.blue() << 16) | (color.green() << 8) | color.red()
        accent.AccentState = 4
        accent.GradientColor = rgba

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.pointer(accent)

        # Set argtypes for robustness
        ctypes.windll.user32.SetWindowCompositionAttribute.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)
        ]
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

    @staticmethod
    def enable_mica(window: QWidget, dark: bool = False):
        """
        Enables the Mica effect on Windows 11.
        """
        hwnd = window.winId()
        
        # DWMWA_MICA_EFFECT = 1029
        # DWMWA_SYSTEMBACKDROP_TYPE = 38
        
        # For Windows 11 22H2 and later
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMSBT_MAINWINDOW = 2  # Mica
        
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_SYSTEMBACKDROP_TYPE, 
                ctypes.byref(ctypes.c_int(DWMSBT_MAINWINDOW)), 
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            # Fallback for older Win11 versions
            DWMWA_MICA_EFFECT = 1029
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_MICA_EFFECT, 
                ctypes.byref(ctypes.c_int(1)), 
                ctypes.sizeof(ctypes.c_int)
            )
