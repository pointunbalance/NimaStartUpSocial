"""
StatsWidget - Displays usage statistics as a visual chart.
"""
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


COLORS = [
    "#0d9488", "#0ea5e9", "#8b5cf6", "#f59e0b",
    "#ef4444", "#10b981", "#6366f1", "#ec4899",
]


class StatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.title = QLabel("📊  Usage Statistics")
        self.title.setStyleSheet("color: #f8fafc; font-size: 16px; font-weight: 700; background: transparent;")
        layout.addWidget(self.title)

        self.chart_container = QWidget()
        self.chart_container.setFixedHeight(160)
        self.chart_container.setStyleSheet("background: transparent;")
        layout.addWidget(self.chart_container)

        self.legend_container = QWidget()
        self.legend_container.setStyleSheet("background: transparent;")
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(4)
        layout.addWidget(self.legend_container)

        layout.addStretch(1)

    def set_data(self, shortcuts):
        total_clicks = sum(s.clicks for s in shortcuts)
        if total_clicks == 0:
            self.data = []
            self.update()
            return

        sorted_shortcuts = sorted(shortcuts, key=lambda s: s.clicks, reverse=True)
        top = sorted_shortcuts[:8]
        self.data = [(s.name, s.clicks) for s in top]
        self._update_legend()
        self.update()

    def _update_legend(self):
        while self.legend_layout.count():
            child = self.legend_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, (name, clicks) in enumerate(self.data):
            color = COLORS[i % len(COLORS)]
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(8)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px; background: transparent;")
            row_layout.addWidget(dot)

            name_label = QLabel(name)
            name_label.setStyleSheet("color: #e2e8f0; font-size: 12px; background: transparent;")
            row_layout.addWidget(name_label)

            row_layout.addStretch(1)

            count_label = QLabel(str(clicks))
            count_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; background: transparent;")
            row_layout.addWidget(count_label)

            self.legend_layout.addWidget(row)

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self.chart_container)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.chart_container.rect()
        cx = rect.width() // 2
        cy = rect.height() // 2
        radius = min(cx, cy) - 10

        total = sum(count for _, count in self.data)
        if total == 0:
            painter.end()
            return

        start_angle = 0
        for i, (name, count) in enumerate(self.data):
            color = QColor(COLORS[i % len(COLORS)])
            span_angle = int(360 * 16 * count / total)

            painter.setBrush(color)
            painter.setPen(QPen(QColor(15, 23, 42), 2))
            painter.drawPie(
                QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
                start_angle, span_angle
            )
            start_angle += span_angle

        inner_radius = radius * 0.55
        painter.setBrush(QColor(15, 23, 42, 230))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            QRectF(cx - inner_radius, cy - inner_radius, inner_radius * 2, inner_radius * 2)
        )

        painter.setPen(QColor("#f8fafc"))
        font = QFont("Segoe UI", 14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            QRectF(cx - inner_radius, cy - 12, inner_radius * 2, 24),
            Qt.AlignmentFlag.AlignCenter,
            str(total)
        )

        painter.setPen(QColor("#94a3b8"))
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.drawText(
            QRectF(cx - inner_radius, cy + 6, inner_radius * 2, 16),
            Qt.AlignmentFlag.AlignCenter,
            "Total Clicks"
        )

        painter.end()
