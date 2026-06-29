"""
ShortcutCard - A draggable tile widget representing a single shortcut.
Uses glassmorphism styling with FontAwesome icons and smooth hover animations.
"""
import qtawesome as qta
from PyQt6.QtCore import Qt, QSize, QMimeData, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QDrag, QPixmap, QColor
from models.shortcut import Shortcut
from logic.catalog_service import SiteCatalog
from utils.constants import DRAG_THRESHOLD, CARD_SIZE, ICON_BUTTON_SIZE


class ShortcutCard(QFrame):
    def __init__(self, shortcut: Shortcut, on_open_clicked):
        super().__init__()
        self.shortcut = shortcut
        self.on_open_clicked = on_open_clicked
        self._drag_start_pos = None
        self._hover_progress = 0.0
        self._icon_color = QColor(13, 148, 136)

        self.setObjectName("shortcutCard")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(CARD_SIZE, CARD_SIZE)

        self._build_ui()
        self._setup_hover_animation()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 20, 16, 16)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_letters, icon_color, fa_icon_name = SiteCatalog.get_icon_meta(self.shortcut)
        self._icon_color = QColor(icon_color)

        self.icon_btn = QPushButton()
        self.icon_btn.setObjectName("siteCircleOpen")
        self.icon_btn.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        if fa_icon_name == "APP_ICON":
            from utils.resource_loader import get_app_icon
            icon = get_app_icon()
            if icon and not icon.isNull():
                self.icon_btn.setIcon(icon)
                self.icon_btn.setIconSize(QSize(42, 42))
            self.icon_btn.setText("")
        elif fa_icon_name:
            icon = qta.icon(fa_icon_name, color='white')
            self.icon_btn.setIcon(icon)
            self.icon_btn.setIconSize(QSize(32, 32))
            self.icon_btn.setText("")
        else:
            self.icon_btn.setText(icon_letters)

        self.icon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {icon_color};
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 32px;
                font-size: 20px;
                font-weight: 700;
            }}
        """)

        self.title = QLabel(self.shortcut.name)
        self.title.setObjectName("shortcutTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setStyleSheet("font-weight: 600; font-size: 15px;")

        main_layout.addWidget(self.icon_btn, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title, 0, Qt.AlignmentFlag.AlignCenter)

        if self.shortcut.hotkey:
            self.hotkey_badge = QLabel(self.shortcut.hotkey)
            self.hotkey_badge.setObjectName("hotkeyBadge")
            self.hotkey_badge.setParent(self)
            self.hotkey_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hotkey_badge.setStyleSheet("""
                QLabel#hotkeyBadge {
                    background-color: rgba(13, 148, 136, 180);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 40);
                    border-radius: 6px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: 700;
                }
            """)
            self.hotkey_badge.move(8, 8)
            self.hotkey_badge.show()

        main_layout.addStretch(1)
        self.setToolTip(self.shortcut.url)

    def _setup_hover_animation(self):
        self._hover_anim = QPropertyAnimation(self, b"hoverProgress")
        self._hover_anim.setDuration(200)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        self._hover_progress = value
        r = self._icon_color.red()
        g = self._icon_color.green()
        b = self._icon_color.blue()
        border_alpha = int(60 + value * 100)
        bg_alpha = int(25 + value * 40)
        border_color = f"rgba({r}, {g}, {b}, {border_alpha})"
        bg_color = f"rgba(255, 255, 255, {bg_alpha})"

        self.setStyleSheet(f"""
            QFrame#shortcutCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 20px;
            }}
        """)

    hoverProgress = pyqtProperty(float, _get_hover_progress, _set_hover_progress)

    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    # ── Drag & Drop ─────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self._drag_start_pos:
            return
        if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < DRAG_THRESHOLD:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.shortcut.url)
        drag.setMimeData(mime)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if (self._drag_start_pos and
                (event.position().toPoint() - self._drag_start_pos).manhattanLength() < DRAG_THRESHOLD):
                self.on_open_clicked(self.shortcut)
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)
