from functools import partial

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QStringListModel
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QGridLayout, QLineEdit,
    QGraphicsOpacityEffect, QFrame, QTabBar, QCompleter
)
from PyQt6.QtGui import QColor

from models.shortcut import Shortcut
from logic.shortcut_service import ShortcutService
from logic.browser_service import BrowserService
from logic.theme_service import ThemeService
from logic.notification_service import NotificationService
from ui.widgets.shortcut_card import ShortcutCard
from ui.widgets.toast_widget import show_toast
from utils.strings import get_string
from utils.resource_loader import get_app_icon
from utils.window_blur import WindowBlurService
from utils.logger_service import logger
from utils.constants import (
    TILE_SPACING, POPULAR_LIMIT,
    ANIM_BASE_DURATION, ANIM_STEP_DURATION
)

LAUNCHER_WIDTH = 340
LAUNCHER_HEIGHT = 700
LAUNCHER_COLS = 2
LAUNCHER_CARD_SIZE = 140


class LauncherScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{get_string('app_name')} - Launcher")
        self.setWindowIcon(get_app_icon())
        self.resize(LAUNCHER_WIDTH, LAUNCHER_HEIGHT)
        self.setMinimumSize(LAUNCHER_WIDTH, 500)
        self.setMaximumWidth(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._apply_blur()

        self._old_pos = None
        self._anims = []

        self.service = ShortcutService()
        self.browsers = BrowserService.get_installed_browsers()
        self.filter_query = ""
        self._main_window = None
        self._settings_dialog = None

        self._build_ui()

        QTimer.singleShot(200, self._refresh_grid)
        self._update_category_tabs()

    def _apply_blur(self):
        theme = ThemeService.get_theme()
        try:
            WindowBlurService.enable_acrylic(self, theme["blur_color"])
        except Exception as e:
            logger.warning(f"Acrylic blur unavailable: {e}")

    def _build_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        theme = ThemeService.get_theme()

        container = QWidget()
        container.setObjectName("launcherContainer")
        container.setStyleSheet(f"""
            QWidget#launcherContainer {{
                background-color: {theme['bg_primary']};
                border: 1px solid {theme['border']};
                border-radius: 20px;
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setDirection(QHBoxLayout.Direction.RightToLeft)

        title = QLabel(get_string("app_name"))
        title.setStyleSheet(f"color: {theme['text_primary']}; font-size: 18px; font-weight: 800; background: transparent;")
        header.addWidget(title)

        header.addStretch(1)

        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(32, 32)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 18);
                color: {theme['text_primary']};
            }}
        """)
        notif_btn.clicked.connect(self._show_notifications)
        header.addWidget(notif_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 16px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: rgba(239, 68, 68, 60);
                color: {theme['text_primary']};
                border-color: rgba(239, 68, 68, 100);
            }}
        """)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)

        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  " + get_string("placeholder_search"))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme['border_hover']};
                background: {theme['bg_secondary']};
            }}
            QLineEdit::placeholder {{
                color: {theme['text_secondary']};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        self._setup_autocomplete()
        layout.addWidget(self.search_input)

        self.category_tabs = QTabBar()
        self.category_tabs.setExpanding(False)
        self.category_tabs.setDrawBase(False)
        self.category_tabs.setStyleSheet(f"""
            QTabBar {{ background: transparent; border: none; }}
            QTabBar::tab {{
                background: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
                color: {theme['text_secondary']};
                font-weight: 600;
                font-size: 11px;
            }}
            QTabBar::tab:hover {{
                background: rgba(255, 255, 255, 18);
                color: {theme['text_primary']};
            }}
            QTabBar::tab:selected {{
                background: {theme['accent']};
                color: #ffffff;
                border-color: {theme['accent']};
            }}
        """)
        self.category_tabs.currentChanged.connect(lambda: self._refresh_grid(animate=False))
        layout.addWidget(self.category_tabs)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 5);
                width: 5px;
                margin: 3px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 100);
                min-height: 25px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(13, 148, 136, 150);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(4, 8, 4, 8)
        self.grid_layout.setSpacing(TILE_SPACING)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll, 1)

        footer = QHBoxLayout()
        footer.setDirection(QHBoxLayout.Direction.RightToLeft)

        self._count_label = QLabel()
        self._count_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 11px; background: transparent;")
        footer.addWidget(self._count_label)

        footer.addStretch(1)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 18);
                color: {theme['text_primary']};
            }}
        """)
        settings_btn.clicked.connect(self._open_settings)
        footer.addWidget(settings_btn)

        layout.addLayout(footer)
        root.addWidget(container)

    def _setup_autocomplete(self):
        names = [s.name for s in self.service.shortcuts]
        names.extend([s.name_en for s in self.service.shortcuts if s.name_en])
        completer = QCompleter(list(set(names)), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setStyleSheet("""
            QCompleter {
                background: rgba(15, 23, 42, 240);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
            }
        """)
        self.search_input.setCompleter(completer)

    def _show_notifications(self):
        notifications = NotificationService.get_all()
        if not notifications:
            show_toast("No notifications", self)
            return
        unread = NotificationService.get_unread_count()
        show_toast(f"{unread} unread notifications", self)
        NotificationService.mark_all_read()

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        self._settings_dialog = SettingsDialog(self)
        if self._settings_dialog.exec():
            theme_name = self._settings_dialog.get_selected_theme()
            ThemeService.set_theme(theme_name)
            self._apply_blur()
            self._rebuild_ui()

    def _rebuild_ui(self):
        self._build_ui()
        QTimer.singleShot(100, self._refresh_grid)
        self._update_category_tabs()

    def _on_search_changed(self, text):
        self.filter_query = text.strip().lower()
        self._refresh_grid(animate=False)

    def _update_category_tabs(self):
        self.category_tabs.blockSignals(True)
        current = self.category_tabs.tabText(self.category_tabs.currentIndex()) if self.category_tabs.count() > 0 else get_string("cat_all")

        while self.category_tabs.count() > 0:
            self.category_tabs.removeTab(0)
        self.category_tabs.addTab(get_string("cat_all"))
        self.category_tabs.addTab(get_string("cat_popular"))

        cat_map = {
            "AI": get_string("cat_ai"),
            "Social": get_string("cat_social"),
            "Work": get_string("cat_work"),
            "General": get_string("cat_general"),
        }
        for cat in self.service.get_categories():
            self.category_tabs.addTab(cat_map.get(cat, cat))
            self.category_tabs.setTabData(self.category_tabs.count() - 1, cat)

        for i in range(self.category_tabs.count()):
            if i == 0 and current == get_string("cat_all"):
                self.category_tabs.setCurrentIndex(i)
                break
            elif self.category_tabs.tabText(i) == current or self.category_tabs.tabData(i) == current:
                self.category_tabs.setCurrentIndex(i)
                break

        self.category_tabs.blockSignals(False)

    def _refresh_grid(self, animate: bool = True):
        self._anims.clear()
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        current_idx = self.category_tabs.currentIndex()
        selected_cat_text = self.category_tabs.tabText(current_idx) if current_idx >= 0 else get_string("cat_all")
        active_cat_data = self.category_tabs.tabData(current_idx)

        is_popular = selected_cat_text == get_string("cat_popular")
        if is_popular:
            visible = self.service.get_popular(POPULAR_LIMIT)
        elif active_cat_data:
            visible = self.service.filter(self.filter_query, active_cat_data)
        else:
            visible = self.service.filter(self.filter_query)

        if self._count_label:
            self._count_label.setText(f"{len(visible)} shortcuts")

        for i, shortcut in enumerate(visible):
            card = ShortcutCard(shortcut, self._open_shortcut)
            card.setFixedSize(LAUNCHER_CARD_SIZE, LAUNCHER_CARD_SIZE)
            self.grid_layout.addWidget(card, i // LAUNCHER_COLS, i % LAUNCHER_COLS)
            if animate:
                eff = QGraphicsOpacityEffect(card)
                card.setGraphicsEffect(eff)
                eff.setOpacity(0)
                anim = QPropertyAnimation(eff, b"opacity")
                anim.setDuration(ANIM_BASE_DURATION + (i * ANIM_STEP_DURATION))
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._anims.append(anim)
                anim.finished.connect(partial(self._clear_effect, card))
                anim.start()
            else:
                card.show()

        self.grid_layout.activate()
        self.grid_widget.adjustSize()

    def _clear_effect(self, widget):
        widget.setGraphicsEffect(None)

    def _open_shortcut(self, shortcut: Shortcut):
        self.service.increment_clicks(shortcut)
        NotificationService.add("shortcut_opened", shortcut.name, "info")
        browser_key = shortcut.browser
        if browser_key == "default":
            browser_key = self.service.global_browser
        success = BrowserService.open_url(shortcut.url, browser_key, self.browsers)
        if not success:
            NotificationService.notify_browser_error()
            show_toast(get_string("msg_browser_error"), self)

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
