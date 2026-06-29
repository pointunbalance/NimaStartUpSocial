from typing import List
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QPushButton, QFrame, QFormLayout, QListWidgetItem, QAbstractItemView, QMessageBox,
    QFileDialog
)
from PyQt6.QtGui import QColor
from pathlib import Path
from logic.catalog_service import Shortcut, SiteCatalog
from database.config_manager import ConfigManager
from utils.strings import get_string
from utils.window_blur import WindowBlurService
from utils.logger_service import logger

class ShortcutsDialog(QDialog):
    def __init__(self, shortcuts: List[Shortcut], parent=None, global_browser: str = "default") -> None:
        super().__init__(parent)
        self.shortcuts = [Shortcut(s.name, s.url, s.browser, s.name_en, s.category, s.hotkey, s.clicks) for s in shortcuts]
        self.global_browser = global_browser
        self.filtered_indices: List[int] = []
        self.filter_text = ""
        self._rebuilding_list = False
        self.setWindowTitle(get_string("shortcuts_manager_title"))
        if parent is not None and hasattr(parent, "windowIcon"):
            self.setWindowIcon(parent.windowIcon())
        self.resize(850, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Enable Glass Effect
        try:
            WindowBlurService.enable_acrylic(self, QColor(255, 255, 255, 5))
        except Exception as e:
            logger.debug(f"Acrylic blur unavailable in dialog: {e}")

        self._old_pos = None
        self._build_ui()
        self._refresh(0)
        self._position_window()

    def _position_window(self) -> None:
        parent = self.parentWidget()
        if parent:
            parent_geo = parent.geometry()
            margin = 32
            # Accurate positioning for larger size
            w, h = 850, 600 
            target_x = parent_geo.right() - w - margin
            target_y = parent_geo.bottom() - h - margin
            self.move(target_x, target_y)

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
        self.setObjectName("shortcutsDialog")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        
        self.main_frame = QFrame()
        self.main_frame.setObjectName("centralWidget") # Use same styling as MainWindow
        root.addWidget(self.main_frame)
        
        main_layout = QVBoxLayout(self.main_frame)
        main_layout.setContentsMargins(28, 28, 28, 24)
        main_layout.setSpacing(20)

        title_row = QHBoxLayout()
        title_row.setDirection(QHBoxLayout.Direction.RightToLeft)
        
        title = QLabel(get_string("shortcuts_manager_title"))
        title.setObjectName("windowMainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet("font-size: 24px;")
        title_row.addWidget(title)
        title_row.addStretch(1)

        main_layout.addLayout(title_row)

        content = QHBoxLayout()
        content.setDirection(QHBoxLayout.Direction.RightToLeft)
        content.setSpacing(14)

        # Right Panel (List)
        right_frame = QFrame()
        right_frame.setObjectName("listPanel")
        right = QVBoxLayout(right_frame)
        right.setContentsMargins(12, 12, 12, 12)
        right.setSpacing(10)
        
        right_title = QLabel(get_string("section_shortcuts"))
        right_title.setObjectName("sectionTitle")
        right_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
        right.addWidget(right_title)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(get_string("placeholder_search"))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.search_input.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.search_input.setMinimumHeight(34)
        self.search_input.textChanged.connect(self._on_search_changed)
        right.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("shortcutsList")
        self.list_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.currentRowChanged.connect(self._on_pick)
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)
        right.addWidget(self.list_widget, 1)

        right_buttons = QHBoxLayout()
        right_buttons.setDirection(QHBoxLayout.Direction.RightToLeft)
        add_btn = QPushButton(get_string("btn_add"))
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._add)
        del_btn = QPushButton(get_string("btn_delete"))
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self._delete)
        right_buttons.addWidget(add_btn)
        right_buttons.addWidget(del_btn)
        right_buttons.addStretch(1)
        right.addLayout(right_buttons)

        io_row = QHBoxLayout()
        io_row.setDirection(QHBoxLayout.Direction.RightToLeft)
        import_btn = QPushButton(get_string("btn_import"))
        import_btn.setObjectName("secondaryBtn")
        import_btn.clicked.connect(self._import_shortcuts)
        export_btn = QPushButton(get_string("btn_export"))
        export_btn.setObjectName("secondaryBtn")
        export_btn.clicked.connect(self._export_shortcuts)
        io_row.addWidget(import_btn)
        io_row.addWidget(export_btn)
        io_row.addStretch(1)
        right.addLayout(io_row)
        right_frame.setMinimumWidth(280)

        # Left Panel (Editor)
        left_frame = QFrame()
        left_frame.setObjectName("editorPanel")
        left = QVBoxLayout(left_frame)
        left.setContentsMargins(14, 14, 14, 14)
        left.setSpacing(12)
        left_title = QLabel(get_string("section_details"))
        left_title.setObjectName("sectionTitle")
        left_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        left_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
        left.addWidget(left_title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setHorizontalSpacing(12)
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(get_string("placeholder_name"))
        self.name_input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.name_input.setMinimumHeight(36)
        
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText(get_string("placeholder_name_en"))
        self.name_en_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.name_en_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.name_en_input.setMinimumHeight(36)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(get_string("placeholder_url"))
        self.url_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.url_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.url_input.setMinimumHeight(36)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(get_string("cat_general"))
        self.category_input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.category_input.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.category_input.setMinimumHeight(36)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText(get_string("placeholder_hotkey"))
        self.hotkey_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.hotkey_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.hotkey_input.setMinimumHeight(36)

        form.addRow(get_string("label_name"), self.name_input)
        form.addRow(get_string("label_name_en"), self.name_en_input)
        form.addRow(get_string("label_url"), self.url_input)
        form.addRow(get_string("label_category"), self.category_input)
        form.addRow(get_string("label_hotkey"), self.hotkey_input)
        left.addLayout(form)

        apply_row = QHBoxLayout()
        apply_row.setDirection(QHBoxLayout.Direction.RightToLeft)
        apply_btn = QPushButton(get_string("btn_apply"))
        apply_btn.clicked.connect(self._apply)
        apply_row.addWidget(apply_btn)
        apply_row.addStretch(1)
        left.addLayout(apply_row)
        left.addStretch(1)

        content.addWidget(right_frame, 1)
        content.addWidget(left_frame, 2)

        footer = QHBoxLayout()
        footer.setDirection(QHBoxLayout.Direction.RightToLeft)
        save_btn = QPushButton(get_string("btn_save_close"))
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_close)
        cancel_btn = QPushButton(get_string("btn_cancel"))
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(save_btn)
        footer.addWidget(cancel_btn)
        footer.addStretch(1)

        main_layout.addLayout(content, 1)
        main_layout.addLayout(footer)

    def _refresh(self, pick: int) -> None:
        self._rebuilding_list = True
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        query = self.filter_text.strip().lower()
        self.filtered_indices = []
        for idx, s in enumerate(self.shortcuts):
            if not query or query in f"{s.name} {s.name_en} {s.url}".lower():
                self.filtered_indices.append(idx)

        for idx in self.filtered_indices:
            s = self.shortcuts[idx]
            item = QListWidgetItem(s.name)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)
        self._rebuilding_list = False

        if not self.shortcuts or not self.filtered_indices:
            self._clear_editor()
            return

        target_row = 0
        if pick in self.filtered_indices:
            target_row = self.filtered_indices.index(pick)
        self.list_widget.setCurrentRow(target_row)

    def _on_pick(self, _: int) -> None:
        idx = self._get_current_index()
        if idx < 0:
            self._clear_editor()
            return
        s = self.shortcuts[idx]
        self.name_input.setText(s.name)
        self.name_en_input.setText(s.name_en)
        self.url_input.setText(s.url)
        self.category_input.setText(s.category)
        self.hotkey_input.setText(s.hotkey)

    def _get_current_index(self) -> int:
        item = self.list_widget.currentItem()
        if not item: return -1
        idx = item.data(Qt.ItemDataRole.UserRole)
        return idx if isinstance(idx, int) else -1

    def _on_search_changed(self, text: str) -> None:
        self.filter_text = text
        self._refresh(self._get_current_index())

    def _on_rows_moved(self, *_) -> None:
        # Reordering only works when not filtering
        if self._rebuilding_list or self.filter_text.strip():
            return
        reordered = []
        for i in range(self.list_widget.count()):
            idx = self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            reordered.append(self.shortcuts[idx])
        self.shortcuts = reordered
        self._refresh(self.list_widget.currentRow())

    def _clear_editor(self) -> None:
        self.name_input.clear()
        self.name_en_input.clear()
        self.url_input.clear()
        self.category_input.clear()
        self.hotkey_input.clear()

    def _add(self) -> None:
        self.shortcuts.append(Shortcut("جديد", "https://", "default", "New", "General"))
        self._refresh(len(self.shortcuts) - 1)

    def _delete(self) -> None:
        idx = self._get_current_index()
        if idx < 0: return
        self.shortcuts.pop(idx)
        self._refresh(min(idx, len(self.shortcuts) - 1))

    def _apply(self) -> None:
        idx = self._get_current_index()
        if idx < 0: return
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        if not name or not url: return
        n1, n2 = SiteCatalog.normalize(name, self.name_en_input.text().strip(), url)
        self.shortcuts[idx] = Shortcut(
            n1, url, self.shortcuts[idx].browser, n2, 
            self.category_input.text().strip() or "General",
            self.hotkey_input.text().strip(),
            self.shortcuts[idx].clicks
        )
        self._refresh(idx)

    def _save_close(self) -> None:
        self.accept()

    def _import_shortcuts(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, get_string("btn_import"), "", "JSON Files (*.json)"
        )
        if not path:
            return
        
        try:
            shortcuts, _ = ConfigManager.import_shortcuts(Path(path))
            if shortcuts:
                self.shortcuts = shortcuts
                self._refresh(0)
                from ui.widgets.toast_widget import show_toast
                show_toast(get_string("msg_import_success"), self)
        except Exception as e:
            QMessageBox.critical(self, get_string("shortcuts_manager_title"), get_string("msg_import_error"))

    def _export_shortcuts(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, get_string("btn_export"), "shortcuts_backup.json", "JSON Files (*.json)"
        )
        if not path:
            return
            
        try:
            ConfigManager.export_shortcuts(Path(path), self.shortcuts, self.global_browser)
            from ui.widgets.toast_widget import show_toast
            show_toast(get_string("msg_export_success"), self)
        except Exception as e:
            QMessageBox.critical(self, get_string("shortcuts_manager_title"), str(e))
