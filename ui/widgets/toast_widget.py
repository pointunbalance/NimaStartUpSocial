"""
ToastWidget - A non-blocking overlay notification that fades out.
"""
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect

class ToastWidget(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._build_ui(message)
        
        # Fade In
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        
        # Position and Auto-close
        QTimer.singleShot(10, self._position_toast)
        QTimer.singleShot(3000, self.fade_out)

    def _build_ui(self, message):
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setObjectName("toastLabel")
        self.label.setStyleSheet("""
            QLabel#toastLabel {
                background-color: rgba(15, 23, 42, 230);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.label)

    def _position_toast(self):
        parent = self.parentWidget()
        if parent:
            p_geo = parent.geometry()
            # Bottom-center of the parent window
            x = p_geo.x() + (p_geo.width() - self.width()) // 2
            y = p_geo.y() + p_geo.height() - self.height() - 40
            self.move(x, y)
        self.show()

    def fade_out(self):
        self.anim.setDirection(QPropertyAnimation.Direction.Backward)
        try:
            self.anim.finished.disconnect(self.close)
        except TypeError:
            pass
        self.anim.finished.connect(self.close)
        self.anim.start()

def show_toast(message, parent):
    """Static helper to show a toast message."""
    toast = ToastWidget(message, parent)
    return toast # Keep reference if needed
