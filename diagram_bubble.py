from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QTimer


class BubbleLabel(QLabel):
    def __init__(self, text="", parent=None):
        # Set Background
        super().__init__(text, parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: black;")  # text color only
        self.radius = 8
        self.bg_color = QColor(255, 255, 160, 255)  # yellow-ish
        self.border_color = QColor(0, 0, 0)
        self.setContentsMargins(10, 6, 10, 6)

        # Timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        # Draw background
        painter.setBrush(self.bg_color)
        painter.setPen(self.border_color)
        painter.drawRoundedRect(rect, self.radius, self.radius)

        # Draw text on top
        super().paintEvent(event)

