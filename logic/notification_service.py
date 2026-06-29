"""
NotificationService - Smart notifications for the application.
"""
from datetime import datetime
from typing import Optional


class Notification:
    def __init__(self, title: str, message: str, category: str = "info"):
        self.title = title
        self.message = message
        self.category = category
        self.timestamp = datetime.now()
        self.read = False

    def mark_read(self):
        self.read = True

    def __str__(self):
        return f"[{self.category}] {self.title}: {self.message}"


class NotificationService:
    _notifications = []
    _max_notifications = 50

    @classmethod
    def add(cls, title: str, message: str, category: str = "info") -> Notification:
        n = Notification(title, message, category)
        cls._notifications.insert(0, n)
        if len(cls._notifications) > cls._max_notifications:
            cls._notifications = cls._notifications[:cls._max_notifications]
        return n

    @classmethod
    def get_all(cls, unread_only: bool = False) -> list:
        if unread_only:
            return [n for n in cls._notifications if not n.read]
        return cls._notifications

    @classmethod
    def get_unread_count(cls) -> int:
        return sum(1 for n in cls._notifications if not n.read)

    @classmethod
    def mark_all_read(cls):
        for n in cls._notifications:
            n.read = True

    @classmethod
    def clear(cls):
        cls._notifications.clear()

    @classmethod
    def notify_shortcut_added(cls, name: str):
        cls.add("shortcut_added", name, "success")

    @classmethod
    def notify_shortcut_removed(cls, name: str):
        cls.add("shortcut_removed", name, "warning")

    @classmethod
    def notify_browser_error(cls):
        cls.add("browser_error", "msg_browser_error", "error")

    @classmethod
    def notify_import_success(cls, count: int):
        cls.add("import_success", f"{count} shortcuts imported", "success")

    @classmethod
    def notify_export_success(cls):
        cls.add("export_success", "msg_export_success", "success")

    @classmethod
    def notify_backup_created(cls):
        cls.add("backup_created", "Backup created successfully", "info")
