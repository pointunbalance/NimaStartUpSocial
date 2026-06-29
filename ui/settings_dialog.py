"""
SettingsDialog - Configuration dialog for theme, card size, and colors.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QFormLayout, QSpinBox, QColorDialog
)
from PyQt6.QtGui import QColor
from logic.theme_service import ThemeService
from utils.strings import get_string
from utils.window_blur import WindowBlurService
from utils.logger_service import logger


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        if parent and hasattr(parent, "windowIcon"):
            self.setWindowIcon(parent.windowIcon())
        self.resize(450, 400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        try:
            WindowBlurService.enable_acrylic(self, QColor(15, 23, 42, 220))
        except Exception as e:
            logger.debug(f"Acrylic blur unavailable: {e}")

        self._old_pos = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("settingsContainer")
        container.setStyleSheet("""
            QFrame#settingsContainer {
                background-color: rgba(15, 23, 42, 230);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.setDirection(QHBoxLayout.Direction.RightToLeft)
        title = QLabel("⚙  Settings")
        title.setStyleSheet("color: #f8fafc; font-size: 20px; font-weight: 800; background: transparent;")
        header.addWidget(title)
        header.addStretch(1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 10);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 16px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 60);
                color: #f8fafc;
            }
        """)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)
        layout.addLayout(header)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 10);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                padding: 8px 12px;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #94a3b8; margin-right: 12px; }
            QComboBox QAbstractItemView {
                background: rgba(15, 23, 42, 240);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                selection-background-color: rgba(13, 148, 136, 100);
            }
        """)
        for name in ThemeService.get_theme_display_names():
            self.theme_combo.addItem(name)

        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        form.addRow(theme_label, self.theme_combo)

        self.card_size_spin = QSpinBox()
        self.card_size_spin.setRange(100, 240)
        self.card_size_spin.setValue(160)
        self.card_size_spin.setSingleStep(10)
        self.card_size_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255, 255, 255, 10);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                padding: 8px 12px;
            }
            QSpinBox:focus { border: 1px solid rgba(13, 148, 136, 150); }
        """)

        size_label = QLabel("Card Size:")
        size_label.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        form.addRow(size_label, self.card_size_spin)

        self.accent_btn = QPushButton("Choose Color")
        self.accent_btn.setFixedHeight(36)
        self.accent_btn.setStyleSheet("""
            QPushButton {
                background: rgba(13, 148, 136, 100);
                color: #f8fafc;
                border: 1px solid rgba(13, 148, 136, 150);
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover { background: rgba(13, 148, 136, 150); }
        """)
        self.accent_btn.clicked.connect(self._pick_color)

        accent_label = QLabel("Accent Color:")
        accent_label.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        form.addRow(accent_label, self.accent_btn)

        layout.addLayout(form)
        layout.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.setDirection(QHBoxLayout.Direction.RightToLeft)

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0d9488;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 700;
            }
            QPushButton:hover { background: #0f766e; }
        """)
        apply_btn.clicked.connect(self._apply)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 10);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 20); }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(apply_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        root.addWidget(container)

    def _pick_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.accent_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color.name()};
                    color: #ffffff;
                    border: 1px solid {color.name()};
                    border-radius: 10px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background: {color.name()}dd; }}
            """)
            self._selected_color = color

    def _apply(self):
        self.accept()

    def get_selected_theme(self) -> str:
        idx = self.theme_combo.currentIndex()
        return ThemeService.get_theme_names()[idx]

    def get_card_size(self) -> int:
        return self.card_size_spin.value()

    def get_accent_color(self) -> QColor:
        return getattr(self, '_selected_color', QColor(13, 148, 136))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None
