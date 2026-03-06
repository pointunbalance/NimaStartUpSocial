"""
MainWindow - Primary application window with glassmorphism UI,
drag-and-drop reordering, system tray integration, and quick filtering.
"""
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from PyQt6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer, 
    QThread, pyqtSignal
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QGridLayout, QCheckBox,
    QGraphicsOpacityEffect, QFrame, QLineEdit, QApplication,
    QComboBox, QTabBar
)
from PyQt6.QtGui import QColor, QShortcut, QKeySequence

from database.config_manager import ConfigManager
from logic.browser_service import BrowserService
from logic.autostart_service import AutostartService
from logic.catalog_service import SiteCatalog, Shortcut
from logic.tray_service import SystemTrayService
from ui.widgets.shortcut_card import ShortcutCard
from ui.widgets.toast_widget import show_toast
from ui.widgets.dashboard_widget import DashboardWidget

from ui.shortcuts_dialog import ShortcutsDialog
from utils.strings import get_string
from utils.resource_loader import get_app_icon
from utils.window_blur import WindowBlurService
from utils.logger_service import logger

# Grid constants
GRID_COLS = 5
TILE_SPACING = 20
TILE_SIZE = 160
TILE_STEP = TILE_SIZE + TILE_SPACING  # 180

class TitleFetcher(QThread):
    finished = pyqtSignal(str, str) # URL, Title

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else ""
                if title:
                    self.finished.emit(self.url, title)
        except requests.exceptions.ConnectionError:
            logger.debug(f"Title fetch failed: No internet connection.")
        except Exception as e:
            logger.debug(f"Title fetch failed for {self.url}: {e}")

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{get_string('app_name')} v1.7.1")
        self.setWindowIcon(get_app_icon())
        self.resize(1100, 750)
        self.setMinimumSize(800, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        try:
            WindowBlurService.enable_acrylic(self, QColor(255, 255, 255, 40))
        except Exception as e:
            logger.warning(f"Acrylic blur unavailable: {e}")

        self._old_pos = None
        self._anims: list = []
        self.shortcuts, self.global_browser = ConfigManager.load()
        self.browsers = BrowserService.get_installed_browsers()
        self.filter_query = ""

        self._build_ui()
        self._setup_window_hotkeys()
        self._setup_shortcuts()
        
        # System Tray Integration
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

        # Quick Filter Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(get_string("placeholder_search"))
        self.search_input.setObjectName("mainSearchInput")
        self.search_input.setFixedWidth(300)
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

        # Category Tabs
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

        # Dashboard Widget [v1.5]
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

        # Global Browser Selection
        browser_label = QLabel(get_string("label_global_browser"))
        browser_label.setStyleSheet("color: #475569; font-weight: 500;")
        footer.addWidget(browser_label)

        self.browser_combo = QComboBox()
        self.browser_combo.setObjectName("browserSelector")
        self.browser_combo.setFixedWidth(200)
        self.browser_combo.addItem(get_string("browser_default"), "default")
        
        for key, path in self.browsers.items():
            name = get_string(f"browser_{key}")
            self.browser_combo.addItem(name, key)
        
        # Select current
        idx = self.browser_combo.findData(self.global_browser)
        if idx != -1:
            self.browser_combo.setCurrentIndex(idx)
        
        self.browser_combo.currentIndexChanged.connect(self._on_global_browser_changed)
        footer.addWidget(self.browser_combo)

        layout.addLayout(footer)

    def _on_global_browser_changed(self, index):
        self.global_browser = self.browser_combo.itemData(index)
        ConfigManager.save(self.shortcuts, self.global_browser)
        show_toast(get_string("msg_browser_saved"), self)

    def _setup_window_hotkeys(self):
        # Clear existing
        if hasattr(self, "_shortcut_bindings"):
            for s in self._shortcut_bindings:
                s.setEnabled(False)
                s.deleteLater()
        
        self._shortcut_bindings = []
        for s in self.shortcuts:
            if s.hotkey:
                qs = QShortcut(QKeySequence(s.hotkey), self)
                qs.activated.connect(lambda target=s: self._open_shortcut(target))
                self._shortcut_bindings.append(qs)

    def _on_search_changed(self, text):
        self.filter_query = text.strip().lower()
        self._refresh_grid(animate=False)

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
        
        if not url: return
            
        pos = event.position().toPoint()
        src_idx = next((i for i, s in enumerate(self.shortcuts) if s.url == url), -1)
        
        if src_idx == -1:
            self._handle_external_drop(url, event)
        else:
            self._handle_internal_reorder(src_idx, url, pos, event)

    def _handle_external_drop(self, url: str, event) -> None:
        info = SiteCatalog.find_by_url(url)
        if info:
            name, name_en = info[1], info[2]
        else:
            host = urlparse(url).netloc.replace("www.", "")
            name = name_en = host or url[:30]
        
        if any(SiteCatalog.get_host(s.url) == SiteCatalog.get_host(url) for s in self.shortcuts):
            show_toast("هذا الموقع موجود بالفعل!", self)
            event.accept()
            return
        
        new_shortcut = Shortcut(name=name, url=url, browser="default", name_en=name_en)
        self.shortcuts.append(new_shortcut)
        ConfigManager.save(self.shortcuts, self.global_browser)
        
        # Async title fetch
        self._fetcher = TitleFetcher(url)
        self._fetcher.finished.connect(self._on_title_fetched)
        self._fetcher.start()
        
        QTimer.singleShot(50, lambda: self._refresh_grid(animate=False))
        self._update_category_tabs()
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        show_toast(f"تمت إضافة: {name}", self)

    def _on_title_fetched(self, url, title):
        for s in self.shortcuts:
            if s.url == url:
                host = urlparse(url).netloc.replace("www.", "")
                if s.name == host:
                    s.name = title[:25] + ("..." if len(title) > 25 else "")
                    ConfigManager.save(self.shortcuts, self.global_browser)
                    self._refresh_grid(animate=False)
                break

    def _handle_internal_reorder(self, src_idx: int, url: str, pos: QPoint, event) -> None:
        target_idx = self._find_target_index(pos)
        if target_idx != -1 and target_idx != src_idx:
            item = self.shortcuts.pop(src_idx)
            self.shortcuts.insert(target_idx, item)
            ConfigManager.save(self.shortcuts, self.global_browser)
            QTimer.singleShot(50, lambda: self._refresh_grid(animate=False))
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()

    def _find_target_index(self, pos: QPoint) -> int:
        child = self.grid_widget.childAt(pos)
        if child:
            parent = child
            while parent and not isinstance(parent, ShortcutCard):
                parent = parent.parentWidget()
            if parent and isinstance(parent, ShortcutCard):
                for i, s in enumerate(self.shortcuts):
                    if s.url == parent.shortcut.url:
                        return i
        
        grid_w = self.grid_widget.width()
        col = (grid_w - pos.x()) // TILE_STEP
        row = pos.y() // TILE_STEP
        return min(len(self.shortcuts) - 1, max(0, row * GRID_COLS + col))

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
        
        if not url: return
            
        pos = event.position().toPoint()
        src_idx = next((i for i, s in enumerate(self.shortcuts) if s.url == url), -1)
        
        if src_idx == -1:
            self._handle_external_drop(url, event)
        else:
            self._handle_internal_reorder(src_idx, url, pos, event)

    def _handle_external_drop(self, url: str, event) -> None:
        info = SiteCatalog.find_by_url(url)
        if info:
            name, name_en = info[1], info[2]
        else:
            host = urlparse(url).netloc.replace("www.", "")
            name = name_en = host or url[:30]
        
        if any(SiteCatalog.get_host(s.url) == SiteCatalog.get_host(url) for s in self.shortcuts):
            show_toast(get_string("msg_site_exists"), self)
            event.accept()
            return
        
        new_shortcut = Shortcut(name=name, url=url, browser="default", name_en=name_en)
        self.shortcuts.append(new_shortcut)
        ConfigManager.save(self.shortcuts, self.global_browser)
        
        # Async title fetch
        self._fetcher = TitleFetcher(url)
        self._fetcher.finished.connect(self._on_title_fetched)
        self._fetcher.start()
        
        QTimer.singleShot(50, lambda: self._refresh_grid(animate=False))
        self._update_category_tabs()
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        show_toast(f"{get_string('msg_added')} {name}", self)

    def _on_title_fetched(self, url, title):
        for s in self.shortcuts:
            if s.url == url:
                host = urlparse(url).netloc.replace("www.", "")
                if s.name == host:
                    s.name = title[:25] + ("..." if len(title) > 25 else "")
                    ConfigManager.save(self.shortcuts, self.global_browser)
                    self._refresh_grid(animate=False)
                break

    def _handle_internal_reorder(self, src_idx: int, url: str, pos: QPoint, event) -> None:
        target_idx = self._find_target_index(pos)
        if target_idx != -1 and target_idx != src_idx:
            item = self.shortcuts.pop(src_idx)
            self.shortcuts.insert(target_idx, item)
            ConfigManager.save(self.shortcuts, self.global_browser)
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
        
        cats = sorted(list(set(s.category for s in self.shortcuts if s.category)))
        for cat in cats:
            display_name = cat
            if cat == "AI": display_name = get_string("cat_ai")
            elif cat == "Social": display_name = get_string("cat_social")
            elif cat == "Work": display_name = get_string("cat_work")
            elif cat == "General": display_name = get_string("cat_general")
            
            self.category_tabs.addTab(display_name)
            self.category_tabs.setTabData(self.category_tabs.count()-1, cat)

        # Restore index
        for i in range(self.category_tabs.count()):
            if i == 0:
                if current == get_string("cat_all"):
                    self.category_tabs.setCurrentIndex(i)
                    break
            elif self.category_tabs.tabText(i) == current or self.category_tabs.tabData(i) == current:
                self.category_tabs.setCurrentIndex(i)
                break
        
        self.category_tabs.blockSignals(False)

    def _refresh_grid(self, animate: bool = True) -> None:
        # Clear existing
        self._anims.clear()
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get active category
        current_idx = self.category_tabs.currentIndex()
        selected_cat_text = self.category_tabs.tabText(current_idx)
        active_cat_data = self.category_tabs.tabData(current_idx)
        
        # Sort and Filter [v1.6]
        # Default: Sort by clicks descending
        sorted_shortcuts = sorted(self.shortcuts, key=lambda x: x.clicks, reverse=True)
        
        visible_shortcuts = []
        for s in sorted_shortcuts:
            matches_search = (
                not self.filter_query or 
                self.filter_query in s.name.lower() or 
                self.filter_query in s.name_en.lower() or 
                self.filter_query in s.url.lower()
            )
            
            is_popular_tab = (selected_cat_text == get_string("cat_popular"))
            
            if is_popular_tab:
                # Popular shows top 10 with at least 1 click
                matches_category = (len(visible_shortcuts) < 10 and s.clicks > 0)
            else:
                matches_category = (
                    not active_cat_data or 
                    s.category == active_cat_data
                )
            
            if matches_search and matches_category:
                visible_shortcuts.append(s)

        # Permanent Developer Shortcut [Fixed at the end]
        dev_shortcut = Shortcut(
            name=get_string("dev_info"),
            url="https://www.facebook.com/profile.php?id=61585982617699",
            browser="default",
            category="General"
        )
        visible_shortcuts.append(dev_shortcut)

        for i, shortcut in enumerate(visible_shortcuts):
            card = ShortcutCard(shortcut, self._open_shortcut)
            self.grid_layout.addWidget(card, i // GRID_COLS, i % GRID_COLS)
            if animate:
                eff = QGraphicsOpacityEffect(card)
                card.setGraphicsEffect(eff)
                eff.setOpacity(0)
                anim = QPropertyAnimation(eff, b"opacity")
                anim.setDuration(400 + (i * 80))
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._anims.append(anim)
                anim.finished.connect(lambda e=eff, c=card: c.setGraphicsEffect(None))
                anim.start()
            else:
                card.show()

        self.grid_layout.activate()
        self.grid_widget.adjustSize()
        self.grid_widget.updateGeometry()
        self.grid_widget.show()
        self.grid_widget.update()

    def _open_shortcut(self, shortcut: Shortcut) -> None:
        # Skip click tracking for developer shortcut (transient object)
        DEV_URL = "https://www.facebook.com/profile.php?id=61585982617699"
        if shortcut.url != DEV_URL:
            shortcut.clicks += 1
            ConfigManager.save(self.shortcuts, self.global_browser)
        
        browser_key = shortcut.browser
        if browser_key == "default":
            browser_key = self.global_browser
        success = BrowserService.open_url(shortcut.url, browser_key, self.browsers)
        if not success:
            show_toast(get_string("msg_browser_error"), self)

    def _open_manager(self) -> None:
        dlg = ShortcutsDialog(self.shortcuts, self)
        if dlg.exec():
            self.shortcuts = dlg.shortcuts
            ConfigManager.save(self.shortcuts, self.global_browser)
            self._update_category_tabs()
        self._setup_window_hotkeys()
        self._refresh_grid()
