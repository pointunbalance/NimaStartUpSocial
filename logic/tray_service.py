"""
TrayService - Handles the system tray icon, context menu, and window visibility.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from utils.strings import get_string
from utils.resource_loader import get_app_icon

class SystemTrayService(QSystemTrayIcon):
    def __init__(self, window, parent=None):
        super().__init__(get_app_icon(), parent)
        self.window = window
        self.setToolTip(get_string("app_name"))
        
        self._setup_menu()
        self.activated.connect(self._on_activated)

    def _setup_menu(self):
        menu = QMenu()
        
        show_action = QAction(get_string("btn_open"), self)
        show_action.triggered.connect(self.window.show_and_activate)
        
        quit_action = QAction("إغلاق نهائي", self) # Fixed Arabic for "Quit"
        quit_action.triggered.connect(self.window.quit_application)
        
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.window.isVisible():
                self.window.hide()
            else:
                self.window.show_and_activate()
