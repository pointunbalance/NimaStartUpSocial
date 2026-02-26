"""
DashboardWidget - A sleek glassmorphism widget for the main window.
Displays real-time clock, date, and a welcome message.
"""
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
import getpass
from utils.strings import get_string

class DashboardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardWidget")
        self.setFixedHeight(120)
        
        self._build_ui()
        
        # Timer for real-time clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        # Left Side: Welcome Message & Date
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        user_name = getpass.getuser()
        self.welcome_label = QLabel(f"{get_string('dash_welcome')} {user_name}")
        self.welcome_label.setObjectName("dashWelcome")
        
        self.date_label = QLabel()
        self.date_label.setObjectName("dashDate")
        
        info_layout.addWidget(self.welcome_label)
        info_layout.addWidget(self.date_label)
        layout.addLayout(info_layout)
        
        layout.addStretch(1)
        
        # Right Side: Clock
        self.clock_label = QLabel()
        self.clock_label.setObjectName("dashClock")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.clock_label)

    def _update_time(self):
        now = QDateTime.currentDateTime()
        
        # Format Time: HH:mm:ss
        self.clock_label.setText(now.toString("hh:mm:ss AP"))
        
        # Format Date: Today is: DD MMMM YYYY
        date_str = now.toString("dd MMMM yyyy")
        self.date_label.setText(f"{get_string('dash_date_prefix')} {date_str}")
