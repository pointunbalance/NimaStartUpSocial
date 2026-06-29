from functools import partial

from PyQt6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QGridLayout, QCheckBox,
    QGraphicsOpacityEffect, QFrame, QLineEdit, QApplication,
    QComboBox, QTabBar
)
from PyQt6.QtGui import QColor, QShortcut, QKeySequence

from models.shortcut import Shortcut
from logic.shortcut_service import ShortcutService
from logic.title_service import TitleFetcher
from logic.browser_service import BrowserService
from logic.autostart_service import AutostartService
from logic.catalog_service import SiteCatalog
from logic.tray_service import SystemTrayService
from ui.widgets.shortcut_card import ShortcutCard
from ui.widgets.toast_widget import show_toast
from ui.widgets.dashboard_widget import DashboardWidget
from ui.shortcuts_dialog import ShortcutsDialog
from utils.strings import get_string
from utils.resource_loader import get_app_icon
from utils.window_blur import WindowBlurService
from utils.logger_service import logger
from utils.path_utils import APP_VERSION
from utils.constants import (
    GRID_COLS, TILE_SPACING, TILE_STEP, DEV_URL,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    SEARCH_INPUT_WIDTH, BROWSER_COMBO_WIDTH, POPULAR_LIMIT,
    ANIM_BASE_DURATION, ANIM_STEP_DURATION
)
from utils.frameless_drag import FramelessDragMixin


class MainWindow(FramelessDragMixin, QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{get_string('app_name')} v{APP_VERSION}")
        self.setWindowIcon(get_app_icon())
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        try:
            WindowBlurService.enable_acrylic(self, QColor(255, 255, 255, 40))
        except Exception as e:
            logger.warning(f"Acrylic blur unavailable: {e}")

        self._anims: list = []
        self._fetchers: list = []

        self.service = ShortcutService()
        self.browsers = BrowserService.get_installed_browsers()
        self.filter_query = ""

        self._build_ui()
        self._setup_window_hotkeys()
        self._setup_shortcuts()

        self.tray = SystemTrayService(self)
        self.tray.show()

        QTimer.singleShot(300, self._refresh_grid)
        self._update_category_tabs()

    def show_and_activate(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def quit_application(self):
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()
            show_toast(get_string("msg_app_background"), self)
        else:
            event.accept()

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self._open_manager)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search_input.setFocus())

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(24)

        top_bar = QHBoxLayout()
        top_bar.setDirection(QHBoxLayout.Direction.RightToLeft)
        top_bar.setSpacing(16)

        title = QLabel(get_string("app_name"))
        title.setObjectName("windowMainTitle")
        top_bar.addWidget(title)

        top_bar.addSpacing(40)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(get_string("placeholder_search"))
        self.search_input.setObjectName("mainSearchInput")
        self.search_input.setFixedWidth(SEARCH_INPUT_WIDTH)
        self.search_input.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self.search_input)

        top_bar.addStretch(1)

        manage_btn = QPushButton(get_string("shortcuts_manager_title"))
        manage_btn.setObjectName("secondaryBtn")
        manage_btn.setToolTip("Ctrl+M")
        manage_btn.clicked.connect(self._open_manager)
        top_bar.addWidget(manage_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("dangerBtn")
        close_btn.setFixedSize(40, 40)
        close_btn.setToolTip("Ctrl+Q")
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        layout.addLayout(top_bar)

        self.category_tabs = QTabBar()
        self.category_tabs.setObjectName("categoryTabs")
        self.category_tabs.setExpanding(False)
        self.category_tabs.setDrawBase(False)
        self.category_tabs.currentChanged.connect(lambda: self._refresh_grid(animate=False))

        tabs_container = QHBoxLayout()
        tabs_container.setContentsMargins(24, 0, 24, 10)
        tabs_container.addWidget(self.category_tabs)
        tabs_container.addStretch(1)
        layout.addLayout(tabs_container)

        self.dashboard = DashboardWidget()
        layout.addWidget(self.dashboard)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("mainScroll")
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.viewport().setAutoFillBackground(False)

        self.grid_widget = QWidget()
        self.grid_widget.setObjectName("shortcutsGrid")
        self.grid_widget.setAcceptDrops(True)
        self.grid_widget.dragEnterEvent = self._grid_drag_enter
        self.grid_widget.dragMoveEvent = self._grid_drag_move
        self.grid_widget.dropEvent = self._grid_drop

        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(24, 24, 24, 40)
        self.grid_layout.setSpacing(TILE_SPACING)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll, 1)

        footer = QHBoxLayout()
        footer.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.autostart_check = QCheckBox(get_string("checkbox_autostart"))
        self.autostart_check.setChecked(AutostartService.is_enabled())
        self.autostart_check.toggled.connect(AutostartService.set_enabled)
        footer.addWidget(self.autostart_check)
        footer.addStretch(1)

        browser_label = QLabel(get_string("label_global_browser"))
        browser_label.setStyleSheet("color: #475569; font-weight: 500;")
        footer.addWidget(browser_label)

        self.browser_combo = QComboBox()
        self.browser_combo.setObjectName("browserSelector")
        self.browser_combo.setFixedWidth(BROWSER_COMBO_WIDTH)
        self.browser_combo.addItem(get_string("browser_default"), "default")

        for key, path in self.browsers.items():
            name = get_string(f"browser_{key}")
            self.browser_combo.addItem(name, key)

        idx = self.browser_combo.findData(self.service.global_browser)
        if idx != -1:
            self.browser_combo.setCurrentIndex(idx)

        self.browser_combo.currentIndexChanged.connect(self._on_global_browser_changed)
        footer.addWidget(self.browser_combo)

        layout.addLayout(footer)

    def _on_global_browser_changed(self, index):
        self.service.global_browser = self.browser_combo.itemData(index)
        self.service.save()
        show_toast(get_string("msg_browser_saved"), self)

    def _setup_window_hotkeys(self):
        if hasattr(self, "_shortcut_bindings"):
            for s in self._shortcut_bindings:
                s.setEnabled(False)
                s.deleteLater()

        self._shortcut_bindings = []
        for s in self.service.shortcuts:
            if s.hotkey:
                qs = QShortcut(QKeySequence(s.hotkey), self)
                qs.activated.connect(lambda target=s: self._open_shortcut(target))
                self._shortcut_bindings.append(qs)

    def _on_search_changed(self, text):
        self.filter_query = text.strip().lower()
        self._refresh_grid(animate=False)

    def _find_target_index(self, pos: QPoint) -> int:
        child = self.grid_widget.childAt(pos)
        if child:
            parent = child
            while parent and not isinstance(parent, ShortcutCard):
                parent = parent.parentWidget()
            if parent and isinstance(parent, ShortcutCard):
                for i, s in enumerate(self.service.shortcuts):
                    if s.url == parent.shortcut.url:
                        return i

        grid_w = self.grid_widget.width()
        col = (grid_w - pos.x()) // TILE_STEP
        row = pos.y() // TILE_STEP
        return min(len(self.service.shortcuts) - 1, max(0, row * GRID_COLS + col))

    def _grid_drag_enter(self, event) -> None:
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _grid_drag_move(self, event) -> None:
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _grid_drop(self, event) -> None:
        mime = event.mimeData()
        url = ""
        if mime.hasUrls():
            url = mime.urls()[0].toString()
        elif mime.hasText():
            url = mime.text().strip()

        if not url:
            return

        pos = event.position().toPoint()
        src_idx = next((i for i, s in enumerate(self.service.shortcuts) if s.url == url), -1)

        if src_idx == -1:
            self._handle_external_drop(url, event)
        else:
            self._handle_internal_reorder(src_idx, url, pos, event)

    def _handle_external_drop(self, url: str, event) -> None:
        shortcut = self.service.add(url)
        if shortcut is None:
            show_toast(get_string("msg_site_exists"), self)
            event.accept()
            return

        fetcher = TitleFetcher(url)
        fetcher.finished.connect(self._on_title_fetched)
        fetcher.finished.connect(lambda *_: self._fetchers.remove(fetcher) if fetcher in self._fetchers else None)
        self._fetchers.append(fetcher)
        fetcher.start()

        QTimer.singleShot(50, lambda: self._refresh_grid(animate=False))
        self._update_category_tabs()
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        show_toast(f"{get_string('msg_added')} {shortcut.name}", self)

    def _on_title_fetched(self, url, title):
        if self.service.update_title(url, title):
            self._refresh_grid(animate=False)

    def _handle_internal_reorder(self, src_idx: int, url: str, pos: QPoint, event) -> None:
        target_idx = self._find_target_index(pos)
        if self.service.reorder(src_idx, target_idx):
            QTimer.singleShot(50, lambda: self._refresh_grid(animate=False))
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()

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

    def _refresh_grid(self, animate: bool = True) -> None:
        self._anims.clear()
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        current_idx = self.category_tabs.currentIndex()
        selected_cat_text = self.category_tabs.tabText(current_idx)
        active_cat_data = self.category_tabs.tabData(current_idx)

        is_popular = selected_cat_text == get_string("cat_popular")
        if is_popular:
            visible_shortcuts = self.service.get_popular(POPULAR_LIMIT)
        elif active_cat_data:
            visible_shortcuts = self.service.filter(self.filter_query, active_cat_data)
        else:
            visible_shortcuts = self.service.filter(self.filter_query)

        visible_shortcuts.append(Shortcut(
            name=get_string("dev_info"),
            url=DEV_URL,
            browser="default",
            category="General"
        ))

        for i, shortcut in enumerate(visible_shortcuts):
            card = ShortcutCard(shortcut, self._open_shortcut)
            self.grid_layout.addWidget(card, i // GRID_COLS, i % GRID_COLS)
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
        self.grid_widget.updateGeometry()
        self.grid_widget.show()
        self.grid_widget.update()

    def _clear_effect(self, widget):
        widget.setGraphicsEffect(None)

    def _open_shortcut(self, shortcut: Shortcut) -> None:
        if shortcut.url != DEV_URL:
            self.service.increment_clicks(shortcut)
            self._refresh_grid(animate=False)

        browser_key = shortcut.browser
        if browser_key == "default":
            browser_key = self.service.global_browser
        success = BrowserService.open_url(shortcut.url, browser_key, self.browsers)
        if not success:
            show_toast(get_string("msg_browser_error"), self)

    def _open_manager(self) -> None:
        dlg = ShortcutsDialog(self.service.shortcuts, self, self.service.global_browser)
        if dlg.exec():
            self.service.replace_all(dlg.shortcuts)
            self._update_category_tabs()
        self._setup_window_hotkeys()
        self._refresh_grid()
