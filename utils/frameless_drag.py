from PyQt6.QtCore import Qt


class FramelessDragMixin:
    """Mixin for frameless window dragging. Use with QMainWindow/QDialog."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._old_pos = None
        super().mouseReleaseEvent(event)
