import sys
import os
import random
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QMovie, QColor, QPainter, QPixmap, QRegion, QPainterPath, QFontMetrics
from PyQt5.QtCore import Qt, QPoint, QTimer, QRectF, QSize
from diagram_bubble import BubbleLabel
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon


class DesktopPet(QWidget):

    def __init__(self, status_dict, win_size=200, gif_size=150):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Load background
        self.background = QPixmap("images/bg.png")
        if self.background.isNull():
            print("⚠️ Background image not found or invalid.")
        self.scaled_bg = None

        # Initialize status
        self.status_dict = status_dict
        self.status_name = None
        self.movie = None
        self.gif_size = QSize(gif_size, gif_size)
        self.win_size = QSize(win_size, win_size)
        self.movies = {
            name: QMovie(path)
            for name, path in self.status_dict.items()
        }
        for movie in self.movies.values():
            movie.setScaledSize(self.gif_size)

        # Setup pet label
        self.label = QLabel(self)

        # Setup dialogue bubble
        self.bubble = BubbleLabel("", None)
        self.bubble.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.bubble.setWordWrap(True)
        self.bubble.setFixedHeight(90)
        self.bubble.setMinimumWidth(80)
        self.bubble.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.bubble.hide()
        self.b_offset = QPoint(-20, -self.bubble.height() + 50)

        # Dragging
        self.drag_position = QPoint()

        # Initialize
        self.pick_random_stat(initial=True)
        self.start_status_timer()
        self.lines = load_lines("lines.json")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.scaled_bg:
            painter.setOpacity(0.8)
            painter.drawPixmap(0, 0, self.scaled_bg)
        else:
            painter.setBrush(QColor(128, 128, 128, 160))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

    def resizeEvent(self, event):
        if not self.background.isNull():
            self.scaled_bg = self.background.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        super().resizeEvent(event)

    def pick_random_stat(self, initial=False):
        old_status = self.status_name
        possible_statuses = list(self.status_dict.keys())
        if old_status in possible_statuses:
            possible_statuses.remove(old_status)
        self.status_name = random.choice(possible_statuses if possible_statuses else list(self.status_dict.keys()))
        new_gif = self.status_dict[self.status_name]

        print(f"🎭 Switching status → {self.status_name}")

        # Replace movie
        if self.movie:
            self.movie.stop()
            self.label.clear()

        self.movie = self.movies[self.status_name]
        self.label.setMovie(self.movie)
        self.movie.start()

        if initial:
            self.movie.frameChanged.connect(self.adjust_size)
        else:
            self.center_gif()

    def adjust_size(self):
        if self.gif_size.width() > 0 and self.gif_size.height() > 0:
            self.resize(self.win_size)
            self.center_gif()
            self.movie.frameChanged.disconnect(self.adjust_size)

            # Rounded mask
            radius = 90
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.rect()), radius, radius)
            self.setMask(QRegion(path.toFillPolygon().toPolygon()))

            self.show()

    def center_gif(self):
        offset_x = (self.win_size.width() - self.gif_size.width()) // 2
        self.label.resize(self.gif_size)
        self.label.move(offset_x, self.win_size.height()-self.gif_size.height())

    def start_status_timer(self):
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.on_status_timer)
        self.status_timer.start(random.randint(15000, 30000))

    def on_status_timer(self):
        self.pick_random_stat()
        self.status_timer.start(random.randint(15000, 30000))

    def update_bubble_text(self, line: str):
        self.bubble.setText(line)

        # Compute required width based on font metrics
        metrics = QFontMetrics(self.bubble.font())
        max_line_width = metrics.width(line) + 20
        wrapped_width = min(max_line_width, 300)

        self.bubble.setFixedWidth(wrapped_width)
        self.bubble.update()
        self.bubble.repaint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

            if self.bubble.isVisible():
                self.bubble.hide()
                self.bubble.clear()
                self.bubble.repaint()

            if self.status_name in self.lines:
                line = random.choice(self.lines[self.status_name])
            else:
                line = "……"

            self.update_bubble_text(line)
            # self.bubble.setText(line)
            # self.bubble.adjustSize()
            # size = self.bubble.sizeHint()
            # print(size.width())
            # self.bubble.setFixedWidth(min(size.width(), self.bubble.maximumWidth()))  # Force consistent redraw
            self.bubble.move(self.mapToGlobal(QPoint(0, 0)) + self.b_offset)
            self.bubble.show()

            self.bubble.timer.start(10000)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()

            # Move bubble with window if visible
            if self.bubble.isVisible():
                self.bubble.move(self.mapToGlobal(QPoint(0, 0)) + self.b_offset)


def load_gif_statuses(folder_path):
    status_dict = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".gif"):
            status_name = os.path.splitext(filename)[0]
            gif_path = os.path.join(folder_path, filename)
            status_dict[status_name] = gif_path
    return status_dict


def load_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set tray icon
    tray_icon = QSystemTrayIcon(QIcon("images/icon.png"), parent=app)
    tray_icon.setToolTip("DesktopPet")

    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    gif_folder = "./GIF"
    statuses = load_gif_statuses(gif_folder)

    win = DesktopPet(statuses, 250, 230)
    win.show()

    sys.exit(app.exec_())
