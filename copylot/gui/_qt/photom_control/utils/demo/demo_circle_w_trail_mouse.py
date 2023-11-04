import sys
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import QWidget, QApplication


class CircleWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the position of the circle
        self.circle_pos = QPoint(50, 50)

        # Initialize the trail points
        self.trail_points = []

        # Create a timer to update the widget
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        # Enable mouse tracking
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the trail lines
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        for i in range(len(self.trail_points) - 1):
            painter.drawLine(self.trail_points[i], self.trail_points[i+1])

        # Draw the circle
        pen = QPen(Qt.NoPen)
        brush = QBrush(QColor(255, 0, 0))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self.circle_pos, 10, 10)

    def moveCircle(self, pos):
        # Update the circle position
        self.circle_pos = pos

        # Add the current position to the trail points
        self.trail_points.append(self.circle_pos)

        # Remove the oldest trail point if there are too many
        if len(self.trail_points) > 100:
            self.trail_points.pop(0)

    def mouseMoveEvent(self, event):
        # Move the circle to the mouse position
        self.moveCircle(event.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = CircleWidget()
    widget.resize(400, 400)
    widget.show()

    sys.exit(app.exec_())
